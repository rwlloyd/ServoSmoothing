/* MultiServoController

  should probably do this with struct and array
  https://forum.arduino.cc/t/multiple-lines-of-code-running-simultaneously/583332/29 29/34
*/

#include <Wire.h>                     // include the Wire Library - needed to communicate with the DAC
#include <Adafruit_MCP4725.h>         // inlcude the DAC library - contains the comms protocol needed to communicate with the DAC

#include <Servo.h>

const int numServos = 7;
int errorPin = 9;
// servo order. bottom -> top. left -> right
int servoPins[] = {2, 3, 4, 5, 6, 7, 8};
// use the servo minimums and maximums worked out with getServoCentres.ino
int servoMins[] = {800, 800, 800, 1900, 1494, 1600, 1100};
int servoMaxs[] = {2100, 2100, 2100, 900, 2095, 970, 1920};
int servoCentres[] = {1385, 1500, 1467, 1360, 1795, 1285, 1648}; 
int servoStart[] = {};


float cmdPos[numServos];
float cmdPosSmoothed[numServos];
float cmdPosSmPrev[numServos];

Servo rotate;
Servo tiltRight;
Servo tiltLeft;
Servo eyeLeft;
Servo blinkLeft;
Servo blinkRight;
Servo eyeRight;

Servo servos[numServos] = {rotate, tiltRight, tiltLeft, eyeLeft, blinkLeft, blinkRight, eyeRight};

// Setup serial communication bytes
// length of data packet. 2*NumberOfMotors + Error + enable
const int messageLength = numServos;
// Array for the received message
int received[messageLength];
// Flag to signal when a message has been received
bool commandReceived = false;

// have a timer for events?
// If we lose connection, we should stop
unsigned long lastMillis;
unsigned long currentMillis;
const unsigned long period = 250;  //the value is a number of milliseconds, ie 2s

bool error = false;


void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println(0);
  for (int i = 0; i < numServos; i++) {
    servos[i].attach(servoPins[i]);
  }
  for (int i = 0; i < numServos; i++) {
    servos[i].write(servoCentres[i]);
    Serial.println(i);
  }

  Serial.println(1);
  // Record the time for connection checking
  lastMillis = millis();
}


//  servoNeck.attach(2);
//  servoTiltLeft.attach(3);
//  servoTiltRight.attach(4);
//  servoEyeLeft.attach(5);
//  servoBlinkLeft.attach(6);
//  servoEyeRight.attach(7);
//  servoBlinkRight.attach(8);
//
//  servoNeck.write(90);
//  servoTiltLeft.write(90);
//  servoTiltRight.write(90);
//  servoEyeLeft.write(90);
//  servoBlinkLeft.write(90);
//  servoEyeRight.write(90);
//  servoBlinkRight.write(90);

void loop() {

  //  for (int i = 0; i < numServos; i++) {
  //    for (cmdPos[i] = servoMin; cmdPos[i] <= servoMax; cmdPos[i] += 1) { // goes from 0 degrees to 180 degrees
  //      // in steps of 1 degree
  //      servos[i].write(cmdPos[i]);              // tell servo to go to position in variable 'pos'
  //      delay(30);                       // waits 15ms for the servo to reach the position
  //    }
  //    for (int i = 0; i < numServos; i++) {
  //      for (cmdPos[i] = servoMax; cmdPos[i] >= servoMin; cmdPos[i] -= 1) { // goes from 180 degrees to 0 degrees
  //        servos[i].write(cmdPos[i]);              // tell servo to go to position in variable 'pos'
  //        delay(30);                       // waits 15ms for the servo to reach the position
  //      }
  //    }
  //  }

  if (commandReceived == true)                     // This code is executed in non interupt time only when a new command has been recieved
  { // A new command has been recieved when a \n or \r character is recieved.
    processSerialCommand();                        // Process the command
    //commandReceived = false;                       // Clear the command pending flag. // done in process serial command now
  }

  for (int i = 0; i < numServos; i++) {
    servos[i].write(servoCentres[i]);
    delay(30);
  }


}

//void calcCmdPos() {
//  for (int i = 0; i < numServos; i++) {
//    cmdPosSmoothed cmdPosSmPrev cmdPos
//  }
//
//}

// When new characters are received, the serialEvent interrupt triggers this function
void serialEvent()   {
  // Read the Serial Buffer
  for (int i = 0; i < messageLength; i++) {
    received[i] = Serial.read();
    delay(1);
  }
  // Change the flag because a command has been received
  commandReceived = true;
  // Record the time
  lastMillis = millis();
}

// Function to split up the received serial command and set the appropriate variables
void processSerialCommand() {
  if (error == false) {
    //    error = bool(received[0]);                                  // Error Flag
  }
  if (error == true) {
    //    received[0] = byte(error);
  }
  //  motorsEnabled = bool(received[1]);                          // Motor Enable Flag
  //  // Motor Directions
  //  motorDirs[0] = bool(received[2]);
  //  motorDirs[1] = bool(received[4]);
  //  motorDirs[2] = bool(received[6]);
  //  motorDirs[3] = bool(received[8]);
  //  // Motor Velocities
  //  motorVels[0] = map(received[3], 0, 100, 200, 4092 * speed_multiplier);
  //  motorVels[1] = map(received[5], 0, 100, 200, 4092 * speed_multiplier);
  //  motorVels[2] = map(received[7], 0, 100, 200, 4092 * speed_multiplier);
  //  motorVels[3] = map(received[9], 0, 100, 200, 4092 * speed_multiplier);
  //  // Implement the new command
  //  updateDirections();
  //  updateDACs();
  //updateUnits();
  // Chirp the message back
  for (int i = 0; i < messageLength; i++) {
    Serial.write(received[i]);
  }
  // Allow a new message
  commandReceived = false;
}
