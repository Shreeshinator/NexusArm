# Hardware — Native + Uno Q (Docker) Bringup

> ✅ **Verified 2026-08-22 — FULL BRINGUP TESTED on Uno Q QRB2210 4GB `aarch64`, QC Debian 13, `shreeshinator/nexusarm:unoq 7.15GB`, `lerobot 0.6.1 + av 14.2.0 + torch 2.7.0/torchvision 0.22.0 + OPENBLAS_CORETYPE=ARMV8`, `fps 15`, `HF_TOKEN` HF_TRANSFER**

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

## VS CODE SSH — GUIDE: LAPTOP/WSL → UNO Q → REAL ARM (START TO FINISH)

> **Step-by-step for Uno Q (2025+).** The Uno Q is the board next to the arm: **Qualcomm QRB2210 + STM32U585, Debian 13 “Trixie” arm64, 16/32 GB eMMC, soldered — no SD card.** The same ROS code runs natively on a laptop (`colcon build`) or on the Uno Q **in Docker** (lunchbox). App Lab is preinstalled and uses Docker internally.

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
2. **Important:** On Uno Q, VS Code Copilot/Roo extensions consume the available RAM. In VS Code Settings on the *remote* (Uno Q), disable Copilot on that host if freezes occur.
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

### Step 5 — FIX 10GB ROOT FIRST (MANDATORY — 2 min) then Build
**Root 10GB with 9.1GB used = 239M free (98%). Slim image alone cannot fit — Docker defaults to `/var/lib/docker` on root. The `18G /home/arduino` partition has 17G free — Docker must be moved there:**

```bash
# Inside Uno Q (VS Code Terminal):
df -h  # confirm: / is 9.8G 98% 239M free, /home/arduino is 18G 4% 17G free
docker builder prune -f; docker image prune -f  # safe clean only, keeps App Lab
sudo systemctl stop docker.socket; sudo systemctl stop docker
sudo mkdir -p /home/arduino/docker
echo '{"data-root":"/home/arduino/docker"}' | sudo tee /etc/docker/daemon.json
sudo rsync -a /var/lib/docker/ /home/arduino/docker/  # copy to 17G partition (1-2 min)
sudo rm -rf /var/lib/docker  # free root (optional, already copied)
sudo systemctl start docker; df -h  # / now ~60%, Docker Root Dir: /home/arduino/docker
docker info 2>/dev/null | grep "Docker Root Dir"  # must be /home/arduino/docker
```
> No resizing or wipe is required. One `echo` line tells Docker to store on `/home/arduino`. Reversible: `sudo rm /etc/docker/daemon.json && sudo systemctl restart docker` to undo. **Critical: `/home/docker` is still on root (239M) — must be `/home/arduino/docker` (17G).**

**What happens next:** `docker compose build` reads **slim** `Dockerfile` (`ros:jazzy-ros-base`, not full desktop) and downloads ~1 GB multi-arch (first time 5-10 min slower on 2GB RAM Uno Q). It creates venv `lerobot==0.6.1` (auto `numpy 2.1.x` + `opencv 5.0`, NOT `1.26.4` bug) + `setuptools 79` + CPU `torch`, copies `src/`, runs `colcon build`. `docker compose up -d` creates `arm-stack` (`Creating arm-stack ... done`), mounts `src/` + `/dev/ttyACM0` + `host` network, runs `sleep infinity` — idle, no ROS auto-started. `docker compose ps` proves `Up`.

```bash
cd ~/NexusArm
docker compose build          # now fits on /home (was No space before)
docker compose up -d          # sleep infinity, NO auto ROS
docker compose ps             # should show arm-stack Up X seconds
docker logs arm-stack         # empty (we slept)
```

**Option C — Build on Laptop then load (avoids building on small Uno Q):** To avoid building on the Uno Q, apply the FIX above first (still required for storage), then on **laptop/WSL** run `docker build -t nexusarm . && docker save nexusarm | gzip > nexusarm.tar.gz`, `scp nexusarm.tar.gz arduino@unoq.local:/home/arduino/`, then on Uno Q `docker load < nexusarm.tar.gz && docker compose up -d` — also lands on `/home`.

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

### FULL COMMAND LIST — EVERYTHING WORKING (no rebuild, live install okay, copy-paste in order)

**Prerequisite: `shreeshinator/nexusarm:unoq 7.15GB` is pulled to `/home/arduino/docker` 17G. This list covers the remaining blockers (meshes `890645f` vendored 3M, `numpy 2.1`, `av 14.2`, `torch A53`, `HF_TOKEN`, `service call` syntax, `venv` path) without rebuilding the image:**

