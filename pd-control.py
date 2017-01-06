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

lower = np.array((hsv0[0]-10, hsv0[1]-40, hsv0[2]-40))
upper = np.array((hsv0[0]+10, 255, 255))

kernel = np.ones((10,10), np.uint8)

R = cv2.Rodrigues(rvecs[0])[0]

ARt = mtx.dot(np.hstack((R,tvecs[0])))  

Ru = np.identity(4)

T = np.array([[1,0,0],
              [0,1,0],
              [0,0,-rB],
              [0,0,1]], np.float32)  

t0 = cv2.getTickCount()
f = 1.0 * cv2.getTickFrequency()
t = t_old = 0.0
t_series = deque([])
dt_series = deque([])

# Estimator

g = 9.82

F = np.array([[0, 0, 1, 0],
              [0, 0, 0, 1],
              [0, 0, 0, 0],
              [0, 0, 0, 0]], np.float32)

c = 3.0/5.0*g

C = np.array([[0, 0],
              [0, 0],
              [c, 0],
              [0, c]], np.float32)

H = np.array([[ 1, 0, 0, 0],
              [ 0, 1, 0, 0]], np.float32)

Kp = np.array([[0.5, 0.0],
               [0.0, 0.5],
               [0.2, 0.0],
               [0.0, 0.2]], np.float32)



x_hat_min = np.array([-0.2, -0.2, -1.0, -1.0])
x_hat_max = np.array([0.2, 0.2, 1.0, 1.0])

x_hat = np.array([0.0, 0.0, 0.0, 0.0])
x_hat_series = deque([])

# Controller

K = np.array([[ 1.5, 0.0, 0.5, 0.0],
              [ 0.0, 1.5, 0.0, 0.5]]) 

Ki = np.array([[0.05, 0.0, 0.0, 0.0],
               [0.0, 0.05, 0.0, 0.0]])

w = np.array([0.0, 0.0, 0.0, 0.0]) # set point
i = np.zeros(4)
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
    
def xy_to_uv(z, u):
    m = ARt.dot(Ru).dot(np.array([[z[0],z[1],0.0,1.0]]).T)
    return m[0:2]/m[2,0] 
    
def set_orientation(u):
    sock.sendto("E,{0:f},{1:f}".format(-math.degrees(u[0]), math.degrees(u[1])), server_address)
    #sock.sendto("E,{0:f},{1:f}".format(0, 0), server_address)
    None

def get_time():
    return (cv2.getTickCount() - t0) / f
    
N = 0

def step(w):
    global t
    global N
    global t_old
    global i
    global u
    global x_hat

    _, frame = cap.read()
    t = get_time()
    N += 1
    dt = t / N
    #dt = t - t_old

    
    # Update estimated state
    
    v = np.array([0.0, 0.00])
    x_hat = x_hat + dt*(F.dot(x_hat) + C.dot(u + v)) 

    # Update Ru

    K_hat = np.array([u[1], -u[0], 0.0])
    theta = np.linalg.norm(K_hat)
    if theta > 0.01:
        K_hat *= math.asin(theta)/theta
    Ru[0:3,0:3] = cv2.Rodrigues(K_hat)[0]
        
    # Vision
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    erosion = cv2.erode(mask, kernel, iterations = 1)
    M = cv2.moments(erosion, True)

    if M['m00'] <= 0:
        z = H.dot(x_hat)
    else:
        c = np.array([M['m10']/M['m00'], M['m01']/M['m00'], 1.0])
        cv2.circle(frame, (int(c[0]), int(c[1])), 10, (0, 0, 255), -1)
        m = np.linalg.solve(ARt.dot(Ru).dot(T), np.array([[c[0], c[1], 1.0]]).T)
        z = np.array([m[0,0],m[1,0]])/m[2,0]
    
    # Estimator
    
    z_tilt = z - H.dot(x_hat)
    Kdt = np.diag([1.0, 1.0, 1.0/dt, 1.0/dt])
    x_hat += Kdt.dot(Kp).dot(z_tilt)
    x_hat = np.clip(x_hat, x_hat_min, x_hat_max)
       
    # Controller    
    e = w - x_hat 
    i += e
    u = K.dot(e)# + Ki.dot(i)
    print x_hat, u
    u = np.clip(u, -0.14, 0.14)
    
    set_orientation(u)
    t_old = t
    error = np.linalg.norm(e)
    
    if len(t_series) < 10000:
        t_series.append(t)
        dt_series.append(dt)
        x_hat_series.append(x_hat)
        e_series.append(e)
        u_series.append(u)
       
    cv2.circle(frame, tuple(xy_to_uv(x_hat[0:2], u)), 3, (0, 255, 0), -1)
    cv2.imshow('frame', frame)
    
    return t, error

def goto(x_start, x_end, speed = 0, tolerance = None):
    global t
    t_start = t
    distance = np.linalg.norm(x_end - x_start)
    T = 0.0
    if speed > 0.0:
        T = distance/speed
    w = np.zeros(4)
    while(True):
        s = 1.0
        if t - t_start < T:
            s = (t - t_start)/T
        w[0:2] = x_start*(1.0 - s) + x_end*s
        if T > 0.0:
            w[2:4] = (x_end - x_start)/T
        t, e = step(w)
        cv2.waitKey(5)
        if (s == 1.0 and (tolerance == None or e < tolerance) ):
            break

def home():
    goto(x_hat[0:2], np.array([0, 0]), -1, 0.08)
    goto(np.array([0, 0]), np.array([-0.08, -0.08]), 0.04, 0.08)
    set_orientation([-0.05, -0.05])
    
try:
    cap = cv2.VideoCapture(0)
    key = 0
    t_wake = 0
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
        t, e = step(w)    
        #print "e: ", e
        if (e > 0.2):
            t_wake = t
        key = cv2.waitKey(5) & 0xFF
#        if t - t_wake > 10.0:
#            home()
#            detect_motion()
#            t_old = t = t_wake = get_time()

finally:
    sock.close()
    cap.release()
    cv2.destroyAllWindows()
    
plt.plot(t_series, x_hat_series, label="z_hat")
plt.plot(t_series, u_series, label="u")
plt.plot(t_series, dt_series, label="dt")
plt.legend()