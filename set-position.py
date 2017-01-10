import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('203.6.152.96', 21568)
sock.sendto("E,{0:f},{1:f}".format(-10,-10), server_address)    
