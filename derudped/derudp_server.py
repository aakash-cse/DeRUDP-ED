import socket
import time
from .utils import *

class DerudpServer():
    def __init__(self,debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.isBinded = False
        self.isListening = False
        self.isClosed = False
        self.debug = debug
        self.clientaddress = None
        self.key = b''
        self.handler = None # creating an handler object to handle the client
    
    def __readData(self,packet,address):
        """This function receives the data from the listener thread and store
        the client address if already created else call the __readData of the handler
        """
        if self.handler != None:
            self.handler.__readData(packet,address)
        else:
            self.clientaddress = address            
    
    def bind(self, address):
        """This function is used to bind the server socket to the address

        Args:
            address ([tuple]): Contains the address of the server
        """
        self.address = address
        self.key = b''.join(self.address)
        self.sock.bind(address)
        self.isBinded = True
    
    def listen(self):
        """This function is used to make the server socket to listen 
        by creating a listener to the server by passing the socket to the constructor
        and start the thread.
        """
        if not self.isBinded:
            raise Exception("Socket is not found")
        self.isListening=True
        self.Listener = Listener(self) # make the listener for the server and passing the
                                       # self to the constructor
        # starting the listener
        self.Listener.start() 

    def accept(self):
        """This function accept the new connection and send the handler object to the 
           client so that it can access it
        """
        self.handler = self.__createHandler()
        return (self.handler,self.address)   

    def __createHandler(self): 
        """This function creates an handler for the client and send it back
        """
        return Handler(self,self.clientaddress,self.debug)
    
    def close(self):
        """This function closes the connection of the handler
        """
        self.isListening = False
        self.isClosed = False
        self.handler.close()  # calling the close method of the handler
        self.Listener.finish()
    
class Handler():
    def __init__(self,derudp,clientAddress,debug=False):
        self.sock = derudp.sock
        self.derudp = derudp
        self.debug = debug
        self.clientAddress = clientAddress
        self.seqSend = 0
        self.seqNext = 0
        self.isConnected = True
        self.runtimer = 0
        self.__sendSynAck()

    def __readData(self,packet,address):
        if self.debug:
            writeLog("Handler reading Data from {} and \n {}".format(address,packet))
        if packet.syn: # got the syn packet send synack
            self.__sendSynAck()
            return
        if packet.fin: # got the fin packet send finack
            self.__sendFinAck()
            return      

    def __sendSynAck(self):
        packet = Packet()
        packet.syn=1
        packet.ack=1
        if self.debug:
            writeLog("Send Syn Ack packet\n",packet)
        self.sock.sendto(packet.encode(),self.clientAddress)

    def __sendFinAck(self):
        packet = Packet()
        self.isConnected = False
        self.seqSend = self.seqNext
        packet.fin=1
        packet.ack=1
        if self.debug:
            writeLog("Send Fin Ack packet\n",packet)
        self.sock.sendto(packet.encode(),self.clientAddress)
    
    def __finAck(self):
        """This function finishes the timer and close the process
        """
        self.seqSend = self.seqNext
        if self.runtimer!=None and self.runtimer.running:
            self.runtimer.finish()
    
    def close(self):
        """This function closes the connection of handler
        """
        self.isClosed = True
        if self.isConnected:
            self.isConnected = False
    
    def __readData(self,packet,address):
        pass
    
    def __writeData(self,packet):
        pass
        
    def recv(self,maxBytes):
        pass
    
    def send(self,data):
        pass

    def timeout(self,data):
        pass