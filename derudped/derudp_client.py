from __future__ import absolute_import
import socket
from aes import AESCipher
from packet import Packet
from constants import MAX_PCKT_SIZE

class DerudpClient():
    def __init__(self,debug=False):
        """
        some class variables goes here
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug = debug
        self.twhShake = False
        pass

    def _sendSyn(self):
        self.synpacket = Packet(b'0001|:|:|syn')
        self.sock.sendto(self.synpacket.encode(),self.address)
        self.synFlag = True
        self._receiveAck()

    def _receiveAck(self):
        data,_ = self.sock.recvfrom(MAX_PCKT_SIZE)
        if data.payload=="ack":
            self.acceptAck = True
            self._sendKey()

    def _sendKey(self):
        key=b''
        self.packKey = Packet(b'0001|:|:|'+key)
        self.sock.sendto(self.packKey.encode(),self.address)
        self.twhShake = True
        pass

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
        while self.synFlag!=True:
            self._sendSyn() # sending syn function
        self._receiveAck() # receiving ack function
        self._sendKey() # sending syn-ack + key function
        if self.twhShake: # checking for above threefunction successful
            self._loadData()     # load the data into the queue   

    def sendto(self):
        pass

    def close(self):
        pass

    def _getLostPacket(self):
        pass    

DerudpClient()