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

degneg45_u = [1582, 1516]
deg45_u = [3777, 3626]

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
    return float(f.readline())
    
def setperiod(path, period):
    setvalue(path+"/period", period)    
    
def setenable(path):
    setvalue(path+"/enable", 1)
    
def setdutycycle(path, dutycycle):
    setvalue(path+"/duty_cycle", dutycycle)

def setangle(pwmpath, angle):
    duty = calculateduty(angle)
    setdutycycle(pwmpath, duty)

    
servo_index = int(sys.argv[1])
angle = float(sys.argv[2])

pwmpath = pwmpaths[servo_index]
adcpath = adcpaths[servo_index]
u_min = degneg45_u[servo_index]
u_max = deg45_u[servo_index]

setperiod(pwmpath, 20000000)
setangle(pwmpath, math.radians(angle))
setenable(pwmpath)

t0 = time.time()
n = 0
u_sum = 0.0

for i in range(1000):
    u = readvalue(adcpath)
    u_sum += u
    actual = (u - u_min)/(u_max - u_min) * 90.0 - 45.0 
    print time.time() - t0, u, actual
    
print u_sum / n