import socket
import struct
import sys

#Mensaje a transmitir
message = "Mensaje en multidifusion"
#Puerto e ip del servidor
multicast_group = ('35.232.44.253',10000)

#Crea un socket UDP que envia datagramas
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Define un timeout de respuesta asi el socket no se bloquea indefinidamente cuando trata de recibir una respuesta
sock.settimeout(0.5)
# Define el time-to-live de los mensajes a 16
ttl = struct.pack('b', 16)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:

    # Send data to the multicast group
    print('Enviando "%s"'% message )
    sent = sock.sendto(message, multicast_group)

    # Look for responses from all recipients
    while True:
        print('Esperando respuesta')
        try:
            data, server = sock.recvfrom(16)
        except socket.timeout:
            print ('timed out, no se recibieron mas repuestas')
            break
        else:
            print('Recibido "%s" de %s' % (data, server))

finally:
    print('cerrando socket')
    sock.close()