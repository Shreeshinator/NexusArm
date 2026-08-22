# NexusArm — 4-DOF Printed Arm: Sim → Hardware → Learning

[![Docker Pulls](https://img.shields.io/badge/docker-shreeshinator%2Fnexusarm%3Aunoq-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/shreeshinator/nexusarm) [![HF Model](https://img.shields.io/badge/HF-shreeshinator%2Farm--pick--blocks--act--first-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/shreeshinator/arm-pick-blocks-act-first) [![HF Dataset](https://img.shields.io/badge/HF-shreeshinator%2Farm--picking--blocks--real-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/shreeshinator/arm-picking-blocks-real) [![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/) [![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

A 4-DOF printed arm with one stable `MoveTo` API across Gazebo Harmonic sim, real hardware, and a learned ACT policy — deployed on **Arduino Uno Q (QRB2210)** via Docker `shreeshinator/nexusarm:unoq`.

Repo root **is** the colcon workspace (`build/`/`install/`/`log/` gitignored). Tested on ROS 2 Jazzy + Gazebo Harmonic. All packages Apache 2.0 — see [LICENSE](LICENSE).

## Where to start

| I want to... | Go to |
|---|---|
| Build from scratch | [docs/01_SETUP.md](docs/01_SETUP.md) |
| Check the math (FK/IK) | [docs/02_KINEMATICS.md](docs/02_KINEMATICS.md) |
| Run simulation (60s) | [docs/sim_setup/README.md](docs/sim_setup/README.md) |
| Build the real arm | [docs/03_HARDWARE.md](docs/03_HARDWARE.md) → [docs/04_HARDWARE_BRINGUP.md](docs/04_HARDWARE_BRINGUP.md) |
| Use Uno Q (Docker) | [HARDWARE.md](HARDWARE.md) — full command list, `fps 15` |
| Collect data / Train / Infer | [docs/05_DATA_COLLECTION.md](docs/05_DATA_COLLECTION.md) · [docs/08_TRAINING.md](docs/08_TRAINING.md) · [docs/06_INFERENCE.md](docs/06_INFERENCE.md) |

## Architecture — one stable API

```
User intent → /modular_arm/move_to (MoveTo.srv) → IK + trajectory → arm motion (sim or real)
```

| Package | Role |
|---|---|
| `modular_arm_interfaces` | `MoveTo.srv` (`x,y,z,pitch,gripper`) — build first |
| `modular_arm_kinematics` | `fk.py` / `ik.py` (pure Python, unit-tested) + `move_to_node.py` |
| `robot_arm_description` | URDF (source of truth) + Gazebo xacro + meshes + controllers |
| `modular_arm_bringup` | `sim_bringup.launch.py` — one-command sim |
| `robot_arm_hardware` | `hw_interface` + `hw_move_to` + `camera_bridge` + `lerobot_infer` |
| `modular_arm_teleop` | Leader-arm teleop |

4-DOF: `joint1` yaw → `joint2` shoulder → `joint3` elbow → `joint4` wrist → gripper. Links `L1=0.198` `L2=0.141` `L3=0.083` m. Gripper gain `1.3`, travel `0.015 m`.

## Quick start — simulation

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install && source install/setup.bash
ros2 launch modular_arm_bringup sim_bringup.launch.py

# In another terminal:
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"
```

## Quick start — real hardware

```bash
# 1. Flash sketch/servo_bridge/servo_bridge.ino to Uno R3 (115200 baud)
# 2. Wire servos + 6V supply + shared GND, connect /dev/ttyACM0
ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0 baud_rate:=115200

# Same MoveTo API:
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"

# Uno Q (Docker):
docker pull shreeshinator/nexusarm:unoq
# See HARDWARE.md for full bringup + inference (HF model, fps 15)
```

Full sim details: [docs/sim_setup/](docs/sim_setup/) · Hardware: [HARDWARE.md](HARDWARE.md) · Setup: [SETUP.md](SETUP.md) · Agent notes: [AGENTS.md](AGENTS.md)

## Credits

Mechanical design: [Robotic Arm with Servo & Arduino by Emre Kalem](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) (MakerWorld, Standard Digital File License). Meshes vendored in `src/robot_arm_description/meshes/`.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Acknowledgement

Built for the Physical AI Challenge (Arduino × robu.in). Kinematics inspired by ROBOTIS OpenMANIPULATOR-X; CAD is the credited MakerWorld design.
