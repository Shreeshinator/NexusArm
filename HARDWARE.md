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

## VS CODE SSH — FULL GUIDE: LAPTOP/WSL → UNO Q → REAL ARM (START TO FINISH)

> **For you, step-by-step.** You sit at your laptop (Windows + WSL or Linux). The Uno Q is the tiny Linux board next to the arm. You control it from VS Code via SSH. Same ROS code runs on laptop (native) or Uno Q (in Docker lunchbox).

### Step 0 — What you need where
| Machine | Role | OS | Install thing |
|---|---|---|---|
| **Laptop** (your daily driver) | Edit code, flash Arduino, run sim | Windows+WSL Ubuntu 24.04 or native Ubuntu | VS Code + Remote-SSH extension |
| **Uno Q** (edge brain) | Runs real arm + cameras (Docker) | Ubuntu/Debian Linux (on the board) | Docker only |
| **Uno R3** (Arduino) | Talks to servos | Arduino firmware `servo_bridge.ino` | Flashed once via USB |

### Step 1 — Find Uno Q on your network
1. Plug Uno Q power + Ethernet/WiFi (same WiFi as your laptop & phone).
2. Find its IP: on your router admin page, or plug HDMI/keyboard and run `hostname -I`, or `ping unoq.local` / `ping uno.local`.
3. Test from laptop terminal (WSL/PowerShell/Linux): `ping <IP>` should reply. Remember it, e.g. `192.168.1.42`. Default user is often `unoq`, `ubuntu`, or `root` — check your Uno Q docs (try `ssh unoq@192.168.1.42`).

### Step 2 — VS Code SSH setup (one-time, 2 min)
1. Install VS Code: `https://code.visualstudio.com`
2. Open VS Code → Extensions (Ctrl+Shift+X) → search **Remote - SSH** (by Microsoft) → Install.
3. `Ctrl+Shift+P` → type `Remote-SSH: Add New SSH Host` → enter `ssh unoq@<IP>` (use your IP/user) → pick the first `~/.ssh/config` file it suggests.
4. `Ctrl+Shift+P` → `Remote-SSH: Connect to Host` → pick `unoq@<IP>` → new VS Code window opens. Bottom-left says `SSH: unoq@<IP>` when connected. First time, accept fingerprint `yes`.
5. If password fails: same WiFi? user wrong? try `ssh unoq@<IP>` in a normal terminal to debug. On Uno Q run `passwd` to set password if needed.

**Alternative without config:** just `Ctrl+Shift+P` → `Remote-SSH: Connect to Host` → `ssh user@IP` each time.

### Step 3 — Clone this repo ON the Uno Q (inside VS Code)
You are now *inside* Uno Q via VS Code. Open Terminal in VS Code (`Ctrl+`` `` `):
```bash
# Check you're on Uno Q (not laptop):
hostname; cat /etc/os-release | head -1

# Install git+docker if missing:
sudo apt update && sudo apt install -y git docker.io docker-compose-plugin tmux
sudo usermod -aG docker $USER  # so docker without sudo; then reconnect VS Code

# Clone NexusArm (SSH key not needed — HTTPS):
git clone https://github.com/Shreeshinator/NexusArm.git ~/NexusArm
cd ~/NexusArm
ls  # should show Dockerfile, docker-compose.yml, src/
```
> Laptop/WSL native side: same clone works: `git clone https://github.com/Shreeshinator/NexusArm.git` then `colcon build` per `docs/01_SETUP.md`. WSL vs Uno Q diverge *only* here — laptop runs `colcon build` directly, Uno Q uses Docker (next).

### Step 4 — Flash Uno R3 firmware (plugged into Uno Q USB)
In the same VS Code terminal on Uno Q:
```bash
ls /dev/ttyACM* /dev/ttyUSB*  # Uno R3 usually /dev/ttyACM0
# Via Arduino IDE (easiest): forward USB or flash from laptop instead — see §Flash below
# Via CLI on Uno Q:
sudo apt install -y arduino-cli
arduino-cli config init 2>/dev/null || true
arduino-cli core update-index && arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:uno sketch/servo_bridge
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/servo_bridge
dmesg | tail  # should show ttyACM0
```
If flashing fails, unplug/replug Uno R3 USB, check `groups` includes `dialout`/`docker`.

