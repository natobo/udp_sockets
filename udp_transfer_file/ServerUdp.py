import socket
import sys
import hashlib

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', 10000)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

file_name='dogs.jpg'
buf =1024

# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'
separador = ','

#Crea un codigo de verificacion MD5 del archivo que se le pase por parametro y lo retorna
def createVerificationCode(filename):
    global Verification_code
    if(Verification_code == 'NoCodigo'):
        file = open(filename, 'rb')
        Verification_code = hashlib.md5(file.read()).hexdigest()
        print("Codigo de verificacion:"+Verification_code)
    return Verification_code

while True:
    print ('\nWaiting to receive message')
    data, address = sock.recvfrom(buf)
    print ('received %s bytes from %s' % (len(data), address))
    print (data)

    #Envia nombre del archivo y el codigo de verificacion de Hash
    print("HII::"+file_name+separador+createVerificationCode(file_name))
    sock.sendto(file_name+separador+createVerificationCode(file_name).encode(),address)
    
    print ('\nEsperando señal de inicio del cliente')
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
        f.close()
        print ('sent %s bytes back to %s' % (sent, address))

        print ('\nEsperando confirmación hash')
        msg_hash, address = sock.recvfrom(buf)
        print(msg_hash)
    