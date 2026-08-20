# Uno Q Port + User-Facing Docs — Plan

## Goal & locked decisions
- **Target**: Uno Q = Linux SBC running the full ROS2 + LeRobot inference stack **in Docker**
  (matches `sketch/servo_bridge/servo_bridge.ino:26-28` "serial port bound into the Docker container").
- **Servo bridge**: Arduino **Uno R3** running `sketch/servo_bridge/servo_bridge.ino`, connected to the
  Uno Q over USB serial (`/dev/ttyACM0`). The Uno R3 is the ONLY place that does the 5→6
  logical→physical servo expansion (see firmware header).
- **Camera**: keep `src/robot_arm_hardware/robot_arm_hardware/camera_bridge.py` pulling DroidCam MJPEG
  over WiFi (network-only, board-agnostic).
- **Deliverables**: new `HARDWARE.md` + `Dockerfile` (+compose) so a non-developer can reproduce from scratch.

---

## A. New files to create
1. **`Dockerfile`** (repo root) — `FROM ros:jazzy` (multi-arch; Uno Q is almost certainly `aarch64` —
   confirm with `uname -m`). Steps:
   - Install `python3-venv`, `python3-pip`, `colcon-common-extensions`, `ros-dev-tools`.
   - Create venv `/opt/venv --system-site-packages` (**mirrors current repo `.venv` so ROS is visible**).
     Inside it pin `lerobot==0.6.1`, `numpy==1.26.4`, `opencv-python-headless`, `h5py`, and a **CPU** torch.
     - Do **not** let lerobot bump `setuptools` past 80 (AGENTS.md rule — breaks colcon).
   - `COPY src/ ./src/`, `colcon build --symlink-install`.
   - Entrypoint sources `/opt/ros/setup.bash` + `install/setup.bash` + activates `/opt/venv`.
2. **`docker-compose.yml`** — binds the serial device (`/dev/ttyACM0` → `devices:` or `--privileged`),
   `network_mode: host` (so DroidCam phone IP + HuggingFace are reachable), mounts workspace for live edits,
   sets `serial_port`/`enable_robot` env.
3. **`src/robot_arm_hardware/launch/real_bringup.launch.py`** (new) — **one command** that launches
   `hw_interface` + `hw_move_to` + `camera_bridge` together with launch args
   (`serial_port`, front/gripper URL, `fps`, `enable_robot`). This directly kills the
   "I run 3 separate custom commands" problem.
4. **`HARDWARE.md`** (repo root) — audience guide: BOM, wiring (Uno R3 PWM pins + external 5–6 V supply +
   shared GND to Uno Q), flash `servo_bridge.ino` (Arduino CLI + IDE), Uno Q Docker bring-up, calibration
   procedure, run teleop/inference/recorder, safety + troubleshooting.
5. **`sketch/servo_bridge/README.md`** — pinout table, `SERVO_PINS`, `RAD_TO_US`/`CENTER_US` meaning,
   how to tune, flash command (`arduino-cli compile -b arduino:avr:uno && arduino-cli upload -p /dev/ttyACM0`).

---

## B. Changes to existing files
- `src/robot_arm_hardware/launch/real_arm.launch.py:14` — add
  `DeclareLaunchArgument("serial_port", default_value="/dev/ttyACM0")` (currently missing →
  `serial_port:=` arg is undeclared). (Also a known bug.)
- `src/robot_arm_hardware/package.xml:10` — add `<depend>modular_arm_interfaces</depend>`
  (currently missing; `hw_move_to` imports `MoveTo` from it).
- `src/robot_arm_hardware/robot_arm_hardware/camera_bridge.py` — expose front/gripper URL + fps as
  **launch args** so `real_bringup.launch.py` can configure them (it already reads params; just wire them).