```bash
# 0. Verify fixes already done (should be ✅):
df -h  # / 9.8G ~60%, /home/arduino 18G ~2G used
cat /etc/docker/daemon.json  # {"data-root":"/home/arduino/docker"}
docker info 2>/dev/null | grep "Docker Root Dir"  # /home/arduino/docker
docker images | grep nexusarm  # shreeshinator/nexusarm:unoq 7.15GB
find src/robot_arm_description/meshes -type l | wc -l  # 0 (real STLS vendored)

# 1. Fix image name mismatch (image is shreeshinator/nexusarm:unoq, compose expects nexusarm-arm:latest):
docker tag shreeshinator/nexusarm:unoq nexusarm-arm:latest
docker compose up -d --no-build
docker compose ps  # arm-stack Up (sleep infinity)

# 2. VS Code SSH + = 3 terminals. In EVERY terminal:
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
# prompt → (venv) root@...:/workspace#  — venv is /opt/venv, NOT .venv (host only, .venv/bin/python: No such file inside Docker)
# check: which python → /opt/venv/bin/python , echo $VIRTUAL_ENV → /opt/venv

# 3. Terminal 1 (W0) KEEP OPEN — arm + cameras at 15Hz:
ros2 launch robot_arm_hardware real_bringup.launch.py serial_port:=/dev/ttyACM0 front_url:=http://<PHONE_IP>:4747/video fps:=15.0
# front_url must be same WiFi as Uno Q, test http://<PHONE_IP>:4747/video in laptop browser first

# 4. Terminal 2 (W1) — verify (while W0 blocking):
ros2 topic hz /front_cam/image_raw/compressed  # ~13-15Hz
ros2 topic echo /joint_states --once
# Correct service call syntax (space after colon!):
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, gripper: 0.0, duration_sec: 1.5}"
# NOT "{x:0.27}" (no space → Failed to populate field)

# 5. Terminal 3 (W2) — LIVE FIX av + torch inside container (no rebuild, installing is okay):
# av was 18.1.0 False (no av.option) → downgrade to wheel that has av.option:
pip show av | grep Version  # 18.1.0
pip uninstall -y av
pip install --no-cache-dir --only-binary=av "av==14.2.0"  # 12.3.0/14.2.0 have av.option
python -c "import av; print(av.__version__, hasattr(av,'option'))"  # 14.2.0 True
# torch 2.11 has dotprod → Illegal instruction on A53 (QRB2210) BUT downgrading to 2.4.0 breaks lerobot 0.6.1 (requires torch>=2.7):
# pip resolver error when torch <2.7: lerobot 0.6.1 requires torch<2.12.0,>=2.7
# FIX: Keep torch 2.7+ (satisfies lerobot) and disable dotprod via env — QRB2210 A53 is armv8-a without dotprod:
pip uninstall -y torch torchvision  # if 2.4.0 is installed (incompatible, lerobot requires >=2.7)
# Use MATCHED pair: torch 2.7.0 + torchvision 0.22.0  OR  torch 2.7.1 + torchvision 0.22.1 (0.22.0 expects 2.7.0 exactly)
pip install --no-cache-dir --only-binary=:all: "torch==2.7.0" "torchvision==0.22.0" --index-url https://download.pytorch.org/whl/cpu
# If you prefer 2.7.1: pip install "torch==2.7.1" "torchvision==0.22.1" --index-url https://download.pytorch.org/whl/cpu
# Force OpenBLAS to use generic ARMv8 (no SDOT) — fixes Illegal instruction without breaking lerobot deps:
export OPENBLAS_CORETYPE=ARMV8
export OPENBLAS_VERBOSE=0
python -c "import torch; x=torch.randn(2,2); print(x @ x)"  # must NOT Illegal instruction
# Keep this export for lerobot_infer below (add to same terminal before python -m ...)

# 6. Terminal 3 (W2) — ACT with HF_TOKEN for faster download (replace hf_... with your token from huggingface.co/settings/tokens):
docker compose exec -e HF_TOKEN=hf_YOUR_TOKEN_HERE -e OPENBLAS_CORETYPE=ARMV8 arm bash
# ^ must include arm bash after -e (requires SERVICE + COMMAND) and pass OPENBLAS fix for A53
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
export HF_HUB_ENABLE_HF_TRANSFER=1  # 2-3x faster if hf_transfer installed (pip show hf_transfer)
export OPENBLAS_CORETYPE=ARMV8
export OPENBLAS_VERBOSE=0
python -m robot_arm_hardware.lerobot_infer --ros-args -p hf_repo:=shreeshinator/arm-pick-blocks-act-first -p enable_robot:=true -p fps:=15 -p n_action_steps:=50
# Log: homing complete — policy running → then ros2 topic hz /joint_command 15Hz (was waiting for /front_cam + /joint_states, now publishing)
# First run downloads ~400MB to /home/arduino/docker hf-cache (17G), next runs instant
```

