# AGENTS.md — Verified 2026-08-22

ROS2 **Jazzy** + **Gazebo Harmonic** colcon workspace for a 4-DOF printed arm (CAD, STL meshes in `robot_arm_description` vendored as `100644` real files — `890645f`, not `120000` symlinks). Repo root IS the colcon workspace: `build/`, `install/`, `log/` live here and are gitignored. See `SETUP.md` for apt deps. **Uno Q bringup verified on QRB2210 4GB `aarch64` Debian 13, `shreeshinator/nexusarm:unoq 7.15GB` on `/home/arduino/docker` (17G), `lerobot 0.6.1 + av 14.2.0 + torch 2.7.0/torchvision 0.22.0 + OPENBLAS_CORETYPE=ARMV8`, `fps 15` — see `HARDWARE.md` FULL COMMAND LIST (Steps 0–6).**

## Build & run
- Source first: `source /opt/ros/jazzy/setup.bash`
- Build from repo root: `colcon build --symlink-install && source install/setup.bash`
  - `--symlink-install` applies pure-Python edits without a rebuild; changing `MoveTo.srv` still requires a rebuild.
- Full sim: `ros2 launch modular_arm_bringup sim_bringup.launch.py`, then:
  `ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 2.0}"`

## Packages (`src/`)
- `modular_arm_interfaces` — `MoveTo.srv`, the stable API boundary; must build before the rest.
- `modular_arm_kinematics` — `fk.py`/`ik.py` are **pure Python, zero ROS deps**; `move_to_node.py` is the thin ROS wrapper. The SIM keyboard teleop (`modular_arm_kinematics/keyboard_teleop.py`) drives the simulated arm via `move_to` and publishes the **commanded** joints on `/joint_commands` (plural, `JointState`) — note the sim teleop does **not** publish the recorder's `/joint_command` action source, so sim recordings need `--action-fallback state`. The real-arm Cartesian teleop lives in `robot_arm_hardware`.
- **`robot_arm_description`** — the REAL arm: `robot_arm.urdf` (source of truth) + `robot_arm.urdf.xacro` (Gazebo copy), meshes, worlds, controllers, launch. **This is the active description package** (legacy `modular_arm_description` has been removed).
- `modular_arm_bringup` — one-command sim bringup.
- `modular_arm_teleop` — Arduino leader-arm teleop; currently uncommitted.
- `robot_arm_hardware` — **REAL hardware**. `hw_interface.py` bridges `/joint_command` (Float64MultiArray, 5 values j1..j4+gripper) → Arduino Uno R3 over serial (CSV at 115200 baud, see `sketch/servo_bridge/`). `hw_move_to.py` is the Cartesian `MoveTo.srv` → joint trajectory server (same API as sim's `move_to_node.py`). `camera_bridge.py` pulls MJPEG (Motion JPEG — an endless HTTP stream of JPEG frames) from DroidCam/phone via `urllib.request` and republishes as `sensor_msgs/CompressedImage` on `/front_cam/image_raw/compressed` + `/gripper_cam/image_raw/compressed` (passthrough JPEG, no cv2 decode). `lerobot_infer.py` loads HF ACT policy `shreeshinator/arm-pick-blocks-act-first` and publishes `/joint_command` at `fps` (see LeRobot inference below). `keyboard_teleop.py` / `joint_keyboard_teleop.py` — Cartesian/joint teleops via MoveTo. Launch: `launch/real_arm.launch.py` (now declares `serial_port`/`baud_rate`), `launch/real_hw.launch.py`. Scripts `scripts/hw_interface`, `hw_move_to`, `camera_bridge`, `lerobot_infer` installed to `lib/robot_arm_hardware/` for `ros2 run`.

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
- Needs `pyserial` (pip name) → `python3-serial` (apt/rosdep key — see Package hygiene below); Arduino sketch at 115200 baud, CSV `j1,j2,j3,j4,btn`. Default port `/dev/ttyACM0` (needs udev perms).
- `config/teleop_params.yaml` joint_mapping overrides the node's `declare_parameter` defaults when launched via `teleop.launch.py`.

## Package & launch hygiene (common pitfalls)
- **ament_python deps MUST be `<exec_depend>` not `<depend>`:** `robot_arm_hardware` is pure Python (`<build_type>ament_python</build_type>` — no C++ to compile). `<depend>` means build+export+exec; `<exec_depend>` means runtime only. The official demo `demo_nodes_py` (`/opt/ros/jazzy/share/demo_nodes_py/package.xml`) uses only `<exec_depend>` for `rclpy`/`std_msgs` etc. REP-149 defines `depend = build + build_export + exec`. We fixed `src/robot_arm_hardware/package.xml:10-14` to `exec_depend` for `rclpy`, `std_msgs`, `sensor_msgs`, `modular_arm_interfaces`, `python3-serial`.
  - **rosdep key is `python3-serial`, not `pyserial`:** pip installs `pyserial` (`import serial`), but Ubuntu apt is `python3-serial` (`apt show python3-serial: Source: pyserial`). `rosdep/python.yaml` maps `python3-serial: {ubuntu: [python3-serial]}` — there is no `pyserial` key (`rosdep resolve pyserial` fails). Use `<exec_depend>python3-serial</exec_depend>`.
- **Every `LaunchConfiguration` needs `DeclareLaunchArgument`:** Without it, `ros2 launch pkg file.py foo:=bar` is silently ignored (“unknown argument”). `src/robot_arm_hardware/launch/real_arm.launch.py:10-48` now declares `serial_port` (`/dev/ttyACM0` — the USB serial device file) + `baud_rate` (`115200` — bits per second, must match `Serial.begin()` in the Arduino sketch). Verify with `ros2 launch --show-args robot_arm_hardware real_arm.launch.py`.

## LeRobot data collection
- Recorder script: `lerobot-ros2-recorder.py` at repo root (extracted from `lerobot-ros2-recorder.md`).
- **venv (with ROS visibility):** the repo-root `.venv` (uv, `include-system-site-packages=true`). Run recorder with `~/NexusArm/.venv/bin/python`. Contains `lerobot 0.6.1 + datasets + h5py` with **host `.venv` pins `numpy==1.26.4` (must stay <2 — cv2 4.13.0 headless is NumPy 1.x ABI; NumPy 2.2.6 crashes the recorder)** vs **Docker `/opt/venv` uses `numpy==2.1.x` (required by `lerobot 0.6.1` — `Dockerfile:32` lets lerobot pull `2.1`, do NOT pin `1.26.4` there, see `HARDWARE.md` FULL COMMAND LIST). Only `opencv-python-headless` is installed (duplicate `opencv-python` removed).
- Our camera topics are `/wrist_camera/image_raw` + `/cam_front/image_raw` (guide assumes `/gripper_cam` + `/front_cam` — rename when invoking).
- `keyboard_teleop` (`ros2 run robot_arm_hardware keyboard_teleop`) drives the arm via `/modular_arm/move_to`.  Controls in the SAME terminal:
    w/a/s/d   X/Y coarse    i/j/k/l  X/Y fine
    q/e      Z up/down     u/o      Z fine
    r/f      pitch ±0.1    [ / ]    wrist (joint4) ±0.05
    space    gripper toggle
    x        print target
    ENTER    recorder start/save   d  discard   q  finish
    Ctrl-C   quit
  - `[` / `]` tilt ONLY joint4 (the wrist) — the rest of the arm stays put; no IK redistribution.
  - `r` / `f` do Cartesian pitch: x,y,z held fixed, IK redistributes shoulder/elbow/wrist together.
  - All moves publish to `/joint_command`; the LeRobot recorder captures the joint-space `action` from this topic automatically.
  - The teleop remembers the last solved joint angles from the `move_to` service response; wrist moves build on that last solution.
START pose `(0.27, 0, 0.08, -1.57)` (grasp height).
- `move_to` actions are Cartesian (x,y,z,pitch,gripper); on the real arm the recorder records joint-space `action` from `/joint_command` (Float64MultiArray, 5 values: j1..j4 + gripper).
- Do NOT `pip install lerobot` into user site (it bumped setuptools to 81 which breaks colcon builds; setuptools must stay <80).

**Episode management** (while recording with the venv recorder):
- **Topic (recommended, works headless)**: `ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: start|save|discard|finish}"`. `start` begins an episode, `save` finalizes the current one, `discard` drops it without saving, `finish` finalizes the last episode, pushes to HF Hub if `--push` was set, and exits the recorder.
- **Keyboard** (only works in the same terminal as the recorder, with a TTY — stdin must not be closed):
    - **ENTER** = start a new episode (or save the current one if recording).
    - **d + ENTER** = discard the current episode without saving (clears the in-memory buffer).
    - **q + ENTER** = finish recording entirely.
- The recorder defaults to `--fps 10`; at 640×480 this matches ~2–5 Hz actual camera rate, so frames will duplicate if you go above ~3 fps unless you lower `--fps` or use 320×240.

## LeRobot inference (ACT on real arm)
- **Policy**: `shreeshinator/arm-pick-blocks-act-first` (ACT, chunk 100) trained on `shreeshinator/arm-picking-blocks-real` (front camera 480×640, 5 joints). **Task string must exactly match training**: `"place the block in the bowl"` (`lerobot_infer.py:101`).
- **Nodes**:
  - `camera_bridge.py` — MJPEG → `sensor_msgs/CompressedImage`. Params `front_url`/`gripper_url` (e.g. `http://phone:4747/video` for DroidCam, `http://esp32:81/stream`), `front_topic`/`gripper_topic`, `fps` (cap, default 15). Publishes **only new frames** (no duplicates) with `BEST_EFFORT depth=1 KEEP_LAST` — **publisher MUST be BEST_EFFORT or DDS RELIABLE↔BEST_EFFORT mismatch drops all images** (see `camera_bridge.py:58`).
  - `lerobot_infer.py` — subscribes `/front_cam/image_raw/compressed` (`BEST_EFFORT`) + `/joint_states`, runs `ACTPolicy.select_action`, publishes `/joint_command` at `fps`. Run via venv Python:
    `source /opt/ros/jazzy/setup.bash && .venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args -p enable_robot:=false` (dry-run, no motion) or `ros2 run robot_arm_hardware lerobot_infer --ros-args -p enable_robot:=true` (live). Installed as `lib/robot_arm_hardware/lerobot_infer` for `ros2 run` (see `setup.py:26`). **Inside Docker use `/opt/venv/bin/python` (not `.venv`) — `.venv/bin/python: No such file` inside `root@...:/workspace`**.
- **Normalization (critical, was a bug)**: policy trained with `MEAN_STD`. Inference MUST load stats from HF `policy_preprocessor_step_3_normalizer_processor.safetensors` — **Visual** mean `[0.485,0.456,0.406]` std `[0.229,0.224,0.225]` (ImageNet, shape `3×1×1`), **State/Action** mean/std from same file. Pipeline: image `uint8 → float32/255 → (x-mean)/std` per channel (`_preprocess_image`), state `(raw-mean)/std` before `select_action`, action `norm*std+mean` after. **Bypasses `PolicyProcessorPipeline.from_pretrained`** — it hard-codes `device: cuda` and crashes CPU-only (`policy_preprocessor.json: device=cuda`). Manual math mirrors `lerobot/_NormalizationMixin._apply_transform`.
- **QoS**: both sides `BEST_EFFORT depth=1 KEEP_LAST`. `camera_bridge` publishes compressed JPEG passthrough (no `cv2.imdecode` — saves CPU); `lerobot_infer` does `cv2.imdecode` + resize to 480×640 (`INTER_AREA`) if needed, validates `format=="jpeg"` and `msg.data`.
- **Safety**: actions clamped to `JOINT_LIMITS` (`joint1 ±3.14`, `joint2-4 ±1.57`) + `GRIPPER_LIMITS [0,1]` before publish; logs `dist`/`maxΔ` vs current state and warns if `dist>2.0`.
- **Auto-home**: `lerobot_infer` calls `/modular_arm/move_to` to `home_x/y/z/pitch/gripper` (`0.27,0,0.08,-1.57,0.0`) for `home_duration` (2s) + `home_delay` (0.5s settle) before policy loop. Disable with `-p auto_home:=false` or dry-run skips hardware (`enable_robot:=false` never calls the service).
- **Chunk horizon**: trained `chunk_size=100`/`n_action_steps=100` (6.6s at 15Hz — too stale). `lerobot_infer.py:116` defaults to `n_action_steps:=50` (3.33s, verified sweet spot; 10 was too reactive, 100 too blind).
- **Runtime commands**: `ros2 topic pub --once /lerobot_infer/command std_msgs/String "{data: enable|disable|reset|home}"` — enable/disable publishing, reset policy queue, re-home.
- **Uno Q 4GB A53 fixes (verified):** Docker image `shreeshinator/nexusarm:unoq 7.15GB` ships `torch 2.11` `aarch64` `dotprod` → `Illegal instruction` on `QRB2210` `Cortex-A53` (`armv8-a` no `SDOT`). **Live fix without rebuild (see `HARDWARE.md` FULL COMMAND LIST Steps 5–6):** `pip install --only-binary=av "av==14.2.0"` (not `18.1.0` `False`, `12.3.0/14.2.0` have `av.option`) and `pip install "torch==2.7.0" "torchvision==0.22.0" --index-url https://download.pytorch.org/whl/cpu` (matched pair, satisfies `lerobot 0.6.1 requires torch>=2.7,<2.12`; `2.4.0` breaks, `2.7.1+0.22.0` mismatched) + `export OPENBLAS_CORETYPE=ARMV8` (forces generic `ARMv8` no `SDOT`, fixes `Illegal instruction`). `HF_TOKEN` via `docker compose exec -e HF_TOKEN=... -e OPENBLAS_CORETYPE=ARMV8 arm bash` (`requires arm bash` after `-e`). Service call needs space `"{x: 0.27, y: 0.0, ...}"` not `"{x:0.27}"`.

## Uno Q port (verified 2026-08-22)
- **Docker on Uno Q + Uno R3 `servo_bridge.ino`** — verified bringup on QRB2210 4GB `aarch64` Debian 13. `shreeshinator/nexusarm:unoq 7.15GB` on `/home/arduino/docker` (17G) with `lerobot 0.6.1 + av 14.2.0 + torch 2.7.0/torchvision 0.22.0 + OPENBLAS_CORETYPE=ARMV8`. See `HARDWARE.md` FULL COMMAND LIST (Steps 0–6) for out-of-box `fps 15`.
- Deliverables: `Dockerfile` (`FROM ros:jazzy-ros-base` multi-arch slim, not full `ros:jazzy`, `venv /opt/venv --system-site-packages`, `lerobot==0.6.1` auto `numpy 2.1`, `setuptools<80`), `docker-compose.yml` (`/dev/ttyACM0` + `network_mode: host`, `sleep infinity`, `image: shreeshinator/nexusarm:unoq` — legacy `docker tag nexusarm-arm:latest` only if compose still expects old name, now `up -d --no-build` uses `image:`), `src/robot_arm_hardware/launch/real_bringup.launch.py` (one-command `hw_interface`+`hw_move_to`+`camera_bridge`), `HARDWARE.md` (wiring, calibration, flash, FULL COMMAND LIST), `sketch/servo_bridge/README.md`.
- **Critical fixes for 10GB root (9.8G 98%):** `daemon.json` `data-root` must be `/home/arduino/docker` (17G), not `/home/docker` (239M) — `df -h` shows `/home/arduino` is separate mount; wrong path still `no space`. `src/robot_arm_description/meshes` vendored as `100644` real STLs `890645f` (was `120000` dangling symlinks to outside `Robotic+Arm...` causing `Failed <<< robot_arm_description` at `Alt_Govde.stl`). See `HARDWARE.md` Troubleshooting.
- Firmware trap: `servo_bridge.ino` (Uno, `yaw +318`, `wrist 477`, `PULSE_MIN 700`) vs `sketch/servo_bridge_esp32.ino` (dev ESP32, `yaw -318`, `wrist 318`, `PULSE_MIN 800`) — must standardize on one table before port.

## Repo hygiene
- Branch is `working` pushed to `NexusArm/main` `794c38f` verified (meshes `890645f`, docs `1e88560`).
- `.gitignore` covers `build/`, `install/`, `log/` at any depth **and** `__pycache__/`, `*.pyc`, `.pytest_cache/` (fixed — was “NOT `__pycache__/`”); still avoid blind `git add .` (see `.gitignore:1-16`).
- No CI, no pre-commit hooks.
