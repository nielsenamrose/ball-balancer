# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:47:40 2017

@author: christian
"""

import socket
import matplotlib.pyplot as plt

HOST, PORT = "203.6.152.96", 21568
data = "r,-10,-10"

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(data):
    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(data + "\n")
    
        # Receive data from the server and shut down
        received = sock.recv(1024)
    finally:
        sock.close()

        
send("s,-45,-45")

        
print "Sent:     {}".format(data)
print "Received: {}".format(received)