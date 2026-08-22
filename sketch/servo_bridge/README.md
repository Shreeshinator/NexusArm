# Servo Bridge — Arduino Uno R3 Firmware Reference

Firmware: `sketch/servo_bridge/servo_bridge.ino`
* Target: Arduino Uno R3
* Baud: 115200
* Serial CSV format: `j1,j2,j3,j4,gripper\n` (raw microsecond pulse widths)
* Update rate: 50 Hz (20 ms loop)

## Pinout

| Pin | Function | Notes |
|-----|----------|-------|
| **3** | joint1 (base yaw) | MG946R |
| **5** | joint2 (shoulder A) | MG995/996R |
| **6** | joint3 (shoulder B) | MG995/996R — *RAD_TO_US -318* |
| **9** | joint4 (wrist pitch) | SG90 |
| **10** | joint4 (wrist pitch) | SG90 |
| **11** | gripper | SG90 | 0.0 open → 1.0 closed |

## Constants (servo_bridge.ino:26-36)

| Constant | Value | Meaning |
|----------|-------|---------|
| `RAD_TO_US {318,318,-318,318,477,0}` | per-joint yaw-to-pulse conversion | 318 = ±90° for joints 1-4; 477 = ±90° for wrist pitch; 0 = fixed gripper roll |
| `CENTER_US {1500×6}` | neutral pulse width | 1500 µs centers all joints |
| `SERVO_PINS {3,5,6,9,10,11}` | which pins drive which joint | physical pin → logical joint mapping |

## Calibration Notes (empirically tuned, do not re-derive)

| Parameter | Value | Effect |
|-----------|-------|--------|
| `RAD_TO_US[2]` = -318 (pin 6) | Shoulder B moves opposite to A — one must be negated so both shoulders drive the same physical joint |
| `RAD_TO_US[4]` = 477 | Wrist pitch scale — smaller than shoulders (SG90 vs MG995) |
| `CENTER_US` = 1500 | Mid-point; servos jitter slightly off this — keep power stable (300 µF cap recommended) |
| Gripper pulse range | NOT driven by RAD_TO_US (fixed at 0); position controlled via `GRIPPER_MAX_TRAVEL=0.015` in `move_to_node.py` |

## Flash commands

```bash
# Arduino IDE: open sketch/servo_bridge/servo_bridge.ino → Board: Uno → Port: /dev/ttyACM0 → Upload
# or CLI (recommended for scripts):
arduino-cli compile --fqbn arduino:avr:uno sketch/servo_bridge/servo_bridge.ino
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno sketch/servo_bridge/servo_bridge.ino

# sanity check — you should see ~1500 µs pulses (or the CSV below at 50 Hz)
picocom /dev/ttyACM0 -b 115200
# e.g. 1500,1500,1500,1500,1500,1500
```

## Power

* Arduino Uno R3: regulated 5 V from USB or barrel jack
* Servo power: **do NOT power 6 servos from the Uno 5 V pin** — it will brown out
* Use a **buck-boost (ZK-4XX with display)** or separate 6 V LiPo pack for the servos, common GND with Arduino
* A **≥300 µF capacitor** across VCC/GND on the servo rail smooths startup inrush

## Wiring summary (canonical — matches servo_bridge.ino:36)

Base yaw (joint1) → MG946R on pin 3
Shoulder (joint2) → 2× MG995/996R on pins 5/6 (opposite `RAD_TO_US -318` on pin 6)
Elbow (joint3) → MG946R on pin 9
Wrist pitch (joint4) → SG90 on pin 10 (`RAD_TO_US 477` for 60°-SG90, else 318)
Gripper → SG90 on pin 11 (`GRIP_OPEN 1250 → GRIP_CLOSED 1800`, 0..1)
> Fixed wrist-roll SG90 (installed, not driven) has no pin.

## Credits

Firmware adapted from Emre Kalem's MakerWorld `Robotic Arm with Servo & Arduino` design.
Modified for 5→6 shoulder expansion (added shoulder B with `RAD_TO_US -318`).