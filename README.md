# AI Challenge Robotic Arm

Building a real-world 4-DOF robotic arm for the Physical AI Challenge by Arduino and robu.in — simulation to hardware to learning.

This repo is a **colcon workspace** (repo root *is* the workspace). `build/` / `install/` / `log/` live here and are gitignored. Tested on **ROS 2 Jazzy + Gazebo Harmonic**.

> **3D print model:** [Robotic Arm with Servo & Arduino by Emre Kalem](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) on MakerWorld — STL meshes adapted in `src/robot_arm_description/meshes/`. See [Credits](#credits).

---

## Where to start

| I want to... | Go to |
|---|---|
| Build from scratch | [`docs/01_SETUP.md`](docs/01_SETUP.md) — OS, apt deps, venv, `colcon build` |
| Check the math | [`docs/02_KINEMATICS.md`](docs/02_KINEMATICS.md) — FK/IK, sync rules, tests |
| Run simulation only | [`docs/sim_setup/README.md`](docs/sim_setup/README.md) — 60-second sim quickstart |
| Understand sim internals | [`docs/sim_setup/`](docs/sim_setup/) — bringup, MoveTo API, cameras, troubleshooting |
| Build the real arm | [`docs/03_HARDWARE.md`](docs/03_HARDWARE.md) — BOM + assembly + circuit, then [`docs/04_HARDWARE_BRINGUP.md`](docs/04_HARDWARE_BRINGUP.md) — flash + ROS bringup |
| Collect data | [`docs/05_DATA_COLLECTION.md`](docs/05_DATA_COLLECTION.md) — regroup? resume? see § Resume |
| Train your policy (free) | [`docs/08_TRAINING.md`](docs/08_TRAINING.md) — Colab/Kaggle ACT, `resume` friendly |
| Run the learned policy | [`docs/06_INFERENCE.md`](docs/06_INFERENCE.md) — ACT inference on hardware |
| Learn LeRobot internals | [`lerobot_custom_hardware.md`](lerobot_custom_hardware.md) (upstream) — optional deep-dive |

> **Uno Q / Docker port** — ready: `Dockerfile` + `docker-compose.yml` (multi-arch `ros:jazzy`, venv `/opt/venv --system-site-packages` pinned `lerobot==0.6.1`) + `real_bringup.launch.py` unified launch. See `HARDWARE.md` + `UNO_Q_PORT_PLAN.md`.

---

## Architecture

```
User intent (text/voice)
  -> Task planner / VLA (future)
  -> /modular_arm/move_to  (MoveTo.srv — stable API boundary)
  -> IK + trajectory controller
  -> arm motion (sim or real)
```

### Packages (`src/`)

| Package | Role |
|---|---|
| `modular_arm_interfaces` | `MoveTo.srv` (`x,y,z,pitch,elbow,gripper,duration_sec` → `success,message,joint_angles`). Must build first. |
| `modular_arm_kinematics` | `fk.py` / `ik.py` — **pure Python, zero ROS deps**, unit-tested — plus `move_to_node.py` thin ROS wrapper |
| `robot_arm_description` | **Active description** — `urdf/robot_arm.urdf` (source of truth) + `robot_arm.urdf.xacro` (Gazebo copy + wrist camera), meshes, `worlds/workspace.sdf`, `config/ros2_controllers.yaml`, launch |
| `modular_arm_bringup` | One-command sim: `sim_bringup.launch.py` (Gazebo + controllers + move_to node) |
| `robot_arm_hardware` | Real hardware: `hw_interface.py` (`/joint_command` Float64MultiArray → serial CSV 115200 to Uno R3 `sketch/servo_bridge/`), `hw_move_to.py` (Cartesian → joint server), `camera_bridge.py` (MJPEG → CompressedImage, DroidCam/ESP32), `lerobot_infer.py` (ACT), teleops |
| `modular_arm_teleop` | Arduino leader-arm teleop — pots + button → `arm_controller` (sim, see `docs/sim_setup/05_teleop.md`) |

**Stable API:** everything (teleop, recorder, future LLM/VLA) calls `/modular_arm/move_to` — never joint angles directly.

### Arm model

* 4-DOF: `joint1` yaw (Z) → `joint2` shoulder → `joint3` elbow → `joint4` wrist → `finger_left/right_joint` + fixed `cap_joint`.
* Link lengths: `L1=0.198`, `L2=0.141`, `L3=0.083` (meters) — defined in `fk.py`/`ik.py` and must match URDF.
* Zero pose points **forward (+X)**; `pitch = -(theta2+theta3+theta4)`; only `elbow='down'` reachable forward (up raises `Unreachable`).
* Gripper: empirically tuned `position_proportional_gain=1.3` in `ros2_controllers.yaml` (1.0 weak, 5-10 oscillates), travel `0.015 m`.

---

## Quick start — simulation

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install && source install/setup.bash

# Full sim (Gazebo Harmonic + controllers + move_to service)
ros2 launch modular_arm_bringup sim_bringup.launch.py

# In another terminal — command a Cartesian target
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"

# Sanity-check kinematics without ROS/Gazebo
cd src/modular_arm_kinematics && python3 -m pytest test/test_kinematics.py -v
```

Full sim guide (cameras, Foxglove, headless, killing orphans): [`docs/sim_setup/`](docs/sim_setup/)

## Quick start — real hardware (summary)

```bash
# 1. Flash sketch/servo_bridge/servo_bridge.ino to Uno R3 (arduino-cli or IDE, 115200 baud)
# 2. Wire servos + 5-6V supply + shared GND, connect Uno R3 via /dev/ttyACM0
# 3. Bring up
ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0 baud_rate:=115200
# or: ros2 launch robot_arm_hardware real_hw.launch.py

# 4. Drive via same MoveTo API
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"
```

Details, BOM, calibration & bringup: [`docs/03_HARDWARE.md`](docs/03_HARDWARE.md) (assembly + circuit) + [`docs/04_HARDWARE_BRINGUP.md`](docs/04_HARDWARE_BRINGUP.md) (flash, pin map, `real_arm.launch.py`) — based on the [Emre Kalem MakerWorld model](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) (see [Credits](#credits)).

---

## Kinematics

`fk.py` / `ik.py` have no ROS dependencies — reusable from notebooks, planners, or VLA post-processors. Critical sync rule: `robot_arm.urdf` is the source of truth; `robot_arm.urdf.xacro` must be diffed and mirrored after any edit (adds wrist-camera `<gazebo>` + `robot_arm.gazebo.xacro` include). See [`docs/02_KINEMATICS.md`](docs/02_KINEMATICS.md).

## Data collection & learning

* **Reference:** [`lerobot_custom_hardware.md`](lerobot_custom_hardware.md) — upstream LeRobot guide for custom `Robot`/`Teleoperator` subclasses (kept intact for reading).
* **Our recorder:** [`lerobot-ros2-recorder.py`](lerobot-ros2-recorder.py) (extracted from `lerobot-ros2-recorder.md`) → LeRobotDataset v3 from ROS 2 topics. Venv at repo root `.venv` (`include-system-site-packages=true`, `lerobot==0.6.1`, `numpy==1.26.4`, `setuptools<80`). Topics: `/wrist_camera/image_raw` + `/cam_front/image_raw` (sim: `/cam_front/image_raw` + `/wrist_camera/image_raw`; real: compressed `/front_cam/image_raw/compressed`). Episode control via `ros2 topic pub /lerobot_recorder/command` or keyboard.
* **Policy:** `shreeshinator/arm-pick-blocks-act-first` (ACT, chunk 100). Task string must be exactly `"place the block in the bowl"`.

Guides: [`docs/05_DATA_COLLECTION.md`](docs/05_DATA_COLLECTION.md) · [`docs/08_TRAINING.md`](docs/08_TRAINING.md) (free Colab/Kaggle + resume) · [`docs/06_INFERENCE.md`](docs/06_INFERENCE.md)

## Troubleshooting

* **Sim won't start / controllers empty** — `ros2 control list_controllers` empty means spawner raced controller_manager; relaunch. Orphaned sims: `pkill -9 -f "gz sim"` (not `killall gz` — it's Ruby) + see [`docs/sim_setup/04_troubleshooting_sim.md`](docs/sim_setup/04_troubleshooting_sim.md).
* **Cameras empty** — verify from same terminal that launched sim; cross-terminal DDS discovery fails. Wrist camera bridge requires robot spawn first.
* **Gripper oscillates / weak** — check `position_proportional_gain=1.3` in `ros2_controllers.yaml`.

Setup details: [`SETUP.md`](SETUP.md) (redirects to `docs/01_SETUP.md`) · Full roadmap: `UNO_Q_PORT_PLAN.md`.

## Credits

* **Mechanical design:** [Robotic Arm with Servo & Arduino](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) by **Emre Kalem (@emrekalem)** on MakerWorld — licensed under Standard Digital File License. Printed at 0.2 mm layer, 3 walls, 20% infill (4 plates, ~14.3 h); meshes adapted/renamed under `src/robot_arm_description/meshes/` for `GZ_SIM_RESOURCE_PATH`.
* **Hardware BOM (this build):** 1× MG946R (base yaw), 2× MG995/MG996R (shoulder — paired opposite rotation), 1× MG995/MG996R (elbow), 1× SG90 (wrist pitch), 1× SG90 (gripper), 1× SG90 (wrist roll — fixed), Arduino Uno R3, 608 + 2× 6203 bearings, M3 screws, perfboards + headers, ZK-4XX buck-boost with display + LiPo — full build in `docs/03_HARDWARE.md`.
* **Acknowledgement:** Project developed as part of the Physical AI Challenge journey inspired by Arduino and robu.in. Arm kinematics pattern inspired by ROBOTIS OpenMANIPULATOR-X; CAD is the credited MakerWorld design, URDF/tuning is project-specific.
