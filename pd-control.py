import cv2
import numpy as np
import socket
import matplotlib.pyplot as plt
import math
from collections import deque
import datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('203.6.152.96', 21568)

# Ball

rB = 0.03952/2.0

# Vision

cap = cv2.VideoCapture(0)

hsv0 = [ 12, 184, 217]
lower = np.array((hsv0[0]-10, hsv0[1]-40, hsv0[2]-40))
upper = np.array((hsv0[0]+10, 255, 255))

kernel = np.ones((10,10), np.uint8)

t0 = cv2.getTickCount()
f = 1.0 * cv2.getTickFrequency()
t = t_old = 0.0
t_series = deque([])

T = np.array([[0.45/640.0,          0, -0.225],
             [       0.0, -0.45/480.0,  0.225],
             [       0.0,        0.0,    1]])


# Estimator

g = 9.82

Kp = np.array([[0.33, 0.0],
               [0.0, 0.33],
               [0.33, 0.0],
               [0.0, 0.33]])

H = np.array([[ 1.0, 0.0, 0.0, 0.0],
              [ 0.0, 1.0, 0.0, 0.0]])

x_hat_min = np.array([-0.225, -0.225, -1.0, -1.0])
x_hat_max = np.array([0.225, 0.225, 1.0, 1.0])

x_hat = np.array([0.0, 0.0, 0.0, 0.0])
x_hat_series = deque([])

# Controller

K = np.array([[ 80.0, 0.0, 33.0, 0.0],
              [ 0.0, -80.0, 0.0, -33.0]]) 

w = np.array([0.0, 0.0, 0.0, 0.0]) # set point
e_series = deque([])
u = np.array([0.0, 0.0])
u_series = deque([])

def detect_motion():
    cv2.waitKey(1000)
    ret, frame = cap.read()
    fgbg = cv2.BackgroundSubtractorMOG()
    d = 0
    while(1):
        ret, frame = cap.read()
        frame = frame[50:370,:]
        fgmask = fgbg.apply(frame)
        erosion = cv2.erode(fgmask, kernel, iterations = 1)
        cv2.imshow('frame',frame)
        #cv2.imshow('erosion',erosion)
        m = cv2.moments(erosion)
        if (m['m00'] > 0):
            d = d + 1
            print d
            if d > 2:
                print 'Motion detected'
                break
        else:
            d = 0
        key = cv2.waitKey(30) & 0xFF
        if key != 255:
            break

def uv_to_3d(u, v, A, rvec, t):
    R, _ = cv2.Rodrigues(rvec)
    Ru = np.identity(4)
    T = np.array([[1,0,0],[0,1,0],[0,0,-rB],[0,0,1]], np.float32)
    H = A.dot(np.hstack((R,t))).dot(Ru).dot(T)
    m = np.array([[u,v,1.0]]).T 
    x = np.linalg.solve(H, m) 
    x = x / x[2,0]
    return x[0:2]
    
def xy_to_uv(z, A, rvec, t):
    R, _ = cv2.Rodrigues(rvec)
    Ru = np.identity(4)
    H = A.dot(np.hstack((R,t))).dot(Ru)
    m = H.dot(np.array([[z[0],z[1],0.0,1.0]]).T)
    return m[0:2]/m[2,0] 
    
def set_orientation(u):
    sock.sendto("E,{0:f},{1:f}".format(u[0], u[1]), server_address)
    #sock.sendto("E,{0:f},{1:f}".format(0, 0), server_address)
    
def get_time():
    return (cv2.getTickCount() - t0) / f

