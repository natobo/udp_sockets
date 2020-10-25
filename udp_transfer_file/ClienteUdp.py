import socket
import sys
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('34.71.37.77', 10000)
message = 'This is the message.  It will be repeated.'
buf=1024

try:
    # Send data
    print('sending "%s"' % message)
    sent = sock.sendto(message.encode(), server_address)

    # Receive response
    #print ('waiting to receive')
    #data, server = sock.recvfrom(4096)
    #print ('received "%s"' % data)

    data,addr = s.recvfrom(buf)
    print ("Received File:",data.decode().strip())
    f = open(data.decode().strip()+'_'+str(time.time()).split('.')[0]+'.jpg','wb')
    data,addr = s.recvfrom(buf)
    try:
        while(data):
            f.write(data)
            s.settimeout(2)
            data,addr = s.recvfrom(buf) 
    f.close()
    sock.close()