# Inference — Run the Learned Policy on the Real Arm

> You've built it, flashed it, and collected demos — now let's let the arm think for itself! This guide deploys the ACT policy that learns to pick the block and place it in the bowl.

## What you're deploying

* **Policy:** `shreeshinator/arm-pick-blocks-act-first` — ACT, chunk 100, trained on `shreeshinator/arm-picking-blocks-real` (front camera 480×640, 5 joints)
* **Task string (must match exactly):** `"place the block in the bowl"` — the model was trained on this phrase, so keep it letter-for-letter
* **Input:** front camera JPEG (`/front_cam/image_raw/compressed`, 480×640) + `/joint_states` (5 values)
* **Output:** `/joint_command` (`Float64MultiArray` 5 values: `joint1..joint4, gripper`) at 15 Hz, clamped to limits, with `n_action_steps=50` (3.33 s horizon — the sweet spot you verified; 100 is too stale, 10 is twitchy)

If your recorder was at 15 fps with front cam 480×640, you're already aligned — no data conversion needed.

## Prerequisites — quick check

* Real arm up: `ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0 baud_rate:=115200` (from `04_HARDWARE_BRINGUP.md`)
* Camera bridge streaming — see `07_CAMERA_BRIDGE.md` (DroidCam/ESP32 setup, QoS, fps) and §1 below — front cam must be `BEST_EFFORT` and actually publishing
* Venv `.venv` with `lerobot==0.6.1`, `numpy==1.26.4`, `opencv-python-headless`, `torch` CPU, `setuptools==79.*` (from `01_SETUP.md` §4 — install setuptools before lerobot, always run via `.venv/bin/python`)

## 1. Start the camera bridge (needs WiFi — see 07_CAMERA_BRIDGE.md)

Your DroidCam/phone or ESP32 feeds MJPEG over WiFi — `camera_bridge` just forwards the JPEG bytes, no decode, so it's light on CPU. Full phone/ESP32 wiring & URLs are in `07_CAMERA_BRIDGE.md` — the snippet below is the real-arm front-only quickstart:

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash

# DroidCam example — replace with your phone's IP:port shown in the app
ros2 run robot_arm_hardware camera_bridge --ros-args \
  -p front_url:=http://192.168.1.50:4747/video \
  -p gripper_url:="" \
  -p fps:=15.0 \
  -p front_topic:=/front_cam/image_raw/compressed

# verify it's alive
ros2 topic hz /front_cam/image_raw/compressed  # ~15 Hz, format jpeg, BEST_EFFORT depth 1
ros2 topic echo /front_cam/image_raw/compressed --once  # look for format: jpeg
```

> The bridge publishes **only new frames** (no duplicates) with `BEST_EFFORT depth=1`. Inference subscribes the same — DDS won't mismatch and drop images.

## 2. Dry-run first (no motion — just prove the pipeline)

This is the friendly safety net — it logs what the policy *would* do, without moving servos:

```bash
source /opt/ros/jazzy/setup.bash
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args \
  -p hf_repo:=shreeshinator/arm-pick-blocks-act-first \
  -p dataset_repo:=shreeshinator/arm-picking-blocks-real \
  -p task:="place the block in the bowl" \
  -p fps:=15.0 \
  -p front_topic:=/front_cam/image_raw/compressed \
  -p enable_robot:=false \
  -p auto_home:=true \
  -p n_action_steps:=50
```

You'll see:

```
lerobot_infer: hf_repo=... device=cpu fps=15 enable_robot=False auto_home=True
policy loaded: ACT chunk_size=100 n_action_steps=50 ...
normalizer: VISUAL mean=[0.485,0.456,0.406] std=[0.229,0.224,0.225] ...
policy timer started @ 15.0 Hz — DRY-RUN — waiting for /front_cam/... + /joint_states
[1] DRY predicted [0.12, -0.20, ...] current [0.10, -0.18, ...] dist=0.12 maxΔ=0.05
```

If you see `no front image yet` or `stale 1.2s`, your camera bridge URL or WiFi is off — fix that before going live.

## 3. Go live (the arm moves!)

Same command, just flip `enable_robot`:

```bash
source /opt/ros/jazzy/setup.bash
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args \
  -p hf_repo:=shreeshinator/arm-pick-blocks-act-first \
  -p dataset_repo:=shreeshinator/arm-picking-blocks-real \
  -p task:="place the block in the bowl" \
  -p fps:=15.0 \
  -p front_topic:=/front_cam/image_raw/compressed \
  -p enable_robot:=true \
  -p auto_home:=true \
  -p n_action_steps:=50