**Update without rebuild:** `git pull` new fix → Codespaces `docker buildx build --platform linux/arm64 -t shreeshinator/nexusarm:unoq --push` → Uno Q `docker pull shreeshinator/nexusarm:unoq && docker tag ... && docker compose up -d --force-recreate --no-build` → re-do Step 5 pip downgrades if new image still has torch 2.11.

## Uno Q + Docker (edge brain) — BEGINNER REFERENCE (Docker preinstalled!)

### What is Docker? What is `docker compose`?
*Think of Docker like a lunchbox.* **Docker** packs your whole computer setup (Ubuntu, ROS Jazzy, Python packages) into one box (called an **image**) so it runs the same everywhere — your laptop or the tiny Uno Q board. You don't install ROS by hand on the Uno Q; you just run the lunchbox.
* **Plain `docker`** = you type one long command every time: `docker run --device /dev/ttyACM0 --net host -v ./src:/workspace/src ros:jazzy bash` — you have to remember every flag.
* **`docker compose`** = you write those flags *once* in a file (`docker-compose.yml`) and just type `docker compose up`. It's the same `docker` underneath, just with a recipe so you don't retype 5 lines each time. That's why we use `compose` — shorter, less error-prone, same result. You *could* use plain `docker run` with the same flags from `docker-compose.yml:7-45` and it would do the same thing; `compose` is just convenient.
* `Dockerfile` = recipe to *build* the lunchbox. `docker-compose.yml` = recipe to *run* it (which devices, network, folders to share).

Uno Q is the SBC that **hosts the same ROS stack in Docker**; the Uno R3 stays the servo bridge over `/dev/ttyACM0` bound into the container (`servo_bridge.ino:26-28`).

### Build + run (container stays idle — you run commands yourself)

**On Uno Q with VS Code SSH multiple terminals are available (Terminal `+` button) — `tmux` is optional legacy for plain `ssh`:**

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

## OPTION C — Build on GitHub Codespaces → Docker Hub → Pull on Uno Q (1 day, no laptop stress)

**Why Codespaces:** Your Uno Q root is 98% (9.8G 239M free) and laptop `buildx` is slow. Codespaces is a cloud Ubuntu VM (32GB disk, `buildx` preinstalled, Docker-in-Docker) — do the heavy `docker build` there, push to your **Docker Hub** account, then Uno Q just `docker pull` (lands on `/home/docker` 17GB free).

**With vendored meshes (`890645f` real 3.0M STLs), the Codespaces build passes `Failed <<< robot_arm_description`.**

**Steps (copy-paste):**

**1. Push vendored meshes (done: `890645f` → `NexusArm/main` ✅).** Now create Codespace:
* GitHub.com → `Shreeshinator/NexusArm` → `Code` → `Codespaces` → `Create codespace on main` (or `working`). Wait 60s, terminal `vscode →` means you are on Codespaces (`uname -m` = `x86_64`).

**2. Codespaces — Build `arm64` for Uno Q + push to Docker Hub:**
```bash
# In Codespace terminal:
git pull
docker --version; docker buildx version  # already there
docker buildx create --use --name nexusarm 2>/dev/null || docker buildx use nexusarm
docker buildx inspect --bootstrap  # 30s

# Login to YOUR Docker Hub (one-time): Docker Hub → Account Settings → Security → New Access Token → copy
echo $DOCKERHUB_PAT | docker login -u YOUR_DOCKERHUB_USER --password-stdin
# Or: docker login -u YOUR_USER  # then paste PAT when asked for password

# Cross-build for Uno Q (aarch64) even though Codespace is x86_64, and push:
docker buildx build --platform linux/arm64 -t YOUR_USER/nexusarm:unoq -f Dockerfile . --push
# 5-10 min first time (ros:jazzy-ros-base ~750MB + pip lerobot/torch ~1GB + colcon). --push pushes manifest directly, no 2GB scp.
# For both laptop + Uno Q: --platform linux/amd64,linux/arm64 -t YOUR_USER/nexusarm:latest --push
docker buildx imagetools inspect YOUR_USER/nexusarm:unoq  # verify arm64
```

