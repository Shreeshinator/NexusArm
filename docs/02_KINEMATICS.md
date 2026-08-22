# Kinematics — How the Arm Knows Where to Go

> Good news: you don't need to understand the math to use the arm — just `ros2 service call /modular_arm/move_to`. This page is for when you want to check, tweak, or trust the geometry. It's friendly, and it links straight to the code.

## What this is

The arm lives in a **vertical plane that yaw picks**. Two pure-Python modules do the thinking — no ROS needed:

* `src/modular_arm_kinematics/modular_arm_kinematics/fk.py` — forward: angles → pose
* `src/modular_arm_kinematics/modular_arm_kinematics/ik.py` — inverse: pose → angles

They're unit-tested and reusable from notebooks, planners, or anything that wants to go from `x,y,z,pitch` to joints.

## Geometry (from your URDF — keep it in sync)

From `fk.py:27-31` — these match `robot_arm.urdf` exactly:

```python
BASE_H = 0.07                # ground → joint1
SHOULDER = (-0.02, 0.11)     # joint2 in (h,z)
SEG1 = (0.047, 0.1925)       # joint2 → joint3
SEG2 = (0.141, -0.001)       # joint3 → joint4
SEG3 = (0.052, -0.008)       # joint4 → gripper
L1, L2, L3 = hypot(SEG1), hypot(SEG2), hypot(SEG3)
A1, A2 = atan2(SEG1), atan2(SEG2)
DELTA = A2 - A1
```

* Segments are **not collinear at zero** — each carries a fixed offset. Zero pose points **forward (+X)**, not up.
* Pitch convention: `pitch = -(theta2 + theta3 + theta4)` → `0` = horizontal, `-1.57` = straight down. See `fk.py:57-71`.

**Limits** (`ik.py:24-29` and `fk.py` header, must match `robot_arm.urdf`):

```
joint1 -3.14 … 3.14
joint2 -1.57 … 1.57
joint3 -1.57 … 1.57
joint4 -1.57 … 1.57
```

## How IK works (just the idea)

1. **Yaw:** `theta1 = atan2(y, x)` — pick the plane.
2. **Wrist centre:** subtract the fixed `SEG3` (rotated by your pitch) from your target — what's left is a 2-link shoulder/elbow problem.
3. **Shoulder/elbow:** classic 2-link solve in `(h,z)` using `L1,L2,A1,A2,DELTA`. Try `elbow=up` and `down` — forward targets only have `down` valid, so just leave `elbow=""` and it picks correctly. Raises `Unreachable` if out of reach.

See full derivation in `ik.py:1-15`.

## Keep these in sync or the arm will lie to you

* **URDF is the truth:** `src/robot_arm_description/urdf/robot_arm.urdf` → after any edit, diff and mirror into `robot_arm.urdf.xacro` (which adds the wrist-camera `<gazebo>` + `robot_arm.gazebo.xacro` include).
* **Joint names everywhere:** `joint1` (yaw), `joint2` (shoulder), `joint3` (elbow), `joint4` (wrist), `finger_left_joint`/`finger_right_joint`, fixed `cap_joint` — must match `config/ros2_controllers.yaml`, `move_to_node.py:JOINT_NAMES`, and your `hw_interface` order.
* **Lengths & limits:** `L1/L2/L3` and `JOINT_LIMITS` live in `fk.py`+`ik.py`. If you re-measure the CAD, update both.

## Try it without ROS (30 seconds)

```bash
cd src/modular_arm_kinematics
python3 -m pytest test/test_kinematics.py -v

# quick check in plain Python
python3 -c "from modular_arm_kinematics.ik import inverse_kinematics; print(inverse_kinematics(0.27, 0.0, 0.08, pitch=-1.57))"
python3 -c "from modular_arm_kinematics.fk import forward_kinematics; print(forward_kinematics(0,0,0,0))"
```

Expected zero pose from `fk.py:74`: `x≈0.22 z≈0.293 pitch=0`.

## Using it from ROS

You never need joint angles — just:

```bash
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 1.5}"
```

If you get `success: false` with `Unreachable`:
* Try `elbow=""` (auto) or `"down"` — forward picks are only `down`.
* Check `pitch` is `-1.57` for top-down picks; `0` points forward and needs more reach.
* Verify your target is inside `d` in `[|L1-L2|, L1+L2]` — the error message tells you the wrist distance.

## Credits

Geometry derived from the adapted MakerWorld mesh — the numbers above are what make the real URDF and the Python agree.
