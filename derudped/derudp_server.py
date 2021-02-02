from __future__ import absolute_import
from packet import Packet
import socket
from aes import AESCipher

class DerudpServer():
    def __init__(self,debug=False):
        """
        some class variables goes here
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        pass

    def _receiveSyn(self):
        pass
    
    def _sendAck(self):
        pass
    
    def _receiveKey(self):
        pass
    
    def _AckHeartBeat(self):
        pass

    def bind(self,address):
        self.sock.bind(address)
        self.binded = True

    def listen(self):
        if not self.binded:
            raise Exception("Socket not binded")
        self.listening = True
        self._receiveSyn()
        self._sendAck()
        self._receiveKey()
    
    def receiveFrom(self):
        pass

    def close(self):
        pass

    def _sendLostPacket(self):
        pass

DerudpServer()