**3. Uno Q (`arduino@shreeshuno`, already `daemon.json=/home/docker` ✅ `Docker Root Dir: /home/docker`):**
```bash
# VS Code SSH to Uno Q:
docker login -u YOUR_USER  # same PAT
docker pull YOUR_USER/nexusarm:unoq  # pulls into /home/docker (17GB), NOT root 239M
cd ~/NexusArm && git pull  # sync vendored meshes
# In docker-compose.yml ensure:  arm:  image: YOUR_USER/nexusarm:unoq  (keep command: sleep infinity)
docker compose up -d && docker compose ps  # arm-stack Up
docker compose exec arm bash  # then source ... && ros2 launch real_bringup...
```
*Why `/home/arduino/nexusarm-unoq.tar.gz` not needed now:* `scp` to `/home/arduino` was a staging file → `docker load` → `/home/docker`. With Codespaces + Docker Hub you skip the 2GB file entirely — `docker pull` writes straight to `/home/docker`.

**Update cadence:** `git pull` new `Dockerfile` → Codespaces `buildx build --push` → Uno Q `docker pull YOUR_USER/nexusarm:unoq && docker compose up -d --force-recreate`.

---

## Troubleshooting

* `ssh: Could not resolve unoq.local` → mDNS blocked by firewall/guest WiFi — use IP `ssh arduino@192.168.1.x`; check `avahi-daemon` running: `sudo systemctl status avahi-daemon`. App Lab must have done onboarding (enables Network Mode).
* `Connection refused port 22` → App Lab onboarding not done: `adb shell` → `sudo systemctl stop sshd; sudo ssh-keygen -A; sudo systemctl start sshd; sudo systemctl enable ssh`.
* `Permission denied` → wrong password: default only pre-setup is `arduino`; after setup it's *your* password. Reset: `adb shell` → `sudo passwd arduino`.
* `Cannot open /dev/ttyACM0` → `sudo usermod -aG dialout $USER` + re-login, or `SERIAL_PORT=/dev/ttyUSB0 docker compose up` if Uno shows as USB0.
* `camera topics empty` → phone/ESP32 must be same WiFi as Uno Q; verify URL in browser before `FRONT_URL`.
* `Gripper crosses over` → travel 0.015 m matches finger collision `y±0.019`; don't increase `upper` without matching `GRIPPER_MAX_TRAVEL`.
* `Failed <<< robot_arm_description Could not create symlink ... Alt_Govde.stl` → You had dangling symlinks (`120000`) to `/home/shreeshinator/Robotic+Arm...` outside repo. Fixed in `890645f` by vendoring real `100644` 3.0M STLs — `git pull` on Codespaces/Uno Q. Verify: `find src/robot_arm_description/meshes -type l | wc -l` must be `0`.
* `No space left` (16 GB eMMC, root 9.8G 239M free 98%) → **Must be `/home/arduino/docker` (17G), NOT `/home/docker` (239M):** `df -h` shows `/` 9.8G + `/home/arduino` 18G separate — `/home` itself is on root. **Incorrect `daemon.json=/home/docker` remains on root → `docker pull 3GB → no space`:**
  ```bash
  # On Uno Q via VS Code / adb shell — DO THIS ONCE:
  df -h  # / 9.8G 98% 239M, /home/arduino 18G 4% 17G free
  docker builder prune -f; docker image prune -f  # SAFE, keeps App Lab
  # NEVER docker system prune -a --volumes -f  (wipes ghcr.io/arduino/app-bricks/*)
  sudo systemctl stop docker.socket; sudo systemctl stop docker
  sudo mkdir -p /home/arduino/docker
  echo '{"data-root":"/home/arduino/docker"}' | sudo tee /etc/docker/daemon.json
  sudo rsync -a /var/lib/docker/ /home/arduino/docker/  # or /home/docker → /home/arduino/docker if already moved
  sudo rm -rf /var/lib/docker; sudo rm -rf /home/docker  # free root
  sudo systemctl start docker; df -h  # / ~60%, Docker Root Dir: /home/arduino/docker
  docker info 2>/dev/null | grep "Docker Root Dir"  # must be /home/arduino/docker
  ```
