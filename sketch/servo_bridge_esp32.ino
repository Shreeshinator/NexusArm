/*
 * servo_bridge_esp32.ino  —  ESP32 DevKit V1 real-robot servo bridge
 *
 * ESP32 port of servo_bridge.ino (which ran on an Arduino Uno R3).
 * Receives 5 LOGICAL joint-angle values over serial (line-delimited CSV) and
 * drives 6 PHYSICAL hobby servos:
 *
 *     "<joint1>,<joint2>,<joint3>,<joint4>,<gripper>\n"
 *
 *   joint1..joint4 : angle in RADIANS (limits match robot_arm.urdf)
 *   gripper        : 0.0 (open) .. 1.0 (closed)
 *
 * Physical servo map (ESP32 DevKit V1 GPIO pins):
 *   0  joint1  yaw        MG946R      GPIO 16
 *   1  joint2  shoulder A  MG946R      GPIO 17   (one side)
 *   2  joint2  shoulder B  MG946R      GPIO 18   (opposite side, moves OPPOSITE)
 *   3  joint3  elbow       MG946R      GPIO 19
 *   4  joint4  wrist       SG90        GPIO 21
 *   5  gripper             SG90        GPIO 22
 *
 * The SHOULDER is two servos mounted on opposite sides: when joint2 rotates +,
 * servo A goes + and servo B goes - (opposite pulse).  That is handled here by
 * giving shoulder B a NEGATIVE RAD_TO_US.  Everything upstream (ROS / LeRobot)
 * only ever sees the single logical "joint2" angle — the 5->6 expansion is the
 * firmware's job and this file is the ONLY place it lives.
 *
 * This node knows nothing about ROS, LeRobot, or arm calibration — it just maps
 * a logical joint angle to PWM pulses via the per-servo CALIBRATION table.  Tune
 * that table for the servos.
 *
 * POWER: 6 servos need a proper 5-6 V external supply, NOT the ESP32's 3.3V or
 * USB 5V.  Share GND between the servo supply and the ESP32.
 */

#include <ESP32Servo.h>   // install via Library Manager: "ESP32Servo" (Kevin Harrington)

const int NUM_SERVOS = 6;
// ESP32 output pins.  Chosen to avoid: strapping pins (0,2,5,12,15),
// flash (6-11), UART0 (1,3), input-only (34-39).  Reassign freely.
const int SERVO_PINS[6] = {16, 17, 18, 19, 21, 22};

Servo servos[6];

// ---------- Calibration (TUNE FOR YOUR ACTUAL SERVOS) ----------
// pulse_us = CENTER_US[i] + RAD_TO_US[i] * angle_rad   (arm servos)
//
//   CENTER_US[i] : PWM pulse (us) when that logical joint angle is 0
//   RAD_TO_US[i] : us per radian (SIGN sets direction; flip if reversed)
// MG946R ~180 deg: full sweep ~1000..2000 us.  SG90 wrist similar.
// Start conservative (PULSE_MIN/MAX) and expand only after measuring real travel.
const float CENTER_US[6] = {1500.0, 1500.0, 1500.0, 1500.0, 1500.0, 1500.0};
const float RAD_TO_US[6] = {-318.0,  318.0, -318.0,  318.0,  318.0,  0.0};
//   index 0 (joint1 yaw) is NEGATIVE -> yaw direction reversed (verified on real arm).
//   index 2 (shoulder B) is NEGATIVE -> moves opposite to shoulder A (index 1).
//   index 5 (gripper) is unused here; gripper has its own 0..1 mapping below.

// Gripper (SG90) maps the 0..1 command to its own pulse range directly.
const int GRIP_OPEN_US   = 1250;   // gripper command = 0.0  (tuned on real arm)
const int GRIP_CLOSED_US = 1800;   // gripper command = 1.0  (tuned on real arm)

const int PULSE_MIN = 800;         // hard safety clamp on every pulse
const int PULSE_MAX = 2200;

// Logical joint limits (radians; gripper 0..1). Must match robot_arm.urdf.
const float JOINT_LIMIT[5][2] = {
  {-3.14159, 3.14159},  // joint1 yaw
  {-1.57080, 1.57080},  // joint2 shoulder
  {-1.57080, 1.57080},  // joint3 elbow
  {-1.57080, 1.57080},  // joint4 wrist
  { 0.00000, 1.00000},  // gripper
};

float lastCmd[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
unsigned long lastCmdMs = 0;
const unsigned long WATCHDOG_MS = 1000;   // hold last pose if host goes silent

void writePulse(int i, float us) {
  int p = (int)constrain(us, (float)PULSE_MIN, (float)PULSE_MAX);
  servos[i].writeMicroseconds(p);
}

void applyPose(const float c[5]) {
  // joint1 yaw
  writePulse(0, CENTER_US[0] + RAD_TO_US[0] * c[0]);

  // joint2 shoulder -> two opposed servos
  float sh = constrain(c[1], JOINT_LIMIT[1][0], JOINT_LIMIT[1][1]);
  writePulse(1, CENTER_US[1] + RAD_TO_US[1] * sh); // shoulder A
  writePulse(2, CENTER_US[2] + RAD_TO_US[2] * sh); // shoulder B (opposite)

  // joint3 elbow
  writePulse(3, CENTER_US[3] + RAD_TO_US[3] * c[2]);

  // joint4 wrist
  writePulse(4, CENTER_US[4] + RAD_TO_US[4] * c[3]);

  // gripper (0..1)
  float g = constrain(c[4], 0.0, 1.0);
  writePulse(5, (float)(GRIP_OPEN_US + g * (GRIP_CLOSED_US - GRIP_OPEN_US)));
}

void parseAndApply(const String& line) {
  float v[5];
  int idx = 0;
  int start = 0;

  for (int i = 0; i <= line.length(); i++) {
    if (i == line.length() || line.charAt(i) == ',') {
      if (idx < 5) {
        v[idx] = line.substring(start, i).toFloat();
        idx++;
      }
      start = i + 1;
      if (idx >= 5) break;
    }
  }
  if (idx == 5) {
    for (int j = 0; j < 5; j++) lastCmd[j] = v[j];
    applyPose(v);
  }
}

void setup() {
  Serial.begin(115200);
  // Give the USB-UART a moment so early debug prints aren't dropped.
  delay(200);

  // ESP32Servo allocates a hardware timer + LEDC channels per servo; attach them all.
  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].setPeriodHertz(50);          // standard 50 Hz servo PWM
    servos[i].attach(SERVO_PINS[i]);
  }

  float home[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
  applyPose(home);                 // safe home before accepting commands
  lastCmdMs = millis();
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      parseAndApply(line);
      lastCmdMs = millis();
    }
  }
  static unsigned long ledT = 0;
  if (millis() - ledT > 500) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    ledT = millis();
  }
  // Watchdog: keep holding last commanded pose (servos retain position)
  (void)WATCHDOG_MS;   // placeholder; lastCmdMs retained for future watchdog use
}
