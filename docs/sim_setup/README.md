> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](../README.md) — it gives the exact reading order for your goal.

# Sim Setup — 60-Second Quickstart

> You're in the right place if you just want the sim running! Only this file needed — hardware folks, you can hop to `docs/03_HARDWARE.md` after.

## Prerequisites

* Ubuntu 24.04 + ROS 2 **Jazzy** + **Gazebo Harmonic** installed
* This repo built once: see `docs/01_SETUP.md` or run below

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install && source install/setup.bash
```

## One-command sim

```bash
ros2 launch modular_arm_bringup sim_bringup.launch.py
```

This launches ([source: `src/modular_arm_bringup/launch/sim_bringup.launch.py`](../../src/modular_arm_bringup/launch/sim_bringup.launch.py) → [`robot_arm_description/launch/gazebo.launch.py`](../../src/robot_arm_description/launch/gazebo.launch.py)):

* Gazebo Harmonic server (`-r -s -v3`) with `src/robot_arm_description/worlds/workspace.sdf`
* `robot_state_publisher` + `ros_gz_sim create` spawning `modular_arm` at `(-0.03, 0, 0)` from `robot_arm.urdf.xacro`
* `ros_gz_bridge` for `/clock`, `/cam_front/*`, `/wrist_camera/*`
* `joint_state_broadcaster` (after 3 s) + `arm_controller` (after 5 s) — both via `RegisterEventHandler(OnProcessExit(spawn_entity))`
* `move_to_node` after 6 s + `foxglove_bridge` after 8 s

Wait ~8 s for `move_to_node ready` in the log.

## Verify

In a **second terminal** (same sourced env — DDS discovery is terminal-specific):

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash

ros2 control list_controllers
# expect: joint_state_broadcaster [active] + arm_controller [active]

ros2 topic echo /joint_states --once
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"
# response: success=True, joint_angles=[...]
```

If `list_controllers` is empty → spawner raced the controller_manager — **relaunch** (see `04_troubleshooting_sim.md`).

## What to read next (in order)

1. [`01_sim_bringup.md`](01_sim_bringup.md) — RViz-only check, headless tuning, timing
2. [`02_move_to_api.md`](02_move_to_api.md) — more poses, pitch/elbow semantics
3. [`03_cameras_and_foxglove.md`](03_cameras_and_foxglove.md) — cameras empty or Foxglove setup
4. [`04_troubleshooting_sim.md`](04_troubleshooting_sim.md) — anything fails — kill sequence, SHM locks, DDS trap
5. [`05_teleop.md`](05_teleop.md) — leader-arm teleop with pots + button → sim arm (Arduino + `modular_arm_teleop`)

> **No hardware needed.** Everything after this is optional for sim-only replication.

## Credits

Sim meshes in `src/robot_arm_description/meshes/` derive from [Robotic Arm with Servo & Arduino](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927) by **Emre Kalem (@emrekalem)** on MakerWorld (Standard Digital File License).