### Step 5 — Build & start Docker lunchbox (Uno Q side)
```bash
cd ~/NexusArm
docker compose build          # first time 5-10 min (ros:jazzy multi-arch, venv pinned)
docker compose up -d          # starts container in background — sleep infinity, NO auto ROS
docker compose ps             # should show arm-stack Up
```
Open VS Code terminal splits for multiple nodes — **one SSH, many windows via `tmux`**:
```bash
tmux new -s arm   # one SSH = many panes. Install if missing: sudo apt install tmux
# Window 0 — arm + cameras:  (Ctrl-B C = new window, Ctrl-B N/P = switch, Ctrl-B D = detach)
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
ros2 launch robot_arm_hardware real_bringup.launch.py serial_port:=/dev/ttyACM0 front_url:=http://<PHONE_IP>:4747/video fps:=15.0
# Keep this running. Ctrl-B C for next window.
```
> Leave Window 0 running. Every other task gets its own window via `Ctrl-B C` + same `docker compose exec arm bash` + `source ...`.

### Step 6 — Verify real stack is alive (Window 1)
```bash
# New tmux window: Ctrl-B C
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
ros2 topic list | grep -E "joint|front_cam"   # should show /joint_states, /front_cam/image_raw/compressed
ros2 topic hz /front_cam/image_raw/compressed  # ~10-15 Hz if phone camera URL correct
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x:0.27,y:0,z:0.08,pitch:-1.57,gripper:0,duration_sec:1.5}"
# Arm should home. Try: gripper:1.0 to close, x:0.25 to move.
```
Phone camera `FRONT_URL`: same WiFi, open `http://<PHONE_IP>:4747/video` in browser first to confirm, then paste into `front_url:=`. See `docs/07_CAMERA_BRIDGE.md`.

### Step 7 — Data / Inference (Windows 2, 3...)
Same pattern — each is a new tmux window:
```bash
# Teleop:
docker compose exec arm bash; source ...; ros2 run robot_arm_hardware keyboard_teleop
# Recorder (from Window 2):
.venv/bin/python lerobot-ros2-recorder.py --repo-id your/dataset --fps 15 --cams front_cam
# Inference (after training, see docs/08_TRAINING.md):
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=your/policy -p enable_robot:=true -p n_action_steps:=50
```
Detach: `Ctrl-B D` (keeps running after you close laptop). Reattach: `tmux attach -t arm`. Without tmux, just open more VS Code terminals — each `Remote-SSH: New Window` is another `docker compose exec`.

### End-to-end cheat sheet (copy-paste after first SSH):
```bash
cd ~/NexusArm && docker compose up -d && tmux new -s arm
# W0: docker compose exec arm bash → source ... → ros2 launch robot_arm_hardware real_bringup...
# W1: docker compose exec arm bash → tests / inference / recorder
```

## Uno Q + Docker (edge brain) — BEGINNER REFERENCE

### What is Docker? What is `docker compose`?
*Think of Docker like a lunchbox.* **Docker** packs your whole computer setup (Ubuntu, ROS Jazzy, Python packages) into one box (called an **image**) so it runs the same everywhere — your laptop or the tiny Uno Q board. You don't install ROS by hand on the Uno Q; you just run the lunchbox.
* **Plain `docker`** = you type one long command every time: `docker run --device /dev/ttyACM0 --net host -v ./src:/workspace/src ros:jazzy bash` — you have to remember every flag.
* **`docker compose`** = you write those flags *once* in a file (`docker-compose.yml`) and just type `docker compose up`. It's the same `docker` underneath, just with a recipe so you don't retype 5 lines each time. That's why we use `compose` — shorter, less error-prone, same result. You *could* use plain `docker run` with the same flags from `docker-compose.yml:7-45` and it would do the same thing; `compose` is just convenient.
* `Dockerfile` = recipe to *build* the lunchbox. `docker-compose.yml` = recipe to *run* it (which devices, network, folders to share).

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

What `docker-compose.yml` does (in plain English):
* `FROM ros:jazzy` → starts from the official ROS lunchbox (works on both your laptop x86_64 and Uno Q aarch64).
* `venv /opt/venv` → Python box inside the lunchbox pinned `lerobot==0.6.1 numpy==1.26.4 setuptools==79.*` + CPU `torch` (no CUDA needed). `colcon build --symlink-install` builds ROS packages.
* `devices: /dev/ttyACM0` → plugs the Uno R3 USB serial into the box so `hw_interface` can talk to it. `network_mode: host` → box shares Uno Q's WiFi so phone camera URL + HuggingFace work.
* `volumes: ./src:/workspace/src:ro` + `hf-cache` → your `src/` stays editable live; model caches persist after reboot.
* `command: sleep infinity` → box stays open with nothing auto-started; you type `ros2 launch ...` yourself (you asked for manual control). If you wanted auto, you'd put `real_bringup.launch.py` there.
* **Plain `docker` equivalent** (same as `compose` above): `docker build -t nexusarm . && docker run -it --net host --device /dev/ttyACM0 -v ./src:/workspace/src nexusarm bash` — longer to type, same effect.

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
