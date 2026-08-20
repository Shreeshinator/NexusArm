/*
 * servo_bridge.ino  —  Arduino Uno R3 real-robot servo bridge
 *
 * Receives 5 LOGICAL joint-angle (in RADIANS) values over serial (line-delimited CSV) and
 * drives 6 PHYSICAL hobby servos:
 *
 *     "<joint1>,<joint2>,<joint3>,<joint4>,<gripper>\n"
 *
 *   joint1..joint4 : angle in RADIANS (limits match robot_arm.urdf)
 *   gripper        : 0.0 (open) .. 1.0 (closed)
 *
 * Physical servo map (Uno R3 PWM pins):
 *   3  joint1  yaw        MG946R
 *   5  joint2  shoulder A  MG946R   (one side)
 *   6  joint2  shoulder B  MG946R   (opposite side, moves OPPOSITE)
 *   9  joint3  elbow       MG946R
 *   10 joint4  wrist       SG90
 *   11 gripper             SG90
 *
 * The SHOULDER is two servos mounted on opposite sides: when joint2 rotates +,
 * servo A goes + and servo B goes - (opposite pulse).  That is handled here by
 * giving shoulder B a NEGATIVE RAD_TO_US.  Everything upstream (ROS / LeRobot)
 * only ever sees the single logical "joint2" angle — the 5->6 expansion is the
 * firmware's job and this file is the ONLY place it lives.

 * The exact same firmware runs on the
 * R3 with PC and on Uno Q (Linux just sends these lines to the serial port
 * bound into the Docker container).
 *
 * POWER: 6 servos need a proper 5-6 V external supply, NOT USB power.
 */

#include <Servo.h> // The servo library

const int NUM_SERVOS = 6;
const int SERVO_PINS[6] = {3, 5, 6, 9, 10, 11}; // PWM pins on the Arduino Uno R3

Servo servos[6];

// ---------- Calibration (TUNE FOR YOUR ACTUAL SERVOS) ----------
//   RAD_TO_US[i] : us per radian, flip if reversed
// MG946R ~180 deg: full sweep ~1000..2000 us.  SG90 wrist similar.

const float CENTER_US[6] = {1500.0, 1500.0, 1500.0, 1500.0, 1500.0, 1500.0};
const float RAD_TO_US[6] = { 318.0,  318.0, -318.0,  318.0,  477.0,  0.0};

//   index 2 (shoulder B) - always moves opposite to shoulder A (index 1).
//   index 5 (gripper) is unused here; gripper has its own 0..1 mapping below.

// Important: the wrist SG90 should rotate close to 90 deg (1.57 rad) in either direction, increase the RAD_TO_US[4] to 477 to get maximum possible range (if it is a 60 deg servo).
// If the SG90 is a 90, deg servo, leave it to 318

//   the clamp below is widened to 700-2300 to let the wrist physically reach max possible range.

// Gripper (SG90) maps the 0 - 1 command to its own pulse range directly.
const int GRIP_OPEN_US   = 1250;   // gripper command = 0.0
const int GRIP_CLOSED_US = 1800;   // gripper command = 1.0

const int PULSE_MIN = 700;         // hard safety clamp on every pulse
const int PULSE_MAX = 2300;

// Logical joint limits (radians; gripper 0..1). Must match robot_arm.urdf.
const float JOINT_LIMIT[5][2] = {
  {-3.14159, 3.14159},  // joint1 yaw,      rotates full circle
  {-1.57080, 1.57080},  // joint2 shoulder, rotates 90 degree in either direction, 0 is straight up
  {-1.57080, 1.57080},  // joint3 elbow    rotates 90 degree in either direction, 0 is straight out
  {-1.57080, 1.57080},  // joint4 wrist,   rotates 90 degree in either direction, 0 is straight out
  { 0.00000, 1.00000},  // gripper
};

float lastCmd[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
unsigned long lastCmdMs = 0;
const unsigned long WATCHDOG_MS = 1000;   // hold last pose if host goes silent

void writePulse(int i, float us) {
  int p = (int)constrain(us, (float)PULSE_MIN, (float)PULSE_MAX); // constrain to safe range,
  servos[i].writeMicroseconds(p); // then write to servo
}

void applyPose(const float c[5]) {
  // Don't need to constrain here; parseAndApply already does that.  But we do need to convert logical joint angles to physical servo pulses.

  // joint1 yaw
  writePulse(0, CENTER_US[0] + RAD_TO_US[0] * c[0]);

  // joint2 shoulder -> two opposed servos
  float sh = constrain(c[1], JOINT_LIMIT[1][0], JOINT_LIMIT[1][1]); // constrain to shoulder limits

  writePulse(1, CENTER_US[1] + RAD_TO_US[1] * sh); // shoulder A
  writePulse(2, CENTER_US[2] + RAD_TO_US[2] * sh); // shoulder B (opposite), RAD_TO_US[2] is negative so it moves opposite

  // joint3 elbow
  writePulse(3, CENTER_US[3] + RAD_TO_US[3] * c[2]);

  // joint4 wrist
  writePulse(4, CENTER_US[4] + RAD_TO_US[4] * c[3]);

  // gripper (0..1)
  float g = constrain(c[4], 0.0, 1.0);
  writePulse(5, (float)(GRIP_OPEN_US + g * (GRIP_CLOSED_US - GRIP_OPEN_US)));
}

void parseAndApply(const String& line) {
  float v[5];     // temporary array to hold parsed joint angles
  int idx = 0;    // index for the v array
  int start = 0;  // start index for substring extraction

  for (int i = 0; i <= line.length(); i++) { // loop through the line, including one extra iteration to handle the last value (because the last value is not followed by a comma)

    if (i == line.length() || line.charAt(i) == ',') { // if we reach the end of the line or find a comma, we extract the substring and convert it to float
      if (idx < 5) { // if we haven't filled the v array yet, we extract the substring from start to i and convert it to float.

        v[idx] = line.substring(start, i).toFloat(); // Extract the substring from start to i and convert it to float, storing it in the v array at index idx
        idx++;
      }
      start = i + 1;
      if (idx >= 5) break;
    }
  }
  if (idx == 5) {
    for (int j = 0; j < 5; j++) lastCmd[j] = v[j]; // store the last commanded pose
    applyPose(v); // Finally, apply the pose to the servos
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < NUM_SERVOS; i++) servos[i].attach(SERVO_PINS[i]);
  float home[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
  applyPose(home);                 // safe home before accepting commands
  lastCmdMs = millis();            // home is the last commanded pose
  pinMode(LED_BUILTIN, OUTPUT);    // built-in LED blinks to show the firmware is alive
}

void loop() {
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim(); // remove any leading/trailing whitespace or newline characters

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
}
