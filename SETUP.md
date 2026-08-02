# Modular_arm — 4-DOF ROS2 arm (Jazzy + Gazebo Harmonic)

## 1. Arm design

Kinematic layout copied from ROBOTIS **OpenMANIPULATOR-X** (for current simulation only) (the most common
open-source 4-DOF arm in the ROS ecosystem — real hardware exists if you ever
want to move off simulation): one yaw joint at the base, then three pitch
joints (shoulder, elbow, wrist) in the vertical plane that yaw selects.

```
joint1 (yaw, Z)  ->  joint2 (shoulder pitch)  ->  joint3 (elbow pitch)  ->  joint4 (wrist pitch)  ->  end_effector_link
```

This gives closed-form (non-iterative) IK: `theta1 = atan2(y, x) for the base yaw`, then a
standard 2-link planar solve for the shoulder/elbow, with the wrist absorbing
whatever pitch is left over. See `modular_arm_kinematics/ik.py` for the full
derivation in comments.

## 2. Package layout

```
src/
  modular_arm_interfaces/    # MoveTo.srv — the stable API boundary
  modular_arm_description/   # URDF/Xacro, RViz config, Gazebo + ros2_control launch
  modular_arm_kinematics/     # fk.py / ik.py (no ROS deps) + move_to_node.py (ROS wrapper)
  modular_arm_bringup/        # one-command launch files
```

Why split this way: `modular_arm_kinematics`'s `fk.py`/`ik.py` have **zero
ROS dependencies** — they're plain Python/math, unit-testable, and reusable
by anything (a future LLM planner, a notebook, a VLA policy's output
converter) without dragging in rclpy. The ROS-facing `move_to_node.py` is a
thin wrapper on top. When you add vision/voice/LLM/VLA later, they should
each be their own package that calls `/modular_arm/move_to` — they never
need to know about joint angles.

## 3. Build

```bash
# One-time: install deps (adjust if some are already present)
sudo apt update
sudo apt install -y ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 \
  ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge \
  ros-jazzy-gz-ros2-control ros-jazzy-controller-manager \
  ros-jazzy-joint-trajectory-controller ros-jazzy-joint-state-broadcaster

cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 4. Run — RViz only (sanity check the URDF first)

```bash
ros2 launch modular_arm_description display.launch.py
```
Move the sliders in the `joint_state_publisher_gui` window and confirm the
arm moves correctly in RViz (Fixed Frame is already set to `world`).

## 5. Run — Gazebo Harmonic simulation

```bash
ros2 launch modular_arm_description gazebo.launch.py
```
This starts Gazebo, spawns the arm, and loads `joint_state_broadcaster` +
`arm_controller` (a `joint_trajectory_controller`). Check it's alive:

```bash
ros2 control list_controllers
ros2 topic echo /joint_states
```

## 6. Run — full stack (Gazebo + move_to API) in one command

```bash
ros2 launch modular_arm_bringup sim_bringup.launch.py
```

## 7. Move the arm via the `move_to` API

```bash
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.15, y: 0.05, z: 0.10, pitch: -1.0, elbow: 'up', duration_sec: 2.0}"
```
- `pitch` is the end-effector angle in radians (0 = horizontal, -1.57 ≈ straight down).
- `elbow` is `'up'` or `'down'` — picks between the two valid solutions.
- Response includes `success`, a `message`, and the `joint_angles` actually
  commanded — useful for logging/debugging.

Watch it move in the Gazebo window, and confirm in RViz/`ros2 topic echo
/joint_states` that the joints reached the commanded angles.

## 8. Test the kinematics in isolation (no ROS, no Gazebo needed)

```bash
cd ~/ros2_ws/src/modular_arm_kinematics
python3 -m pytest test/test_kinematics.py -v
```
This round-trips IK → FK for several targets and checks an out-of-reach
target correctly raises `Unreachable`.

You can also call the IK solver directly from plain Python for quick checks:
```bash
python3 -c "from modular_arm_kinematics.ik import inverse_kinematics; print(inverse_kinematics(0.15, 0.05, 0.10, pitch=-1.0))"
```

## 9. What's deliberately NOT here yet

No vision, no speech, no LLM planner, no VLA integration. Those should each
land as their own package (e.g. `modular_arm_vision`, `modular_arm_voice`,
`modular_arm_planner`) that talks to `/modular_arm/move_to`

## 10. Known things to double check on your machine

- Gazebo Harmonic package names (`ros_gz_sim`, `ros_gz_bridge`,
  `gz_ros2_control`) assume a standard Jazzy + Harmonic apt install. If
  `gz_ros2_control` isn't in apt for your setup, you may need to build it
  from source (https://github.com/ros-controls/gz_ros2_control).
- If `ros2 control list_controllers` shows nothing, it usually means the
  controller spawners ran before the controller_manager was ready — rerun
  `ros2 launch modular_arm_description gazebo.launch.py` (the event-handler
  delays in the launch file should handle this, but Gazebo startup time
  varies by machine).