# or via ros2 run after colcon build (installs to lib/robot_arm_hardware/lerobot_infer):
# colcon build --symlink-install && source install/setup.bash
# ros2 run robot_arm_hardware lerobot_infer --ros-args -p enable_robot:=true -p n_action_steps:=50
```

What happens:

1. **Auto-home** — calls `/modular_arm/move_to` to `home_x/y/z 0.27/0.0/0.08 pitch -1.57 gripper 0.0` for `home_duration 2.0s` + `home_delay 0.5s` settle. Disable with `-p auto_home:=false` if you want manual control.
2. **Policy loop** — at 15 Hz it grabs the latest front JPEG + joint state, normalizes (`uint8→float/255→(x-mean)/std` per `safetensors`, state `(raw-mean)/std`), runs `select_action`, unnormalizes `norm*std+mean`, clamps to `JOINT_LIMITS` (`±3.14, ±1.57`) + `GRIPPER 0…1`, publishes `/joint_command`.

Watch the logs: `publish action [...] dist=... maxΔ=...` — if `dist > 2.0` it warns (big jump).

## 4. Tweak it live (no restart needed)

In another terminal:

```bash
ros2 topic pub --once /lerobot_infer/command std_msgs/String "{data: disable}"  # pause
ros2 topic pub --once /lerobot_infer/command std_msgs/String "{data: enable}"   # resume
ros2 topic pub --once /lerobot_infer/command std_msgs/String "{data: reset}"    # clear action queue
ros2 topic pub --once /lerobot_infer/command std_msgs/String "{data: home}"     # re-home to start pose
```

## 5. If it won't pick (or acts weird)

* **Front vs gripper:** this policy uses **front only** — `gripper_url` can stay empty.
* **Not dipping to pick?** `n_action_steps=50` is the verified balance (10 was too reactive, 100 too blind). Try `5` or `1` for more reactivity, but 50 should be your default now (set in `lerobot_infer.py:116`).
* **Image size:** DroidCam at 480×640 is perfect — if yours is different, the node resizes with `INTER_AREA` before normalizing.
* **Task string:** must be exactly `"place the block in the bowl"` — copy-paste it.
* **Safety first:** actions are clamped to joint/gripper limits, but keep your hand near the LiPo/ZK-4XX power switch and start with blocks centered at `y≈0.06`. No dedicated e-stop — cut power if needed.

## 6. Under the hood (just so you trust it)

* **Normalization:** loads `policy_preprocessor_step_3_normalizer_processor.safetensors` from the HF cache (`~/.cache/huggingface/hub` or `$HF_HOME`) — visual ImageNet mean `[0.485,0.456,0.406]` std `[0.229,0.224,0.225]` shape `3×1×1`, plus state/action mean/std from the same file. First run pulls ~2 GB — allow a minute. Bypasses `PolicyProcessorPipeline.from_pretrained` which hard-codes `cuda` and crashes CPU. Manual math mirrors `_NormalizationMixin`.
* **QoS:** both sides `BEST_EFFORT depth=1 KEEP_LAST` — no drops.
* **Device:** auto `cuda` if available else `cpu`.

Have fun — the bowl should start filling up! When you're ready for the edge, the Uno Q Docker port lives in `UNO_Q_PORT_PLAN.md`.

## Credits

Policy and dataset by the project team on Hugging Face — trained on the very demos from `05_DATA_COLLECTION.md`.
