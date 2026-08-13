#!/usr/bin/env python3
"""Record a LeRobotDataset v3 from ROS 2 topics (simulated arm, 2 cameras).

Episode control:
  * Keyboard (in the terminal running the node):
      ENTER = start episode / save episode,  d = discard episode,  q = finish & exit
  * Or publish std_msgs/String to /lerobot_recorder/command:
      "start" | "save" | "discard" | "finish"
    e.g.  ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: start}"
"""

import argparse
import sys
import threading
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage, Image, JointState
from std_msgs.msg import String

from lerobot.datasets.lerobot_dataset import LeRobotDataset
# >>> CUSTOMIZE: on some lerobot versions the import path is
#     `from lerobot.datasets import LeRobotDataset` — try that if the above fails.

try:
    from cv_bridge import CvBridge
    BRIDGE = CvBridge()
except ImportError:
    BRIDGE = None  # manual decoding fallback below handles rgb8/bgr8 + compressed

import cv2


# ----------------------------------------------------------------------------
# Configuration defaults
# ----------------------------------------------------------------------------
# >>> CUSTOMIZE: topic names — check yours with `ros2 topic list`.
DEFAULT_GRIPPER_CAM_TOPIC = "/gripper_cam/image_raw"
DEFAULT_FRONT_CAM_TOPIC = "/front_cam/image_raw"
DEFAULT_JOINT_STATES_TOPIC = "/joint_states"
# >>> CUSTOMIZE: the topic carrying *commanded* joint positions (what your
#     controller / scripted policy publishes). This becomes `action`.
#     Set to "" (empty) if you have none — the node then falls back to using
#     the measured state as the action (see --action-fallback below).
DEFAULT_JOINT_COMMANDS_TOPIC = "/joint_commands"

# >>> CUSTOMIZE: fixed joint ordering. JointState.name order is NOT guaranteed
#     to be stable across publishers, so we always reindex by this list.
#     Replace with your arm's joint names (see `ros2 topic echo /joint_states --once`).
#     Leave as None to lock in the order from the FIRST JointState received.
DEFAULT_JOINT_NAMES = None
# Example:
# DEFAULT_JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow",
#                        "wrist_1", "wrist_2", "wrist_3", "gripper"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-id", required=True,
                   help="e.g. your-hf-username/sim-arm-pick-cube")
    p.add_argument("--task", required=True,
                   help='Natural-language task, e.g. "pick up the red cube"')
    # >>> CUSTOMIZE: fps — must be <= the slowest camera's publish rate,
    #     otherwise consecutive frames will contain duplicated images.
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--root", default=None,
                   help="Local dataset dir (default: ~/.cache/huggingface/lerobot/<repo-id>)")
    p.add_argument("--gripper-cam-topic", default=DEFAULT_GRIPPER_CAM_TOPIC)
    p.add_argument("--front-cam-topic", default=DEFAULT_FRONT_CAM_TOPIC)
    p.add_argument("--joint-states-topic", default=DEFAULT_JOINT_STATES_TOPIC)
    p.add_argument("--joint-commands-topic", default=DEFAULT_JOINT_COMMANDS_TOPIC)
    p.add_argument("--joint-names", nargs="*", default=DEFAULT_JOINT_NAMES,
                   help="Explicit joint ordering (recommended).")
    p.add_argument("--action-fallback", choices=["state"], default="state",
                   help="What to use as `action` when no command topic exists.")
    p.add_argument("--compressed", action="store_true",
                   help="Camera topics are sensor_msgs/CompressedImage "
                        "(e.g. .../image_raw/compressed).")
    p.add_argument("--push", action="store_true", help="Push to the Hub at the end.")
    p.add_argument("--private", action="store_true", help="Push as a private repo.")
    return p.parse_args()


