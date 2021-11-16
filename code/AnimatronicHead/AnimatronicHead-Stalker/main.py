#!/usr/bin/env python3

"""
Current status

still mashing 
"""

## General Stuff
import serial
import math
from time import sleep
## Opencv
import cv2
import numpy as np
from math import floor
## Bluetooth controller
# import fbox as bt
# import subprocess as sp

print("   ------------------------------------------------------------")
print("    Animatronic Head Puppet with Webcam Body and Face Tracking")
print("   ------------------------------------------------------------")
print("    E = Enable/Disable")
print("    ")
print("     - Rob Lloyd. 11/2021")
print("    ")

# print("   ----------------------------------------------------------")
# print("    Animatronic Head Puppet with Generic Bluetooth Controller")
# print("   ----------------------------------------------------------")
# print("    Button A = Enable/Disable")
# print("    Left Thumbstick X = Rotation")
# print("    Left Thumbstick Y = Pitch")
# print("    Right Thumbstick X = Eyes left and right")
# print("    Right Thumbstick Y = Tilt head")
# print("    Left/Right triggers = Left / Right Blink")
# print("    ")
# print("     - Rob Lloyd. 11/2021")
# print("    ")

### Bluetooth Controller Stuff

# # change to unique MAC address of bluetooth controller
# controllerMAC = "DD:44:63:38:84:07" 

# # joystick Deadzone size 0-255 
# deadzone = 15

# # create an object for the bluetooth control
# try:
#     controller = bt.fbox("/dev/input/event1")
# except:
#     print("Make sure the controller is connected before starting the script")
#     exit

### OPENCV stuff 
# Create a VideoCapture object
cap = cv2.VideoCapture(1)

# https://docs.opencv.org/3.4/d1/de5/classcv_1_1CascadeClassifier.html
b_cascade = cv2.CascadeClassifier("D:\dev\ServoSmoothing\code\AnimatronicHead\AnimatronicHead-Stalker\haarcascade_fullbody.xml")
f_cascade = cv2.CascadeClassifier("D:\dev\ServoSmoothing\code\AnimatronicHead\AnimatronicHead-Stalker\haarcascade_frontalface_default.xml")
# Check if camera opened successfully
if (cap.isOpened() == False): 
  print("Unable to read camera feed")
 
# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# create an object for the serial port controlling the servos
try:
    # servoData = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
    servoData = serial.Serial("COM6", 115200, timeout=1)
    print("Connected to Serial Client")
except:
    print("Serial client failed to connect")
    pass

## Functions -----------------------------------------------------------------------

def rescale(val, in_min, in_max, out_min, out_max):
    """
    Function to mimic the map() function in processing and arduino.
    """
    return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))

def generateMessage(rotation, tiltRight, tiltLeft, eyeLeft, blinkLeft, blinkRight, eyeRight):
    """

    """
    messageToSend = []
    messageToSend.append(int(rotation))
    messageToSend.append(int(tiltRight))
    messageToSend.append(int(tiltLeft))
    messageToSend.append(int(eyeLeft))
    messageToSend.append(int(blinkLeft))
    messageToSend.append(int(blinkRight))
    messageToSend.append(int(eyeRight))

    return messageToSend

def send(message_in):
    """
    Function to send a message_in made of ints, convert them to bytes and then send them over a serial port
    message length, 10 bytes.
    """
    messageLength = 7
    message = []
    for i in range(0, messageLength):
        message.append(message_in[i].to_bytes(1, 'little'))
    print("Sending: %s" % str(message_in))
    for i in range(0, messageLength):
        servoData.write(message[i])
    # print(message)

def receive(message):
    """
    Function to read whatever is presented to the serial port and print it to the console.
    Note: For future use: Currently not used in this code.
    """
    messageLength = len(message)
    last_message = []
    try:
        while servoData.in_waiting > 0:
            for i in range(0, messageLength):
                last_message.append(int.from_bytes(servoData.read(), "little"))
        print("Receiving: ", last_message)
        return last_message
    except:
        print("Failed to receive serial message")
        pass

