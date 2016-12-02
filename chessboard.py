import socket
import numpy as np
import cv2

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = (np.mgrid[0:7,0:7].T.reshape(-1,2) - 3)*0.208/8.0  

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

cap = cv2.VideoCapture(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('203.6.152.96', 21568)

def set_orientation(v1, v2):
    sock.sendto("E,{0:f},{1:f}".format(v1, v2), server_address)
    cv2.waitKey(3000)

for i in range(5):
    v1 = i * 20.0/4 - 10.0
    for j in range(5):
        v2 = j * 20.0/4 - 10.0
        
        set_orientation(v1, v2)
        
        _, img = cap.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7,7),None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
    
            cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners)
    
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (7,7), corners,ret)
            cv2.imshow('img',img)
        else:
            print "Failed to find chessboard"
            
set_orientation(0, 0)
#
#
_, img = cap.read()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

coord = np.float32([(0,0,0),(0.100,0,0),(0,0.100,0),(0,0,0.100)])
p,_ = cv2.projectPoints(coord, rvecs[12], tvecs[12], mtx, dist)
p = p.reshape(-1,2)
print p
cv2.line(img,tuple(p[0]),tuple(p[1]),(0,0,255),2)
cv2.line(img,tuple(p[0]),tuple(p[2]),(0,255,0),2)
cv2.line(img,tuple(p[0]),tuple(p[3]),(255,0,0),2)

cv2.imshow('img',img)
cv2.waitKey(100000)
cv2.destroyAllWindows()
cap.release()