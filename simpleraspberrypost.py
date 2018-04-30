#!/usr/bin/env python

#-------------------------------------------------------------------------------------------------------
#
# Author: Jonathan Marpaung
# Description: Simple python script to manage motors, IR sensors, servos, and serve http
# Purpose: To remotely control MiniPatrol robot for OSU Mercury 2018 Competition
# Version: 1.0
# License: MIT License
#
#-------------------------------------------------------------------------------------------------------

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import urlparse, json
import time, sys
import sys
import RPi.GPIO as GPIO
import termios, sys, os
import threading
import maestro #this is the pololu maestro python script

#set gpio mode to board (printed on the board) instead of bcm (broadcom soc channel)
GPIO.setmode(GPIO.BOARD)

#setup motor inputs
GPIO.setup(12,GPIO.OUT)   #Left motor input A
GPIO.setup(15,GPIO.OUT)   #Left motor input B
GPIO.setup(11,GPIO.OUT)  #Left motor input A
GPIO.setup(13,GPIO.OUT)  #Left motor input B
GPIO.setup(40,GPIO.OUT)   #Right motor input A
GPIO.setup(38,GPIO.OUT)   #Right motor input B
GPIO.setup(37,GPIO.OUT)  #Right motor input A
GPIO.setup(36,GPIO.OUT)  #Right motor input B
GPIO.setwarnings(False)

#not used why is this here
TERMIOS = termios

IRPIN = 8 #robot arm IR distance sensor. assumes you've connected the IR Out wire to GPIO4. This sensor has to be charged first.

IRPIN1 = 7 #front middle distance sensor GPIO4
GPIO.setup(IRPIN1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set pin to pull down to ground 0v

IRPIN2 = 35 #front right distance sensor GPIO13
GPIO.setup(IRPIN2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set pin to pull down to ground 0v

IRPIN3 = 33 #front left distance sensor GPIO19
GPIO.setup(IRPIN3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set pin to pull down to ground 0v

IRPIN4 = 31 #back middle distance sensor GPIO6
GPIO.setup(IRPIN4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # set pin to pull down to ground 0v

servo = maestro.Controller()
servo.setAccel(0,150)      #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. Horizontal servo.
servo.setAccel(1,150)      #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. Vertical servo.
servo.setAccel(2,150)      #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. Gripper servo.
servo.setAccel(3,150)      #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. Reserved for gripper pivot.
servo.setAccel(4,0)        #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. Backup not in use.
servo.setAccel(5,0)        #set servo Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start. WIFI connection flag.

#start simple http server
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        f = open("index.html", "r")
        self.wfile.write(f.read())

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # POST data from browser will go here
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self._set_headers() #set header using function above
		
        print post_data #make sure we're getting data

        # call function based on POST data
        if post_data == 'k=w':
			robotkey = getkey('w') #forward
        elif post_data == 'k=a':
			robotkey = getkey('a') #left
        elif post_data == 'k=s':
			robotkey = getkey('s') #reverse
        elif post_data == 'k=d':
			robotkey = getkey('d') #right
        elif post_data == 'k=q':
            robotkey = getkey('q') #hard left
        elif post_data == 'k=e':
            robotkey = getkey('e') #hard right
        elif post_data == 'k=0':
            osensorstatus = irsensorstatus()
            self.wfile.write(osensorstatus) #return all sensor status
        elif post_data == 'k=o':
            servostat = servoarmreset() #reset arm
        elif post_data == 'k=l':
            servostat = servoarmup() #arm up
        elif post_data == 'k=k':
            servostat = servoarmdown() #arm down
        elif post_data == 'k=p':
            servostat = servoautograb() #autograb
        else:
            pass

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

def getkey(strcomp):

	if strcomp == 'w': #forward
	
		sensor_stat = irsensorfrontmiddle() #call the function for front middle sensor and get the output to sensor_stat
		sensor_stat1 = irsensorfrontleft() #call the function for front left sensor and get the output sensor_stat1
		sensor_stat2 = irsensorfrontright() #call the function for front right sensor and get the output sensor_stat2
		
		if sensor_stat == '1' and sensor_stat1 == '1' and sensor_stat2 == '1':
		
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			motor_stat = irsensorforwardrun() #call the function that will dictate how long the motor will run and do collision detection
			
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			motor_stat2 = irsensorforwardstop() #call the function that will do collision detection after the motor is turned off
			
		else:
			pass
			
	elif strcomp == 's': #reverse
	
		sensor_stat = irsensorbackmiddle() #call the function for back middle sensor and get the output sensor_stat
		print sensor_stat
		
		if sensor_stat == '1':
		
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,1) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,1) #Rear Left motor input B
			GPIO.output(37,1) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,1) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			motor_stat = irsensorreverserun() #call the function that will dictate how long the motor will run and do collision detection
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			motor_stat2 = irsensorreversestop() #call the function for back middle sensor and get the output sensor_stat
			
		else:
			pass
	
	elif strcomp == 'a': #left
	
		sensor_stat = irsensorfrontleft() #call the function for front left sensor and get the output sensor_stat
		print sensor_stat
		
		if sensor_stat == '1':
		
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			motor_stat = irsensorleftrun()
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
		
		else:
			pass
	
	elif strcomp == 'd': #right
	
		sensor_stat = irsensorfrontright() #call the function for front middle sensor and get the output sensor_stat
		print sensor_stat
		
		if sensor_stat == '1':
		
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			motor_stat = irsensorrightrun()
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
		
		else:
			pass
	
	elif strcomp == 'q': #hard left
	
		sensor_stat = irsensorfrontleft() #call the function for front middle sensor and get the output sensor_stat
		print sensor_stat
		
		if sensor_stat == '1':
		
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,1) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,1) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			motor_stat = irsensorleftrun()
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
		
		else:
			pass
	
	elif strcomp == 'e': #hard right
		
		sensor_stat = irsensorfrontright() #call the function for front middle sensor and get the output sensor_stat
		print sensor_stat
		
		if sensor_stat == '1':
		
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,1) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,1) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			motor_stat = irsensorrightrun()
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
		
		else:
			pass
	
	else:
		pass
	return 1

