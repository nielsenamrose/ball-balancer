# -*- coding: utf-8 -*-
"""
Created on Sun Jan 08 15:49:15 2017

@author: Christian
"""

import math
import sys
import time

pwmpaths = ["/sys/class/pwm/pwmchip0/pwm0",
	   "/sys/class/pwm/pwmchip0/pwm1"]
    
adcpaths = ["/sys/bus/iio/devices/iio:device0/in_voltage1_raw",
"/sys/bus/iio/devices/iio:device0/in_voltage0_raw"]

#pwmpaths = ["c:/temp/pwm0",
#	   "c:/temp/pwm1"]
#    
#adcpaths = ["c:/temp/in_voltage0_raw"]

def clamp(minx, maxx, x):
    if (x < minx):
        return minx
    elif (x > maxx):
        return maxx
    else:
        return x

def calculateduty(v):
    duty = int((v*4.0 / math.pi) * 600000 + 1500000)
    return clamp(900000, 2100000, duty)

def setvalue(path, value):
    f = open(path,"w")   
    f.write(str(value))
   
def readvalue(path):
    f = open(path,"r")   
    return int(f.readline())
    
def setperiod(path, period):
    setvalue(path+"/period", period)    
    
def setenable(path):
    setvalue(path+"/enable", 1)
    
def setdutycycle(path, dutycycle):
    setvalue(path+"/duty_cycle", dutycycle)

def setangle(pwmpath, angle):
    duty = calculateduty(angle)
    setdutycycle(pwmpath, duty)

def readvoltage(adcpath):
    return readvalue()
    
servo_index = int(sys.argv[1])
angle = float(sys.argv[2])

pwmpath = pwmpaths[servo_index]
adcpath = adcpaths[servo_index]

setperiod(pwmpath, 20000000)
setangle(pwmpath, math.radians(angle))
setenable(pwmpath)

t0 = time.time()

for i in range(1000):
    print time.time() - t0 + "," + readvalue(adcpath)
    