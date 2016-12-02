import numpy as np
import cv2

u = 2.217020111083984375e+02	
v = 1.478026123046875000e+02

u = 4.457016906738281250e+02	
v = 3.456819458007812500e+02


def uv_to_3d(u, v, A, rvec, t):
    R, _ = cv2.Rodrigues(rvec)
    Ru = np.identity(4)
    z = 0.0
    T = np.array([[1,0,0],[0,1,0],[0,0,z],[0,0,1]], np.float32)
    H = A.dot(np.hstack((R,t))).dot(Ru).dot(T)
    m = np.array([[u,v,1.0]]).T 
    x = np.linalg.solve(H, m) 
    x = x / x[2,0]
    print x

#M =  np.linalg.inv(np.hstack((R[:,0:2],tvecs[0]))).dot(np.linalg.inv(mtx)).dot(m)
#M /= M[2,0]

uv_to_3d(u, v, mtx, rvecs[0], tvecs[0])