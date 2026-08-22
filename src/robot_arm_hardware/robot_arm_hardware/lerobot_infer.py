"""lerobot_infer — ACT policy inference for the real arm (front camera only).

Loads the HF ACT policy (shreeshinator/arm-pick-blocks-act-first) trained on
shreeshinator/arm-picking-blocks-real (front camera @ 480x640, 5 joints)
and streams joint commands to /joint_command at 10 Hz.

Observation features (must match training):
  - observation.images.front  <- /front_cam/image_raw/compressed (CompressedImage)
  - observation.state        <- /joint_states (JointState, 5 values)
  - task                   <- fixed string "place the block in the bowl"

Action (JointState order):
  Float64MultiArray on /joint_command, 5 values [joint1,joint2,joint3,joint4,gripper]
  clamped to JOINT_LIMITS + gripper [0,1] for safety.

Uses the venv's lerobot 0.6.1 + torch. Run with:
  source /opt/ros/jazzy/setup.bash
  .venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args \
    -p hf_repo:=shreeshinator/arm-pick-blocks-act-first \
    -p dataset_repo:=shreeshinator/arm-picking-blocks-real \
    -p task:=\"place the block in the bowl\" \
    -p fps:=10.0 -p enable_robot:=false

Or via ros2 run:
  ros2 run robot_arm_hardware lerobot_infer --ros-args -p enable_robot:=true

Dry-run (enable_robot:=false) verifies the pipeline without moving hardware:
  logs predicted vs current state and distance. This is step 3 verification.
"""

import time
import threading

import cv2
import numpy as np
import torch

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage, JointState
from std_msgs.msg import Float64MultiArray, String


JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4", "gripper_joint"]
JOINT_LIMITS = {
    "joint1": (-3.14, 3.14),
    "joint2": (-1.57, 1.57),
    "joint3": (-1.57, 1.57),
    "joint4": (-1.57, 1.57),
}
GRIPPER_LIMITS = (0.0, 1.0)
EXPECTED_H = 480
EXPECTED_W = 640


def _decode_compressed(msg: CompressedImage) -> np.ndarray | None:
    """JPEG bytes -> RGB uint8 (H, W, 3). Returns None on failure."""
    try:
        arr = np.frombuffer(msg.data, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            return None # cv2.imdecode returns None on failure
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) # convert to RGB
    except Exception:
        return None


def _preprocess_image(
    rgb: np.ndarray,
    img_mean: np.ndarray | None = None,
    img_std: np.ndarray | None = None,
) -> torch.Tensor:
    """RGB uint8 (H,W,3) -> float32 CHW tensor, resized to 480x640 if needed.

    Pipeline matches training: uint8 -> float32 [0,1] (/255) -> (x - mean)/std.
    mean/std are (3,1,1) from policy_preprocessor_step_3_normalizer_processor.safetensors.
    If mean/std are None (offline test without HF cache), returns [0,1] only.
    Returns contiguous float32 tensor (no strided torch.from_numpy view).
    """
    h, w = rgb.shape[:2]
    if h != EXPECTED_H or w != EXPECTED_W:
        rgb = cv2.resize(rgb, (EXPECTED_W, EXPECTED_H), interpolation=cv2.INTER_AREA)
    # float32 /255 — use 255.0 as float32 literal, not float64 promotion
    f = rgb.astype(np.float32) / np.float32(255.0)
    chw = np.transpose(f, (2, 0, 1))  # HWC -> CHW, still float32
    if img_mean is not None and img_std is not None:
        # img_mean/std are (3,1,1) float32 — broadcast over H,W
        chw = (chw - img_mean) / (img_std + 1e-8)
    # ensure contiguous (transpose is strided; torch.from_numpy would keep stride)
    chw = np.ascontiguousarray(chw, dtype=np.float32)
    return torch.from_numpy(chw)


