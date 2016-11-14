import cv2
import numpy as np

import socket
#import sys

def calculateU(x):
    return x

def sendMessage(message):
    sock.sendto(message, server_address)
    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 21568)
#server_address = ('203.6.152.96', 21567)
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
    x = (cx - 320, cy - 240)
    u = calculateU(x)
    sendMessage("E,{0:f},{1:f}".format(u[0], u[1]))
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

sock.close()
cap.release();
cv2.destroyAllWindows()