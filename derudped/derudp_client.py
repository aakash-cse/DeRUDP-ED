import socket
import time
from threading import Lock
from .aes import AESCipher
from .timer import Timer
from .listener import Listener
from .const import POLL_INTERVAL,MAX_BYTES,MAX_PCKT_SIZE,RWND,TIMEOUT
from .packet import Packet
from .utils import writeLog

class DerudpClient():
    def __init__(self,debug=False):
        """
        class definition of our custom derudpclient| sender 
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.seqSend = 0
        self.seqNext = 0
        self.seqReceived = 0
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
        self.key = '{}{}'.format(list(self.serverAddress)[0],list(self.serverAddress)[1])
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
        this includes the getting the mutex lock and release and change the sequence number

        Args:
            packet ([Packet]): Contains the custom UDPdata
        """
        self.mutexW.acquire()
        packet.seqno = self.seqNext
        self.writeBuff[self.seqNext%MAX_BYTES] = packet
        self.seqNext = self.seqNext+1
        self.mutexW.release()
        if self.debug:
            writeLog("Packet sent:\n{}".format(packet))
        self.sock.sendto(packet.encode(),self.serverAddress)
        if self.timer == None or not self.timer.isRunning:
            self.timer = Timer(self.timeoutcallback,TIMEOUT)
            self.timer.start()
    def __sendfinAck(self):
        """This function will send the fin-Ack to the server that it got fin packet
        """
        packet = Packet()
        packet.fin=1
        packet.ack=1
        self.isConnected = False
        self.seqSend = self.seqNext
        self.sock.sendto(packet.encode(),self.serverAddress)

    def __SynAck(self):
        """This funciton will read the syn-ACk packet from the server and clear the buffer
        """
        if  self.isConnected:
            return 
        else:
            self.writeBuff[0] = None
            self.isConnected = True
            self.seqReceived+=1
            self.seqSend +=1

    def __readData(self,packet,address):
        """This function is used to read the packet from the address

        Args:
            packet ([Packet]): Contains the custom UDPdata
            address ([tuple]): Contains the server address as a tuples
        """
        if self.debug:
            writeLog("Packet received \n{}".format(packet))
        if self.serverAddress==address:
            if packet.fin:
                self.__SynAck()
                return
            if packet.fin and packet.ack:
                self.__sendfinAck()
                return
            if packet.syn and packet.ack:
                self.__SynAck()
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

    def timeoutcallback(self):
        """This function is used as the callback for the timeoutevent
        """
        if self.seqSend == self.seqNext:
            return
        cnt = 0
        i = self.seqSend
        idx = i % MAX_BYTES
        b = self.seqNext
        # retransmission of unacked packets
        while i < b:
            # packet already acked
            if self.writeBuff[idx] == None:
                i += 1
                idx += 1
                if idx >= MAX_BYTES:
                    idx -= MAX_BYTES
                continue
            cnt += 1
            packet = self.writeBuff[idx]
            if self.debug:
                writeLog("Packet Send\n{}".format(packet))
            self.sock.sendto(packet.encode(), self.serverAddress)
            if cnt >= RWND:
                break
            i += 1
            idx += 1
            if idx >= MAX_BYTES:
                idx -= MAX_BYTES
        self.timer = Timer(self.timeoutcallback(), TIMEOUT)
        self.timer.start()

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
            self.__writeData(pckt)
    
    def recv(self,max_bytes):
        """This function is called by end user to receive the 
        data packet form the server
        """
        if self.isClosed:
            raise Exception("Socket is closed")
        while True:
            if len(self.readBuff) > 0:
                self.mutexR.acquire()
                l = min(len(self.readBuff), max_bytes)
                data = self.readBuff[:l]
                self.readBuff = self.readBuff[l:]
                self.mutexR.release()
                return self.cipher.decrypt(data)

            if not self.isConnected:
                return None
            time.sleep(POLL_INTERVAL)
        

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
    
    def __finAck(self):
        """This funciton will perform clean up as close function is already called
        """
        self.seqSend = self.seqNext
        if self.timer!=None and self.timer.isRunning:
            self.timer.done()
        self.Listener.done()

