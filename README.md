# MiniPatrol
Simple python script and html to control raspberry pi based robot

## Purposes
A fun project to learn Python and robotics in general. In addition, to compete in 2018 Mercury robotics at OSU.
Hope you will find it useful in learning to build a simple robot.

## Prereq
* You will need maestro.py to control the servos using pololu Micro Maestro 6-Channel USB Servo Controller. https://github.com/FRC4564/Maestro
* Script to stream webcam/IPcam

## Description
There are two files in this repo. First is the index.html file and the other one is simpleraspberrypost.py

### index.html
This is a simple UI that the driver can access using a web browser. An iframe at the top of the page can be used to hold webcam stream. The driver can control the robot movement by clicking on the buttons or typing into the textbox (WASD). The arm will be controlled by the buttons below the movement buttons.

Sensor status is displayed on top and below the movement buttons. When the sensor does not detect an obstacle in front of it, it will show "CLEAR" with a light-green background. When the sensor detects and obstacle, it will show "BLOCKED" with a red background.

### simpleraspberrypost.py
This script:
* Serve simple http server and process POST request
* Process POST request to control robot's movement and arm
* Return sensor status to UI
* Simple logic to avoid collision and auto-grab payload

## The robot
* Raspberry PI X 1
* Pololu dual motor driver DRV8833 X 1
* Pololu Micro Maestro 6-Channel USB Servo Controller X 1
* Pololu reflectance sensor QTR-1RC X 1
* Pololu Carrier with Sharp GP2Y0D815Z0F Digital Distance Sensor 15cm X 1
* Pololu Carrier with Sharp GP2Y0D810Z0F Digital Distance Sensor 10cm X 3
* Logitech C270 X 1
* Chasis and motors: 4 wheels cheap hobbyist kit from Amazon

## Installation
Copy both files to the desired folder

## Usage
Run the py script with an elevated privilege

## License
This project is licensed under the MIT License
