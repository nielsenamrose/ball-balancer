# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 08:12:25 2016

@author: christian
"""

import socket
import math

pwmpath = ["/sys/class/pwm/pwmchip0/pwm0",
	   "/sys/class/pwm/pwmchip0/pwm1"]

pwmenabled = [ False, False ]

L1 = 23.93
L2 = 27.50
L3 = 87.68
L4 = 26.11
L5 = 63.73

v_min = -10.0 #deg
v_max = 10.0 #deg

def angle_to_q(v):
    Bx = L5 - L3*math.cos(v)
    By = L4 - L3*math.sin(v)
    alpha = math.atan2(By,Bx)
    d_sq = Bx*Bx + By*By
    d = math.sqrt(d_sq)
    if d < (L1+L2):
        beta = math.acos((L1*L1 + d_sq - L2*L2)/(2.0*L1*d))
    else:
        beta = 0
    q = beta + alpha - math.pi
    return q

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

while True:
    data,addr = UDPSock.recvfrom(1024)
    print data.strip(),addr
    split = data.split(",")
    for i in [0 ,1]:
        v = float(split[i+1])
        if (v < v_min):
            print "Warning angle {0} below limit {1}".format(v, v_min)
            v = v_min
        elif (v > v_max):
            print "Warning angle {0} above limit {1}".format(v, v_max)
            v = v_max
        q = angle_to_q(math.radians(v))
        if not pwmenabled[i]:
            startpwm(pwmpath[i], 20000000)
            pwmenabled[i] = True
        setangle(pwmpath[i], q)d
