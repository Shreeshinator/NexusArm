// Leader Arm Teleoperation Sketch
// Reads 4 potentiometers + 1 debounced pullup button, sends CSV over Serial.
//
// Potentiometer specs: 270 degree rotation range, but mechanically constrained
// to the middle ~180 degrees in the leader arm.
//
// Wiring:
//   A0 - Joint 1 (base yaw)    pot
//   A1 - Joint 2 (shoulder)     pot
//   A2 - Joint 3 (elbow)        pot
//   A3 - Joint 4 (wrist)        pot
//   D2 - Gripper button         pushbutton to GND (pulled HIGH internally)
//
// Serial format: "j1,j2,j3,j4,btn\n"
//   j1..j4 = raw 10-bit ADC (0-1023)
//   btn    = 0 when pressed (gripper close), 1 when released (gripper open)
//
// Baud rate: 115200 (to match the ROS2 node default)

const int PIN_J1 = A0;
const int PIN_J2 = A1;
const int PIN_J3 = A2;
const int PIN_J4 = A3;
const int PIN_BTN = 2;

const int NUM_SAMPLES = 4;
const unsigned long SEND_INTERVAL_US = 20000;  // 20ms = 50Hz
const unsigned long DEBOUNCE_MS = 50;           // button debounce time

unsigned long last_send_us = 0;

int btn_state = HIGH;          // current stable button state
int last_btn_read = HIGH;      // previous raw reading
unsigned long last_debounce_time = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN, INPUT_PULLUP);

  unsigned long start = millis();
  while (!Serial && millis() - start < 3000) {
    delay(10);
  }
}

void loop() {
  unsigned long now = micros();
  if (now - last_send_us < SEND_INTERVAL_US) {
    return;
  }
  last_send_us = now;

  int j1 = readAverage(PIN_J1);
  int j2 = readAverage(PIN_J2);
  int j3 = readAverage(PIN_J3);
  int j4 = readAverage(PIN_J4);

  int reading = digitalRead(PIN_BTN);
  if (reading != last_btn_read) {
    last_debounce_time = millis();
  }
  if ((millis() - last_debounce_time) > DEBOUNCE_MS) {
    if (reading != btn_state) {
      btn_state = reading;
    }
  }
  last_btn_read = reading;

  Serial.print(j1);
  Serial.print(',');
  Serial.print(j2);
  Serial.print(',');
  Serial.print(j3);
  Serial.print(',');
  Serial.print(j4);
  Serial.print(',');
  Serial.println(btn_state);
}

int readAverage(int pin) {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(pin);
    delayMicroseconds(100);
  }
  return sum / NUM_SAMPLES;
}
