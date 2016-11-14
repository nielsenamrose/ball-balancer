# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 08:12:25 2016

@author: christian
"""

import socket

pwm0path = "/sys/class/pwm/pwmchip0/pwm0"
pwm1path = "/sys/class/pwm/pwmchip0/pwm1"

def clamp(minx, maxx, x):
    if (x < minx):
        return minx
    elif (x > maxx):
        return maxx
    else:
        return x

def calculateduty(v):
    duty = int((v / 45) * 600000 + 1500000)
    return clamp(900000, 2100000, duty)

def setvalue(path, value):
    f = open(path,"w")   
    f.write(str(value))
    
def startpwm(path, period):
    setvalue(path+"/period", period)    
    setvalue(path+"/enable", 1)
    
def setdutycycle(path, dutycycle):
    setvalue(path+"/duty_cycle", dutycycle)

def setangle(pwmpath, angle):
    duty = calculateduty(angle)
    setdutycycle(pwmpath, duty)

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",21568)
UDPSock.bind(listen_addr)
print "Server listening on {0}".format(listen_addr)
pwmenabled = False

while True:
    data,addr = UDPSock.recvfrom(1024)
    print data.strip(),addr
    split = data.split(",")
    q1 = float(split[1])
    q2 = float(split[2])
    setangle(pwm0path, q1)
    setangle(pwm1path, q2)
    if not pwmenabled:
        startpwm(pwm0path, 20000000)
        startpwm(pwm1path, 20000000)
        pwmenabled = True
