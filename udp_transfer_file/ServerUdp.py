import socket
import sys
import hashlib
import time
import datetime

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('', 10000)
print ('starting up on %s port %s' % server_address)
sock.bind(server_address)

buf =1024

# Aplicacion de ejecucion del servidor UDP para definir cual archivo es que el que va transmitir y a cuantos clientes.
print("Hola!, bienvenido a la aplicacion de transferencia de archivos UDP del grupo 11, por favor selecciona el archivo de video a mandar: "+"\n")
print("1. Video 1 de  100 MB"+"\n")
print("2. Video 2 de  250 MB"+"\n")
print("3. Imagen jpg de perritos"+"\n")
opcion = int(input("Ingresa una opcion: "))
file_name = 'ventilador_100.mp4' if (opcion == 1) else 'hielo_250.mp4' if (opcion == 2) else 'dogs.jpg'
print("Listo, menciona el numero de clientes a los que quieres antender en simultaneo para enviar el archivo: "+"\n")
opcion2 = int(input("Ingresa el numero de clientes: "))
# Preparacion del log
LogTxt = 'log_servidor' + \
    '_'+str(datetime.datetime.now()).split('.')[0] + '.txt'

with open(LogTxt, 'w') as log:
    log.write("Fecha y hora de la prueba: " +
              str(datetime.datetime.now()) + '\n')
    log.write("Archivo a transmitir: " + file_name)
    log.write("Tamano archivo: " + str(sys.getsizeof(file_name)))
    log.close()

clientId = 0

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
    
    print ('\nEsperando indicador de inicio del cliente')
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

        print ('\nEsperando confirmacion hash')
        msg_hash, address = sock.recvfrom(buf)
        print(msg_hash)
    