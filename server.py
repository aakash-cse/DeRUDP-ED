from derudped.packet import Packet

## Again we import the necessary socket python module
import socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

out = []
while True:
    try:
        data, addr = serverSock.recvfrom(1024)
        out.append(Packet(data))
        if len(out)==4:
            break
    except KeyboardInterrupt:
        break
def getseq(Packet):
    return Packet.seqno
out = sorted(out,key=getseq)
for val in out:
    print(val.payload)
serverSock.close()

