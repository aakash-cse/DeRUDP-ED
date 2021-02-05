from __future__ import absolute_import
import socket
import time
from threading import Lock
from .utils import *

class DerudpClient():
    def __init__(self,debug=False):
        """
        class definition of our custom derudpclient| sender 
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.seqSend = 0
        self.seqNext = 0
        self.writeBuff = [None]*MAX_BYTES # replace it with queue
        self.readBuff = b'' # replace it with queue
        self.order = [None]*MAX_BYTES 
        self.mutexW = Lock()
        self.mutexR = Lock()
        self.isConnected = False
        self.isClosed = False
        self.timer = None
        self.buffer = 0
        self.debug = debug
        self.dropped = 0
        self.key = b''
    
    def connect(self,address):
        """
        This function is used to initiate the threeway handshake to address
        send the syn packet and wait for the connection to establish

        Args:
            address ([tuple]): (ipaddress,port) : eg ("192.168.72.2",8080)
        """
        packet = Packet()
        packet.syn = 1
        self.Listener = Listener(self) # passing the client socket for the listener
        self.Listener.start()
        self.serverAddress = address
        self.key = b''.join(address)
        self.cipher = AESCipher(self.key)
        self.__writeData(packet)
        # wait for the connection to establish so make listener to sleep
        ite = 0
        while not self.isConnected:
            ite+=1 #increment the iterator
            time.sleep(POLL_INTERVAL)
            if ite>=150:
                raise Exception("Cannot Reach the Host")
    
    def __writeData(self,packet):
        """This funciton is used to write the packet into the writebuffer

        Args:
            packet ([Packet]): Contains the custom UDPdata
        """
        pass

    def __readData(self,packet,address):
        """This function is used to read the packet from the address

        Args:
            packet ([Packet]): Contains the custom UDPdata
            address ([tuple]): Contains the server address as a tuples
        """
        pass
    
    def timeoutcallback(self):
        """This function is used as the callback for the timeoutevent
        """
        pass

    def send(self,data):
        """This function sends the packet to write function where the payload is encrypted

        Args:
            data ([Packet]): Data which was packet and send through the write function
        """
        if self.isClosed and not self.isConnected:
            raise Exception("Cannot send the data")
        while len(data) > 0:
            rem = min(len(data), MAX_PCKT_SIZE)
            payload = data[:rem] # replace the data with the queue
            # wait till receiver has acked enough bytes
            while self.buffer + rem > MAX_BYTES:
                time.sleep(POLL_INTERVAL)
            self.buffer += rem
            data = data[rem:] 
            pckt = Packet()
            pckt.payload = self.cipher.encrypt(payload) # encrypting the data
            self.write(pckt)

    def close(self):
        """This function closes the connection with the server
        """
        self.isClosed = True
        if self.isConnected:
            self.isConnected = False    
            while self.seqSend<self.seqNext:
                time.sleep(POLL_INTERVAL)

            # send the fin packet
            packet = Packet()
            packet.fin = 1
            self.__writeData(packet)
            ite = 0
            while self.seqSend<self.seqNext and ite <100:
                time.sleep(POLL_INTERVAL)
                ite +=1
        self.__finAck()