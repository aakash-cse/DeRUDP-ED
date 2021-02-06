from derudped.derudp_client import DerudpClient

client = DerudpClient()
client.connect(("127.0.0.1", 8000))
print('Connected established...')

client.send('hello'.encode('ascii'))
msg = client.recv(1000)
print("Server messsage:",msg.decode('ascii'))

client.close()

'''
from derudped.packet import  Packet

pack1 = Packet(b'0001|:|:|A')
pack2 = Packet(b'0002|:|:|B')
pack3 = Packet(b'0003|:|:|C')
pack4 = Packet(b'0004|:|:|D')


import socket

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

clientSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

dataqueue = [pack4,pack3,pack2,pack1]
flag =True
while flag:
    for i in range(0,len(dataqueue)):
        clientSock.sendto(dataqueue[i].encode(), (UDP_IP_ADDRESS, UDP_PORT_NO))
    flag = False
clientSock.close()
'''