def isEnabled(newStates, enable, estopState):
    """ 
    Function to handle enable and estop states. it was getting annoying to look at.
    """
    enable = True

    return enable

def getCentre(x, y, w, h):
    """
    Function to get the centre of a face from the object returned by a *_cascade.detectMultiScale() 
    """
    return floor(x+(w/2)), floor(y+(h/2))

def limit(num, minimum=1, maximum=255):
  """Limits input 'num' between minimum and maximum values.
  Default minimum value is 1 and maximum value is 255."""
  return max(min(num, maximum), minimum)


def main():
    # Initialise  values for enable and estop
    estopState = False
    enable = False
    # Switch so we can toggle the servos on and off
    puppet = False

    

    # instantiate dx and dy. 
    dx=127
    dy=127

    # Main Loop
    while (True):
        newMessage = []
        
        enable = True
       
        # Deal with getting a frame from the camera and detecting a face
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame")
            break
        
        if ret == True: 
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # bodies = b_cascade.detectMultiScale(gray)
            faces = f_cascade.detectMultiScale(gray, 1.3, 5)
            # print(bodies,faces)
            # print(faces)

            if len(faces) ==  1:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.drawMarker(frame, getCentre(x, y, w, h), (0, 0, 255), 0, 20, 1)

                    ### Need to convert the pixel position into servo positions really
                    ## But we can be hacky for now?

                    face_centre_x, face_centre_y = getCentre(x, y, w, h)
                    dx = math.fabs(frame_width - face_centre_x)
                    dy = math.fabs(frame_height - face_centre_y)
                    # print(dx, dy)
                        
                    # control rotation depending on x offset
                    rotation = rescale(dx, 0, frame_width, 0, 255)

                    # controlling depending on input from the camera
                    # rotateAll
                    # rotation = 127

                    # Head Up/Down  with tiltRight and tiltleft in parrallel
                    # tiltRight = 127
                    # tiltLeft = 255 - 127

                    # Control Head Up/Down  with tiltRight and tiltleft in parrallel
                    # y motion depending on y offset
                    tiltRight = 255-rescale(dy, 0, frame_height, 0, 255)
                    tiltLeft = rescale(dy, 0, frame_height, 0, 255)
                    print(rotation, tiltRight, tiltLeft) 
                    
                    tilt = 127  #tilt is a number 0-255 that represents the tilt - full left to full right
                    deadzone = 10 #pixels?
                    
                    # tilt the head with right_y and tiltRight and tiltLeft in opposition
                    if tilt >= 128 - deadzone or tilt <= 128 - deadzone:
                        tiltRight += (128 - tilt)
                        tiltLeft += (128 - tilt)

                    # eyeLeft
                    eyeLeft = 127
                    # blinkLeft
                    blinkLeft = 0
                    # blinkRight
                    blinkRight = 0
                    # eyeRight
                    eyeRight = 127

                    # Make sure we don't try and send a negative value after mixing
                    rotation = floor(limit(rotation, 1, 254))
                    tiltRight = floor(limit(tiltRight, 10, 245))
                    tiltLeft = floor(limit(tiltLeft, 10, 245))

            elif len(faces)==0:
                                # controlling depending on input from the camera
                # rotateAll
                rotation = 127

                # Head Up/Down  with tiltRight and tiltleft in parrallel
                tiltRight = 127
                tiltLeft = 255 - 127
            # eyeLeft
                eyeLeft = 127
                # blinkLeft
                blinkLeft = 0
                # blinkRight
                blinkRight = 0
                # eyeRight
                eyeRight = 127
            
            # # Build new message for the servos 
            newMessage = generateMessage(rotation, tiltRight, tiltLeft, eyeLeft, blinkLeft, blinkRight, eyeRight)     
            # print(newMessage) 
            # if puppet == True:
                # Send the new message to the servo controller (arduino) 
            send(newMessage) 
            #receive(lastMessage)                                                                    
            sleep(0.2)          # So that we don't keep spamming the Arduino....

           # Display the resulting frame    
            cv2.imshow('frame',frame)
    
            # Press Q on keyboard to stop recording
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Break the loop
        else:
            print("Can't read Viideo stream")
            break 


    
    # When everything done, release the video capture and video write objects
    cap.release()
    
    # Closes all the frames
    cv2.destroyAllWindows() 

