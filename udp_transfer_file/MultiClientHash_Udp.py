import socket
import time
from threading import Thread
import struct
import hashlib
import datetime
import sys

# Constante que representa la ip del servidor con el que los clientes debe comunicarse
UDP_IP = '34.71.37.77'
# Constante que representa el puerto por el que se debe hacer la conexión ip
UDP_PORT = 65432
# Constante que representa el número de bytes que se envían por segmento en el buffer
BUFFER_SIZE = 1024
# Constante que representa el mensaje de que se finalizo la transmisión de un mensaje
END_TRANSMISION = b'TERMINO'

# Método que permite verificar la integridad del archivo enviado
def VerificateHash(originalHash, filename):
    file = open(filename, 'rb')
    md5_returned = hashlib.md5(file.read()).hexdigest()
    if originalHash.decode() == md5_returned:
        return "HASH VERIFICADO"
    else:
        return "HASH ALTERADO"

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

# Clase que genera un Thread de tipo cliente el cual genera un log único
class ClientThread(Thread):
    #Metodo que inicia un Thread
    def __init__(self, id):
        Thread.__init__(self)
        print(" Nuevo thread en"+str(time.time())+":"+str(UDP_PORT))
        self.id = id
    #Metodo que inicia la ejecución del Thread Cliente
    def run(self):
        # Preparacion del log
        LogTxt = 'log_cliente_' + \
            str(self.id) + '_' + \
            str(time.time()) + '.txt'
        # Variables usadas por el log
        tInicio = 0
        tFinal = 0
        numPaquetesRecibidos = 0
        bytesRecibidos = 0
        with open(LogTxt, 'w') as log:
            log.write("Fecha y hora de la prueba: " +
                      str(datetime.datetime.now()) + '\n')
            # Ejecucion del programa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((UDP_IP, UDP_PORT))
            tInicio = time.time_ns()
            log.write("Tiempo de inicio de ejecucion de Th_" +
                      str(self.id)+" : "+str(tInicio)+'\n')
            recived_f = 'archivo' + \
                str(self.id) + str(time.time()).split('.')[0] + '.mp4'

            with open(recived_f, 'wb') as f:
                print('Archivo abierto')
                while True:
                    data = recv_one_message(s)
                    # print('data=%s', (data))
                    if repr(data) == repr(END_TRANSMISION):
                        f.close()
                        print('file close()')
                        tFinal = time.time_ns()
                        log.write("Tiempo final de ejecucion de Th_"+str(self.id) + " : "
                                  + str(tFinal) + '\n')
                        log.write("Tiempo de ejecucion de Th_"+str(self.id)+" : "
                                  + str((tFinal-tInicio)) + '\n')
                        break
                    # write data to a file
                    f.write(data)
                    numPaquetesRecibidos += 1
                    bytesRecibidos += sys.getsizeof(data)
                log.write("Numero paquetes recibidos de Th_" +
                          str(self.id)+" : "+str(numPaquetesRecibidos) + '\n')
                log.write("Bytes recibidos por Th_" +
                          str(self.id)+" : "+str(bytesRecibidos) + '\n')
                codigoVerificacion = recv_one_message(s)
                rtaVerificacion = VerificateHash(codigoVerificacion, recived_f)
                print('Resultado de validacion: ' + rtaVerificacion)
                send_one_message(s, rtaVerificacion.encode())
                send_one_message(
                    s, (str(numPaquetesRecibidos)+";"+str(bytesRecibidos)).encode())
            print('Archivo descargado con exito')
            s.close()
            print('Conexion cerrada')
#Inicializa los Threads definidos por el range
for i in range(1):
    ClientThread(i).start()
