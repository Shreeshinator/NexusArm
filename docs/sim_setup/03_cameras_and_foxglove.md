# Cameras & Foxglove — Sim

## Topics (all `sensor_msgs`)

| Topic | Source | Notes |
|---|---|---|
| `/cam_front/image_raw` + `/cam_front/camera_info` | World model in `worlds/workspace.sdf` | Always present; bridges start immediately |
| `/wrist_camera/image_raw` + `/wrist_camera/camera_info` | `robot_arm.urdf.xacro` `<gazebo reference="link4">` sensor | Only exists after `ros_gz_sim create`; bridges **delayed** by `RegisterEventHandler(OnProcessExit(spawn_entity)) + TimerAction(1.0s)` |
| `/joint_states` | `joint_state_broadcaster` | |
| `/clock` | `ros_gz_bridge` clock bridge | `use_sim_time:=true` for all nodes |

*If you move the wrist camera in xacro, update the bridge prefix in `gazebo.launch.py`: `/world/workspace/model/modular_arm/link/link4/sensor/wrist_camera/...`.*

## Bridging

* `ros_gz_bridge` `parameter_bridge` per camera: `image` + `camera_info` (both types `sensor_msgs/Image` / `CameraInfo` ↔ `gz.msgs.Image/CameraInfo`).
* `camera_info` IS needed for Foxglove intrinsics; both publish continuously.
* Gripper merges into `link4` via fixed joints — camera is on `link4`, not a separate link.

## Foxglove

```bash
# auto-started by sim_bringup.launch.py after 8 s
# manual:
ros2 run foxglove_bridge foxglove_bridge --ros-args -p use_sim_time:=true
```

Requires `sudo apt install ros-jazzy-foxglove-bridge`. Connect Foxglove Studio to `ws://localhost:8765`. Use Foxglove for cameras/topics; **RViz is the reliable robot visualizer** (`ros2 launch robot_arm_description display.launch.py`) — Foxglove may mis-resolve `package://` meshes.

## Gazebo resources

`gazebo.launch.py` sets `GZ_SIM_RESOURCE_PATH` to `install/share/..` so `model://robot_arm_description/meshes/*.stl` resolves. Ensure STL names with spaces have renamed or URL-encoded copies (e.g. `Parmak_2_X_2.stl`).

## Resolution vs actual framerate

* Requested: `640×480 RGB8 @30 Hz`
* Measured on dev machine: **2–5 Hz at 640×480**, **13–15 Hz at 320×240** — CPU-bound (rendering + opencode/Foxglove contention).
* Recorder must sample **≤ measured rate** or frames duplicate. Close heavy clients during recording.

## DDS measurement trap

`ros2 topic hz /cam_front/image_raw` or a Python subscriber in a **separate terminal** may show "empty/unknown" due to cross-terminal DDS discovery. Verify from the **same terminal** that launched the sim, or via Foxglove.