def irsensorstatus(): #function to get all value from IR sensors
    irmiddle = str(GPIO.input(IRPIN1))
    irright = str(GPIO.input(IRPIN2))
    irleft = str(GPIO.input(IRPIN3))
    irback = str(GPIO.input(IRPIN4))
    irall = irmiddle + '' + irright + '' + irleft + '' + irback
    return irall
	
def irsensorfrontmiddle(): #function to get value from IR sensor
    return str(GPIO.input(IRPIN1))

def irsensorfrontright(): #function to get value from IR sensor
    return str(GPIO.input(IRPIN2))

def irsensorfrontleft(): #function to get value from IR sensor
    return str(GPIO.input(IRPIN3))

def irsensorbackmiddle(): #function to get value from IR sensor
    return str(GPIO.input(IRPIN4))

def irsensorforwardrun(): #function to get value from IR sensor
	t_end = time.time() + 0.5 #how long will the motor run - 0.5 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN1)) == "0" or str(GPIO.input(IRPIN2)) == "0" or str(GPIO.input(IRPIN3)) == "0": #quick reverse and stop when a sensor(s) tripped
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,1) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,1) #Rear Left motor input B
			GPIO.output(37,1) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,1) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			print "close"
		else:
			pass
		time.sleep(.01)

def irsensorforwardstop(): #function to get value from IR sensor
	t_end = time.time() + 0.25 #how long will the motor run - 0.25 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN1)) == "0" or str(GPIO.input(IRPIN2)) == "0" or str(GPIO.input(IRPIN3)) == "0": #quick reverse and stop when a sensor(s) tripped
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,1) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,1) #Rear Left motor input B
			GPIO.output(37,1) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,1) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			print "close"
		else:
			pass
		time.sleep(.01)
	
def irsensorreverserun(): #function to get value from IR sensor
	t_end = time.time() + 0.5 #how long will the motor run - 0.5 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN4)) == "0": #quick forward and stop when a sensor(s) tripped
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			print "close"
		else:
			pass
		time.sleep(.01)

def irsensorreversestop(): #function to get value from IR sensor
	t_end = time.time() + 0.25 #how long will the motor run - 0.25 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN4)) == "0": #quick forward and stop when a sensor(s) tripped
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			print "close"
		else:
			pass
		time.sleep(.01)
		
def irsensorleftrun(): #function to get value from IR sensor
	t_end = time.time() + 0.1 #how long will the motor run - 0.1 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN3)) == "0": #quick right and stop when a sensor(s) tripped
		
			GPIO.output(12,1) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,1) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			
			print "close"
		else:
			pass
		time.sleep(.01)
		
