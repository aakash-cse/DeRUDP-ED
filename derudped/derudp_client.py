from __future__ import absolute_import
import socket
from aes import AESCipher
from packet import Packet

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
        pass
    
    def _receiveAck(self):
        pass

    def _sendKey(self):
        #key = ""
        pass

    def _sendHeartBeat(self):
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