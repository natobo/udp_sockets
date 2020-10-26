import socket
import struct
import cv2
import numpy as np
import threading
from queue import Queue
import time
import argparse
import sys

# Obtener argumentos
parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, help='La IP donde el servidor escucha nuevos clientes', default="127.0.0.1")
parser.add_argument('--puerto', type=int, help='El puerto donde el servidor escucha nuevos clientes', default=25000)
parser.add_argument('--variable', type=bool, help='Permite que la ventana cambie de tamaño cuando hay perdidas', default=False)
args = parser.parse_args()

# Variables de conexion con servidor
IP = args.ip
Puerto = args.puerto
TamBuffer = 1024
Variable= args.variable

#Control para terminar captura
cap=True
#Buffer de frames
buff=Queue()

def capturar(IP="224.1.1.1",Puerto=20001,TamBuffer= 1024):
    global cap
    global buff
    # Crear socket
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as Socket:

        # Conectar socket a un puerto
        Socket.bind(('',Puerto))

        # Conectarse al grupo multicast...
        grupo = socket.inet_aton(IP)
        Socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack('4sL', grupo, socket.INADDR_ANY))
        print("Iniciando captura en la IP: "+IP+" y puerto: "+str(Puerto))

        # Variables varias
        m=None # Arreglo con  tamaños
        Alto=2 # Alto del frame
        Capas=2 # Capas de color del Frame
        n=[] # Contador
        Ancho=0 # Ancho del frame
        p=[] #Lista de
        p1=[]

        # Recibir
        while cap:
            # Recibir mensaje
            mensaje = Socket.recvfrom((Alto*Capas*8)+16)
            # Si se tiene un nuevo frame se espera un mensaje con el tamaño
            if len(mensaje[0])==24:
                # Se recibe tamaño
                m = np.frombuffer(mensaje[0],dtype='int64')
                Alto=m[0]
                Capas=m[1]
                Ancho=m[2]
                # Se genera el frame
                frame=np.array(p)
                # Se verifica y proyecta el frame
                if np.size(frame)>5:
                    if Variable:
                        buff.put(frame)
                    else:
                        buff.put(p1)
                # Reiniciar variables
                p1=np.zeros((Ancho,Alto,Capas),dtype="uint8")
                p=[]
                n=[]
                continue
            # Recibir fragmentos de un frame
            if Ancho>0:
                # Recibir frame
                #entrada=Socket.recvfrom((Alto*Capas*8)+16)[0]

                # Obtener posicion
                entrada = bytearray(mensaje[0])
                num1 = entrada.pop(len(entrada)-1)
                num2 = entrada.pop(len(entrada)-1)
                num = bytearray(num2.to_bytes(1, byteorder='big'))
                num.extend(num1.to_bytes(1, byteorder='big'))
                num = int.from_bytes(num,byteorder='big')
                # Reconstruir seccion de frame
                recibido=np.frombuffer(entrada,dtype='uint8')
                if len(recibido)==Alto*Capas:
                    reconstruido = recibido.reshape(Alto,Capas)
                    p.append(reconstruido)
                    if num not in n:
                        p1[num,:,:]=reconstruido
                        n.append(num)
    print("Captura en la IP: "+IP+" y puerto: "+str(Puerto)+" terminada")


print ("\nBienvenido al cliente de streaming por broadcast UDP\n")

while True:
    # Contactar servidor
    dir=""
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as Socket:
        # Enviar mensaje al servidor
        Socket.sendto(str.encode("Hola"), (IP, Puerto))
        print("Esperando servidor en "+IP+":"+str(Puerto)+"...")
        # Obtener respuesta
        recibido = Socket.recvfrom(TamBuffer)
        dir = (recibido[0].decode()).split(" ")
        # Verificar respuesta
        if dir[0] != "Canales:":
            print("Error de conexion")
            sys.exit()
        dir.pop(0)

    # Obtener canales e ips de respuesta
    ips=[]
    can=[]
    print("Canales disponibles:\n")
    for i in range(len(dir)):
        info = dir[i].split(",")
        print(str(i+1)+". "+info[1])
        ips.append(info[0])
        can.append(info[1])

    # Solicitar al usuario seleccionar un canal
    canal=input("\nSeleccione un canal (escriba un numero de la lista, 'x' para salir)\n")
    # Verificar input
    if canal == "x":
        print("Saliendo...")
        sys.exit()
    try:
        canal=int(canal)
    except:
        print("Ingrese un numero de la lista")
        sys.exit()
    if canal<1 or canal>len(ips):
        print("Ingrese un numero de la lista")
        sys.exit()
    print()

    # Reiniciar variables
    buff=Queue()
    cap=True

    print("Iniciando streaming en el canal: "+can[canal-1]+" (presione 'q' en la ventana para salir)\n")
    #Inicia captura para el canal seleccionado
    t1 = threading.Thread(target = capturar,kwargs={'IP':ips[canal-1]})
    t1.start()



    #Inicia reproduccion
    while True:
        # revisar que el buffer tenga mas de un frame
        if buff.qsize() > 0:
            cv2.imshow(can[canal-1], buff.get())
            # Salir al presionar q
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    # Terminar captura
    cap=False
    t1.join()
