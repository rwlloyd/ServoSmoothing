# Animatronic head Puppet
## Setup Instructions.

### Hardware:
- Raspberry Pi 3B+ 
- Generic Bluetooth Controller (xbox style)

The sevice to read from the controller will be one of the last to start. It requires the controller to be already paired and on/connected. Then it will automatically connect at startup 

NOTE: In normal use: CONTROLLER ON AND SEARCHING BEFORE PI STARTUP.

## From a fresh Raspberry Pi OS install:

    sudo raspi-config
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt install python3-pip
    pip3 install evdev
    pip3 install pyserial

## To pair the bluetooth controller:

Power on controller in Windows mode (X+Start)  <-- This may differ depending on your controller

Start bluetooth control

    sudo bluetoothctl

Scan for devices

	scan on
	- get the mac address of the correct controller

Connect, pair and trust the controller. You may need to agree to the pair command

	connect XX:XX:XX:XX:XX:XX
	pair XX:XX:XX:XX:XX:XX
	trust XX:XX:XX:XX:XX:XX

Leave bluetooth control. 

	exit

NOTE: TAB autocomplete will work with the mac addresses ;)

## To add a service and make it run on startup

sudo nano /etc/systemd/system/remoteControl.service


    [Unit]
    Description=Service for Bluetooth Remote Control
    After=getty.target

    [Service]
    ExecStart=python3 main.py
    WorkingDirectory=/home/pi/ServoSmoothing/code/AnimatronicHead/AnimatronicHead-Puppet/
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=pi

    [Install]
    WantedBy=multi-user.target

Make the service executable

    sudo chmod a+r /etc/systemd/system/remoteControl.service

Reload the services

    sudo systemctl daemon-reload

Start the service for the first time

    sudo systemctl start remoteControl.service

Check everything is working. Then stop the service. 

To tail the command line output of the service, run ```journalctl -f -u remoteControl.service```

    sudo systemctl stop remoteControl.service

After manually starting and stopping the service successfully, we can enable it to start automagically.

    sudo systemctl enable remoteControl.service

Reboot and get ready for that sweet delayed gratification.

    sudo reboot

## Everything should work

The main effort here is making sure the bluetooth connection is happy, it's the bit that always causes me headaches anyway. especially with these cheap, no-name controllers.

To help debug:

    sudo systemctl status remoteControl.service

To tail the cmd line output of the service...

    journalctl -f -u remoteControl.service 
