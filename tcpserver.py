# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 15:56:06 2017

@author: christian
"""

import SocketServer

pwmpaths = ["/sys/class/pwm/pwmchip0/pwm0",
            "/sys/class/pwm/pwmchip0/pwm1"]
    
adcpaths = ["/sys/bus/iio/devices/iio:device0/in_voltage1_raw",
            "/sys/bus/iio/devices/iio:device0/in_voltage0_raw"]

#pwmpaths = ["d:/temp/pwm0",
#            "d:/temp/pwm1"]
#    
#adcpaths = ["d:/temp/in_voltage1_raw", 
#            "d:/temp/in_voltage0_raw"]

degneg45_u = [1580.698, 1513.921]
deg45_u = [3776.617, 3626.202]

def clamp(minx, maxx, x):
    if (x < minx):
        return minx
    elif (x > maxx):
        return maxx
    else:
        return x

def calculateduty(v):
    duty = int((v*4.0 / 180.0) * 600000 + 1500000)
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

def setangle(servo_index, angle):
    duty = calculateduty(angle)
    setdutycycle(pwmpaths[servo_index], duty)

def readangle(servo_index):
    u_min = degneg45_u[servo_index]
    u_max = deg45_u[servo_index]
    u = float(readvalue(adcpaths[servo_index]))
    return (u - u_min)/(u_max - u_min)*90.0 - 45.0

class RequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).strip()
        split = data.split(",")
        command = split[0].lower()
        response = "ack"
        if (command == "s"):
            setangle(0, float(split[1]))
            setangle(1, float(split[2]))            
        elif (command == "r"):
            v1, v2 = readangle(0), readangle(1)
            response = "{0},{1}".format(v1, v2)
        self.request.sendall(response)
        print "{0}: {1} => {2}".format(self.client_address[0], data, response)

if __name__ == "__main__":
    for i in range(2):
        setperiod(pwmpaths[i], 20000000)
        setangle(i, readangle(i))
        setenable(pwmpaths[i])

    HOST, PORT = "", 21568
    server = SocketServer.TCPServer((HOST, PORT), RequestHandler)
    server.serve_forever()