# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 08:08:43 2016

@author: christian
"""
import cv2
import numpy as np

kernel = np.ones((10,10), np.uint8)

cap = cv2.VideoCapture(0)

fgbg = cv2.BackgroundSubtractorMOG()

d = 0

while(1):
    ret, frame = cap.read()
    frame = frame[100:370,:]
    fgmask = fgbg.apply(frame)
    erosion = cv2.erode(fgmask, kernel, iterations = 1)
    cv2.imshow('frame',frame)
    cv2.imshow('erosion',erosion)
    m = cv2.moments(erosion)
    if (m['m00'] > 0):
        d = d + 1
        print d
        if d > 3:
            print 'Motion detected'
            break
    else:
        d = 0
    key = cv2.waitKey(30) & 0xFF
    if key != 255:
        break 
    
cv2.destroyAllWindows()
cap.release()