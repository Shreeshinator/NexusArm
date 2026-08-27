> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](../README.md) — it gives the exact reading order for your goal.

# MoveTo API — `/modular_arm/move_to`

Service: `modular_arm_interfaces/srv/MoveTo` ([source](../../src/modular_arm_interfaces/srv/MoveTo.srv))

```
# Request
float64 x          # target X (m) in base frame
float64 y          # target Y (m)
float64 z          # target Z (m)
float64 pitch      # end-effector pitch rad: 0=horizontal, -1.57=straight down
string  elbow      # "up" | "down" | "" (auto) — forward targets only support "down"
float64 gripper    # 0.0 open → 1.0 closed (maps to 0.015 m finger travel)
float64 duration_sec  # trajectory time, e.g. 2.0

---
bool success
string message
float64[] joint_angles  # [j1,j2,j3,j4, finger_left, finger_right] commanded
```

`JOINT_NAMES` must match URDF + `ros2_controllers.yaml`: `["joint1","joint2","joint3","joint4","finger_left_joint","finger_right_joint"]` ([`move_to_node.py:33`](../../src/modular_arm_kinematics/modular_arm_kinematics/move_to_node.py)).

## Canned calls

```bash
# START / home pose — grasp height, used by teleop + lerobot_infer auto-home
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"

# Offset grasp (from README)
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"

# Horizontal reach
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.15, y: 0.05, z: 0.10, pitch: -0.3, elbow: 'down', duration_sec: 2.0}"

# Close gripper in place (keep x,y,z,pitch, just set gripper)
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 1.0, duration_sec: 1.0}"
```

## Pitch & elbow semantics

* **Link geometry:** segments NOT collinear at zero; L1=0.198, L2=0.141, L3=0.083. Zero pose points forward (+X).
* **Pitch:** `pitch = -(theta2+theta3+theta4)`. `-1.57` = vertical down; `0` = forward.
* **Elbow:** only `down` is reachable for forward targets; `up` raises `Unreachable` (see `ik.py`).
* **Gripper:** `gripper * 0.015` = prismatic travel per finger; matches URDF `upper="0.015"` and `GRIPPER_MAX_TRAVEL` in `move_to_node.py`.

## Kinematics without ROS

```bash
cd src/modular_arm_kinematics
python3 -m pytest test/test_kinematics.py -v

python3 -c "from modular_arm_kinematics.ik import inverse_kinematics; print(inverse_kinematics(0.27, 0.06, 0.06, pitch=-1.57))"
```

## Implementation note

`move_to_node` is fire-and-forget (`send_goal_async` + `SingleThreadedExecutor`). Do not block inside the service callback — it pegs CPU. Response `success` means goal *sent*, not *finished*.