- **Firmware standardization** — `servo_bridge.ino` becomes canonical for the port. Its calibration
  (`yaw +318`, `wrist 477`, `PULSE_MIN 700`) currently **differs** from the ESP32 developed on
  (`yaw -318`, `wrist 318`, `PULSE_MIN 800`). Decide one truth:
  (a) keep `servo_bridge.ino` as-is and verify on the real arm, or
  (b) port the ESP32's verified `-318` yaw signs into `servo_bridge.ino`.
  Recommend: **verify on hardware, document the final table in `HARDWARE.md`/`sketch/README`**, and clearly
  mark `servo_bridge_esp32.ino` as "dev-only / not for Uno Q" to avoid the swap trap.
- (Recommended hardening, not strictly port-blocking):
  `hw_interface.py:48-50` replace blocking `Serial(); time.sleep(2)` with non-blocking open + reconnect,
  and don't publish a zero pose before the first `/joint_command` (`hw_interface.py:79`).

---

## C. Remaining bugs (from audit, after fixes 1–6 done)
### High
- `lerobot_infer.py:344` `while wait_for_service(1.0)` **blocks the single-threaded executor** for up to
  10 s during auto-home → camera/state callbacks freeze on the Uno Q. Make it async (timer-poll or
  `wait_for_service` with `None` + callback).
- `lerobot_infer.py` `_homed`/`_timer`/settle-timer **race without a lock** (multiple callbacks touch
  shared state) — wrap in the existing `_lock`.

### Medium
- `lerobot_infer.py:441` `policy.reset()` only fires after `home_duration+home_delay` (2.5 s) → first
  predictions average the pre-home queue (stale).
- `camera_bridge.py:134` `buf.find(boundary)` reads 4 KB chunks; a JPEG boundary straddling two chunks is
  dropped → lost frames.
- `hw_interface.py:48` serial init blocks + no reconnect; zero-pose published before first command (above).
- **Firmware desync** Uno vs ESP32 (`servo_bridge.ino:45` vs `servo_bridge_esp32.ino:52`): yaw `+318 vs
  -318`, wrist `477 vs 318`, `PULSE_MIN 700 vs 800` — standardize (port item B).
- `lerobot_infer.py:102` `fps=15` vs recorder default `--fps 10` vs `lerobot-ros2-recorder.md:30` `fps 30`
  — align (recorder dupes frames if > camera rate).
- `lerobot_infer.py:101` `task` string must match dataset exactly — brittle; consider a launch arg + validation.
- `lerobot-ros2-recorder.md:118` doc drift: says `raw Image` + `/joint_commands` (plural) but code uses
  **compressed** + `/joint_command` (singular) → copy-pasting the md records `action==state` fallback.
- `package.xml` (`modular_arm_interfaces` depend) and `real_arm.launch.py` (`DeclareLaunchArgument`) —
  covered in B.

### Low
- `lerobot_infer.py` fps readout staleness 1.0 s; `destroy_timer` `InvalidHandle` on re-home;
  `robot_arm.urdf` vs `robot_arm.urdf.xacro` drift (wrist_camera block).

---

## D. Suggested sequence
1. Firmware: pick canonical `servo_bridge.ino` calibration, flash to Uno R3, verify motion on bench.
2. Packaging: fix `package.xml` + `real_arm.launch.py` args; add `real_bringup.launch.py` (unified launch).
3. Container: `Dockerfile` + `compose.yml`; build on Uno Q;
   `ros2 launch robot_arm_hardware real_bringup.launch.py`.
4. Docs: `HARDWARE.md` + `sketch/servo_bridge/README.md` with the calibration table and troubleshooting.
5. (Optional next pass) Harden `hw_interface` + `lerobot_infer` async-home/lock bugs for live reliability.

---

## Open questions to confirm before implement
- **Uno Q arch**: `uname -m` on the board (to choose the right base image / torch wheel)?
- **Servo calibration truth**: keep `servo_bridge.ino` (`+318` yaw) or adopt the ESP32's verified `-318`
  signs for the R3 firmware?
- **Inference on-device**: is the Uno Q powerful enough for CPU torch, or should inference stay on a host
  and only `hw_interface`/`camera_bridge` run on the board?
