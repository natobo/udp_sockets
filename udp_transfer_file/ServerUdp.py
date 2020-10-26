import socket
import sys
import hashlib
import time
import datetime
from threading import Thread

# Clase que genera un Thread que representa un cliente al cual transmitirle los datos dentro del servidor
class ClientThread(Thread):
    # Contructor del Thread
    def __init__(self, id, address):
        Thread.__init__(self)
        self.id = id
        self.address = address
        self.enviados = 0
        print("Nuevo Thread comenzado por "+ address)
    #Metodo que ejecuta el thread
    def run(self):
        global buf
        global separador
        global Verification_code
        global file_name
        global sock

        #Envia nombre del archivo y el codigo de verificacion de Hash
        print("filename_md5::"+file_name+separador+Verification_code)
        sock.sendto((file_name+separador+Verification_code).encode(),self.address)
        
        print ('\nEsperando indicador de inicio del cliente')
        ack, address = sock.recvfrom(buf)
        print ('received %s bytes from %s' % (len(ack), address))
        print (ack)
        
        if ack:
            f=open(file_name,"rb")
            data = f.read(buf)
            tInicial = time.time()
            while (data):
                sent = sock.sendto(data, address)
                if(sent):
                    print ('sent %s bytes back to %s' % (sent, address))
                    data = f.read(buf)
                    self.enviados += 1
            f.close()
            print ('sent %s bytes back to %s' % (sent, address))

            print ('\nEsperando confirmacion hash y num datagramas recibidos')
            msg_last, address = sock.recvfrom(buf)
            tFinal = time.time()
            print(msg_last)
            msg_hash, recibidos = msg_last.split(separador)
            
            with open(LogTxt, 'w') as log:
                log.write('Cliente %i - fragmentos enviados: %i' % (self.id, self.enviados) + '\n')
                log.write('Cliente %i - fragmentos recibidos: %s' % (self.id, recibidos) + '\n')
                log.write('Cliente %i - verificacion: %s' % (self.id, msg_hash)+ '\n' )
                log.write('Cliente %i - tInicial: %s seg' % (self.id,str(tInicial)) + '\n')
                log.write('Cliente %i - tFinal: %s seg' % (self.id, str(tFinal)) + '\n')
                log.write('Cliente %i - tTotal: %s seg' % (self.id, str(tFinal - tInicial)) + '\n')
                log.close()
    

# Create a UDP socket
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
    log.write("Archivo a transmitir: " + file_name + '\n')
    log.write("Tamano archivo: " + str(sys.getsizeof(file_name))+ '\n')
    log.close()

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

verification_code = createVerificationCode(file_name)
clientId = 0

while True:
    print ('\nWaiting to receive message')
    data, address = sock.recvfrom(buf)
    print ('received %s bytes from %s' % (len(data), address))

    print ("ADDRESS::"+address)
    print (data)

    newthread = ClientThread(clientId, address)
    newthread.start()

    clientId +=1
    #A partir de aqui va el cliente
    
    
    #Numero de datagramas enviados
    #enviados = 0
    #Id del cliente
    #clientId = 0
    
    #Envia nombre del archivo y el codigo de verificacion de Hash
    #print("filename_md5::"+file_name+separador+createVerificationCode(file_name))
    #sock.sendto(file_name+separador+createVerificationCode(file_name).encode(),address)
    
    #print ('\nEsperando indicador de inicio del cliente')
    #ack, address = sock.recvfrom(buf)
    #print ('received %s bytes from %s' % (len(ack), address))
    #print (ack)
    
    #if ack:
    #    f=open(file_name,"rb")
    #    data = f.read(buf)
    #    tInicial = time.time()
    #    while (data):
    #        sent = sock.sendto(data, address)
    #        if(sent):
    #            print ('sent %s bytes back to %s' % (sent, address))
    #            data = f.read(buf)
    #            enviados += 1
    #    f.close()
    #    print ('sent %s bytes back to %s' % (sent, address))

     #   print ('\nEsperando confirmacion hash y num datagramas recibidos')
     #   msg_last, address = sock.recvfrom(buf)
     #   tFinal = time.time()
     #   print(msg_last)
     #   msg_hash, recibidos = msg_last.split(separador)
        
     #   with open(LogTxt, 'w') as log:
     #       log.write('Cliente %i - fragmentos enviados: %i' % (clientId, enviados) + '\n')
     #       log.write('Cliente %i - fragmentos recibidos: %s' % (clientId, recibidos) + '\n')
     #       log.write('Cliente %i - verificacion: %s' % (clientId, msg_hash)+ '\n' )
     #       log.write('Cliente %i - tInicial: %s seg' % (clientId,str(tInicial)) + '\n')
     #       log.write('Cliente %i - tFinal: %s seg' % (clientId, str(tFinal)) + '\n')
     #       log.write('Cliente %i - tTotal: %s seg' % (clientId, str(tFinal - tInicial)) + '\n')
     #       log.close()
    