* `Error: No such image: nexusarm-arm:latest` after `docker pull shreeshinator/nexusarm:unoq 7.15GB` → Compose expects `nexusarm-arm:latest` but you pulled `shreeshinator/nexusarm:unoq`: `docker tag shreeshinator/nexusarm:unoq nexusarm-arm:latest && docker compose up -d --no-build`
* `Failed to populate field: MoveTo_Request has no attribute 'x:0.27'` → Missing space after colon: use `"{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, gripper: 0.0, duration_sec: 1.5}"` (space after `:`), not `"{x:0.27}"`
* `bash: .venv/bin/python: No such file` inside Docker `root@...:/workspace#` → Venv inside Docker is `/opt/venv` (`Dockerfile:24`), not `.venv` (host only). Use `python -m ...` or `/opt/venv/bin/python -m ...` after `source /opt/venv/bin/activate` (`which python → /opt/venv/bin/python`)
* `ImportError: 'av' is required` / `av 18.1.0 False` → `Dockerfile` installed `lerobot 0.6.1` without `av`: `pip install --only-binary=av "av==14.2.0"` (14.2.0/12.3.0 have `av.option`, 18.1.0 False on aarch64). Also `pip install --only-binary=av` needs no source build — if `Getting requirements to build wheel ... libavdevice not found` then `av` wheel missing → use `--only-binary=av`
* `AttributeError: module 'av' has no attribute 'option'` at `pyav_utils.py:73` → Same `av` version mismatch (`av 18.1.0 False`), downgrade to `av==14.2.0` as above. Type hint `av.option.Option` only
* `Package libavdevice was not found ... REQUIRED ffmpeg 7` when `pip install av` → `ros:jazzy-ros-base` has `ffmpeg 6` (`libav 59`), `av` source needs `ffmpeg 7` + `libav*dev`; use `--only-binary=av` wheel (no dev needed) or `apt install ffmpeg libavcodec-dev ...` then `pip install av==14.2.0`
* `requires at least 2 arg(s), only received 0` on `docker compose exec -e HF_TOKEN=...` → Forgot `arm bash`: `docker compose exec -e HF_TOKEN=hf_... arm bash` (needs `SERVICE COMMAND`)
* `Illegal instruction (core dumped)` after `homing complete — policy running` → `torch 2.11` `aarch64` wheel compiled `armv8.2-a+dotprod` but `QRB2210 4×A53` is `armv8-a` without `dotprod` → `SDOT` illegal. Downgrading to `2.4.0` breaks `lerobot 0.6.1 requires torch>=2.7` (`ERROR: lerobot requires torch<2.12.0,>=2.7, but you have 2.4.0`). Live fix (no rebuild): `pip install "torch==2.7.0" "torchvision==0.22.0" --index-url https://download.pytorch.org/whl/cpu` (matched pair, satisfies lerobot) + `export OPENBLAS_CORETYPE=ARMV8` (forces generic ARMv8, no SDOT) → `python -c "import torch; x=torch.randn(2,2); print(x@x)"` must not crash. Keep `av==14.2.0` + `HF_TOKEN` + `fps 15`
* `ERROR: pip's dependency resolver ... lerobot 0.6.1 requires torch<2.12.0,>=2.7, but you have torch 2.4.0` → Version too low. Reinstall `torch==2.7.0 torchvision==0.22.0` (matched, `>=2.7,<2.12`) + `export OPENBLAS_CORETYPE=ARMV8` instead of `2.4.0`
* `ERROR: Cannot install torch==2.7.1 and torchvision==0.22.0 because torchvision 0.22.0 depends on torch==2.7.0` → Mismatched pair. Use **matched** `torch==2.7.0 torchvision==0.22.0` OR `torch==2.7.1 torchvision==0.22.1` (0.22.0 needs 2.7.0 exactly)
* `still waiting for /modular_arm/move_to ...` then `homing ... waiting 2.0s` forever → W0 `real_bringup` not running or `serial_port` wrong — `ros2 topic list | grep modular_arm` must show `/modular_arm/move_to`
* `policy timer started ... waiting for /front_cam/... + /joint_states` but not publishing `/joint_command` → Camera or joint_state `0Hz`: `ros2 topic hz /front_cam/image_raw/compressed` and `ros2 topic echo /joint_states --once` in W1 must be `>0Hz` while W0 `real_bringup fps:=15.0` running
* `Deleted app-bricks/python-apps-base` after prune `-a --volumes` → **Recovery:** `docker pull ghcr.io/arduino/app-bricks/python-apps-base:0.12.0`, verify `docker images | grep app-bricks`. Do NOT `prune -a --volumes` again.
* `VS Code freezes on Uno Q (2 GB)` → disable Copilot/Roo on remote host (known RAM issue).

Credits: mechanical design by **Emre Kalem (@emrekalem)** — MakerWorld Standard Digital File License.
