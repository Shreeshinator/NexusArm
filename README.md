# AI Challenge Robotic Arm

Building a real-world robotic arm for the Physical AI Challenge by Arduino and robu.in.

This project is currently a work in progress and is focused on creating a modular arm stack that can evolve from simulation to hardware, then to language-guided physical intelligence.

## Why this project is exciting

- A practical 4-DOF robotic arm foundation with ROS2 and Gazebo
- A clean API-first design (`/modular_arm/move_to`) for future AI modules
- Planned natural-language control for human-friendly interaction
- Planned cloud-hosted VLA (Vision-Language-Action) model integration for high-level behavior
- Hardware direction centered around the Arduino Uno Q board as the edge brain

## Vision

The goal is to build an arm that can understand intent, reason about a scene, and execute motion safely.

Today:
- Kinematics and simulation are working foundations
- Service-based arm control is in place

Next:
- NLP command layer ("pick the red block", "move 5 cm left")
- Cloud VLA policy integration for perception-to-action workflows
- Real hardware bringup with Arduino Uno Q coordinating Linux capabilities plus real-time control behavior

## Current architecture

This repository currently follows a modular ROS2 package structure:

- `src/modular_arm_interfaces`: stable service API (`MoveTo.srv`)
- `src/modular_arm_description`: URDF/Xacro, RViz, Gazebo, ros2_control launch
- `src/modular_arm_kinematics`: ROS-independent FK/IK core + ROS wrapper node
- `src/modular_arm_bringup`: one-command simulation bringup

The arm model follows a proven 4-DOF pattern inspired by OpenMANIPULATOR-X:

- 1 base yaw joint
- 3 pitch joints (shoulder, elbow, wrist)

This gives simple and reliable inverse kinematics for fast target-to-joint conversion.

## Development status

WIP status:

- [x] ROS2 package layout and API boundary
- [x] FK/IK implementation and kinematics testing
- [x] RViz and Gazebo Harmonic simulation
- [x] `/modular_arm/move_to` service path for commanding targets
- [ ] NLP control package
- [ ] Cloud VLA integration package
- [ ] Physical arm hardware integration
- [ ] Safety and calibration routines for deployment

## Quick start

For complete setup and command details, see [SETUP.md](SETUP.md).

Typical flow:

```bash
# Build
colcon build --symlink-install
source install/setup.bash

# Bring up full simulation stack
ros2 launch modular_arm_bringup sim_bringup.launch.py

# Command a Cartesian target
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.10, y: 0.05, z: 0.10, pitch: -0.3, elbow: '', duration_sec: 2.0}"
```

## Planned AI stack (high level)

```text
User intent (voice/text)
    -> NLP parser + task planner
    -> Cloud VLA reasoning (scene + action proposal)
    -> Target pose generation
    -> /modular_arm/move_to
    -> IK + trajectory controller
    -> Robotic arm motion
```

## Notes

- This repository is intentionally modular so new AI capabilities can be added without rewriting low-level arm logic.
- The kinematics core is ROS-independent, making it easy to test and reuse in future planning modules.
- Hardware and cloud-AI integration are active roadmap items and will be added iteratively.

## Acknowledgement

Project developed as part of a Physical AI Challenge journey inspired by Arduino and robu.in.