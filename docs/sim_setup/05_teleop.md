# Leader-Arm Teleop in Simulation — Pots on Arduino → Sim Arm

> Want to *feel* the arm? Build a tiny leader with 4 pots + a button, and the sim follower mirrors you in real time. It's friendly, cheap, and great for demos or collecting intuition before you train.

This works **only in simulation** — it drives the `arm_controller` (`FollowJointTrajectory`) directly. For the real arm, servos are driven by `hw_interface.py` via the Uno R3's `servo_bridge.ino` (pins 3/5/6/9/10/11) — that's a different path.

---

## 1. What you'll build

* **Leader arm:** 4× 10k pots (one per joint) + 1× pushbutton to GND
* **Arduino:** Uno/Nano/Mega — any board with 4 analog inputs + 1 digital input
* **Follower:** the simulated arm in Gazebo (`joint1, joint2, joint3, joint4, finger_left/right_joint`)

```
Pots (A0..A3) + Button (D2 to GND)
        │
        │ Serial CSV @115200: "j1,j2,j3,j4,btn\n"  (0-1023, 0=pressed)
        ▼
src/modular_arm_teleop/teleop_node.py  →  /arm_controller/follow_joint_trajectory
        │
        ▼
Gazebo sim arm (same URDF you see in RViz)
```

---

## 2. Wire the leader

From `sketch/teleop_sketch.ino:11-17`:

| Arduino | Pot / Button | Note |
|---------|--------------|------|
| A0 | Joint1 (base yaw) | middle wiper → A0, ends → 5V/GND |
| A1 | Joint2 (shoulder) |  |
| A2 | Joint3 (elbow) |  |
| A3 | Joint4 (wrist) |  |
| D2 | Gripper button | button → GND, use `INPUT_PULLUP` internally |
| 5V/GND | Pots power | share ground with Arduino |

* Pots: **270°** rotation, mechanically used in the **middle ~180°** (so raw ADC lives around 170–853). Any 10k linear pot works.
* Button: normally `1` (released → open), `0` when pressed → close. Debounced 50 ms in sketch.

---

## 3. Flash the sketch

```bash
# Arduino IDE: open sketch/teleop_sketch.ino → Board: Uno → Port: /dev/ttyACM0 → Upload
# or cli:
arduino-cli compile --fqbn arduino:avr:uno sketch/teleop_sketch.ino
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/teleop_sketch.ino

# sanity check — you should see CSV at 50 Hz
picocom /dev/ttyACM0 -b 115200   # or: screen /dev/ttyACM0 115200
# e.g. 512,400,612,510,1
```

Settings in sketch (`teleop_sketch.ino:33-36`): `NUM_SAMPLES=4` averaged, `SEND_INTERVAL_US=20000` (50 Hz), `DEBOUNCE_MS=50`, baud `115200`.

---

## 4. How the mapping works (friendly math)

In `src/modular_arm_teleop/config/teleop_params.yaml:16,23`:

```yaml
pot_min: 170          # ADC at ~45° physical
pot_max: 853          # ADC at ~225° physical
# centre = 512 (~135°)
# unit = (raw - 170)/(853-170) clamped 0…1
# follower_angle = scale * unit + offset   per joint
joint_mapping:
  joint1: {scale: 3.14159, offset: -1.5708} # 512 = forward, ±90°
  joint2: {scale: 3.0,    offset: 0.5}
  joint3: {scale: 2.0,    offset: -2.5}    # 512 = straight down
  joint4: {scale: 2.0,    offset: -1.5}    # 512 = centre
```

Follower rest pose is `j1=0, j2=2.0, j3=-1.5, j4=-0.5`. Gripper (`teleop_params.yaml:64-65`) is `0.0` open → `0.0075` closed — both prismatic fingers get the same value. Edit this YAML to tune feel; no code change needed.

Other tunables (`teleop_node.py:39-43`):

* `publish_rate: 25.0` Hz, `deadband: 3` LSBs (skip micro-jitter), `trajectory_duration_ms: 100` (how fast the follower chases)

Limits are clamped per `joint_limits` in the same YAML — safety even if a pot spikes.

---

## 5. Launch it — three friendly ways

### A. One command (Gazebo + teleop together)

```bash
colcon build --symlink-install && source install/setup.bash
ros2 launch modular_arm_teleop teleop.launch.py
# Gazebo launches, then 6 s later teleop_node starts with teleop_params.yaml + use_sim_time
```

`teleop.launch.py` internally does: `gazebo.launch.py` → `TimerAction(6.0, teleop_node)`. Move the leader — the sim follows.

### B. Sim already running, add teleop

```bash
# terminal 1 — sim without move_to (teleop drives directly)
ros2 launch robot_arm_description gazebo.launch.py
# terminal 2 — teleop alone, with sim time
ros2 run modular_arm_teleop teleop_node --ros-args \
  -p serial_port:=/dev/ttyACM0 -p baud_rate:=115200 -p use_sim_time:=true \
  --params-file src/modular_arm_teleop/config/teleop_params.yaml
```

> **Note:** `teleop_node` talks to `arm_controller` directly, so `move_to_node` isn't needed — don't launch `sim_bringup` at the same time or two drivers fight.

### C. Quick test without hardware (fake serial)

Not possible — this node needs real serial. For headless checks, just echo a fake CSV via `socat` or test the sim with `ros2 service call /modular_arm/move_to` from `02_move_to_api.md` instead.

---

## 6. Calibrate quickly (if it feels off)

```bash
# watch raw ADC
ros2 run modular_arm_teleop teleop_node --ros-args -p serial_port:=/dev/ttyACM0
# wiggle each pot end-to-end, note min/max, then edit pot_min/pot_max in teleop_params.yaml

# tune a single joint feel — e.g. make base yaw less twitchy
# in teleop_params.yaml: joint_mapping.joint1.scale 3.14 → 2.5

# tighter grip
# gripper_close_pos: 0.0075 → 0.010 (but keep ≤0.015 to avoid crossing fingers)

# more/less filtering
# deadband: 3 → 6, publish_rate: 25 → 15, trajectory_duration_ms: 100 → 200
```

After editing `teleop_params.yaml`, just rerun `ros2 launch` — the launch loads the YAML fresh.

---

## 7. Troubleshooting — quick fixes

| What you see | Why | Fix |
|---|---|---|
| `Cannot open /dev/ttyACM0` | dialout perms or wrong port | `ls /dev/ttyACM*`, `sudo usermod -aG dialout $USER` (re-login), or `serial_port:=/dev/ttyUSB0` |
| `Action server not available after 10s` | Gazebo controllers not ready | Launch `gazebo.launch.py` first, then teleop 6 s later (as `teleop.launch.py` does), or check `ros2 control list_controllers` |
| Leader moves, follower jitters | pot noise | raise `deadband` 3→6, lower `publish_rate` 25→15, or increase `trajectory_duration_ms` 100→150 |
| Button inverted | wiring vs code | button is active-low (to GND) — `0`=pressed→close, `1`=open. Swap logic or flip `gripper_open_pos`/`close_pos` |
| Range off (can't reach) | pot_min/max wrong | measure raw at both ends, set `pot_min`/`pot_max` to those values |
| Teleop + MoveTo fighting | two drivers | use one: either `teleop.launch.py` *or* `sim_bringup.launch.py` with `move_to`, not both |

Still stuck? Copy your `teleop_params.yaml` + a `screen /dev/ttyACM0 115200` log and we're happy to tune it together.

## Credits

Leader sketch + ROS node are project additions — the sim arm itself still uses the adapted MakerWorld mesh from Emre Kalem.
