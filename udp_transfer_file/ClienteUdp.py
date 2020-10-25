import socket
import sys
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('34.71.37.77', 10000)
buf=1024

try:
    # Send data
    message1 = 'Hola servidor!'
    print('sending "%s"' % message1)
    sent = sock.sendto(message1.encode(), server_address)

    # Receive response
    #print ('waiting to receive')
    #data, server = sock.recvfrom(4096)
    #print ('received "%s"' % data)
    
    filename,addr = sock.recvfrom(buf)
    print ("Received File:",filename.decode())
    
    # Send data
    message2 = 'Estoy listo para recibir!'
    print('sending "%s"' % message2)
    sent = sock.sendto(message2.encode(), server_address)

    f = open(filename+'_'+str(time.time()).split('.')[0]+'.jpg','wb')
    data,addr = sock.recvfrom(buf)
    
    while(data):
        f.write(data)
        data,addr = sock.recvfrom(buf) 
    print('closing socket')
    f.close()
finally:
    sock.close()