import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# AF_INET corresponds to ipv4 and sock_stream corresponds to tcp

s.bind((socket.gethostname(),1234)) # ip and host

s.listen(5) # it will listen for the queue of 5
dataqueue = ["hi " ,"how ","are ","you "]

while True:
    clientsocket , address = s.accept()
    print(f"Connection from {address} has been established!")
    for val in dataqueue:
        clientsocket.send(bytes(val,"utf-8"))
    clientsocket.close()



'''

from derudp.server import server

server = server()
server.bind(addr)
server.listen()

sock, addr = server.accept()

sock.send(data)
data = sock.recv(1024)

'''