class LerobotInfer(Node):
    def __init__(self):
        super().__init__("lerobot_infer")

        self.declare_parameter("hf_repo", "shreeshinator/arm-pick-blocks-act-first")
        self.declare_parameter("dataset_repo", "shreeshinator/arm-picking-blocks-real")
        self.declare_parameter("task", "place the block in the bowl")
        self.declare_parameter("fps", 15.0)
        self.declare_parameter("front_topic", "/front_cam/image_raw/compressed")
        self.declare_parameter("enable_robot", False)
        self.declare_parameter("device", "")  # auto if empty
        # auto-home: move to dataset recording start pose before policy runs
        self.declare_parameter("auto_home", True)
        self.declare_parameter("home_x", 0.27)
        self.declare_parameter("home_y", 0.0)
        self.declare_parameter("home_z", 0.08)
        self.declare_parameter("home_pitch", -1.57)
        self.declare_parameter("home_gripper", 0.0)
        self.declare_parameter("home_duration", 2.0)
        self.declare_parameter("home_delay", 0.5)  # extra settle after trajectory
        # bug 1 fix: executing 100 steps (10 s) is too stale at 10 Hz; override here
        self.declare_parameter("n_action_steps", 50)  # how many chunk steps to replay before re-querying vision; 50 = 3.33 s @15Hz (verified pick→place sweet spot; 100=6.6s too stale, 10 too twitchy)
        self.declare_parameter("temporal_ensemble_coeff", -1.0)  # <0 = disabled, >=0 enables temporal ensembling

        self.hf_repo = self.get_parameter("hf_repo").get_parameter_value().string_value
        self.dataset_repo = self.get_parameter("dataset_repo").get_parameter_value().string_value
        self.task_str = self.get_parameter("task").get_parameter_value().string_value
        self.fps = self.get_parameter("fps").get_parameter_value().double_value
        self.front_topic = self.get_parameter("front_topic").get_parameter_value().string_value
        self.enable_robot = self.get_parameter("enable_robot").get_parameter_value().bool_value
        dev_param = self.get_parameter("device").get_parameter_value().string_value
        self.auto_home = self.get_parameter("auto_home").get_parameter_value().bool_value
        self.home_x = self.get_parameter("home_x").get_parameter_value().double_value
        self.home_y = self.get_parameter("home_y").get_parameter_value().double_value
        self.home_z = self.get_parameter("home_z").get_parameter_value().double_value
        self.home_pitch = self.get_parameter("home_pitch").get_parameter_value().double_value
        self.home_gripper = self.get_parameter("home_gripper").get_parameter_value().double_value
        self.home_duration = self.get_parameter("home_duration").get_parameter_value().double_value
        self.home_delay = self.get_parameter("home_delay").get_parameter_value().double_value
        self.n_action_steps_param = self.get_parameter("n_action_steps").get_parameter_value().integer_value
        self.temporal_ensemble_coeff = self.get_parameter("temporal_ensemble_coeff").get_parameter_value().double_value

        if dev_param:
            self.device = dev_param
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.get_logger().info(
            f"lerobot_infer: hf_repo={self.hf_repo} dataset={self.dataset_repo} "
            f"task='{self.task_str}' device={self.device} fps={self.fps} "
            f"enable_robot={self.enable_robot} auto_home={self.auto_home}"
        )

        # -- load policy + normalization stats (blocking, downloads from HF on first run) --
        self.policy = self._load_policy()
        self.get_logger().info(
            f"policy loaded: {type(self.policy).__name__} chunk_size={self.policy.config.chunk_size} "
            f"n_action_steps={self.policy.config.n_action_steps} temporal_ensemble={self.policy.config.temporal_ensemble_coeff}"
        )
        # stats are populated inside _load_policy (img/state mean/std, action mean/std)
        if getattr(self, "_img_mean", None) is not None:
            self.get_logger().info(
                f"normalizer: VISUAL mean={self._img_mean.flatten().tolist()} std={self._img_std.flatten().tolist()} "
                f"STATE mean={self._state_mean.tolist()} std={self._state_std.tolist()} "
                f"ACTION mean={self._action_mean.tolist()} std={self._action_std.tolist()}"
            )
        else:
            self.get_logger().warn("normalizer stats not loaded — falling back to raw [0,1] images (distribution shift!)")

        # -- ROS I/O --
        self._lock = threading.Lock()
        self._latest_front: CompressedImage | None = None
        self._latest_front_t = 0.0
        self._latest_state: JointState | None = None
        self._latest_state_t = 0.0
        self._homed = False
        self._timer = None

        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(CompressedImage, self.front_topic, self._on_front, img_qos)
        self.create_subscription(JointState, "/joint_states", self._on_state, 10)
        self.create_subscription(String, "/lerobot_infer/command", self._on_command, 10)

        self._pub = self.create_publisher(Float64MultiArray, "/joint_command", 10)

        # home service client (used once at startup if auto_home)
        from modular_arm_interfaces.srv import MoveTo as MoveToSrv
        self._MoveToSrv = MoveToSrv
        self._move_client = self.create_client(MoveToSrv, "/modular_arm/move_to")

        self._step = 0
        self._last_pred: np.ndarray | None = None

        mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
        self._home_timer = None
        if self.auto_home:
            self.get_logger().info(
                f"auto_home enabled -> will call /modular_arm/move_to "
                f"x={self.home_x:.3f} y={self.home_y:.3f} z={self.home_z:.3f} "
                f"pitch={self.home_pitch:.2f} gripper={self.home_gripper:.1f} duration={self.home_duration:.1f}s "
                f"then delay {self.home_delay:.1f}s before policy"
            )
            # defer homing slightly so hw_move_to has time to appear
            self._home_timer = self.create_timer(1.0, self._do_home_once)
        else:
            self.get_logger().info(f"auto_home disabled — starting policy immediately ({mode})")
            self._start_policy_timer(mode)

    # -- policy loading ----------------------------------------------------
    def _load_policy(self):
        from lerobot.policies.act.configuration_act import ACTConfig
        from lerobot.policies.factory import make_policy
        from lerobot.datasets.lerobot_dataset import LeRobotDatasetMetadata

        cfg = ACTConfig.from_pretrained(self.hf_repo)
        # The saved pretrained_path is a stale local path from the training machine.
        cfg.pretrained_path = self.hf_repo
        cfg.device = self.device
        # --- fix 2: limit how many predicted steps we replay before looking at camera again
        # Trained cfg has chunk_size=100 / n_action_steps=100 → at 15 Hz that's 6.6 s of blind replay
        # (gripper stays up, never goes low). Override to a shorter horizon for reactive control.
        # Default 50 = 3.33 s at 15 Hz (verified pick→place sweet spot); 10 = 0.66 s; 1 = fully reactive.
        if self.n_action_steps_param > 0:
            orig = cfg.n_action_steps
            cfg.n_action_steps = min(int(self.n_action_steps_param), int(cfg.chunk_size))
            if orig != cfg.n_action_steps:
                self.get_logger().info(f"overriding n_action_steps {orig} -> {cfg.n_action_steps} (chunk_size={cfg.chunk_size})")
        # optional temporal ensembling (smooths jitter); only enable if coeff >=0
        if self.temporal_ensemble_coeff >= 0:
            cfg.temporal_ensemble_coeff = float(self.temporal_ensemble_coeff)
            self.get_logger().info(f"enabling temporal_ensemble_coeff={cfg.temporal_ensemble_coeff}")
        # --- fix 1: load MEAN_STD normalizer stats from policy preprocessor/postprocessor
        # The model was trained on (x - mean)/std for VISUAL+STATE and outputs normalized ACTION.
        # We bypass PolicyProcessorPipeline (hard-codes cuda) and apply (un)normalization manually.
        self._img_mean = self._img_std = None
        self._state_mean = self._state_std = None
        self._action_mean = self._action_std = None
        try:
            from safetensors.torch import load_file as _load_st
            from huggingface_hub import hf_hub_download as _dl
            p = _dl(self.hf_repo, "policy_preprocessor_step_3_normalizer_processor.safetensors")
            st = _load_st(p)
            # compare means of state vs action (only warn on near-exact match;
            # your dataset has diff~0.00096 with real /joint_command — so threshold 1e-4 avoids false positive)
            s_mean = st.get("observation.state.mean")
            a_mean = st.get("action.mean")
            if s_mean is not None and a_mean is not None:
                diff = float((s_mean - a_mean).abs().max().item())
                if diff < 1e-4:
                    self.get_logger().warn(
                        "dataset looks like action==state (max mean diff %.6f) — recorder may have used "
                        "--action-fallback state; policy will output near-current pose and move very little. "
                        "Consider retraining with real /joint_command action stream." % diff
                    )
            # VISUAL stats are (3,1,1) — keep that shape for broadcasting in _preprocess_image
            if "observation.images.front.mean" in st and "observation.images.front.std" in st:
                self._img_mean = st["observation.images.front.mean"].cpu().numpy().astype(np.float32)
                self._img_std = st["observation.images.front.std"].cpu().numpy().astype(np.float32)
                # ensure (3,1,1) shape even if saved as (3,) — reshape for broadcast
                if self._img_mean.ndim == 1:
                    self._img_mean = self._img_mean.reshape(-1, 1, 1)
                    self._img_std = self._img_std.reshape(-1, 1, 1)
            if "observation.state.mean" in st and "observation.state.std" in st:
                self._state_mean = st["observation.state.mean"].cpu().numpy().astype(np.float32).flatten()
                self._state_std = st["observation.state.std"].cpu().numpy().astype(np.float32).flatten()
            # ACTION stats live in same file (preprocessor) and also in postprocessor — either is fine
            if "action.mean" in st and "action.std" in st:
                self._action_mean = st["action.mean"].cpu().numpy().astype(np.float32).flatten()
                self._action_std = st["action.std"].cpu().numpy().astype(np.float32).flatten()
            # fallback: also try postprocessor file for action stats if missing
            if self._action_mean is None:
                try:
                    p2 = _dl(self.hf_repo, "policy_postprocessor_step_0_unnormalizer_processor.safetensors")
                    st2 = _load_st(p2)
                    if "action.mean" in st2 and "action.std" in st2:
                        self._action_mean = st2["action.mean"].cpu().numpy().astype(np.float32).flatten()
                        self._action_std = st2["action.std"].cpu().numpy().astype(np.float32).flatten()
                except Exception:
                    pass
            # clamp tiny std to avoid div-by-zero (eps already in pipeline, but be safe)
            if self._img_std is not None:
                self._img_std = np.maximum(self._img_std, 1e-6)
            if self._state_std is not None:
                self._state_std = np.maximum(self._state_std, 1e-6)
            if self._action_std is not None:
                self._action_std = np.maximum(self._action_std, 1e-6)
        except Exception as e:
            self.get_logger().warn(f"failed to load normalizer stats: {e} — will use raw [0,1] (expect distribution shift)")
            self._img_mean = self._img_std = None
            self._state_mean = self._state_std = None
            self._action_mean = self._action_std = None
        # ensure eval mode dropout off happens in select_action, but set here too
        meta = LeRobotDatasetMetadata(self.dataset_repo)
        policy = make_policy(cfg, ds_meta=meta)
        policy.eval()
        # move to device explicitly if make_policy didn't (it should)
        try:
            policy.to(self.device)
        except Exception:
            pass
        return policy

    # -- callbacks ---------------------------------------------------------
    def _on_front(self, msg: CompressedImage):
        with self._lock:
            self._latest_front = msg
            self._latest_front_t = time.monotonic()

    def _on_state(self, msg: JointState):
        with self._lock:
            self._latest_state = msg
            self._latest_state_t = time.monotonic()

    # -- homing ----------------------------------------------------------
    def _start_policy_timer(self, mode: str):
        if self._timer is not None:
            return
        self._timer = self.create_timer(1.0 / max(self.fps, 0.1), self._tick)
        self.get_logger().info(f"policy timer started @ {self.fps:.1f} Hz — {mode} — waiting for {self.front_topic} + /joint_states")

    def _do_home_once(self):
        if self._homed:
            return
        # cancel the one-shot home timer
        if self._home_timer is not None:
            try:
                self._home_timer.cancel()
                self.destroy_timer(self._home_timer)
            except Exception:
                try:
                    self._home_timer.cancel()
                except Exception:
                    pass
            self._home_timer = None
        self._do_home()

    def _do_home(self):
        if self._homed:
            return True
        if not self.auto_home:
            self._homed = True
            mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
            self._start_policy_timer(mode)
            return True
        # Fix 4: dry-run must never move hardware — skip service call, just start policy
        # enable_robot:=false is step-3 verification (log predictions, don't publish/home)
        if not self.enable_robot:
            self.get_logger().info("dry-run (enable_robot:=false) — skipping auto-home service call")
            self._homed = True
            mode = "DRY-RUN (not publishing)"
            self._start_policy_timer(mode)
            return True

        self.get_logger().info("waiting for /modular_arm/move_to service ...")
        waited = 0.0
        while not self._move_client.wait_for_service(timeout_sec=1.0):
            waited += 1.0
            if not rclpy.ok():
                return False
            if waited >= 10.0:
                self.get_logger().error("timed out waiting for /modular_arm/move_to — check hw_move_to is running")
                self.get_logger().warn("proceeding without homing; policy will run from current pose")
                self._homed = True
                mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
                self._start_policy_timer(mode)
                return False
            self.get_logger().info("still waiting for /modular_arm/move_to ...")

        req = self._MoveToSrv.Request()
        req.x = float(self.home_x)
        req.y = float(self.home_y)
        req.z = float(self.home_z)
        req.pitch = float(self.home_pitch)
        req.elbow = ""
        req.gripper = float(self.home_gripper)
        req.duration_sec = float(self.home_duration)

        self.get_logger().info(
            f"calling /modular_arm/move_to x={req.x:.3f} y={req.y:.3f} z={req.z:.3f} "
            f"pitch={req.pitch:.2f} gripper={req.gripper:.1f} duration={req.duration_sec:.1f}s ..."
        )
        # non-blocking: spin_until_future_complete would deadlock inside executor
        self._home_future = self._move_client.call_async(req)
        self._home_start_t = time.monotonic()
        self._home_poll_timer = self.create_timer(0.1, self._poll_home_future)
        return False  # will complete async

    def _poll_home_future(self):
        # called every 0.1s until the service future completes
        future = getattr(self, "_home_future", None)
        if future is None:
            return
        if not future.done():
            if time.monotonic() - self._home_start_t > 10.0:
                self.get_logger().error("move_to call timed out after 10s — proceeding without homing")
                try:
                    future.cancel()
                except Exception:
                    pass
                self._cleanup_home_poll()
                self._homed = True
                mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
                self._start_policy_timer(mode)
            return

        # completed — capture result before cleanup
        self._cleanup_home_poll()
        try:
            resp = future.result()
        except Exception as e:
            self.get_logger().error(f"homing future failed: {e} — proceeding without homing")
            self._homed = True
            mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
            self._start_policy_timer(mode)
            return

        if resp is None or not resp.success:
            msg = getattr(resp, "message", "no response") if resp else "no response"
            self.get_logger().error(f"homing move_to rejected: {msg} — proceeding without homing")
            self._homed = True
            mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
            self._start_policy_timer(mode)
            return

        self.get_logger().info(
            f"homing accepted: joint_angles={[round(v,3) for v in resp.joint_angles]} — "
            f"waiting {self.home_duration:.1f}s + {self.home_delay:.1f}s settle ..."
        )
        # schedule settle delay then start policy (non-blocking)
        settle = float(self.home_duration) + float(self.home_delay)
        self._settle_timer = self.create_timer(settle, self._finish_homing)

    def _cleanup_home_poll(self):
        if hasattr(self, "_home_poll_timer") and self._home_poll_timer is not None:
            try:
                self._home_poll_timer.cancel()
                self.destroy_timer(self._home_poll_timer)
            except Exception:
                pass
            self._home_poll_timer = None
        self._home_future = None

    def _finish_homing(self):
        if hasattr(self, "_settle_timer") and self._settle_timer is not None:
            try:
                self._settle_timer.cancel()
                self.destroy_timer(self._settle_timer)
            except Exception:
                pass
            self._settle_timer = None
        try:
            self.policy.reset()
        except Exception:
            pass
        self._homed = True
        mode = "LIVE (publishing /joint_command)" if self.enable_robot else "DRY-RUN (not publishing)"
        self._start_policy_timer(mode)
        self.get_logger().info("homing complete — policy running")

    def _on_command(self, msg: String):
        cmd = msg.data.strip().lower()
        if cmd in ("enable", "start", "on", "true"):
            self.enable_robot = True
            self.get_logger().info("enable_robot -> True (will publish /joint_command)")
        elif cmd in ("disable", "stop", "off", "false", "dry"):
            self.enable_robot = False
            self.get_logger().info("enable_robot -> False (dry-run)")
        elif cmd in ("reset",):
            try:
                self.policy.reset()
                self.get_logger().info("policy action queue reset")
            except Exception as e:
                self.get_logger().warn(f"reset failed: {e}")
        elif cmd in ("home", "rehome"):
            self.get_logger().info("manual re-home requested")
            self._homed = False
            # destroy policy timer to pause inference during re-home
            if self._timer is not None:
                try:
                    self.destroy_timer(self._timer)
                except Exception:
                    try:
                        self._timer.cancel()
                    except Exception:
                        pass
                self._timer = None
            self._do_home()
        else:
            self.get_logger().warn(f"unknown command '{msg.data}' (use enable/disable/reset/home)")

    # -- main loop ---------------------------------------------------------
    def _tick(self):
        if not self._homed:
            return
        # snapshot
        with self._lock:
            front_msg = self._latest_front
            front_t = self._latest_front_t
            state_msg = self._latest_state
            state_t = self._latest_state_t

        now = time.monotonic()
        if front_msg is None:
            self.get_logger().warn("no front image yet — waiting for camera_bridge", throttle_duration_sec=2.0)
            return
        if state_msg is None:
            self.get_logger().warn("no /joint_states yet — waiting for hw_interface", throttle_duration_sec=2.0)
            return
        # staleness guard
        if now - front_t > 1.0:
            self.get_logger().warn(f"front image stale ({now - front_t:.1f}s) — camera down?", throttle_duration_sec=2.0)
            return
        if now - state_t > 1.0:
            self.get_logger().warn(f"/joint_states stale ({now - state_t:.1f}s)", throttle_duration_sec=2.0)
            return

        rgb = _decode_compressed(front_msg)
        if rgb is None:
            self.get_logger().warn("failed to decode front JPEG", throttle_duration_sec=2.0)
            return

        # Fix 1: MEAN_STD normalization — (x/255 - mean)/std for VISUAL, (x - mean)/std for STATE.
        # DroidCam already streams 480x640, so resize is no-op; we keep guard for safety.
        # Use float32 contiguous tensor to avoid strided view bug.
        img_t = _preprocess_image(rgb, self._img_mean, self._img_std)  # (3,480,640) normalized

        # joint state vector in JOINT_NAMES order (raw, for logging/clamping)
        try:
            idx = {n: i for i, n in enumerate(state_msg.name)}
            state_vec = np.array([state_msg.position[idx[j]] for j in JOINT_NAMES], dtype=np.float32)
        except (KeyError, IndexError) as e:
            self.get_logger().error(f"joint state missing {e} (got {state_msg.name})", throttle_duration_sec=2.0)
            return

        # normalize state before feeding policy (if stats available)
        if self._state_mean is not None and self._state_std is not None:
            state_norm = (state_vec - self._state_mean) / (self._state_std + 1e-8)
        else:
            state_norm = state_vec

        # build batch — policy expects normalized tensors
        batch = {
            "observation.state": torch.from_numpy(state_norm.astype(np.float32)).unsqueeze(0).to(self.device),
            "observation.images.front": img_t.unsqueeze(0).to(self.device),
            "task": [self.task_str],
        }

        # predict — returns normalized action chunk (model was trained on normalized ACTION)
        try:
            with torch.no_grad():
                action_t = self.policy.select_action(batch)  # (5,) or (1,5) normalized on device
            if action_t.dim() == 2:
                action_norm = action_t[0].detach().cpu().numpy().astype(np.float32)
            else:
                action_norm = action_t.detach().cpu().numpy().astype(np.float32)
        except Exception as e:
            self.get_logger().error(f"policy inference failed: {e}")
            return

        if np.any(np.isnan(action_norm)) or np.any(np.isinf(action_norm)):
            self.get_logger().error(f"policy returned non-finite action {action_norm} — skipping")
            return

        # unnormalize action: action = norm * std + mean (inverse of MEAN_STD)
        if self._action_mean is not None and self._action_std is not None:
            action = action_norm * self._action_std + self._action_mean
            action = action.astype(np.float32)
        else:
            action = action_norm

        # clamp to limits (safety)
        clamped = np.array(action, dtype=np.float32)
        for i, jn in enumerate(JOINT_NAMES):
            if jn == "gripper_joint":
                lo, hi = GRIPPER_LIMITS
            else:
                lo, hi = JOINT_LIMITS[jn]
            clamped[i] = float(np.clip(clamped[i], lo, hi))

        # verification logging (step 3): distance to current state
        dist = float(np.linalg.norm(clamped - state_vec))
        max_abs = float(np.max(np.abs(clamped - state_vec)))
        self._last_pred = clamped
        self._step += 1

        if self.enable_robot:
            msg = Float64MultiArray()
            msg.data = clamped.tolist()
            self._pub.publish(msg)
            self.get_logger().info(
                f"[{self._step}] publish action {np.round(clamped,3).tolist()} "
                f"dist={dist:.3f} maxΔ={max_abs:.3f}",
                throttle_duration_sec=0.5,
            )
        else:
            # dry-run: do not publish, just verify
            self.get_logger().info(
                f"[{self._step}] DRY predicted {np.round(clamped,3).tolist()} "
                f"current {np.round(state_vec,3).tolist()} dist={dist:.3f} maxΔ={max_abs:.3f}",
                throttle_duration_sec=0.5,
            )
            # also warn if predicted is far from reasonable (heuristic)
            if dist > 2.0:
                self.get_logger().warn(f"large predicted jump dist={dist:.2f} — check camera/state alignment")


def main(args=None):
    rclpy.init(args=args)
    node = LerobotInfer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
