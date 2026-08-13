# AGENTS.md

ROS2 **Jazzy** + **Gazebo Harmonic** colcon workspace for a 4-DOF printed arm (custom CAD, STL meshes in `robot_arm_description`). Repo root IS the colcon workspace: `build/`, `install/`, `log/` live here and are gitignored. See `SETUP.md` for apt deps.

## Build & run
- Source first: `source /opt/ros/jazzy/setup.bash`
- Build from repo root: `colcon build --symlink-install && source install/setup.bash`
  - `--symlink-install` applies pure-Python edits without a rebuild; changing `MoveTo.srv` still requires a rebuild.
- Full sim: `ros2 launch modular_arm_bringup sim_bringup.launch.py`, then:
  `ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"`

## Packages (`src/`)
- `modular_arm_interfaces` — `MoveTo.srv`, the stable API boundary; must build before the rest.
- `modular_arm_kinematics` — `fk.py`/`ik.py` are **pure Python, zero ROS deps**; `move_to_node.py` is the thin ROS wrapper; `keyboard_teleop.py` drives via `move_to`.
- **`robot_arm_description`** — the REAL arm: `robot_arm.urdf` (source of truth) + `robot_arm.urdf.xacro` (Gazebo copy), meshes, worlds, controllers, launch. **This is the active description package.** `modular_arm_description` is the old/legacy OMX-pattern sim and should be ignored/removed.
- `modular_arm_bringup` — one-command sim bringup.
- `modular_arm_teleop` — Arduino leader-arm teleop; currently uncommitted.

## Critical sync rules (the arm only works if these match)
- **`robot_arm.urdf` is the source of truth.** The user edits it directly; `robot_arm.urdf.xacro` must be kept in sync (same links/joints/visuals) + it adds the wrist-camera `<gazebo>` block and the `robot_arm.gazebo.xacro` include. After editing the URDF, diff the two and mirror changes.
- Joint names: `joint1`(yaw) `joint2`(shoulder) `joint3`(elbow) `joint4`(wrist) `finger_left_joint` `finger_right_joint` `cap_joint`(fixed). Must match across: URDF/xacro, `config/ros2_controllers.yaml`, `move_to_node.py` `JOINT_NAMES`.
- Link lengths (L1=0.198, L2=0.141, L3=0.083) and joint limits live in `fk.py` + `ik.py` (`JOINT_LIMITS`). `ik.py` conventions must match `fk.py` exactly.
- FK/IK model the real URDF: segments are NOT collinear at zero pose; zero pose points **forward** (+X), pitch = `-(theta2+theta3+theta4)`. Only `elbow='down'` is reachable for forward targets (elbow-up raises `Unreachable`).
- Test without ROS, from the package dir:
  `cd src/modular_arm_kinematics && python3 -m pytest test/test_kinematics.py -v`

## Gripper control (empirically tuned — do not re-derive)
- `gz_ros2_control` moves position joints via a P-gain velocity controller: `target_vel = -gain * error * update_rate`. There is NO native position servo.
- `position_proportional_gain` is a **node param** set in `config/ros2_controllers.yaml` under the `gz_ros_control:` namespace (NOT per-joint URDF params — those are ignored).
- **Current gain = 1.3** (stable sweet spot on this machine). 1.0 = stable but too weak (fingers barely move); 5–10 = violent oscillation (whole robot vibrates).
- Finger URDF limits: `upper="0.015"` (travel), `velocity="1.0"`. `GRIPPER_MAX_TRAVEL = 0.015` in `move_to_node.py` must match.
- Finger collision boxes are at `y=±0.019` (the visual mesh inner face) so they actually contact the 25 mm blocks when closing. If fingers "cross over" (right becomes left): travel is too large for the mesh offset — reduce `upper` + `GRIPPER_MAX_TRAVEL` together.
- `move_to_node` uses a **SingleThreadedExecutor** (was MultiThreadedExecutor(4) which pegged a core at 85% CPU). `_send_trajectory` is fire-and-forget (no `threading.Event.wait` blocking). Do NOT reintroduce blocking inside the service callback.

## Killing the sim (IMPORTANT)
- **`killall gz` does NOT work** — `gz sim` is a Ruby script, so the process `comm` name is `ruby`, not `gz`. Use `pkill -9 -f "gz sim"` (matches full command line).
- To fully reset: `pkill -9 -f "gz sim"; pkill -9 -f parameter_bridge; pkill -9 -f robot_state_publisher; pkill -9 -f foxglove_bridge; pkill -9 -f move_to_node; pkill -9 -f controller_manager; pkill -9 -f spawner; pkill -9 -f "ros2 launch"`, then `ros2 daemon stop && ros2 daemon start`.
- Leftover sims cause `RTPS_TRANSPORT_SHM open_and_lock_file failed` + `Controller already loaded` + `Failed to configure controller` + dead foxglove + empty camera topics. If you see these, an orphaned sim is holding ports — kill everything above and relaunch. Stale SHM locks live in `/dev/shm/fastrtps_port*` (remove them if the error persists).
- After killing, verify clean: `ps aux | grep -iE 'gz sim|parameter_bridge|robot_state|foxglove|move_to|controller' | grep -v grep` should print nothing.

