# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:47:40 2017

@author: christian
"""

import socket
import time
import matplotlib.pyplot as plt
from collections import deque

server_address = ('203.6.152.96', 21568)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

t_series = deque([])        
v_series = deque([])       
        
try:
    sock.sendto("s,-40,-40", server_address)
    data = sock.recv(1024)
    #print data
    t0 = time.time()
    
    for x in range(200):
        t = time.time() - t0
        sock.sendto("r", server_address)
        data = sock.recv(1024)
        #print "{0}: {1} {2}".format(t, data, len(data))
        split = data.split(",")
        v = (float(split[0]), float(split[1]))
        t_series.append(t)
        v_series.append(v)

finally:
    sock.close()
        
plt.plot(t_series, v_series, label="v")