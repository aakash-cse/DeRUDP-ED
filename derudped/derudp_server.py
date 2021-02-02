from __future__ import absolute_import
from packet import Packet
import socket
from aes import AESCipher
from constants import MAX_PCKT_SIZE

class DerudpServer():
    def __init__(self,debug=False):
        """
        some class variables goes here
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        self.key = ""
        pass

    def _receiveSyn(self):
        data , _ = self.sock.recvfrom(MAX_PCKT_SIZE)
        if data.payload=="syn":
            self.acceptSyn = True  
            self._sendAck()
    
    def _sendAck(self):
        self.ackpacket = Packet(b'0001|:|:|ack')
        self.sock.sendto(self.ackpacket.encode(),self.address)
        self.ackFlag=True
        self._receiveKey()
    
    def _receiveKey(self):
        data,_ = self.sock.recvfrom(MAX_PCKT_SIZE)
        if data.payload >0:
            self.key = data.decode("utf-8") 
    
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

DerudpServer()