# ----------------------------------------------------------------------------
# Image conversion helpers
# ----------------------------------------------------------------------------
def image_msg_to_rgb(msg) -> np.ndarray:
    """Convert Image/CompressedImage to an RGB uint8 (H, W, 3) array."""
    if isinstance(msg, CompressedImage):
        arr = np.frombuffer(msg.data, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    if BRIDGE is not None:
        return BRIDGE.imgmsg_to_cv2(msg, desired_encoding="rgb8")

    # Manual fallback (no cv_bridge) for the two most common encodings.
    # >>> CUSTOMIZE: add branches here if your sim publishes e.g. "mono8",
    #     "rgba8" or "32FC1" depth — or just install cv_bridge.
    data = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
    if msg.encoding == "rgb8":
        return data[:, :, :3]
    if msg.encoding == "bgr8":
        return cv2.cvtColor(data[:, :, :3], cv2.COLOR_BGR2RGB)
    raise ValueError(f"Unsupported encoding '{msg.encoding}' — install cv_bridge.")


# ----------------------------------------------------------------------------
# Recorder node
# ----------------------------------------------------------------------------
class LeRobotRecorder(Node):
    def __init__(self, args):
        super().__init__("lerobot_recorder")
        self.args = args
        self.lock = threading.Lock()

        # Latest-message caches: (msg, wall-clock receive time)
        self.last = {"gripper": None, "front": None, "state": None, "cmd": None}

        self.joint_names = list(args.joint_names) if args.joint_names else None
        self.dataset = None          # created lazily once shapes are known
        self.recording = False
        self.frames_in_episode = 0
        self.episodes_saved = 0
        self.finished = False

        # >>> CUSTOMIZE: QoS — sim camera plugins (Gazebo/Isaac) usually publish
        #     RELIABLE, but some use BEST_EFFORT. If a subscription connects but
        #     never receives, switch reliability here.
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,   # depth=1: we only ever want the newest frame
        )

        img_type = CompressedImage if args.compressed else Image
        self.create_subscription(img_type, args.gripper_cam_topic,
                                 lambda m: self._cache("gripper", m), img_qos)
        self.create_subscription(img_type, args.front_cam_topic,
                                 lambda m: self._cache("front", m), img_qos)
        self.create_subscription(JointState, args.joint_states_topic,
                                 lambda m: self._cache("state", m), 10)
        if args.joint_commands_topic:
            self.create_subscription(JointState, args.joint_commands_topic,
                                     lambda m: self._cache("cmd", m), 10)
        # >>> CUSTOMIZE: if your commands are NOT a JointState (e.g.
        #     trajectory_msgs/JointTrajectory or std_msgs/Float64MultiArray),
        #     change the message type above and adapt _extract_action() below.

        self.create_subscription(String, "/lerobot_recorder/command",
                                 self._on_command, 10)

        self.create_timer(1.0 / args.fps, self._tick)
        self.get_logger().info(
            f"Waiting for messages on:\n"
            f"  {args.gripper_cam_topic}\n  {args.front_cam_topic}\n"
            f"  {args.joint_states_topic}"
            + (f"\n  {args.joint_commands_topic}" if args.joint_commands_topic else "")
        )

    # -- caching ---------------------------------------------------------
    def _cache(self, key, msg):
        with self.lock:
            self.last[key] = (msg, time.monotonic())

    # -- dataset creation (lazy, once first messages arrived) -------------
    def _try_create_dataset(self):
        with self.lock:
            snap = dict(self.last)
        if snap["gripper"] is None or snap["front"] is None or snap["state"] is None:
            return False

        state_msg = snap["state"][0]
        if self.joint_names is None:
            # Lock in ordering from the first message.
            self.joint_names = list(state_msg.name)
            self.get_logger().warn(
                f"No --joint-names given; locked joint order to: {self.joint_names}")

        gripper_shape = image_msg_to_rgb(snap["gripper"][0]).shape
        front_shape = image_msg_to_rgb(snap["front"][0]).shape
        n = len(self.joint_names)

        features = {
            "observation.state": {
                "dtype": "float32", "shape": (n,), "names": self.joint_names},
            "action": {
                "dtype": "float32", "shape": (n,), "names": self.joint_names},
            "observation.images.gripper": {
                "dtype": "video", "shape": gripper_shape,
                "names": ["height", "width", "channels"]},
            "observation.images.front": {
                "dtype": "video", "shape": front_shape,
                "names": ["height", "width", "channels"]},
        }
        # >>> CUSTOMIZE: add extra features here if useful — e.g. joint
        #     velocities ("observation.velocity", from JointState.velocity),
        #     gripper open/close as a separate scalar, or end-effector pose
        #     from TF. Anything you add must also be added in _tick().

        self.dataset = LeRobotDataset.create(
            repo_id=self.args.repo_id,
            fps=self.args.fps,
            root=self.args.root,
            features=features,
            robot_type="sim_arm",   # >>> CUSTOMIZE: free-form label for metadata
            use_videos=True,
            # >>> CUSTOMIZE: image writer parallelism. Raise threads if
            #     add_frame can't keep up at your fps/resolution (watch for
            #     "queue full" style warnings / rising RAM).
            image_writer_processes=0,
            image_writer_threads=4 * 2,  # rule of thumb: 4 per camera
        )
        self.get_logger().info(
            f"Dataset created at {self.dataset.root}\n"
            f"  gripper cam {gripper_shape}, front cam {front_shape}, {n} joints.\n"
            f"  Press ENTER to start an episode.")
        return True

    # -- joint vector extraction ------------------------------------------
    def _joint_vector(self, msg: JointState) -> np.ndarray:
        idx = {name: i for i, name in enumerate(msg.name)}
        try:
            return np.array(
                [msg.position[idx[j]] for j in self.joint_names], dtype=np.float32)
        except KeyError as e:
            raise KeyError(f"Joint {e} missing from message with joints {msg.name}")

    def _extract_action(self, snap) -> np.ndarray:
        # >>> CUSTOMIZE: this is the single most important design decision.
        #     `action` should be what you want a trained policy to OUTPUT.
        #     Default: commanded joint positions from the command topic.
        #     Fallback: measured state (fine for state-cloning; alternatively
        #     post-process the dataset to shift next-state into action).
        if snap["cmd"] is not None:
            return self._joint_vector(snap["cmd"][0])
        return self._joint_vector(snap["state"][0])

    # -- main sampling loop ------------------------------------------------
    def _tick(self):
        if self.dataset is None:
            self._try_create_dataset()
            return
        if not self.recording:
            return

        with self.lock:
            snap = dict(self.last)
        now = time.monotonic()

        # Staleness guard: warn if a source stopped updating.
        # >>> CUSTOMIZE: 0.5 s threshold; tighten for fast tasks.
        for key in ("gripper", "front", "state"):
            if now - snap[key][1] > 0.5:
                self.get_logger().warn(
                    f"'{key}' data is stale ({now - snap[key][1]:.2f}s old)",
                    throttle_duration_sec=1.0)

        self.dataset.add_frame({
            "observation.state": self._joint_vector(snap["state"][0]),
            "action": self._extract_action(snap),
            "observation.images.gripper": image_msg_to_rgb(snap["gripper"][0]),
            "observation.images.front": image_msg_to_rgb(snap["front"][0]),
            "task": self.args.task,
            # >>> CUSTOMIZE: for multi-task datasets, make the task dynamic
            #     (e.g. cache a String from a /current_task topic).
        })
        self.frames_in_episode += 1

    # -- episode control -----------------------------------------------------
    def _on_command(self, msg: String):
        self.handle_command(msg.data.strip().lower())

    def handle_command(self, cmd: str):
        if cmd == "start":
            if self.dataset is None:
                self.get_logger().warn("Not ready yet (waiting for first messages).")
                return
            if not self.recording:
                self.frames_in_episode = 0
                self.recording = True
                self.get_logger().info(f"▶ Episode {self.episodes_saved} started.")
        elif cmd == "save":
            if self.recording:
                self.recording = False
                if self.frames_in_episode == 0:
                    self.get_logger().warn("Empty episode; nothing to save.")
                    return
                self.dataset.save_episode()
                self.episodes_saved += 1
                self.get_logger().info(
                    f"■ Saved episode ({self.frames_in_episode} frames). "
                    f"Total: {self.episodes_saved}")
        elif cmd == "discard":
            if self.recording:
                self.recording = False
                self.dataset.clear_episode_buffer()
                self.get_logger().info("✗ Episode discarded.")
        elif cmd == "finish":
            self.recording = False
            self.finished = True
        else:
            self.get_logger().warn(f"Unknown command '{cmd}'")