def step(w):
    global t
    global t_old
    global u
    global x_hat
        
    # Vision
    
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    erosion = cv2.erode(mask, kernel, iterations = 1)
    M = cv2.moments(erosion, True)

    t = get_time()
    dt = t - t_old
    t_series.append(t)
    
    # Estimator
    
    x_hat[0] += dt*x_hat[2] 
    x_hat[1] += dt*x_hat[3]
    x_hat[2] += -dt*3.0*g*math.sin(math.radians(u[0]))/5.0
    x_hat[3] += dt*3.0*g*math.sin(math.radians(u[1]))/5.0
    
    if M['m00'] <= 0:
        z = np.matmul(H, x_hat)# + np.array([np.random.normal()*0.01, np.random.normal()*0.01])
    
    else:
        c = np.array([M['m10']/M['m00'], M['m01']/M['m00'], 1.0])
        z = uv_to_3d(c[0], c[1], mtx, rvecs[12], tvecs[12]).ravel()
        #print z
        #z = np.matmul(T, c)[0:2]
        cv2.circle(frame, (int(c[0]), int(c[1])), 10, (0, 0, 255), -1)
        
    z_tilt = z - np.matmul(H, x_hat)
    print z
    Kdt = np.diag([1.0, 1.0, 1.0/dt, 1.0/dt])
    Kp_dt = np.matmul(Kdt, Kp)
    x_hat = np.matmul(Kp_dt, z_tilt) + x_hat
    x_hat = np.clip(x_hat, x_hat_min, x_hat_max)
    x_hat_series.append(x_hat)
    
    # Controller    
    e = x_hat - w 
    #print e, np.linalg.norm(e)
    e_series.append(e)
    
    u = np.matmul(K, e)
    u = np.clip(u, -10.0, 10.0)
    u_series.append(u)        

    #print t, x_hat, u
    set_orientation(u)
    
    t_old = t
    
    if len(t_series) > 2500:
        t_series.popleft()
        x_hat_series.popleft()
        e_series.popleft()
        u_series.popleft()

    
    cv2.circle(frame, tuple(xy_to_uv(x_hat[0:2], mtx, rvecs[12], tvecs[12])), 3, (0, 255, 0), -1)
    cv2.imshow('frame', frame)
    
    return np.linalg.norm(e)

def goto(x_start, x_end, speed = 0, tolerance = None):
    global t
    distance = np.linalg.norm(x_end - x_start)
    T = 0.0
    if speed > 0.0:
        T = distance/speed
    t_start = t
    w = np.zeros(4)
    while(True):
        s = 1.0
        if t - t_start < T:
            s = (t - t_start)/T
        w[0:2] = x_start*(1.0 - s) + x_end*s
        if T > 0.0:
            w[2:4] = (x_end - x_start)/T
        e = step(w)
        cv2.waitKey(5)
        if (s == 1.0 and (tolerance == None or e < tolerance) ):
            break

def home():
    goto(x_hat[0:2], np.array([0, 0]), -1, 0.08)
    goto(np.array([0, 0]), np.array([0.07, 0.07]), 0.04, 0.05)
    set_orientation([-2.0, 2.0])
    
try:
    key = 0
    t_wake = get_time()
    while(key != 27): # Esc
        R = 0.06
#        W = -1.0/60.0*math.pi*2
#        now = datetime.datetime.now() 
#        s = 15.0 + now.second + now.microsecond / 1000000.0
#        
#        w = -2.0/12.0*math.pi
#        now = datetime.datetime.now() 
#        s = 3.0 + now.hour + now.minute/60.0 + now.second/3600.0
    
#        w = np.array([R*math.cos(W*s) + 0.01, 
#                      R*math.sin(W*s) - 0.03, 
#                      R*W*math.sin(W*s), 
#                      -R*W*math.cos(W*s)])
#        
        w = np.zeros(4)
        e = step(w)    
        #print "e: ", e
        if (e > 0.2):
            t_wake = get_time()
        key = cv2.waitKey(5) & 0xFF
        if t - t_wake > 60.0:
            home()
            detect_motion()
            t_old = t = t_wake = get_time()
    home()

finally:
    sock.close()
    cap.release();
    cv2.destroyAllWindows()
    
plt.plot(t_series, x_hat_series, label="z_hat")
plt.plot(t_series, u_series, label="u")
plt.legend()