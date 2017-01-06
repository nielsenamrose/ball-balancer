import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):
    ok, frame = cap.read()
    
    if ok:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.circle(frame,(320, 240), 10, (0,0,255), -1)
        cv2.imshow('frame',frame)        
        k = cv2.waitKey(1) & 0xFF        
        if k == 13:
            hsv0 = hsv[240,320]
            print hsv0
            break
    else:
        print "Failded to capture frame"
        break

    
cap.release()
cv2.destroyAllWindows()
