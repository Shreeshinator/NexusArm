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

## VS CODE SSH — PERFECT GUIDE: LAPTOP/WSL → UNO Q → REAL ARM (START TO FINISH)

> **For you, step-by-step. Researched for Uno Q (2025+).** You sit at your laptop (Windows + WSL or Linux). The Uno Q is the tiny Linux board next to the arm: **Qualcomm QRB2210 + STM32U585, Debian 13 “Trixie” arm64, 16/32 GB eMMC, soldered — no SD card.** Same ROS code runs natively on laptop (`colcon build`) or on Uno Q **in Docker** (lunchbox). App Lab is preinstalled and uses Docker internally.

### Step 0 — What you need where
| Machine | Role | OS | You install |
|---|---|---|---|
| **Laptop** (your daily) | Edit, sim, flash fallback | Windows+WSL Ubuntu 24.04 or native Ubuntu | VS Code + Remote-SSH |
| **Uno Q** (edge brain) | Runs real arm + cameras **in Docker** | **Debian 13 Trixie arm64** (onboard) | **Nothing — Docker is already there** |
| **Uno R3** (Arduino) | Talks to 6 servos via `servo_bridge.ino` | Arduino firmware | Flashed once over USB |

**Crucial Uno Q facts (so you don't break it):**
* **User is ALWAYS `arduino`** — not `unoq`/`ubuntu`/`root`. Factory password `arduino`/`arduino` → during first App Lab onboarding you pick your own name + password. After that, `arduino` + *your* password is the only login (change anytime with `passwd` on board).
* **SSH is auto-enabled by App Lab onboarding** (Network Mode + `avahi-daemon` + `ssh.service`). You don't `sudo systemctl enable ssh` unless you skipped App Lab. If SSH `Connection refused`, run on board via `adb shell`: `sudo systemctl status ssh` / `sudo ssh-keygen -A && sudo systemctl start sshd`.
* **Docker is PRE-INSTALLED** — App Lab uses containers. **DO NOT** run `curl https://get.docker.com | sh` — it warns “Docker appears installed” and can break the existing install. Just check `docker --version`.
* **Disk is small** — 16 GB eMMC, ~4 GB can be `/var/lib/docker/overlay2`. Don't `docker system prune -f` blindly while App Lab apps run. If full, see Troubleshooting § Disk.

### Step 1 — First boot → find Uno Q on network
1. Plug USB-C **data** cable (charge-only won't work) from Uno Q USB-C to laptop, plus power delivery via dongle. Wait ~60 s after power — App Lab needs time to appear in `adb devices`.
2. Do App Lab onboarding once: open Arduino App Lab → it finds Uno Q via **mDNS / Network Mode** → set **board name** (e.g. `unoq`, unique per board), WiFi SSID/password, Linux password. This enables SSH + WiFi.
3. Find it from laptop terminal (WSL/Linux/macOS/WSL):
   ```bash
   ping unoq.local            # use YOUR board name from onboarding
   ping 192.168.1.x           # or IP from App Lab Settings / router admin / on board via HDMI: `hostname -I`
   ssh arduino@unoq.local     # mDNS, no IP needed — needs same WiFi, firewall must allow mDNS (Windows Firewall can block)
   # Fallback without WiFi — direct cable:
   adb devices                # should list board after ~60s
   adb shell                  # no password until setup done; after setup use your password
   hostname -I; cat /etc/os-release  # Debian 13 Trixie aarch64
   ```
   If `unoq.local` fails but `192.168.1.x` works → Windows Firewall/guest WiFi/corporate VLAN blocking mDNS — use IP.

### Step 2 — VS Code SSH (one-time, 2 min)
1. VS Code → Extensions (`Ctrl+Shift+X`) → **Remote - SSH** (Microsoft) → Install.
2. **Important:** On Uno Q, VS Code Copilot/Roo extensions eat the 2/4 GB RAM. In VS Code Settings on the *remote* (Uno Q), disable Copilot on that host if you see freezes (confirmed by Edge Impulse docs).
3. `Ctrl+Shift+P` → `Remote-SSH: Add New SSH Host` → enter `ssh arduino@unoq.local` **or** `ssh arduino@192.168.1.x` → pick first `~/.ssh/config`.
4. `Ctrl+Shift+P` → `Remote-SSH: Connect to Host` → `arduino@unoq.local` → new window, bottom-left `SSH: unoq.local` when connected. First time `yes` to fingerprint, enter *your* Linux password from onboarding (not `arduino` anymore).
5. Debug: `ssh arduino@unoq.local` in a normal terminal. If `Permission denied`, reset password via `adb shell`: `sudo passwd arduino`. If `Connection refused`, see Step 0 SSH fix. If board not found, check `avahi-daemon` + `ssh` are running: `sudo systemctl status avahi-daemon ssh`.

### Step 3 — Clone this repo ON the Uno Q (inside VS Code `Ctrl+`` `)
You are now *inside* Uno Q via VS Code (bottom-left confirms). Terminal is on the board:
```bash
# Prove you're on Uno Q (not laptop):
hostname; cat /etc/os-release | head -1   # unoq, Debian GNU/Linux 13 (trixie)
uname -m; dpkg --print-architecture       # aarch64, arm64

# Docker is ALREADY there — verify, don't reinstall:
docker --version          # e.g. Docker version 26.x
docker compose version    # e.g. v2.x  — if missing, only then: sudo apt update && sudo apt install -y docker-compose-plugin
# NEVER run: curl https://get.docker.com | sh  (breaks App Lab containers)

# Only tool you may need:
sudo apt update && sudo apt install -y git tmux   # docker already present

# Optional: no-sudo docker + ssh key (so you skip passwords next time):
sudo usermod -aG docker $USER   # reconnect VS Code after
ssh-copy-id arduino@unoq.local  # from laptop — deposits your key to ~/.ssh/authorized_keys

git clone https://github.com/Shreeshinator/NexusArm.git ~/NexusArm
cd ~/NexusArm && ls  # Dockerfile, docker-compose.yml, src/
```
> **Laptop/WSL native side** — same repo but *no* Docker: `git clone ...` → `source /opt/ros/jazzy/setup.bash && colcon build --symlink-install` per `docs/01_SETUP.md`. WSL vs Uno Q diverge only here.

### Step 4 — Flash Uno R3 firmware (Uno R3 USB plugged into Uno Q USB-A)
In same VS Code terminal on Uno Q:
```bash
ls /dev/ttyACM* /dev/ttyUSB* /dev/serial/by-id/*  # Uno R3 usually /dev/ttyACM0
sudo apt install -y arduino-cli
arduino-cli config init 2>/dev/null || true
arduino-cli core update-index && arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:uno sketch/servo_bridge
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/servo_bridge
dmesg | tail; ls -l /dev/ttyACM0  # heartbeat LED blinks 500 ms if alive
```
If fails: unplug/replug Uno R3, `groups` must contain `dialout` (re-login after `sudo usermod -aG dialout $USER`), or flash from laptop via Arduino IDE instead (same sketch, same port).

### Step 5 — Build & start Docker lunchbox (Uno Q side) — IN DETAIL
**What happens here:** `docker compose build` reads **slim** `Dockerfile` (`ros:jazzy-ros-base`, not full desktop) and downloads ~1 GB multi-arch x86_64/arm64 (works on laptop *and* Uno Q aarch64, first time 5-10 min slower on 2 GB Uno Q — shows pulling layers). It creates a venv `/opt/venv` pinned `lerobot==0.6.1` (auto pulls `numpy 2.1.x` + `opencv 5.0` aarch64, **not** pinned `1.26.4`) + `setuptools==79.*` + CPU `torch`, copies `src/`, runs `colcon build --symlink-install`. `docker compose up -d` then **creates the running container** `arm-stack` from that image (you see `Creating arm-stack ... done`), mounts `src/` live + `hf-cache`, binds `/dev/ttyACM0` + `host` network, and runs `sleep infinity` — i.e. **it sits idle, no ROS auto-started** (you asked for manual). `docker compose ps` proves it's `Up`.

```bash
cd ~/NexusArm
docker compose build          # builds image nexusarm-arm (~5-10 min first, cached next time)
docker compose up -d          # starts container in background — sleep infinity, NO auto ROS
docker compose ps             # should show arm-stack Up X seconds
docker logs arm-stack         # should be empty (we slept, not launched)
```

**Now — run ROS yourself. You need 2-3 terminals. With VS Code SSH this is EASY — no tmux required:**

> **What is W0 / W1?** Just labels for **Terminal Tabs**. `W0` = Window 0 = Terminal 1, `W1` = Terminal 2. In the old `tmux` world these were `Ctrl-B C` windows inside one SSH. With **VS Code SSH you already have multiple terminals** — click `+` (New Terminal) in VS Code. No `Ctrl-B` needed. `tmux` is only if you use plain `ssh` from a single laptop Terminal and want to keep things alive after closing the laptop.

**Method A — VS Code SSH (recommended, easiest):**
1. In VS Code on Uno Q, open Panel → Terminal (`Ctrl+` ` `` `). You see `arduino@unoq:~/NexusArm$`.
2. Click `+` to add **Terminal 1 (W0)** and **Terminal 2 (W1)** (and 3 if you want). Top dropdown lists them.
3. In **every** terminal you must `exec` into the **same** container and `source` ROS (the container is the “lunchbox” — ROS lives *inside* it):
   ```bash
   docker compose exec arm bash
   source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
   # prompt becomes root@arm-stack:/workspace#
   ```
   `docker compose exec arm bash` = “open a shell *inside* the running container”. Without it you’re on bare Debian, not ROS.

**Terminal 1 (W0) — KEEP THIS RUNNING (arm + cameras):**
```bash
# (already exec'd + sourced above in W0)
ros2 launch robot_arm_hardware real_bringup.launch.py serial_port:=/dev/ttyACM0 front_url:=http://<PHONE_IP>:4747/video fps:=15.0
# This blocks — leaves it open. It starts hw_interface + hw_move_to + camera_bridge together.
# If you Ctrl+C it, the arm stops. Leave W0 alone.
```

**Terminal 2 (W1) — Tests / teleop / recorder / inference:**
```bash
# In Terminal 2 (W1), again:
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
ros2 topic list | grep -E "joint|front_cam"   # /joint_states, /front_cam/image_raw/compressed
ros2 topic hz /front_cam/image_raw/compressed  # ~10-15 Hz if phone URL correct
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x:0.27,y:0,z:0.08,pitch:-1.57,gripper:0,duration_sec:1.5}"
# Arm should home. Try gripper:1.0 to close, x:0.25 to move. See docs/07_CAMERA_BRIDGE.md.
```

**Terminal 3 (W2) — Extra tasks (each gets its own terminal):**
```bash
docker compose exec arm bash; source ...; ros2 run robot_arm_hardware keyboard_teleop
# or .venv/bin/python lerobot-ros2-recorder.py --repo-id your/dataset --fps 15 --cams front_cam
# or .venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=your/policy -p enable_robot:=true -p n_action_steps:=50
```
Phone `FRONT_URL` must be same WiFi — test `http://<PHONE_IP>:4747/video` in laptop browser first.

**Method B — plain `ssh` without VS Code (only then you need `tmux`):**
If you `ssh arduino@unoq.local` from a single laptop Terminal (no VS Code), you have only one window. Then `tmux new -s arm` gives you `W0`/`W1` inside that one SSH (`Ctrl-B C` new window, `Ctrl-B N/P` switch, `Ctrl-B D` detach to keep running after you close laptop, `tmux attach -t arm` to come back). With VS Code's `+` terminals, you skip this entirely.

### Step 6 — End-to-end cheat sheet (after first SSH):
```bash
# VS Code SSH — no tmux needed:
cd ~/NexusArm && docker compose up -d
# Terminal 1 (W0): docker compose exec arm bash → source ... → ros2 launch ... real_bringup...
# Terminal 2 (W1): docker compose exec arm bash → source ... → ros2 topic hz / service tests
# Terminal 3 (W2): docker compose exec arm bash → inference / recorder
```

## Uno Q + Docker (edge brain) — BEGINNER REFERENCE (Docker preinstalled!)

### What is Docker? What is `docker compose`?
*Think of Docker like a lunchbox.* **Docker** packs your whole computer setup (Ubuntu, ROS Jazzy, Python packages) into one box (called an **image**) so it runs the same everywhere — your laptop or the tiny Uno Q board. You don't install ROS by hand on the Uno Q; you just run the lunchbox.
* **Plain `docker`** = you type one long command every time: `docker run --device /dev/ttyACM0 --net host -v ./src:/workspace/src ros:jazzy bash` — you have to remember every flag.
* **`docker compose`** = you write those flags *once* in a file (`docker-compose.yml`) and just type `docker compose up`. It's the same `docker` underneath, just with a recipe so you don't retype 5 lines each time. That's why we use `compose` — shorter, less error-prone, same result. You *could* use plain `docker run` with the same flags from `docker-compose.yml:7-45` and it would do the same thing; `compose` is just convenient.
* `Dockerfile` = recipe to *build* the lunchbox. `docker-compose.yml` = recipe to *run* it (which devices, network, folders to share).

Uno Q is the SBC that **hosts the same ROS stack in Docker**; the Uno R3 stays the servo bridge over `/dev/ttyACM0` bound into the container (`servo_bridge.ino:26-28`).

### Build + run (container stays idle — you run commands yourself)

**On Uno Q with VS Code SSH you already have multiple terminals (Terminal `+` button) — `tmux` is optional legacy for plain `ssh`: **

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

What `docker-compose.yml` does (in plain English) — now **SLIM, fits 16 GB**:
* `FROM ros:jazzy-ros-base` → slim ROS base (not full desktop `ros:jazzy` which pulls RViz/Qt/Gazebo = your No space error). Sim runs on laptop natively, **Uno Q never needs Gazebo**.
* `apt` → ONLY real-arm: `xacro`, `robot-state-publisher`, `controller_manager`, `joint-trajectory-controller`, `joint-state-broadcaster`, `ros2-control`, `cv-bridge`, `colcon` — **no `ros-dev-tools` (that alone dragged mercurial+subversion+bloom+PyQt5+OpenCV 260 MB), no `rviz2`/`gz-sim`/`foxglove`**.
* `venv /opt/venv` → `lerobot==0.6.1` (auto `numpy 2.1.x` + `opencv 5.0`) + `setuptools==79.*` + CPU `torch` (no CUDA). `colcon build --symlink-install`.
* `devices: /dev/ttyACM0` + `network_mode: host` + `volumes: ./src:ro` + `hf-cache` — same as before.
* `command: sleep infinity` → manual as you requested.
* **Plain `docker` equivalent:** `docker build -t nexusarm . && docker run -it --net host --device /dev/ttyACM0 -v ./src:/workspace/src nexusarm bash`.

### Inference on the edge

Same as `docs/06_INFERENCE.md` / `08_TRAINING.md`, but from inside the container via `docker compose exec arm bash`:
```bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=your/policy -p enable_robot:=true -p n_action_steps:=50
```

## Troubleshooting

* `ssh: Could not resolve unoq.local` → mDNS blocked by firewall/guest WiFi — use IP `ssh arduino@192.168.1.x`; check `avahi-daemon` running: `sudo systemctl status avahi-daemon`. App Lab must have done onboarding (enables Network Mode).
* `Connection refused port 22` → App Lab onboarding not done: `adb shell` → `sudo systemctl stop sshd; sudo ssh-keygen -A; sudo systemctl start sshd; sudo systemctl enable ssh`.
* `Permission denied` → wrong password: default only pre-setup is `arduino`; after setup it's *your* password. Reset: `adb shell` → `sudo passwd arduino`.
* `Cannot open /dev/ttyACM0` → `sudo usermod -aG dialout $USER` + re-login, or `SERIAL_PORT=/dev/ttyUSB0 docker compose up` if Uno shows as USB0.
* `camera topics empty` → phone/ESP32 must be same WiFi as Uno Q; verify URL in browser before `FRONT_URL`.
* `Gripper crosses over` → travel 0.015 m matches finger collision `y±0.019`; don't increase `upper` without matching `GRIPPER_MAX_TRAVEL`.
* `No space left` (16 GB eMMC, `/var/lib/docker/overlay2` ~4 GB — **you hit this**) → Slim Dockerfile (`ros:jazzy-ros-base`, no `ros-dev-tools`) now fixes *future* builds. **No partition move needed** (per your request). Just SAFE clean before rebuilding — **NEVER `docker system prune -a --volumes -f`** (deletes `python-apps-base:0.12.0` you just saw):
  ```bash
  # On Uno Q via VS Code / adb shell — BEFORE rebuilding — SAFE clean (keeps App Lab):
  df -h; du -sh /var/lib/docker  # confirm full
  docker builder prune -f                    # only build cache, safe
  docker image prune -f                      # only dangling images, safe
  docker system prune -f                     # safe prune (no -a --volumes)
  # NOT: docker system prune -a --volumes -f  (wipes ghcr.io/arduino/app-bricks/*)
  ```
  Then: `cd ~/NexusArm && docker compose build --no-cache` — slim now fits.
* `Deleted app-bricks/python-apps-base` after prune `-a --volumes` → **Recovery (run now):** `docker pull ghcr.io/arduino/app-bricks/python-apps-base:0.12.0` (re-downloads ~300MB, SHA `35eb218...`), or open Arduino App Lab → it auto-repulls missing bricks on next App start. Verify: `docker images | grep app-bricks`. Do NOT prune with `-a --volumes` again.
* `VS Code freezes on Uno Q (2 GB)` → disable Copilot/Roo on remote host (known RAM issue).

Credits: mechanical design by **Emre Kalem (@emrekalem)** — MakerWorld Standard Digital File License.
