# AGENTS.md

ROS2 **Jazzy** + **Gazebo Harmonic** colcon workspace for a 4-DOF arm (OpenMANIPULATOR-X pattern). Repo root IS the colcon workspace: `build/`, `install/`, `log/` live here and are gitignored. See `SETUP.md` for apt deps and `README.md` for the roadmap.

## Build & run
- Source first: `source /opt/ros/jazzy/setup.bash`
- Build from repo root: `colcon build --symlink-install && source install/setup.bash`
  - `--symlink-install` applies pure-Python edits without a rebuild; changing `MoveTo.srv` still requires a rebuild.
- Full sim: `ros2 launch modular_arm_bringup sim_bringup.launch.py`, then:
  `ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x: 0.10, y: 0.05, z: 0.10, pitch: -0.3, elbow: '', duration_sec: 2.0}"`
- RViz-only URDF sanity check: `ros2 launch modular_arm_description display.launch.py` (use_sim_time=false). Sim nodes use `use_sim_time: True`.

## Packages (`src/`)
- `modular_arm_interfaces` — `MoveTo.srv`, the stable API boundary; must build before the rest.
- `modular_arm_kinematics` — `fk.py`/`ik.py` are **pure Python, zero ROS deps**; `move_to_node.py` is the thin ROS wrapper.
- `modular_arm_description` — URDF/xacro, RViz config, Gazebo + ros2_control launch.
- `modular_arm_bringup` — one-command sim bringup.
- `modular_arm_teleop` — Arduino leader-arm teleop; currently uncommitted.

## Extension seam
Future AI packages (NLP, VLA, vision) must call `/modular_arm/move_to`; they should never touch joint angles or IK. That is the whole point of the split.

## Kinematics gotchas
- Link lengths `L0–L3` and joint limits are duplicated in **three files that must stay in sync**: `fk.py`, `ik.py` (`JOINT_LIMITS`), and `urdf/modular_arm.urdf.xacro`. `ik.py` angle conventions must match `fk.py` exactly.
- Zero pose (all thetas = 0) points the arm **backward** (−X). IK is closed-form: `theta1 = atan2(y, x)`, then a 2-link planar solve; `elbow: 'up'|'down'` (or `''`/None = auto) picks between the two solutions; unreachable targets raise `Unreachable`.
- Test without ROS, from the package dir:
  `cd src/modular_arm_kinematics && python3 -m pytest test/test_kinematics.py -v`
- `move_to_node` waits for the action goal via `threading.Event` + `ReentrantCallbackGroup`. Do NOT switch to `rclpy.spin_until_future_complete` inside the service callback — it re-enters the executor and wedges the node.

## Controller startup timing
- `sim_bringup` and `teleop` launches delay their node 6 s (`TimerAction`) so controllers finish loading. If `ros2 control list_controllers` shows nothing, the spawner lost the race — just relaunch the sim.

## Simulation cameras & Foxglove
- `gazebo.launch.py` loads `worlds/workspace.sdf` (table + 3 coloured blocks + front camera) and bridges camera images to ROS topics `/cam_front/image_raw` and `/wrist_camera/image_raw`.
- Static front camera: 640×480 RGB8 @ 30 Hz, angled view of the workspace.
- Wrist camera: 640×480 RGB8 @ 30 Hz, 60° HFOV, mounted on `gripper_base`, looks forward into the grasp zone. Near clip at 5 mm for extreme close-ups. Critical for LeRobot policy training (egocentric gripper view).
- A `foxglove_bridge` node is launched for Foxglove visualisation. Requires: `sudo apt install ros-jazzy-foxglove-bridge`. If missing, the node fails but the rest of the sim still works.
- Camera topics are standard `sensor_msgs/Image` — visible in Foxglove, RViz, or any ROS subscriber.

## Teleop quirks (serial)
- Needs `pyserial` (`exec_depend python3-serial`); node logs an install hint if missing.
- Arduino side: `sketch/sketch.ino`, 115200 baud, CSV `j1,j2,j3,j4,btn` (btn=0 closes gripper). Default port `/dev/ttyACM0` (needs udev perms).
- `teleop_node` commands **6 joints** (4 arm + 2 gripper fingers); `arm_controller` requires `allow_partial_joints_goal: true` (already set in `config/ros2_controllers.yaml`).
- `config/teleop_params.yaml` joint_mapping overrides the node's `declare_parameter` defaults — when launched via `teleop.launch.py`, the YAML wins.
- `move_to_node.py` `GRIPPER_MAX_TRAVEL` must equal `(gripper_spread - finger_width) / 2` from the URDF; if you change finger size or spread, update both.

## Repo hygiene
- Branch is `working` with uncommitted changes incl. untracked `modular_arm_teleop/` and `sketch/`.
- `.gitignore` covers `build/`, `install/`, `log/` at any depth but NOT `__pycache__/` or `.pytest_cache/` (several already exist untracked) — avoid blind `git add .`.
- No CI, no pre-commit hooks; `ament_flake8`/`ament_pep257` are declared as test deps but unused.
