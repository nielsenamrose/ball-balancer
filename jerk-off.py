import cv2
import numpy as np
import math

import socket
#import sys

def calculateU(x):
    return x

def sendMessage(message):
    sock.sendto(message, server_address)
    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server_address = ('localhost', 21568)
server_address = ('203.6.152.96', 21568)
cap = cv2.VideoCapture(0)

while(1):
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.circle(frame,(320, 240), 10, (0,0,255), -1)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 13:
        hsv0 = hsv[240,320]
        lower = np.array((hsv0[0]-10,hsv0[1]-40,hsv0[2]-40))
        upper = np.array((hsv0[0]+10,255,255))
        break

print hsv0
print lower
print upper
kernel = np.ones((20,20),np.uint8)

e1 = cv2.getTickCount()
e2 = cv2.getTickCount()

t0 = cv2.getTickCount()
f = 1.0 * cv2.getTickFrequency()
    
while(1):
    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    erosion = cv2.erode(mask, kernel, iterations = 1)
    
    M = cv2.moments(erosion, True)

    if M['m00'] > 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])         
    
    cv2.circle(frame,(cx, cy), 10, (0,0,255), -1)

    cv2.imshow('frame', frame)
    #cv2.imshow('mask', mask)
    #cv2.imshow('erosion', erosion)
    
    x = 0.4*cx/640.0
    y = 0.4*(480.0 - cy)/480.0
    
    v1 = math.atan((0.24 - x)/(y + 0.05))
    v2 = math.atan((0.18 - x)/(y + 0.05))
    
    t = (cv2.getTickCount() - t0) / f
    
    print t
    v1 = math.sin(t*1*2*math.pi) * 45
    v2 = math.sin(t*1.1*2*math.pi) * 45

   
    sendMessage("E,{0:f},{1:f}".format(v1, v2))
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

sendMessage("E,{0:f},{1:f}".format(0, 0))
    
sock.close()
cap.release();
cv2.destroyAllWindows()