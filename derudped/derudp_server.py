from __future__ import absolute_import
from packet import Packet
import socket
from aes import AESCipher
from constants import MAX_PCKT_SIZE
import time

class DerudpServer():
    def __init__(self,debug=False):
        """
        some class variables goes here
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(1)
        self.debug = debug
        self.key = ""
        pass

    def _receiveSyn(self):
        data , _ = self.sock.recvfrom(MAX_PCKT_SIZE)
        data = Packet(data).payload.decode("utf-8")
        if data=="syn":
            self.acceptSyn = True
            print("Received the syn packet")  
            self._sendAck()
    
    def _sendAck(self):
        self.ackpacket = Packet(b'0001|:|:|ack')
        self.sock.sendto(self.ackpacket.encode(),self.address)
        self.ackFlag=True
        print("Send the Ack packet")
        time.sleep(2)
        self._receiveKey()
    
    def _receiveKey(self):
        data,_ = self.sock.recvfrom(MAX_PCKT_SIZE)
        data = Packet(data).payload.decode("utf-8")
        if len(data) >0:
            self.key = data
            print("Key is Received",self.key)
    
    def _AckHeartBeat(self):
        """
        This function will receive the heartbeat
        and this should be done simulataneously with
        transfering the files
        """
        pass

    def bind(self,address):
        self.sock.bind(address)
        self.address = address
        self.binded = True

    def listen(self):
        if not self.binded:
            raise Exception("Socket not binded")
        self.listening = True
        self._receiveSyn()
    
    def receiveFrom(self):
        pass

    def close(self):
        pass

    def _sendLostPacket(self):
        pass


def test():
    server = DerudpServer()
    server.bind(("127.0.0.1",6789))
    server.listen()

test()