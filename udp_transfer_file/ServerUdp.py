import socket
import sys


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', 10000)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

file_name='dogs.jpg'
buf =1024

while True:
    print ('\nwaiting to receive message')
    data, address = sock.recvfrom(buf)
    print ('received %s bytes from %s' % (len(data), address))
    print (data)

    #Envia nombre del archivo
    print("HII::"+file_name.encode())
    sock.sendto(file_name.encode(),address)
    
    print ('\nEsperando Confirmacion de cliente')
    ack, address = sock.recvfrom(buf)
    print ('received %s bytes from %s' % (len(data), address))
    print (ack)
    
    
    if ack:
        f=open(file_name,"rb")
        data = f.read(buf)
        while (data):
            sent = sock.sendto(data, address)
            if(sent):
                print ('sent %s bytes back to %s' % (sent, address))
                data = f.read(buf)
        sock.close()
        f.close()
        print ('sent %s bytes back to %s' % (sent, address))