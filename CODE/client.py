import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# AF_INET corresponds to ipv4 and sock_stream corresponds to tcp

s.connect((socket.gethostname(),1234))

dataqueue = []
while True:
    msg = s.recv(4) # buffer size 1024
    if len(msg) <=0:
        break
    dataqueue.append(msg.decode("utf-8"))
    print(dataqueue)

'''

from derudp.client import client

sock = client()
server_addr("127.0.0.1", 8000)
sock.connect(server_addr)
server.listen()

sock, addr = server.accept()

sock.send(data)
data = sock.recv(1024)
sock.close()

'''