# ----------------------------------------------------------------------------
# Keyboard control (runs in a side thread; plain stdin, no extra deps)
# ----------------------------------------------------------------------------
def keyboard_loop(node: LeRobotRecorder):
    print("Controls: ENTER = start/save episode | d+ENTER = discard | q+ENTER = finish")
    while not node.finished:
        line = sys.stdin.readline()
        if line == "":          # stdin closed (running headless) → rely on topic
            return
        key = line.strip().lower()
        if key == "":
            node.handle_command("save" if node.recording else "start")
        elif key == "d":
            node.handle_command("discard")
        elif key == "q":
            node.handle_command("finish")


def main():
    args = parse_args()
    rclpy.init()
    node = LeRobotRecorder(args)

    threading.Thread(target=keyboard_loop, args=(node,), daemon=True).start()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        node.get_logger().info("Interrupted — finalizing what was saved so far.")
    finally:
        if node.dataset is not None:
            # REQUIRED in v3: closes parquet writers; without this the
            # dataset is corrupt and won't load.
            node.dataset.finalize()
            node.get_logger().info(
                f"Finalized dataset with {node.episodes_saved} episodes "
                f"at {node.dataset.root}")
            if args.push and node.episodes_saved > 0:
                node.dataset.push_to_hub(private=args.private)
                node.get_logger().info("Pushed to the Hub.")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()