def irsensorrightrun(): #function to get value from IR sensor
	t_end = time.time() + 0.1 #how long will the motor run - 0.1 second
	while time.time() < t_end:
		if str(GPIO.input(IRPIN2)) == "0": #quick left and stop when a sensor(s) tripped
		
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,1) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,1) #Rear Right motor input B
			time.sleep(.05)
			
			GPIO.output(12,0) #Front Left motor input A
			GPIO.output(15,0) #Front Left motor input B
			GPIO.output(11,0) #Rear Left motor input A
			GPIO.output(13,0) #Rear Left motor input B
			GPIO.output(37,0) #Front Right motor input A
			GPIO.output(36,0) #Front Right motor input B
			GPIO.output(40,0) #Rear Right motor input A
			GPIO.output(38,0) #Rear Right motor input B
			
			print "close"
		else:
			pass
		time.sleep(.01)

def irsensor1(): #function to get value from the IR sensor on the arm. Once it finds an object, the arm will grab it.
    GPIO.setup(IRPIN, GPIO.OUT) #set pin to an output
    GPIO.output(IRPIN, GPIO.HIGH) #charge sensor
    time.sleep(0.01) #charge the sensor for 0.01 sec - you can set it higher if the reading is too erratic
    pulse_start = time.time() #start the count
    GPIO.setup(IRPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # pull pin to 0V
    while GPIO.input(IRPIN)> 0:
        pass #repeat until its 0V
    if  GPIO.input(IRPIN)==0:
        pulse_end = time.time() #stop count when it hits zero
    pulse_duration = pulse_end - pulse_start
    print "duration:", pulse_duration #debug purposes
    if pulse_duration > 0.0005: #0.0005 works for me - you might have to change yours
        sensor_stat = "NO"
    else:
        sensor_stat = "YES"
    return sensor_stat

def servoarmup(): #function to get get the robot arm up
    servo.setTarget(1,3500)  #vertical servo up
    time.sleep(1)
    return 1

def servoarmdown(): #function to get get the robot arm down
    servo.setTarget(1,7200)  #vertical servo down
    time.sleep(1)
    return 1
	
def servoarmreset(): #function to reset servo arm
    servo.setTarget(2,9000)  #set gripper servo to open position
    time.sleep(1)
	servo.setTarget(0,5500)  #set horizontal servo to move to off-center position
    time.sleep(1)
    servo.setTarget(1,7300)  #set vertical servo to move to floating position
    time.sleep(1)
    return 1

def servoautograb(): #function to get auto grab payload
    servo.setTarget(0,4000)  #set servo to move to off center position
    time.sleep(1)
    servo.setTarget(1,6000)  #set servo to move to float position
    time.sleep(1)
    servo.setTarget(2,9000)  #grab
    time.sleep(1)
	
    flag = 1
	
    while flag == 1:
	
		sensor_stat = irsensor1() #call the function and get the output sensor_stat
		print sensor_stat
		#get current servo 0 position
		servoposition0 = servo.getPosition(0)
		print servoposition0
		if sensor_stat == "NO":
			if servoposition0 == 0:
				servo.setTarget(0,5000)  #set servo to move to off center position
				print "set to center"
				time.sleep(1) #pause for 1 second before repeating, use ctrl+\ to stop
			else:
				servopositionnew = servoposition0 + 200
				if servopositionnew < 7000:
					servo.setTarget(0,servopositionnew)  #set servo to move to center position
					print "set to new position"
					time.sleep(1) #pause for 1 second before repeating, use ctrl+\ to stop
				else:
					print "end of line - not found"
					flag = 0
					time.sleep(1) #pause for 1 second before repeating, use ctrl+\ to stop
		else:
			servoposition0 = servo.getPosition(0)
			servopositionnew = servoposition0 + 600
			servo.setTarget(0,servopositionnew)  #set servo to move to grab position
			time.sleep(2)
			servo.setTarget(1,7500)  #lower arm
			time.sleep(2)
			servo.setTarget(2,5700)  #grab
			time.sleep(2)
			servo.setTarget(1,6000)  #raise arm
			time.sleep(1)
			servo.setTarget(0,5500)  #set servo to move to off center position
			time.sleep(1)
			print "grab"
			flag = 0
			time.sleep(1) #pause for 1 second before repeating, use ctrl+\ to stop
	
    return 1

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
		run()