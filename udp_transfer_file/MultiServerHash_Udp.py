import socket
from threading import Thread
import struct
import hashlib
import time
import sys
import datetime

UDP_IP = ''
UDP_PORT = 65432
BUFFER_SIZE = 1024
END_TRANSMISION = b'TERMINO'

# Variable que almacena el codigo md5 en hexadecimal del archivo a enviar
Verification_code = 'NoCodigo'
# Variables usadas por el log
fileGlobal = ""

#Crea un codigo de verificacion MD5 del archivo que se le pase por parametro y lo retorna
def createVerificationCode(filename):
    global Verification_code
    if(Verification_code == 'NoCodigo'):
        file = open(filename, 'rb')
        Verification_code = hashlib.md5(file.read()).hexdigest()
        print("Codigo de verificacion:"+Verification_code)
    return Verification_code

""" Los siguientes métodos auxiliares se usaron para conformar los mensajes con protocolo TCP
Fueron tomados de este blog: https://stupidpythonideas.blogspot.com/2013/05/sockets-are-byte-streams-not-message.html"""
# Método auxiliar que cumple la funcion de recibir en su totalidad un paquete (contraparte del método sendall de socket)
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# Envía un mensaje que se compone de una estructura que indica la cantidad de bytes en su encabezado
def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

# Recibe un mensaje enviado por el servidor, interpretando la estructura de este (encabezado y bytes de archivo)
def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

# Clase que genera un Thread que representa un cliente al cual transmitirle los datos dentro del servidor
class ClientThread(Thread):
    # Contructor del Thread
    def __init__(self, ip, port, sock, id):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.id = id
        print(" Nuevo Thread comenzado por "+ip+":"+str(port))
    #Metodo que ejecuta el thread
    def run(self):
        #Variables para la escritura del log
        tInicio = 0
        tFinal = 0
        numPaquetesEnviados = 0
        numPaquetesRecibidos = 0
        bytesEnviados = 0
        bytesRecibidos = 0
        global fileGlobal
        correctoGlobal = True
        filename = fileGlobal
        print('Filename'+filename)
        f = open(filename, 'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                numPaquetesEnviados += 1
                bytesEnviados += sys.getsizeof(l)
                send_one_message(self.sock, l)
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                print('Termino la transferencia')
                break
        print('Enviando Comando:', repr(END_TRANSMISION))
        send_one_message(self.sock, END_TRANSMISION)
        # Envia codigo de verificacion
        send_one_message(self.sock, createVerificationCode(filename).encode())
        # Recibe respuesta del cliente
        print(self.sock)
        rta = recv_one_message(self.sock).decode()
        print(rta)
        correctoGlobal &= rta == 'HASH VERIFICADO'
        numPaquetesCliente, numBytesCliente = recv_one_message(
            self.sock).decode().split(';')
        print("num"+numPaquetesCliente)
        numPaquetesRecibidos += int(numPaquetesCliente)
        print("by"+numBytesCliente)
        bytesRecibidos += int(numBytesCliente)
        self.sock.close()
        with open(LogTxt, 'w') as log:
            tFinal = time.time_ns()
            log.write("Tiempo final de ejecucion del th" +
                      self.id + ": " + str(tFinal) + '\n')
            log.write("Tiempo de ejecucion desde inicio de la prueba" +
                      self.id + ": " + str((tFinal-tInicio)) + '\n')
            log.write("Numero de paquetes enviados hasta el th" + self.id + ": " +
                      str(numPaquetesEnviados) + "\n")
            log.write("Numero de paquetes recibidos hasta el th" + self.id + ": " +
                      str(numPaquetesRecibidos) + "\n")
            log.write("Numero de bytes enviados hasta el th" +
                      self.id + ": " + str(bytesEnviados) + "\n")
            log.write("Numero de bytes recibidos hasta el th" + self.id + ": " +
                      str(bytesRecibidos) + "\n")
            log.write("Correctitud del envio hasta el th" +
                      self.id + ": " + str(correctoGlobal) + "\n")
            log.close()
            
# Crea el socket por el que el servidor estará escuchando a los clientes
ucpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ucpsock.bind((UDP_IP, UDP_PORT))
threads = []
# Aplicacion de ejecucion del servidor para definir cual archivo es que el que va transmitir y a cuantos clientes.
print("Hola!, bienvenido a la aplicacion del grupo 11, por favor selecciona el archivo de video a mandar: "+"\n")
print("1. Video 1 de  100 MB"+"\n")
print("2. Video 2 de  250 MB"+"\n")
opcion = int(input("Ingresa una opción: "))
fileGlobal = 'ventilador_100.mp4' if (opcion == 1) else 'hielo_250.mp4'
print("Listo, menciona el numero de clientes a los que quieres antender en simultaneo para enviar el archivo: "+"\n")
opcion2 = int(input("Ingresa el numero de clientes: "))
# Preparacion del log
LogTxt = 'log_servidor' + \
    '_'+str(time.time()) + '.txt'
with open(LogTxt, 'w') as log:
    log.write("Fecha y hora de la prueba: " +
              str(datetime.datetime.now()) + '\n')
    log.close()
clientId = 0
#Loop infinito que acepta conexiones de clientes entrantes
while True:
    ucpsock.listen(25)
    print("Esperando por conexiones entrantes...")
    (conn, (ip, port)) = ucpsock.accept()
    print('Conexion desde  ', (ip, port))
    clientId += 1
    newthread = ClientThread(ip, port, conn, clientId)
    threads.append(newthread)
    while len(threads) >= opcion2:
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            threads.remove(t)
