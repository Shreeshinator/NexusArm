> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](../README.md) — it gives the exact reading order for your goal.

# Troubleshooting — Sim

## Reset — kill everything (IMPORTANT)

`killall gz` does **NOT** work — `gz sim` is a Ruby script (comm=`ruby`), not `gz`.

```bash
pkill -9 -f "gz sim"; pkill -9 -f parameter_bridge; pkill -9 -f robot_state_publisher
pkill -9 -f foxglove_bridge; pkill -9 -f move_to_node; pkill -9 -f controller_manager
pkill -9 -f spawner; pkill -9 -f "ros2 launch"
ros2 daemon stop; ros2 daemon start
```

Stale SHM locks: `rm -f /dev/shm/fastrtps_port*` if you see `RTPS_TRANSPORT_SHM open_and_lock_file failed`.

Verify clean:

```bash
ps aux | grep -iE 'gz sim|parameter_bridge|robot_state|foxglove|move_to|controller' | grep -v grep
# should print nothing
```

## Symptoms → fixes

| Symptom | Cause | Fix |
|---|---|---|
| `RTPS_TRANSPORT_SHM open_and_lock_file failed` / `Controller already loaded` / `Failed to configure controller` / empty `/cam_front/image_raw` | Orphaned sim holding ports | Full kill above + relaunch |
| `ros2 control list_controllers` empty | Spawner raced `controller_manager` | Relaunch `sim_bringup.launch.py` (delays 3 s/5 s in `gazebo.launch.py` handle normal case but vary by machine) |
| `/wrist_camera/image_raw` empty while `/cam_front/image_raw` works | Wrist bridge started before spawn | Check ordering in `gazebo.launch.py` — wrist bridges are `RegisterEventHandler(OnProcessExit(spawn_entity), TimerAction(1.0s))`. Front cam is world model, immune. |
| `ros2 topic hz` shows 0 while Foxglove shows video | Cross-terminal DDS discovery | Check from **same terminal** that launched sim, or via Foxglove — not a second shell |
| Foxglove robot model weird / missing meshes | `package://` not resolved in Foxglove | Use RViz (`display.launch.py`) for robot viz; Foxglove for cameras |
| Robot vibrates / fingers oscillate | `position_proportional_gain` too high | Set `1.3` in `ros2_controllers.yaml` under `gz_ros_control:` namespace (per-joint URDF gains ignored) |
| Fingers barely move | Gain too low | Raise toward 1.3 |
| Fingers cross over (left becomes right) | Travel too large for mesh offset | Reduce `upper="0.015"` in URDF + `GRIPPER_MAX_TRAVEL=0.015` in `move_to_node.py` together; collision boxes at `y=±0.019` |
| `move_to` returns `Unreachable` | Elbow up for forward target | Use `elbow='down'` or `''` (auto) |
| Gazebo shows grey / meshes missing | `GZ_SIM_RESOURCE_PATH` unset or STL names with spaces | Check `gazebo.launch.py` env setup; rename `Parmak_2_X_2.stl` variants |
| High CPU (80%+ on idle) | `MultiThreadedExecutor` in `move_to_node` | Already fixed to `SingleThreadedExecutor` + fire-and-forget; don't re-add blocking |

## Controller startup timing

`sim_bringup` delays `move_to_node` 6 s; controllers via `TimerAction` (broadcaster 3 s, arm 5 s after spawn). If `list_controllers` shows nothing on first try, **just relaunch** — Gazebo startup varies.

## Recording-specific

* `fps` 30 at 640×480 → every frame duplicated (actual ~2-5 Hz). Use `--fps 3` at 640×480 or `--fps 10` at 320×240. See `docs/05_DATA_COLLECTION.md`.
* Sim teleop `modular_arm_kinematics/keyboard_teleop.py` publishes **commanded** joints on `/joint_commands` (plural, `JointState`) — recorder's default `--joint-commands-topic /joint_commands` works, but real-arm recorder uses `/joint_command` (singular Float64MultiArray) — need `--action-fallback state` for sim if not remapped.