## Controller startup timing
- `sim_bringup` delays the move_to node 6 s; controllers spawn via `TimerAction` (broadcaster 3 s, arm controller 5 s after spawn). If `ros2 control list_controllers` shows nothing, the spawner lost the race — relaunch.

## Simulation performance (current tuned config)
- **Headless**: `gz_args: -r -s` (server-only; `-s` is enough, cameras render server-side. `--headless-rendering` only needed on machines with NO display).
- **Physics**: `real_time_update_rate: 250` in `worlds/workspace.sdf`. Lower = less CPU.
- **Controller**: `update_rate: 50` Hz in `ros2_controllers.yaml`.
- **Cameras**: **640×480 RGB8 @ 30 Hz** requested; actual rate is CPU-bound (~2–5 Hz at 640×480, ~13–15 Hz at 320×240). The bottleneck is rendering + CPU contention (opencode, Foxglove). Close those during recording.
- Recorder `--fps` must be ≤ measured camera rate (e.g. `--fps 3` at 640×480, `--fps 10` at 320×240) or frames duplicate.

## Simulation cameras & Foxglove
- Camera topics: `/cam_front/image_raw`, `/wrist_camera/image_raw`, plus `/cam_front/camera_info`, `/wrist_camera/camera_info` (all working, `sensor_msgs`). camera_info IS needed for Foxglove intrinsics; both publish continuously.
- **Front camera**: world model in `worlds/workspace.sdf`, always present → its bridges start immediately.
- **Wrist camera**: defined in `robot_arm.urdf.xacro` as `<gazebo reference="link4">` sensor (gripper merges into link4 via fixed joints). Bridge listens on `.../link/link4/sensor/wrist_camera/...`. If you move the camera, update the bridge path in `gazebo.launch.py`.
- **Wrist camera bridges MUST start after the robot spawns.** The wrist sensor only exists once `ros_gz_sim create` runs; the wrist bridges are wrapped in `RegisterEventHandler(OnProcessExit(spawn_entity, ...))` + 1 s `TimerAction`. If `/wrist_camera/image_raw` is empty, check this ordering first (front camera is a world model so it's immune).
- `GZ_SIM_RESOURCE_PATH` must point at the install `share/` dir or STL meshes won't render: set via `os.environ` in `gazebo.launch.py`. Mesh filenames with spaces need URL-encoded or renamed versions (e.g. `Parmak_2_X_2.stl`).
- `foxglove_bridge` requires `sudo apt install ros-jazzy-foxglove-bridge`. Foxglove may render the robot model oddly (can't resolve `package://`); RViz (`ros2 launch robot_arm_description display.launch.py`) is the reliable robot visualizer. Use Foxglove for cameras/topics.
- **DDS measurement trap:** `ros2 topic hz`/`topic list`/Python subscribers from a SEPARATE terminal may show "empty"/"unknown" due to cross-terminal DDS discovery — especially in this repo's dev environment. Verify camera/camera_info data via the same terminal that launched the sim, or via Foxglove.

## Teleop quirks (serial)
- Needs `pyserial`; Arduino sketch at 115200 baud, CSV `j1,j2,j3,j4,btn`. Default port `/dev/ttyACM0` (needs udev perms).
- `config/teleop_params.yaml` joint_mapping overrides the node's `declare_parameter` defaults when launched via `teleop.launch.py`.

## LeRobot data collection (in progress)
- Recorder script: `lerobot-ros2-recorder.py` at repo root (extracted from `lerobot-ros2-recorder.md`).
- **venv (with ROS visibility):** `~/lerobot_learning/.venv` (uv, `--system-site-packages`). Run recorder with `/home/shreeshinator/lerobot_learning/.venv/bin/python`. Contains lerobot 0.6.1 + datasets + h5py + **numpy pinned to 1.26.4** (must stay <2 — cv2 4.13.0 is NumPy 1.x ABI; NumPy 2.2.6 crashes the recorder).
- Our camera topics are `/wrist_camera/image_raw` + `/cam_front/image_raw` (guide assumes `/gripper_cam` + `/front_cam` — rename when invoking).
- `keyboard_teleop` (`ros2 run modular_arm_kinematics keyboard_teleop`) drives the arm via `/modular_arm/move_to` and publishes commanded joints on `/joint_commands` (the recorder's `action` source) + recorder commands on `/lerobot_recorder/command` (ENTER=start/save, t=discard, y=finish). START pose `(0.27, 0, 0.08, -1.57)` (grasp height).
- `move_to` actions are Cartesian (x,y,z,pitch,gripper); the recorder records joint-space `action` from `/joint_commands`.
- Do NOT `pip install lerobot` into user site (it bumped setuptools to 81 which breaks colcon builds; setuptools must stay <80).

## Repo hygiene
- Branch is `working` with uncommitted changes incl. untracked `modular_arm_teleop/` and `sketch/`.
- `.gitignore` covers `build/`, `install/`, `log/` at any depth but NOT `__pycache__/` or `.pytest_cache/` — avoid blind `git add .`.
- No CI, no pre-commit hooks.