if __name__ == "__main__":
    main()


# You know i'm reusing old code right... this might be useful for later

        #Check Enables and ESTOP
        #enable = isEnabled(newStates, enable, estopState)
        
        # # Handle the input for the raising and lowering of the tool. Don't let the tool go too high or low (0-255)
        # if newStates["dpad_y"] == -1 and toolPos < 255 - toolStep:
        #     # move up
        #     toolPos += toolStep 
        # elif newStates["dpad_y"] == 1 and toolPos > toolStep:
        #     #move down
        #     toolPos += -1 * toolStep 
        # else:
        #     print("Tool it too close to its limits")
                       
        # commandTool = rescale(toolPos, 255, 0, 100, 0)                                      # Rescale the tool position. 100 is full up, 0 is full down. 
        # commandAngle = rescale(newStates["right_x"], 0, 65535, 65, 190)                 # JC 14/04/21 65 to 190 safe wheel angles

        # Check the enable state via the function
        # if isEnabled: 
        #     # # Calculate the final inputs rescaling the absolute value to between -100 and 100
        #     # commandVel = rescale(newStates["left_y"], 65535, 0, 0, 255)                   
            
        #     # ###### THIS IS THE STUPID KINEMATIC MODEL ########
        #     # v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)
        #     # #print(v1,v2,v3,v4)

        # else:
            # commandVel = 0
            # #v1, v2, v3, v4 = calculateVelocities(vehicleLength, vehicleWidth, cmdAng, 0)
            # v1, v2, v3, v4 = calculateSimpleVelocities(commandVel)

## AND SOME MORE

 # # # hcitool check status of bluetooth devices
        # # stdoutdata = sp.getoutput("hcitool con")
        # # check bluetooth controller is connected if not then estop
        # if controllerMAC not in stdoutdata.split():
        #     print("Bluetooth device is not connected")
        #     enable = False
        #     estopState = True
        # else:
        #     enable = True
        # # Check to see if there is new input from the controller. Most of the time there isn't, so handle the error
        # try:
        #     # Save the new inputs
        #     newStates = controller.readInputs()
        # except IOError:
        #     pass

        # Do Something with the controller here -----------------------------------------------------------------

        # Simply mapping sticks to the servos
        # # rotateAll
        # rotation = newStates["left_x"]
        # # tiltRight
        # tiltRight = newStates["left_y"]
        # # tiltleft
        # tiltLeft = 255 - newStates["left_y"]
        # # eyeLeft
        # eyeLeft = newStates["right_x"]
        # # blinkLeft
        # blinkLeft = newStates["right_tr_a"]
        # # blinkRight
        # blinkRight = newStates["left_tr_a"]
        # # eyeRight
        # eyeRight = 255 - newStates["right_x"]

        # # If we press the 'a' button, the puppet control will turn on and off
        # if newStates["button_y"]:
        #     puppet = not puppet
        

        # # controlling depending on joystick values
        # # rotateAll
        # rotation = newStates["left_x"]

        # # Head Up/Down  with tiltRight and tiltleft in parrallel
        # tiltRight = newStates["left_y"]
        # tiltLeft = 255 - newStates["left_y"]

        # # tilt the head with right_y and tiltRight and tiltLeft in opposition
        # if newStates["right_y"] >= 128 - deadzone or newStates["right_y"] <= 128 - deadzone:
        #     tiltRight += (128 - newStates["right_y"])
        #     tiltLeft += (128 - newStates["right_y"])

        # # eyeLeft
        # eyeLeft = newStates["right_x"]
        # # blinkLeft
        # blinkLeft = newStates["right_tr_a"]
        # # blinkRight
        # blinkRight = newStates["left_tr_a"]
        # # eyeRight
        # eyeRight = 255 - newStates["right_x"]