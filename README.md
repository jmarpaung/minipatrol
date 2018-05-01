# MiniPatrol
Simple python script and html to control raspberry pi based robot

## Purposes
A fun project to learn Python and robotics in general. In addition, to compete in 2018 Mercury robotics at OSU.

## Description
There are two files in this repo. First is the index.html file and the other one is simpleraspberrypost.py

### index.html
This is a simple UI that the driver can access using a web browser. An iframe at the top of the page can be used to hold webcam stream. The driver can control the robot movement by clicking on the buttons or typing into the textbox (WASD). The arm will be controlled by the buttons below the movement buttons.

Sensor status is displayed on top and below the movement buttons. When the sensor doesn't detect an obstacle in front of it, it will show "CLEAR" with a light-green background. When the sensor detects and obstacle, it will show "BLOCKED" with a red background.

### simpleraspberrypost.py


## The robot
* Raspberry PI
* Pololu dual motor driver DRV8833
* Pololu Micro Maestro 6-Channel USB Servo Controller
* Pololu reflectance sensor QTR-1RC 
* Pololu Carrier with Sharp GP2Y0D815Z0F Digital Distance Sensor 15cm
* Logitech C270

## Installation
Copy both files to desired folder

## Usage
Run the py script with an elevated privilage

## License
This project is licensed under the MIT License
