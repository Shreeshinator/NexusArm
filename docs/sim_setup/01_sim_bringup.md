# Sim Bringup — Detailed

> Friendly tip: start with option 1 — it's the easiest way to see the arm move. The other two are there when you want to dig deeper.

## Launch options

### 1. Full stack (recommended)

```bash
ros2 launch modular_arm_bringup sim_bringup.launch.py
```

*Sources: [`sim_bringup.launch.py`](../../src/modular_arm_bringup/launch/sim_bringup.launch.py) includes [`gazebo.launch.py`](../../src/robot_arm_description/launch/gazebo.launch.py).*

### 2. Gazebo + controllers only (no move_to, no Foxglove)

```bash
ros2 launch robot_arm_description gazebo.launch.py
```
Then manually:
```bash
ros2 run modular_arm_kinematics move_to_node --ros-args -p use_sim_time:=true
```

### 3. RViz only (no physics)

```bash
ros2 launch robot_arm_description display.launch.py
```
Move sliders in `joint_state_publisher_gui`. Fixed frame `world`. Useful to sanity-check URDF before spawning Gazebo.

## Timing & why it matters

`gazebo.launch.py` uses `RegisterEventHandler(OnProcessExit(spawn_entity))`:

* `+3.0 s` → `joint_state_broadcaster` spawner
* `+5.0 s` → `arm_controller` spawner (`joint_trajectory_controller`, update_rate 50 Hz)
* `sim_bringup.launch.py` adds:
  * `+6.0 s` → `move_to_node` (`SingleThreadedExecutor`, fire-and-forget `_send_trajectory`)
  * `+8.0 s` → `foxglove_bridge` (`use_sim_time:=true`)

If you see `Controller already loaded` or `Failed to configure controller`, an orphaned sim is holding ports — kill per `04_troubleshooting_sim.md`.

> **Teleop variant:** `modular_arm_teleop/teleop.launch.py` also waits `6 s` then starts `teleop_node` (instead of `move_to_node`). Don't run both at once or two drivers fight — see `05_teleop.md`.

## Tuning for your machine

| Knob | File | Current | Effect |
|---|---|---|---|
| Physics rate | `src/robot_arm_description/worlds/workspace.sdf` `real_time_update_rate` | `250` | Lower → less CPU, slower sim |
| Controller rate | `src/robot_arm_description/config/ros2_controllers.yaml` `controller_manager.update_rate` | `50 Hz` | Lower → less CPU, coarser control |
| Gazebo headless | `gazebo.launch.py` `gz_args` | `-r -s` | Server-only; cameras still render server-side. Add `--headless-rendering` only on machines with no display |
| Camera resolution | `workspace.sdf` + xacro sensor blocks | `640×480 RGB8 @30Hz` requested | Actual ~2-5 Hz at 640×480, ~13-15 Hz at 320×240 due to CPU rendering. Close Foxglove/opencode during recording |

Recorder `--fps` must be **≤ measured camera rate** or frames duplicate.

## Environment note

`gazebo.launch.py` sets `GZ_SIM_RESOURCE_PATH` to include the install `share/` dir so `model://robot_arm_description/meshes/*.stl` resolves. Mesh files with spaces (e.g. `Parmak_2_X_2.stl`) need URL-encoded or renamed variants.
