from __future__ import absolute_import
import socket
from aes import AESCipher
from packet import Packet
from constants import MAX_PCKT_SIZE
import time

class DerudpClient():
    def __init__(self,debug=False):
        """
        some class variables goes here
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(1)
        self.debug = debug
        self.twhShake = False
        self.synFlag = False
        pass

    def _sendSyn(self):
        self.synpacket = Packet(b'0001|:|:|syn')
        self.sock.sendto(self.synpacket.encode(),self.address)
        print("Send the syn packet")
        self.synFlag = True
        time.sleep(2)
        self._receiveAck()

    def _receiveAck(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        data,_ = self.sock.recvfrom(MAX_PCKT_SIZE)
        data = Packet(data).payload.decode("utf-8")
        if data=="ack":
            self.acceptAck = True
            print("Received the ACK packet")
            self._sendKey()

    def _sendKey(self):
        self.packKey = Packet(b'0001|:|:|HelloWorld')
        self.sock.sendto(self.packKey.encode(),self.address)
        print("Send the key packet")
        self.twhShake = True
        time.sleep(2)

    def _sendHeartBeat(self):
        """
        This function send the heartbeat
        packet to the server to make the conneciton
        alive
        """
        pass

    def _loadData(self): # additional method for sender/client alone
        pass

    def connect(self,address):
        """
        This method does the following thing
        1. three way handshake with the address
        2. load the data 
        3. set the address as the class variables
        """
        self.address = address
        self._sendSyn() # sending syn function
        #if self.twhShake: # checking for above threefunction successful
        #    self._loadData()     # load the data into the queue   

    def sendto(self):
        pass

    def close(self):
        pass

    def _getLostPacket(self):
        pass    

def test():
    client = DerudpClient()
    client.connect(("127.0.0.1",6789))

test()