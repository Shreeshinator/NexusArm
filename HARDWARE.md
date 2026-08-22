# Hardware — Native + Uno Q (Docker) Bringup

Full wiring + flash + bringup for the **real arm**. Native Ubuntu is the default; **Uno Q** adds the Docker container as the “edge brain” (same Uno R3 firmware).

> For mechanical build + perfboard details see `docs/03_HARDWARE.md` + pin table in `sketch/servo_bridge/README.md`. This file is the one-command bringup + Uno Q port guide.

---

## BOM (this build)

1× MG946R (yaw), 2× MG995/996R (shoulder paired opposite), 1× MG995/996R (elbow), 1× SG90 (wrist pitch), 1× SG90 (gripper), 1× SG90 wrist-roll (fixed, not driven), Arduino Uno R3, ZK-4XX buck-boost with display + LiPo, 608 + 2× 6203 bearings, M3 screws, perfboards + headers, ≥300 µF cap. See `docs/03_HARDWARE.md` § BOM + MakerWorld model by Emre Kalem.

## Firmware — canonical calibration

`sketch/servo_bridge/servo_bridge.ino` is the **only** place that does 5→6 expansion. Verified on hardware:

| Constant | Value |
|---|---|
| `SERVO_PINS` | `{3,5,6,9,10,11}` (3 yaw, 5 shoulder A, 6 shoulder B opposite, 9 elbow, 10 wrist, 11 gripper) |
| `CENTER_US` | `{1500×6}` |
| `RAD_TO_US` | `{318,318,-318,318,477,0}` (pin 6 is `-318` opposite) |
| `GRIP_OPEN/CLOSED` | `1250 → 1800` µs (0..1) |
| `PULSE_MIN/MAX` | `700 / 2300` |

Shoulder B `-318` is intentional — don't “fix” to +318. Wrist `477` is for 60° SG90; use `318` if yours is true 90° SG90 (see `servo_bridge.ino:50-51`).

## Flash Uno R3 (same for PC and Uno Q)

```bash
# Arduino IDE: open servo_bridge.ino → Board Uno → Port /dev/ttyACM0 → Upload
# CLI:
arduino-cli config init 2>/dev/null || true
arduino-cli core update-index && arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:uno sketch/servo_bridge
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/servo_bridge
# heartbeat LED blinks 500 ms when alive
dmesg | grep ttyACM; ls -l /dev/serial/by-id/  # find port
```

Power: LiPo → ZK-4XX (~6 V) → bottom perfboard bus → yaw + top perfboard bus. Share GND everywhere, ≥300 µF cap on rail. **Not** USB power for servos.

---

## Native bringup (one command: arm + cameras)

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash

# Unified: hw_interface + hw_move_to + camera_bridge together
ros2 launch robot_arm_hardware real_bringup.launch.py \
  serial_port:=/dev/ttyACM0 baud_rate:=115200 \
  front_url:=http://<phone-ip>:4747/video fps:=15.0

# Or split (legacy):
ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0
ros2 run robot_arm_hardware camera_bridge --ros-args -p front_url:=http://<phone-ip>:4747/video
```

Verify: `ros2 topic echo /joint_states --once`, `ros2 topic hz /front_cam/image_raw/compressed` (~10–15 Hz phone, see `docs/07_CAMERA_BRIDGE.md`), then `docs/04_HARDWARE_BRINGUP.md` §5 MoveTo calls.

---

## Uno Q + Docker (edge brain)

Uno Q is the SBC that **hosts the same ROS stack in Docker**; the Uno R3 stays the servo bridge over `/dev/ttyACM0` bound into the container (`servo_bridge.ino:26-28`).

### Build + run (container stays idle — you run commands yourself)

**On Uno Q, you SSH once and use `tmux` for multiple terminals** (one SSH = many panes):

```bash
# On Uno Q via SSH (e.g. ssh unoq@<uno-q-ip>)
# 1. Build + start container (no ROS auto-started — sleep infinity)
docker compose build
docker compose up -d

# 2. Start tmux (one SSH session, many windows)
tmux new -s arm   # if not installed: sudo apt install tmux

# Inside tmux — Pane 0: arm + cameras
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
ros2 launch robot_arm_hardware real_bringup.launch.py \
  serial_port:=/dev/ttyACM0 front_url:=http://<phone-ip>:4747/video fps:=15.0
# Ctrl-B then C = new window, Ctrl-B then N/P = switch windows

# Pane 1: inference / teleop / recorder (new tmux window)
# Ctrl-B C, then:
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=your/policy -p enable_robot:=true
# or: ros2 run robot_arm_hardware keyboard_teleop
# or: .venv/bin/python lerobot-ros2-recorder.py --repo-id your/dataset --fps 15 ...

# Pane 2: quick checks
docker compose exec arm bash
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x:0.27,y:0,z:0.08,pitch:-1.57,gripper:0,duration_sec:1.5}"
ros2 topic hz /front_cam/image_raw/compressed
```

**tmux cheatsheet (inside SSH):** `Ctrl-B C` new window, `Ctrl-B N` next, `Ctrl-B P` prev, `Ctrl-B D` detach (keeps running), `tmux attach -t arm` reattach after disconnect.

Without tmux, you can also open **multiple SSH sessions** and each runs its own `docker compose exec arm bash` — same effect, just more connections.

What `docker-compose.yml` does:
* `FROM ros:jazzy` (aarch64 + x86_64), venv `/opt/venv --system-site-packages` pinned `lerobot==0.6.1 numpy==1.26.4 opencv-python-headless h5py setuptools==79.* CPU torch`, `colcon build --symlink-install`.
* `devices: /dev/ttyACM0`, `network_mode: host` (DroidCam + HF), mounts `src/` live + `hf-cache`/`lerobot-cache` volumes.
* `command: sleep infinity` — container stays alive for manual `ros2 launch` / `ros2 run`.

### Inference on the edge

Same as `docs/06_INFERENCE.md` / `08_TRAINING.md`, but from inside the container via `docker compose exec arm bash`:
```bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=your/policy -p enable_robot:=true -p n_action_steps:=50
```

## Troubleshooting

* `Cannot open /dev/ttyACM0` → `sudo usermod -aG dialout $USER` + re-login, or `SERIAL_PORT=/dev/ttyUSB0 docker compose up` if Uno shows as USB0.
* `camera topics empty` → phone/ESP32 must be same WiFi as host/Uno Q; verify URL in browser before passing to `FRONT_URL`.
* `Gripper crosses over` → travel 0.015 m matches finger collision `y±0.019`; don't increase `upper` without matching `GRIPPER_MAX_TRAVEL`.

Credits: mechanical design by **Emre Kalem (@emrekalem)** — MakerWorld Standard Digital File License.
