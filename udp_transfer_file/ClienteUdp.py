import socket
import sys
import time
import hashlib

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('34.71.37.77', 10000)
buf=1024
separador=','
new_filename=''
hashcode=''

# Método que permite verificar la integridad del archivo enviado
def VerificateHash(originalHash, filename):
    file = open(filename, 'rb')
    md5_returned = hashlib.md5(file.read()).hexdigest()
    if originalHash == md5_returned:
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
    filename,extension = msg.decode().split(separador)[0].split('.')
    hashcode = msg.decode().split(separador)[1]   
    new_port = msg.decode().split(separador)[2]
    sock.close() 

    new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_server_address=(server_address[0],int(new_port))
    
    # Send data
    message2 = 'Estoy listo para recibir!'
    print('sending "%s"' % message2)
    sent = new_sock.sendto(message2.encode(), new_server_address)

    #Crea el archivo
    new_filename= filename+'_'+str(time.time()).split('.')[0]+'.'+extension
    f = open(new_filename,'wb')

    #Numero de datagramas recibidos
    recibidos = 1
    data,addr = new_sock.recvfrom(buf)
    while(data):
        recibidos+=1
        f.write(data)
        new_sock.settimeout(2)
        data,addr = new_sock.recvfrom(buf)
except:
    f.close()
    msgHash=VerificateHash(hashcode,new_filename)
    msgToSend=msgHash+separador+str(recibidos)
    print("File Downloaded")
    print('sending "%s"' % msgToSend)
    sent = new_sock.sendto(msgToSend.encode(), new_server_address)
    new_sock.close() 