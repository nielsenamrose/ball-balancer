# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 08:12:25 2016

@author: christian
"""

import socket

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_addr = ("",21567)
UDPSock.bind(listen_addr)
print "Server listening on {0}".format(listen_addr)

while True:
        data,addr = UDPSock.recvfrom(1024)
        print data.strip(),addr