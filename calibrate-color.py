import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.circle(frame,(320, 240), 10, (0,0,255), -1)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 13:
        hsv0 = hsv[240,320]
        break

print hsv0
    
cap.release();
cv2.destroyAllWindows()