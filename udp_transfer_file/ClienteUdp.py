import socket
import sys
import time
import hashlib

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('34.71.37.77', 10000)
buf=1024
separador=','
filename=''
hashcode=''

# Método que permite verificar la integridad del archivo enviado
def VerificateHash(originalHash, filename):
    file = open(filename, 'rb')
    md5_returned = hashlib.md5(file.read()).hexdigest()
    if originalHash.decode() == md5_returned:
        return "HASH VERIFICADO"
    else:
        return "HASH ALTERADO"

try:
    # Send data
    message1 = 'Hola servidor!'
    print('sending "%s"' % message1)
    sent = sock.sendto(message1.encode(), server_address)
    # Receive response
    msg,addr = sock.recvfrom(buf)
    print ("Msg recibido:",msg.decode())
    filename = msg.decode().split(separador)[0]  
    hashcode = msg.decode().split(separador)[1]   
    # Send data
    message2 = 'Estoy listo para recibir!'
    print('sending "%s"' % message2)
    sent = sock.sendto(message2.encode(), server_address)
    
    f = open(filename.decode()+'_'+str(time.time()).split('.')[0]+'.jpg','wb')
    
    data,addr = sock.recvfrom(buf)
    while(data):
        f.write(data)
        sock.settimeout(2)
        data,addr = sock.recvfrom(buf)
except:
    f.close()
    sock.close()
    print(VerificateHash(hashcode,filename))
    print("File Downloaded")