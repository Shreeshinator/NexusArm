> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](README.md) — it gives the exact reading order for your goal.

# Setup — Prerequisites & Build

> Hey, welcome! This doc takes you from zero to `colcon build` without surprises. If you just want to play in sim, hop to `docs/sim_setup/README.md` — for the real arm, keep reading, we've got you covered.

## 1. What you'll need

* **Ubuntu 24.04** (Noble) + **ROS 2 Jazzy** (apt — no need to build from source, just install) — this is for your **dev laptop**.
* **Gazebo Harmonic** (it pairs nicely with Jazzy — `gz sim --version` should say Harmonic)
* Your dev laptop (x86_64) runs **native Ubuntu 24.04** — that's what the steps below assume. The **Uno Q is different: its onboard OS is Debian 13 (Trixie), *not* Ubuntu.** On the Uno Q, ROS runs inside the Ubuntu-based `shreeshinator/nexusarm:unoq` Docker image (see `HARDWARE.md`). **Only follow the native-apt steps here on your laptop**; on the Uno Q, use the Docker path.

Quick check:

```bash
lsb_release -a          # should say 24.04 noble
ros2 --help             # should show Jazzy
gz sim --version        # should say Harmonic, e.g. 8.x
python3 --version       # 3.12 on Noble
```

## 2. Install ROS 2 Jazzy + Gazebo Harmonic (if not already)

Follow https://docs.ros.org/en/jazzy/Installation.html then:

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 \
  ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge \
  ros-jazzy-gz-ros2-control ros-jazzy-controller-manager \
  ros-jazzy-joint-trajectory-controller ros-jazzy-joint-state-broadcaster \
  ros-jazzy-foxglove-bridge \
  ros-jazzy-cv-bridge \
  python3-pip python3-venv colcon-common-extensions ros-dev-tools \
  python3-serial python3-pytest

# serial udev (real hardware only, but harmless in sim)
sudo usermod -aG dialout $USER   # log out and back in after
```

> **Heads-up:** if `ros-jazzy-gz-ros2-control` is missing in your mirror, don't stress — just build it from source: https://github.com/ros-controls/gz_ros2_control (Harmonic branch).

## 3. Clone & build (colcon workspace = repo root)

```bash
git clone https://github.com/Shreeshinator/NexusArm.git ~/NexusArm
cd ~/NexusArm
# or if you already cloned, just cd to it

source /opt/ros/jazzy/setup.bash
rosdep update 2>/dev/null || sudo rosdep init && rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy

colcon build --symlink-install
source install/setup.bash
```

* `source /opt/ros/jazzy/setup.bash` **first**, every terminal.
* `--symlink-install` applies pure-Python edits (e.g. `fk.py`) without rebuild; changing `modular_arm_interfaces/srv/MoveTo.srv` **does** need a rebuild.
* After build, `source install/setup.bash` in each new terminal (or add to `~/.bashrc`).

Verify:

```bash
ros2 pkg list | grep robot_arm          # should show robot_arm_description, robot_arm_hardware
ros2 pkg list | grep modular_arm        # interfaces, kinematics, bringup, teleop
ros2 interface show modular_arm_interfaces/srv/MoveTo
```

Package list (`src/` — what actually builds):

```
modular_arm_interfaces   # MoveTo.srv — build first (stable API)
modular_arm_kinematics   # fk.py/ik.py (pure Python, zero ROS) + move_to_node
robot_arm_description    # ACTIVE — robot_arm.urdf + xacro + meshes + worlds + controllers
modular_arm_bringup      # sim_bringup.launch.py (includes robot_arm_description)
robot_arm_hardware       # real hardware: hw_interface, hw_move_to, camera_bridge, lerobot_infer
modular_arm_teleop       # optional — Arduino pots → sim teleop (needs hardware)
```

## 4. Python venv for LeRobot (recorder + inference)

> Do **not** `pip install lerobot` into system Python — it bumps `setuptools` past 80 and breaks `colcon` builds. Use the repo-root `.venv`.

The repo ships without `.venv` (it's gitignored). Create it once:

```bash
# install uv if needed (one-time)
pipx install uv  # or: curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv --system-site-packages .venv   # or: python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install "setuptools==79.*"         # must be <80 BEFORE lerobot (81 breaks colcon)
uv pip install "lerobot==0.6.1" "numpy==1.26.4" "opencv-python-headless" h5py datasets
# torch: CPU wheel (dev machine)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

Pins (critical — don't change without testing):

* `lerobot==0.6.1`, `numpy==1.26.4` (<2 — `opencv-python-headless 4.13.0` is NumPy 1.x ABI; 2.x crashes recorder)
* **Only** `opencv-python-headless` — remove `opencv-python` if present: `pip uninstall -y opencv-python`
* `setuptools==79.*` (<80) — install *before* lerobot, or `colcon build` will error

Run venv tools as:

```bash
.venv/bin/python lerobot-ros2-recorder.py --help
source /opt/ros/jazzy/setup.bash && .venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p enable_robot:=false
```

## 5. Quick checks

```bash
# Kinematics without ROS (needs python3-pytest from apt, or pip install pytest)
cd src/modular_arm_kinematics && python3 -m pytest test/test_kinematics.py -v

# RViz (URDF check — no Gazebo needed)
ros2 launch robot_arm_description display.launch.py

# Gazebo full sim (needs ros-jazzy-foxglove-bridge; if missing, sim still runs but Foxglove won't start)
ros2 launch modular_arm_bringup sim_bringup.launch.py

# second terminal — source the workspace first, then check (DDS is per-terminal):
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 control list_controllers   # expect joint_state_broadcaster [active] + arm_controller [active]
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"
```

If sim fails, see `sim_setup/04_troubleshooting_sim.md` (from repo root) or `docs/sim_setup/04_troubleshooting_sim.md`.

## 6. Next steps

* Understand the geometry → `02_KINEMATICS.md` (FK/IK, sync rules, tests)
* Sim-only → `sim_setup/README.md` — then `01_sim_bringup.md` → `02_move_to_api.md` → `03_cameras_and_foxglove.md` → `04_troubleshooting_sim.md` → `05_teleop.md` (pots)
* Build the arm → `03_HARDWARE.md` (BOM + assembly + circuit) → `04_HARDWARE_BRINGUP.md` (flash + ROS bringup) — based on [Emre Kalem's MakerWorld model](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927)
* Set up cameras → `07_CAMERA_BRIDGE.md` (phone/ESP32 MJPEG → ROS 2, params, QoS, fps) — required for collection & inference
* Collect demos → `05_DATA_COLLECTION.md` (with § Resume — append after `finish`)
* Train your own ACT → `08_TRAINING.md` (free Colab/Kaggle, `lerobot-train` + `--resume`)
* Deploy the policy → `06_INFERENCE.md` (ACT, `n_action_steps=50` @15Hz, verified sweet spot)

## Credits

* **3D model:** [Robotic Arm with Servo & Arduino](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) by **Emre Kalem (@emrekalem)** on MakerWorld (Standard Digital File License). Print: 0.2 mm, 3 walls, 20% infill, 4 plates. STLs in `src/robot_arm_description/meshes/` are adapted from this source.
