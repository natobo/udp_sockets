import socket
import struct
import sys

#Respuesta de conexion
ack= 'ack'
#Datos de conexion
multicast_group = '224.3.29.71'
server_address = ('', 10000)
# Crea el socket udp
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enlaza el socket con la direccion del servidor
sock.bind(server_address)

# Contar al sistema operativo que añada el socket al grupo multicast
# en todas las interfaces
# Coga todas las interfaces de red y escuche en multicast
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
# Receive/respond loop
while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(1024)

    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    print('sending acknowledgement to', address)
    sock.sendto(b'ack', address)