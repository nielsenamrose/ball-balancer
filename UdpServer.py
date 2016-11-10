# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 08:12:25 2016

@author: christian
"""

import socket

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",21567)
UDPSock.bind(listen_addr)
print "Server started"

while True:
        data,addr = UDPSock.recvfrom(1024)
        print data.strip(),addr