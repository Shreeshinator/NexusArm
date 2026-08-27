> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](README.md) — it gives the exact reading order for your goal.

# Hardware — Flash & Bringup

> You built it — now let's wake it up! This one's short and friendly: flash the Arduino, launch the ROS bridge, and move the real arm with the same `MoveTo` API you used in sim.

This follows [`03_HARDWARE.md`](03_HARDWARE.md) (assembly + rough circuit). If you skipped that, just know: the **top perfboard has 5 servos** (2× shoulder opposite + elbow + SG90 wrist + SG90 gripper), the **MG946R base yaw** is separate inside the base, and the **ZK-4XX** with its display sits between your LiPo and the power rails.

---

## 1. What the firmware does (30-second version)

`sketch/servo_bridge/servo_bridge.ino` lives on the **Arduino Uno R3 inside the base**. It's the *only* place that does the **5 → 6 logical → physical expansion**:

* ROS sends **5 logical values** over serial at **115200 baud**: `joint1,joint2,joint3,joint4,gripper` (radians, gripper 0→1) as a CSV line ending in `\n`
* The sketch expands `joint2` to **two physical shoulder servos** that move **opposite** — that sign flip lives only here

```
ROS /joint_command (5) --115200 CSV--> Uno R3 servo_bridge --6 PWM--> servos
```

No ROS code knows about the doubled shoulder — that's intentional.

---

## 2. Pin map & calibration (so you know what's what)

**Physical pins on the Uno R3** (`SERVO_PINS` in `servo_bridge.ino:36`):

| Pin | Logical | Servo | Type | Note |
|-----|---------|-------|------|------|
| 3 | joint1 | yaw | MG946R | base |
| 5 | joint2 A | shoulder A | MG946R | one side |
| 6 | joint2 B | shoulder B | MG946R | opposite side — moves **opposite** |
| 9 | joint3 | elbow | MG946R | |
| 10 | joint4 | wrist pitch | SG90 | |
| 11 | gripper | gripper | SG90 | 0 open → 1 closed |

**Opposite shoulders — how it works:**

```cpp
CENTER_US[6] = {1500, 1500, 1500, 1500, 1500, 1500}
RAD_TO_US[6] = { 318,  318, -318,  318,  477,    0}  // pin 6 is -318!
```

* Pin 5 and 6 share the same logical `joint2` angle, but **RAD_TO_US[2] = -318** makes shoulder B go the other way (`servo_bridge.ino:45`). The top perfboard still has 5 headers — the doubling happens in firmware, not wiring.

**Gripper & limits** (`servo_bridge.ino:56-69`):

* Gripper `0.0 → 1250 µs` (open), `1.0 → 1800 µs` (closed) — interpolated
* Hard clamp `PULSE_MIN 700 … PULSE_MAX 2300` — safety wall for every servo
* Logical limits match `robot_arm.urdf`: `joint1 ±3.14`, `joint2-4 ±1.57`, `gripper 0…1`
* Wrist `RAD_TO_US[4] = 477` gives extra reach for SG90 — if yours is a true 90° SG90, you can use 318 instead (comment in sketch:46-51)

> Nice-to-know: the fixed **wrist roll SG90** is installed but not driven — no pin, no header.

---

## 3. Flash the Uno R3

You’ve got two friendly options. Use whichever you already have.

### Option A — Arduino IDE (easiest if you’re new)

1. Install Arduino IDE 2.x, plug the Uno R3 via USB (you’ll see `/dev/ttyACM0` or `/dev/ttyUSB0`)
2. Open `sketch/servo_bridge/servo_bridge.ino`
3. Select **Board: Arduino Uno**, **Port: /dev/ttyACM0**
4. Click **Upload** — the onboard LED should start blinking (500 ms heartbeat from `loop():146`)

### Option B — arduino-cli (quick for pros)

```bash
arduino-cli config init 2>/dev/null || true
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli compile --fqbn arduino:avr:uno sketch/servo_bridge
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/servo_bridge
# Verify the LED blinks — that's the firmware saying "I'm alive"
# Not sure which /dev entry? Try:
dmesg | grep -i ttyACM
ls -l /dev/serial/by-id/
```

**Power warning — please read this:** Servos need a proper **5–6 V external supply** (your LiPo → ZK-4XX → rails), **not USB power**. Set the ZK-4XX display to ~6 V *before* connecting servos, and keep Arduino GND shared with servo GND (you already did this via the bottom-hole wiring). The 300 µF+ cap smooths spikes — leave it in.

---

## 4. Bring up the real arm in ROS 2

You already built the workspace in [`01_SETUP.md`](01_SETUP.md). Now source and launch:

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash

# Option 0 — unified (arm + cameras in one) — also used by Uno Q Docker
ros2 launch robot_arm_hardware real_bringup.launch.py \
  serial_port:=/dev/ttyACM0 front_url:=http://<phone-ip>:4747/video fps:=15.0

# Option 1 — arm stack (bridge + Cartesian service) then camera separately
ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0 baud_rate:=115200

