import socket
import struct
import cv2
import numpy as np
import time
import threading
import os
import argparse
import sys
import select
from queue import Queue

# Obtener argumentos
parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, help='La IP donde el servidor escucha nuevos clientes', default="127.0.0.1")
parser.add_argument('--puerto', type=int, help='El puerto donde el servidor escucha nuevos clientes', default=25000)
args = parser.parse_args()

# Variables de conexion con clientes
IP = args.ip
Puerto = args.puerto
TamBuffer = 1024

#Canales activos
ca = []
estado = [True]

# Variables de craga simultanea
cargado=Queue()

# Cargar video
def cargar(ruta=""):
    global cargado
    p=[]
    Video = cv2.VideoCapture(ruta)
    if (Video.isOpened()== False):
        print("Error cargando el video: "+ruta)
        return None
    while(Video.isOpened()):
        ret, frame = Video.read()
        if ret == True:
            p.append(frame)
        else:
            break
    Video.release()
    cargado.put((ruta,p))
    return None

# Inicia un canal de broadcast
def canal(IP = "224.1.1.1",Puerto = 20001,v=None,e=0,nombre="Canal"):
    global estado
    # Crear socket
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as Socket:

        # Que los mensajes vivan un segundo!
        Socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        # Informar
        print("Canal "+nombre+": Arranqué en "+IP+":"+str(Puerto))

        # Transmitir
        while estado[e]:
            for i in v:
                time.sleep(0.005)
                if not estado[e]:
                    break
                # Se envia el tamaño anunciando un nuevo frame
                Socket.sendto(np.array([np.size(i[0,:,0]),np.size(i[0,0,:]),np.size(i[:,0,0])]).tobytes(), (IP,Puerto))
                # Se secciona el frame y se envia
                for j in range(np.size(i[:,0,0])):
                    # Transformar seccion a bytes
                    enviar = bytearray(i[j,:,:].tobytes())
                    # Agregar info de posicion
                    enviar.extend(j.to_bytes(2, byteorder='big'))
                    # Enviar
                    Socket.sendto(enviar, (IP,Puerto))

    print("Canal "+nombre+": Termine en "+IP+":"+str(Puerto))



print ("\nBienvenido al servidor de streaming por broadcast UDP (presione 'z' para salir)\n")

# Cargar contenido
print ("Cargando contenido...")
cargando=[]
contenido = {}
# Explora carpeta canales
for (direccion, directorios, archivos) in os.walk(os.path.abspath("")+"/canales"):
    for directorio in directorios:
        # Para cada canal explora archivos
        for (direccion, directorios, archivos) in os.walk(os.path.abspath("")+"/canales/"+directorio):
            print(directorio,end=": ")
            # Contador para verificar si mas de 0 videos en el canal
            cont = 0
            for video in archivos:
                # Verifica si archivo es video
                if video.endswith(".mp4"):
                    print(video,end=" ")
                    # Crea thread de caraga
                    t=threading.Thread(target = cargar,kwargs={'ruta':"canales/"+directorio+"/"+video})
                    t.start()
                    # Agrega thread a lista
                    cargando.append(t)
                    cont=cont+1
            if cont==0:
                print("Ningun video (no se toma en cuenta)",end="")
            else:
                contenido[directorio.replace(" ", "")]=[]
            print()
            break
    break

# Espera a que terminen las cargas de cada video
for i in cargando:
    i.join()

# Asignar videos a canales
while cargado.qsize()>0:
    video=cargado.get()
    nombrecanal = (video[0].split("/")[1]).replace(" ", "")
    contenido[nombrecanal].extend(video[1])


print("\nIniciando canales...")
#Inicia canal
r=1
for infocanal in contenido:
    estado.append(True)
    # Ip del canal
    dir="224.1.1."+str(r)
    # Thread del canal
    t = threading.Thread(target = canal,kwargs={'IP':dir,'v':contenido[infocanal],'e':r,'nombre':infocanal})
    t.start()
    # Se guarda info del canal
    ca.append((dir,t,infocanal))
    r=r+1

# Loop principal
# Inicia escucha de teclado
    # Crear socket
with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as Socket:
	# Conecta socket a ip y puerto
	Socket.bind((IP, Puerto))
	# Iniciando escucha de clientes
	print("\nEscuchando clientes en: "+IP+":"+str(Puerto)+"\n")
	while True:
		# Verifica si llego mensaje
		leer, escribir, error = select.select([Socket],[],[],10)
		# Si llego
		if Socket in leer:
			recibido = Socket.recvfrom(TamBuffer)
			# Verifica mensaje
			if recibido[0].decode() == "Hola":
				# Informa solicitud
				print("Solicitud de catalogo: "+recibido[1][0]+":"+str(recibido[1][1]))
				# Envia catalogo
				s = "Canales: "
				for i in ca:
					s=s+i[0]+","+i[2]+" "
				Socket.sendto(str.encode(s.strip()), recibido[1])
#listener.join()

# Detener threads
print("Apagando canales...")
for i in range(len(estado)):
    estado[i]=False
for i in ca:
    i[1].join()
print()
