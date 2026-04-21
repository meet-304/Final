// Arduino Uno R3 Servo Control Sketch
// Receives servo angle commands from Raspberry Pi via Serial
// Format: "S{angle}\n" where angle is 0-180 degrees

#include <Servo.h>

#define SERVO_PIN 9  // PWM pin for servo motor
#define LED_PIN 13   // Built-in LED for feedback

Servo servo;
int currentAngle = 90;  // Default to center position

void setup() {
  Serial.begin(9600);  // Match RPi baud rate

  pinMode(LED_PIN, OUTPUT);
  servo.attach(SERVO_PIN);
  servo.write(currentAngle);  // Initialize to 90 degrees

  digitalWrite(LED_PIN, HIGH);
  delay(100);
  digitalWrite(LED_PIN, LOW);

  Serial.println("Arduino Ready!");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Parse servo command: "S90", "S180", "S0", etc.
    if (command.startsWith("S")) {
      int angle = command.substring(1).toInt();

      // Validate angle range
      if (angle >= 0 && angle <= 180) {
        servo.write(angle);
        currentAngle = angle;

        // Blink LED for feedback
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);

        Serial.print("OK:");
        Serial.println(angle);
      } else {
        Serial.println("ERROR:Invalid angle");
      }
    }
  }
}
