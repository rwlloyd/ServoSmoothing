/*
  Controlling a servo position using a potentiometer (variable resistor)
  by Michal Rinott <http://people.interaction-ivrea.it/m.rinott>

  modified on 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Knob
*/

#include <Servo.h>

Servo rightServo;  // create servo object to control a servo
Servo leftServo;
Servo rightEyeball;
Servo leftEyeball;
Servo rightEyelid;
Servo leftEyelid;

int potpin = 0;  // analog pin used to connect the potentiometer
int val, valRight, valLeft;    // variable to read the value from the analog pin
int servoMin = 800;
int servoMax = 2100;
int blinkLeftMin = 1494;
int blinkLeftMax = 2095;
int blinkRightMin = 1600;
int blinkRightMax = 970;

bool tilt = false;
bool nod = true;
bool look = false;
bool blinker = true;

void setup() {
  Serial.begin(115200);
  rightServo.attach(3);  // robotRight attaches the servo on pin 9 to the servo object
  leftServo.attach(4);  // robotLeft attaches the servo on pin 9 to the servo object
  rightEyeball.attach(5);
  leftEyeball.attach(8);
  rightEyelid.attach(7);
  leftEyelid.attach(6);
}

void loop() {
  val = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023)
  if (tilt) {
    valRight = map(val, 0, 1023, servoMin, servoMax);
    valLeft = map(val, 0, 1023, servoMin, servoMax);

    rightServo.writeMicroseconds(valRight);                  // sets the servo position according to the scaled value
    leftServo.writeMicroseconds(valLeft);
  }
  else if (nod) {
    valRight = map(val, 0, 1023, servoMin, servoMax);
    valLeft = map(val, 0, 1023, servoMax, servoMin);

    rightServo.writeMicroseconds(valRight);                  // sets the servo position according to the scaled value
    leftServo.writeMicroseconds(valLeft);
  }
  if (look) {
    int offset = 200;
    valRight = map(val, 0, 1023, servoMin + offset, servoMax - offset);
    valLeft = map(val, 0, 1023, servoMin + offset, servoMax - offset);

    rightEyeball.writeMicroseconds(valRight);                  // sets the servo position according to the scaled value
    leftEyeball.writeMicroseconds(valLeft);
  }
  if (blinker) {
    int offset = 200;
    valRight = map(val, 0, 1023, blinkRightMin, blinkRightMax);
    valLeft = map(val, 0, 1023, blinkLeftMin, blinkLeftMax);

    rightEyelid.writeMicroseconds(valRight);                  // sets the servo position according to the scaled value
    leftEyelid.writeMicroseconds(valLeft);
  }
  Serial.print(valRight);
  Serial.print(",");
  Serial.println(valLeft);
  delay(15);                           // waits for the servo to get there
}
