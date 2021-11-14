/* MultiServoController

  should probably do this with struct and array
  https://forum.arduino.cc/t/multiple-lines-of-code-running-simultaneously/583332/29 29/34
*/

#include <Servo.h>

// how many servos are we controlling?
const int numServos = 7;
// Surely theres an on off button?
int errorPin = 9;
// servo order. keep careful track of this.
int servoPins[] = {2, 3, 4, 5, 6, 7, 8};
// use the servo minimums and maximums worked out with getServoCentres.ino
int servoMins[] = {800, 800, 800, 1900, 1494, 1600, 1100};
int servoMaxs[] = {2100, 2100, 2100, 900, 2095, 970, 1920};
int servoCentres[] = {1385, 1485, 1468, 1360, 1795, 1285, 1648}; 

// Set up the arrays for the future, present and past servo positions
float cmdPos[numServos];
float cmdPosSmoothed[numServos];
float cmdPosSmPrev[numServos];

// instantiate each servo, with a particular name. probably not necessary in this instance, but it cant hurt. You're welcome future me.
Servo rotate;
Servo tiltRight;
Servo tiltLeft;
Servo eyeLeft;
Servo blinkLeft;
Servo blinkRight;
Servo eyeRight;

// Put the servos into an array
Servo servos[numServos] = {rotate, tiltRight, tiltLeft, eyeLeft, blinkLeft, blinkRight, eyeRight};

// Setup serial communication bytes
// length of data packet. Just the number of servos for now
const int messageLength = numServos;
// Array for the received message
int received[messageLength];
// Flag to signal when a message has been received
bool commandReceived = false;

// have a timer for events?
// If we lose connection, we should do something?
unsigned long lastMillis;
unsigned long currentMillis;
const unsigned long period = 250;  //the value is a number of milliseconds, ie 2s

// an error flag is always useful
bool error = false;


void setup() {
  // Start serial comms
  Serial.begin(115200);
  // Give it a chance to settle. using delay() might give you grief if porting to a different ucontroller
  delay(50);   
  // Announce start of setup over serial 
  Serial.println(0);
  // loop thorough and attach the servos
  for (int i = 0; i < numServos; i++) {
    servos[i].attach(servoPins[i]);
    // set the cmdPos for the first time
    cmdPos[i] = servoCentres[i];
  }
  // set the servos to their centre positions
  for (int i = 0; i < numServos; i++) {
    servos[i].write(cmdPos[i]);
    //Serial.println(i);
  }

  // Record the time for connection checking
  lastMillis = millis();
  // Announce end of setup
  Serial.println(1);
}

void loop() {
  if (commandReceived == true)   {                  // This code is executed in non interupt time only when a new command has been recieved
   // A new command has been recieved when a \n or \r character is recieved.
    processSerialCommand();                        // Process the command
  }

  // Write the desired command position to the servo
  for (int i = 0; i < numServos; i++) {
    servos[i].write(cmdPos[i]);
  }
}

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
  // Loop throught the received serial 0-255 bytes, cast them to ints and map them to the servo microsecond values. Store values in cmdPos array.
  for (int i = 0; i < messageLength; i++) {
    cmdPos[i] = floor(map(int(received[i]), 0, 255, servoMins[i], servoMaxs[i]));
  }
  // Chirp the message back just because.
  for (int i = 0; i < messageLength; i++) {
    Serial.write(received[i]);
  }
  // Allow a new message
  commandReceived = false;
}