# Option 2 — bridge only (if you just want to poke /joint_command)
ros2 launch robot_arm_hardware real_hw.launch.py serial_port:=/dev/ttyACM0
```

Uno Q users (all-on-Uno-Q): container is `sleep infinity` — it does **not** auto-start ROS. After `docker compose up` (see `HARDWARE.md` for the full Uno Q guide), enter the container and launch yourself:
```bash
docker compose exec arm bash
source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && source /opt/venv/bin/activate
ros2 launch robot_arm_hardware real_bringup.launch.py serial_port:=/dev/ttyACM0 front_url:=http://<phone-ip>:4747/video fps:=15.0
```
Full step-by-step including `daemon.json`, `docker pull`, `docker tag`, and inference: see [`HARDWARE.md`](../HARDWARE.md) (FULL COMMAND LIST).

What you’ll see:

* `hw_interface ready on /dev/ttyACM0 @ 115200` — bridge listening on `/joint_command` (Float64MultiArray, 5 values) and publishing `/joint_states` (commanded pose, real servos have no feedback)
* `hw_move_to ready on /modular_arm/move_to` — same `/modular_arm/move_to` service as sim! (`real_arm.launch.py:18-32` starts both nodes; `real_hw.launch.py` is bridge-only)

**Check your args anytime:**

```bash
ros2 launch --show-args robot_arm_hardware real_arm.launch.py
ros2 launch --show-args robot_arm_hardware real_hw.launch.py
# both now declare serial_port (/dev/ttyACM0) + baud_rate (115200) — so serial_port:=/dev/ttyUSB0 works
```

Need dialout permission? `sudo usermod -aG dialout $USER` then re-login, or `sudo chmod 666 /dev/ttyACM0` for a quick test. Find your port with `ls /dev/ttyACM* /dev/ttyUSB*` or `dmesg | grep tty`.

> **Cameras are separate** — the launch above does **not** start `camera_bridge`. For DroidCam / ESP32 setup, see `07_CAMERA_BRIDGE.md` (one more command) — then `05_DATA_COLLECTION.md` / `06_INFERENCE.md` will show you the full 3-terminal flow.

---

## 5. Move it! (same API as sim — yay)

In another sourced terminal:

```bash
# Home / START pose — the safe middle you saw in sim
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.0, z: 0.08, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 1.5}"

# Tiny nudge to see it live
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 0.0, duration_sec: 1.0}"

# Close the gripper in place
ros2 service call /modular_arm/move_to modular_arm_interfaces/srv/MoveTo \
  "{x: 0.27, y: 0.06, z: 0.06, pitch: -1.57, elbow: '', gripper: 1.0, duration_sec: 1.0}"
```

* `x,y,z` in meters, `pitch` rad (0 horizontal, -1.57 straight down), `elbow ''` lets the solver pick, `gripper 0…1`, `duration_sec` smooth-interpolates at 50 Hz with easing (`hw_move_to.py:96-113` — no jerks)
* Response `joint_angles` is the 5 logical values sent → expanded to 6 servos in firmware
* The shoulder pair moves opposite automatically — you only ever command one `joint2`

**Watch the ZK-4XX display while moving — current will spike a bit, voltage should stay flat. That’s the cap doing its job.**

---

## 6. How the nodes fit together (if you’re curious)

* `hw_interface.py:63-73` — subscribes `/joint_command` → writes `"j1,j2,j3,j4,grip\n"` at 115200, 2 s Arduino reset delay on open, publishes `/joint_states` at 20 Hz
* `hw_move_to.py:52-81` — `MoveTo` → `ik.py` → interpolates `start → target` over `duration_sec` at `CMD_RATE 50 Hz` with smoothstep, publishes `/joint_command`
* Both respect the same `JOINT_NAMES` order as the sketch: `joint1, joint2, joint3, joint4, gripper`

Serial line example: `0.00000,0.50000,-0.30000,0.10000,0.00000\n`

---

## 7. Troubleshooting — quick fixes with a smile

| What you see | Likely cause | Friendly fix |
|---|---|---|
| `Cannot open /dev/ttyACM0` / permission denied | Not in `dialout` or wrong port | `ls /dev/ttyACM*` to find it, `sudo usermod -aG dialout $USER`, re-login, retry `115200` |
| Arm doesn’t move but service says success | ZK-4XX not set or cap missing, or GND not shared | Set ZK-4XX to ~6 V *before* servos, check GND wire from bottom hole is on the rail, check 300 µF cap orientation (stripe = –) |
| One shoulder goes the wrong way | Pin 6 sign | Keep `RAD_TO_US[2] = -318` — don’t “fix” it to +318 |
| Wrist barely reaches 90° | SG90 variant | Try `RAD_TO_US[4] = 477` (as set) for extra range; if overshoot, use 318 |
| Grip jitter / reset | Power sag | Thicker power wires, keep runs short, ensure LiPo charged, cap ≥300 µF |
| `/joint_command expected 5 values` | Wrong topic type | Publish `Float64MultiArray` with 5 floats: `ros2 topic pub --once /joint_command std_msgs/Float64MultiArray "{data: [0,0,0,0,0]}"` |

Still stuck? Capture the `hw_interface` + `hw_move_to` logs and the ZK-4XX reading — we’ll sort it together.

---

## 8. What’s next?

* Need cameras? See [`07_CAMERA_BRIDGE.md`](07_CAMERA_BRIDGE.md) — DroidCam / ESP32 MJPEG → ROS 2 (front_url / gripper_url, fps, QoS).
* Ready to collect demos for learning? Head to [`05_DATA_COLLECTION.md`](05_DATA_COLLECTION.md) — or jump to [`06_INFERENCE.md`](06_INFERENCE.md) to deploy the policy.
* Full wiring details & sketch reference: [`../sketch/servo_bridge/README.md`](../sketch/servo_bridge/README.md)

## Credits

Mechanical design by **Emre Kalem (@emrekalem)** — [MakerWorld](https://makerworld.com/en/models/1134925-robotic-arm-with-servo-arduino?from=search#profileId-1135927). Firmware & ROS bridge are our adaptation for the 5→6 shoulder expansion.
