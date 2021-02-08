<<<<<<< HEAD
import socket
import time
from threading import Lock
from .aes import AESCipher
from .timer import Timer
from .listener import Listener
from .const import POLL_INTERVAL,MAX_BYTES,MAX_PCKT_SIZE,RWND,TIMEOUT
from .packet import Packet
from .utils import writeLog

class DerudpServer():
    def __init__(self,debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection = {}
        self.isBinded = False
        self.isListening = False
        self.isClosed = False
        self.debug = debug
        self.newConnection = []
        self.key = b''
        self.debug = debug

    def __readData(self,packet,address):
        """This function receives the data from the listener thread and store
        the client address if already created else call the __readData of the handler
        """
        if address in self.connection:
            self.connection[address].__readData(packet,address)
            return
        if packet.syn:
            if not self.isListening:
                return
            self.__newConnection(address)
            return
    
    def bind(self, address):
        """This function is used to bind the server socket to the address

        Args:
            address ([tuple]): Contains the address of the server
        """
        self.address = address
        self.key = '{}{}'.format(list(self.address)[0],list(self.address)[1])
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

    def __newConnection(self,clientAddress):
        """This function will create an new connection with the client address

        Args:
            clientAddress ([tuple]): 
        """
        self.connection[clientAddress] = Handler(self,clientAddress,debug=self.debug)
        self.newConnection.append(clientAddress)

    def accept(self):
        """This function accept the new connection and send the handler object to the 
           client so that it can access it
        """
        while True:
            if len(self.newConnection)>0:
                address = self.newConnection[0]
                self.newConnection = self.newConnection[1:]
                return self.connection[address],address
            time.sleep(POLL_INTERVAL)
    
    def close(self):
        """This function closes the connection of the handler
        """
        self.isListening = False
        self.isClosed = False
        for add in self.newConnection:
            nc = self.connection[add]
            nc.close()
        self.Listener.done()
    
    def close_connection(self, addr):
        '''
        Handle close upcall from client handler. Remove connection from data structure
        '''
        del self.connection[addr]
    
class Handler():
    def __init__(self,derudp,clientAddress,debug=False):
        self.sock = derudp.sock
        self.derudp = derudp
        self.debug = debug
        self.clientAddress = clientAddress
        self.seqSend = 0
        self.seqNext = 0
        self.seqReceived = 0
        self.mutexW = Lock()
        self.mutexR = Lock()
        self.isConnected = True
        self.runtimer = 0
        self.writeBuff = [None] * MAX_BYTES
        self.readBuff = b''
        self.order = [None] * MAX_BYTES
        self.buffer = 0
        self.key = derudp.key
        self.cipher = AESCipher(self.key)
        self.__sendSynAck()   

    def __sendSynAck(self):
        packet = Packet()
        packet.syn=1
        packet.ack=1
        if self.debug:
            writeLog("Send Syn Ack packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)

    def __sendFinAck(self):
        packet = Packet()
        self.isConnected = False
        self.seqSend = self.seqNext
        packet.fin=1
        packet.ack=1
        if self.debug:
            writeLog("Send Fin Ack packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)
    
    def __finAck(self):
        """This function finishes the timer and close the process
        """
        self.seqSend = self.seqNext
        if self.runtimer!=None and self.runtimer.isRunning:
            self.runtimer.done()
    
    def close(self):
        """This function closes the connection of handler
        """
        self.isClosed = True
        if self.isConnected:
            self.isConnected = False
            while self.seqSend < self.seqNext:
                time.sleep(POLL_INTERVAL)
            # send FIN
            packet = Packet()
            packet.fin = 1
            self.__writeData(packet)
            cnt = 0
            while self.seqSend < self.seqNext and cnt < 100: 
                time.sleep(POLL_INTERVAL)
                cnt += 1
        self.__finAck()
    
    def __writeData(self,packet):
        self.mutexW.acquire()
        packet.seqno = self.seqNext
        self.writeBuff[self.seqNext%MAX_BYTES] = packet
        self.seqNext+=1
        self.mutexW.release()
        if self.debug:
            writeLog("Written the data packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)
        if self.runtimer == None or not self.runtimer.isRunning:
            self.runtimer = Timer(self.timeoutcallback(),TIMEOUT)
            self.runtimer.start()
    
    def __readData(self,packet,address):
        """This function read the data from the 

        Args:
            packet ([Packet]): Data packet 
            address ([type]): clientAddress
        """
        if self.debug:
            writeLog("Packet received\n{}".format(packet))
        
        if self.clientAddress==address:
            if packet.syn:
                self.__sendSynAck()
                return
            if packet.fin and packet.ack:
                self.__finAck()
                return
            if packet.fin:
                self.__sendFinAck()
                return

            if packet.ack:
                if packet.seqno <= self.seqSend:
                    return
                self.mutexW.acquire()
                ite = self.seqSend % MAX_BYTES
                v = self.seqSend
                while self.seqSend<packet.ackno:
                    if self.writeBuff[ite]:
                        self.buffer -= len(self.writeBuff[ite].payload)
                    self.writeBuff[ite] = None
                    v+=1
                    ite+=1
                    if ite>=MAX_BYTES:
                        ite-=MAX_BYTES
                self.seqSend = v
                self.mutexW.release()
            else:
                ite = packet.seqno%MAX_BYTES
                if packet.seqno>=self.seqReceived:
                    if self.order[ite] == None:
                        self.order[ite] = packet
                    else:
                        self.dropped=1
                if packet.seqno == self.seqNext:
                    i = ite
                    data = b''
                    seq = packet.seqno
                    while 1:
                        if self.order[i] == None:
                            break
                        data +=self.order[i].payload
                        self.order[i] = None
                        i+=1
                        seq+=1    
                        if i>=MAX_BYTES:
                            i-=MAX_BYTES
                    self.mutexR.acquire()
                    self.readBuff+=data
                    self.seqReceived = seq
                    self.mutexR.release()
                packet = Packet()
                packet.ack = 1
                packet.ackno = self.seqReceived
                self.sock.sendto(packet.encode(),address)            

    def recv(self,maxBytes):
        while True:
            if len(self.readBuff) > 0:
                self.mutexR.acquire()
                l = min(len(self.readBuff), maxBytes)
                data = self.readBuff[:l]
                self.readBuff = self.readBuff[l:]
                self.mutexR.release()
                return data
            if not self.isConnected:
                return None
            time.sleep(POLL_INTERVAL)
    
    def send(self,data):
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
            self.__writeData(pckt)

    def timeoutcallback(self):
        """This function will be called as an callback for the timer thread

        Args:
            data ([Packet]): Packet in which the data is send format
        """
        # no packet to send
        if self.seqSend == self.seqNext:
            return
        cnt = 0
        i = self.seqSend
        idx = i % MAX_BYTES
        b = self.seqNext
        while i < b:
            if self.writeBuff[idx] == None:
                i += 1
                idx += 1
                if idx >= MAX_BYTES:
                    idx -= MAX_BYTES
                continue
            cnt += 1
            packet = self.writeBuff[idx]
            if self.debug:
                writeLog("Data sent\n{}".format(packet))
            self.sock.sendto(packet.encode(), self.clientAddress)
            if cnt >= RWND:
                break
            i += 1
            idx += 1
            if idx >= MAX_BYTES:
                idx -= MAX_BYTES
        # restart timer
        self.timer = Timer(self.timeoutcallback(), TIMEOUT)
=======
import socket
import time
from threading import Lock
from .aes import AESCipher
from .timer import Timer
from .listener import Listener
from .const import POLL_INTERVAL,MAX_BYTES,MAX_PCKT_SIZE,RWND,TIMEOUT
from .packet import Packet
from .utils import writeLog

class DerudpServer():
    def __init__(self,debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection = {}
        self.isBinded = False
        self.isListening = False
        self.isClosed = False
        self.debug = debug
        self.newConnection = []
        self.key = b''
        self.debug = debug

    def __readData(self,packet,address):
        """This function receives the data from the listener thread and store
        the client address if already created else call the __readData of the handler
        """
        if address in self.connection:
            self.connection[address].__readData(packet,address)
            return
        if packet.syn:
            if not self.isListening:
                return
            self.__newConnection(address)
            return
    
    def bind(self, address):
        """This function is used to bind the server socket to the address

        Args:
            address ([tuple]): Contains the address of the server
        """
        self.address = address
        self.key = '{}{}'.format(list(self.address)[0],list(self.address)[1])
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

    def __newConnection(self,clientAddress):
        """This function will create an new connection with the client address

        Args:
            clientAddress ([tuple]): 
        """
        self.connection[clientAddress] = Handler(self,clientAddress,debug=self.debug)
        self.newConnection.append(clientAddress)

    def accept(self):
        """This function accept the new connection and send the handler object to the 
           client so that it can access it
        """
        while True:
            if len(self.newConnection)>0:
                address = self.newConnection[0]
                self.newConnection = self.newConnection[1:]
                return self.connection[address],address
            time.sleep(POLL_INTERVAL)
    
    def close(self):
        """This function closes the connection of the handler
        """
        self.isListening = False
        self.isClosed = False
        for add in self.newConnection:
            nc = self.connection[add]
            nc.close()
        self.Listener.done()
    
    def close_connection(self, addr):
        '''
        Handle close upcall from client handler. Remove connection from data structure
        '''
        del self.connection[addr]
    
class Handler():
    def __init__(self,derudp,clientAddress,debug=False):
        self.sock = derudp.sock
        self.derudp = derudp
        self.debug = debug
        self.clientAddress = clientAddress
        self.seqSend = 0
        self.seqNext = 0
        self.seqReceived = 0
        self.mutexW = Lock()
        self.mutexR = Lock()
        self.isConnected = True
        self.runtimer = 0
        self.writeBuff = [None] * MAX_BYTES
        self.readBuff = b''
        self.order = [None] * MAX_BYTES
        self.buffer = 0
        self.key = derudp.key
        self.cipher = AESCipher(self.key)
        self.__sendSynAck()   

    def __sendSynAck(self):
        packet = Packet()
        packet.syn=1
        packet.ack=1
        if self.debug:
            writeLog("Send Syn Ack packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)

    def __sendFinAck(self):
        packet = Packet()
        self.isConnected = False
        self.seqSend = self.seqNext
        packet.fin=1
        packet.ack=1
        if self.debug:
            writeLog("Send Fin Ack packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)
    
    def __finAck(self):
        """This function finishes the timer and close the process
        """
        self.seqSend = self.seqNext
        if self.runtimer!=None and self.runtimer.isRunning:
            self.runtimer.done()
    
    def close(self):
        """This function closes the connection of handler
        """
        self.isClosed = True
        if self.isConnected:
            self.isConnected = False
            while self.seqSend < self.seqNext:
                time.sleep(POLL_INTERVAL)
            # send FIN
            packet = Packet()
            packet.fin = 1
            self.__writeData(packet)
            cnt = 0
            while self.seqSend < self.seqNext and cnt < 100: 
                time.sleep(POLL_INTERVAL)
                cnt += 1
        self.__finAck()
    
    def __writeData(self,packet):
        self.mutexW.acquire()
        packet.seqno = self.seqNext
        self.writeBuff[self.seqNext%MAX_BYTES] = packet
        self.seqNext+=1
        self.mutexW.release()
        if self.debug:
            writeLog("Written the data packet\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.clientAddress)
        if self.runtimer == None or not self.runtimer.isRunning:
            self.runtimer = Timer(self.timeoutcallback(),TIMEOUT)
            self.runtimer.start()
    
    def __readData(self,packet,address):
        """This function read the data from the 

        Args:
            packet ([Packet]): Data packet 
            address ([type]): clientAddress
        """
        if self.debug:
            writeLog("Packet received\n{}".format(packet))
        
        if self.clientAddress==address:
            if packet.syn:
                self.__sendSynAck()
                return
            if packet.fin and packet.ack:
                self.__finAck()
                return
            if packet.fin:
                self.__sendFinAck()
                return

            if packet.ack:
                if packet.seqno <= self.seqSend:
                    return
                self.mutexW.acquire()
                ite = self.seqSend % MAX_BYTES
                v = self.seqSend
                while self.seqSend<packet.ackno:
                    if self.writeBuff[ite]:
                        self.buffer -= len(self.writeBuff[ite].payload)
                    self.writeBuff[ite] = None
                    v+=1
                    ite+=1
                    if ite>=MAX_BYTES:
                        ite-=MAX_BYTES
                self.seqSend = v
                self.mutexW.release()
            else:
                ite = packet.seqno%MAX_BYTES
                if packet.seqno>=self.seqReceived:
                    if self.order[ite] == None:
                        self.order[ite] = packet
                    else:
                        self.dropped=1
                if packet.seqno == self.seqNext:
                    i = ite
                    data = b''
                    seq = packet.seqno
                    while 1:
                        if self.order[i] == None:
                            break
                        data +=self.order[i].payload
                        self.order[i] = None
                        i+=1
                        seq+=1    
                        if i>=MAX_BYTES:
                            i-=MAX_BYTES
                    self.mutexR.acquire()
                    self.readBuff+=data
                    self.seqReceived = seq
                    self.mutexR.release()
                packet = Packet()
                packet.ack = 1
                packet.ackno = self.seqReceived
                self.sock.sendto(packet.encode(),address)            

    def recv(self,maxBytes):
        while True:
            if len(self.readBuff) > 0:
                self.mutexR.acquire()
                l = min(len(self.readBuff), maxBytes)
                data = self.readBuff[:l]
                self.readBuff = self.readBuff[l:]
                self.mutexR.release()
                return data
            if not self.isConnected:
                return None
            time.sleep(POLL_INTERVAL)
    
    def send(self,data):
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
            self.__writeData(pckt)

    def timeoutcallback(self):
        """This function will be called as an callback for the timer thread

        Args:
            data ([Packet]): Packet in which the data is send format
        """
        # no packet to send
        if self.seqSend == self.seqNext:
            return
        cnt = 0
        i = self.seqSend
        idx = i % MAX_BYTES
        b = self.seqNext
        while i < b:
            if self.writeBuff[idx] == None:
                i += 1
                idx += 1
                if idx >= MAX_BYTES:
                    idx -= MAX_BYTES
                continue
            cnt += 1
            packet = self.writeBuff[idx]
            if self.debug:
                writeLog("Data sent\n{}".format(packet))
            self.sock.sendto(packet.encode(), self.clientAddress)
            if cnt >= RWND:
                break
            i += 1
            idx += 1
            if idx >= MAX_BYTES:
                idx -= MAX_BYTES
        # restart timer
        self.timer = Timer(self.timeoutcallback(), TIMEOUT)
>>>>>>> 62fb2c8b4db22d5730f02d5abe185771a52773d3
        self.timer.start()