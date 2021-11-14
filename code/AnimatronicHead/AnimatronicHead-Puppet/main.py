#!/usr/bin/env python3

"""
Current status

still mashing 
"""


import serial
import math
from time import sleep
import fbox as bt
import subprocess as sp

print("   ----------------------------------------------------------")
print("    Animatronic Head Puppet with Generic Bluetooth Controller")
print("   ----------------------------------------------------------")
print("    Button A = Enable/Disable")
print("    Left Thumbstick X = Rotation")
print("    Left Thumbstick Y = Pitch")
print("    Right Thumbstick X = Eyes left and right")
print("    Right Thumbstick Y = Tilt head")
print("    Left/Right triggers = Left / Right Blink")
print("    ")
print("     - Rob Lloyd. 11/2021")
print("    ")
# change to unique MAC address of bluetooth controller
controllerMAC = "DD:44:63:38:84:07" 

# joystick Deadzone size 0-255 
deadzone = 15

# create an object for the bluetooth control
try:
    controller = bt.fbox("/dev/input/event1")
except:
    print("Make sure the controller is connected before starting the script")
    exit

# create an object for the serial port controlling the curtis units
try:
    servoData = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
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
        while arduinoData.in_waiting > 0:
            for i in range(0, messageLength):
                last_message.append(int.from_bytes(arduinoData.read(), "little"))
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
    # # to reset after estop left and right bumper buttons - press together to cancel estop
    # if newStates["trigger_l_1"] == 1 and newStates["trigger_r_1"] == 1:
    #     estopState = False

    # # left and right joystick buttons trigger estop
    # if newStates["button_left_xy"] == 1 or newStates["button_right_xy"] == 1:
    #     estopState = True 
    
    # if estopState == True:
    #     enable = False #ok
    # print(newStates["trigger_l_1"])
    # # dead mans switch left or right trigger button
    # if newStates["trigger_l_2"] >= 1 or newStates["trigger_r_2"] >= 1:
    #     if estopState == False:
    #         enable = True
    # else:
    #     enable = False

    return enable

# def calculateSimpleVelocities(inputVel: float):
#     velocity = rescale(inputVel, 0, 255, -100, 100)
#     v1 = velocity
#     v2 = velocity
#     v3 = velocity
#     v4 = velocity

#     return v1, v2, v3, v4

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

    # Seems to be necessary to have a placeholder for the message here
    last_message = []

    # Main Loop
    while True:
        newMessage = []
        # hcitool check status of bluetooth devices
        stdoutdata = sp.getoutput("hcitool con")
        # check bluetooth controller is connected if not then estop
        if controllerMAC not in stdoutdata.split():
            print("Bluetooth device is not connected")
            enable = False
            estopState = True
        else:
            enable = True
        # Check to see if there is new input from the controller. Most of the time there isn't, so handle the error
        try:
            # Save the new inputs
            newStates = controller.readInputs()
        except IOError:
            pass

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

        # If we press the 'a' button, the puppet control will turn on and off
        if newStates["button_y"]:
            puppet = not puppet
        

        # controlling depending on joystick values
        # rotateAll
        rotation = newStates["left_x"]

        # Head Up/Down  with tiltRight and tiltleft in parrallel
        tiltRight = newStates["left_y"]
        tiltLeft = 255 - newStates["left_y"]

        # tilt the head with right_y and tiltRight and tiltLeft in opposition
        if newStates["right_y"] >= 128 - deadzone or newStates["right_y"] <= 128 - deadzone:
            tiltRight += (128 - newStates["right_y"])
            tiltLeft += (128 - newStates["right_y"])

        # eyeLeft
        eyeLeft = newStates["right_x"]
        # blinkLeft
        blinkLeft = newStates["right_tr_a"]
        # blinkRight
        blinkRight = newStates["left_tr_a"]
        # eyeRight
        eyeRight = 255 - newStates["right_x"]

        # Make sure we don't try and send a negative value after mixing
        rotation = limit(rotation, 1, 254)
        tiltRight = limit(tiltRight, 10, 245)
        tiltLeft = limit(tiltLeft, 10, 245)

        # # Build new message for the servos 
        newMessage = generateMessage(rotation, tiltRight, tiltLeft, eyeLeft, blinkLeft, blinkRight, eyeRight)     
        # print(newMessage) 
        if puppet == True:
            # Send the new message to the servo controller (arduino) 
            send(newMessage)                                                                     
            # sleep(0.2)          # So that we don't keep spamming the Arduino....

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