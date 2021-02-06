from .rudp_server import RUDPServer 
import time

server = RUDPServer(debug=True)
server.bind(("127.0.0.1", 8000))
server.listen()

client, addr = server.accept()
print('Client connected...', addr)

client.close()
server.close()