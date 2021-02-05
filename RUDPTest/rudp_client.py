import socket
import time
from packet import Packet
from listener import Listener
from constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from timer import Timer
from collections import deque
import datetime 
from threading import Lock

class RUDPClient:
    # need to add the buffer queue for the retransmission and then another list for set of seqno for retransmission
    def __init__(self, debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_seq = 0
        self.recv_seq = 0
        self.write_buffer = deque()  # this has to be replaced with Queue
        self.read_buffer = deque()  # this has to be replaced with Queue
        self.mut = Lock()
        self.connected = False
        self.closed = False
        self.timer = None
        self.debug = debug

    # this is user calling function {done}
    def connect(self, address):
        # Create a SYN packet
        pckt = Packet()
        pckt.syn = 1
        self.listener = Listener(self)
        self.listener.start()
        self.server_addr = address
        self.write(pckt)
        # Wait till connection is established
        while not self.connected:
            time.sleep(POLL_INTERVAL)

    def synack(self):
        '''
        Called when client receives SYN-ACK from server
        '''
        if not self.connected:
            self.connected = True
            self.recv_seq += 1
            self.send_seq += 1
            self.write_buffer.popleft()   # this has to be replaced with Queue poping the left size

    def send_finack(self):
        self.connected = False
        self.write_buffer.clear()  # this has to be replaced with Queue
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.sock.sendto(pckt.encode(), self.server_addr)

    # called by listener thread and used to read the data packet to particular source_addr
    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener process
        Note: this function is upcalled by the listener thread
        '''
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)

        # Ignore unknown response
        if source_addr != self.server_addr:
            return
        
        # Handle SYN-ACK
        if pckt.ack and pckt.syn:
            self.synack()
            return
        
        # Handle FIN-ACK
        if pckt.ack and pckt.fin:
            self.finack()
            return

        # Handle FIN
        if pckt.fin:
            self.send_finack()
            return
        
        # If ACK packet (no piggy backed ack for now)
        # Discarding out of order packets for now
        if pckt.ack:
            count = pckt.ackno - self.send_seq
            if count <= 0:
                return
            # Access write buffer with mutex 
            self.mut.acquire()
            self.write_buffer = deque(list(self.write_buffer)[count:])   # this has to be replaced with Queue
            self.send_seq = pckt.ackno
            self.mut.release()
        else:
            if pckt.seqno == self.recv_seq:
                self.read_buffer.append(pckt.payload)    # this has to be replaced with Queue
                self.recv_seq += 1
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            self.sock.sendto(pckt.encode(), source_addr)

    def write(self, pckt):
        self.mut.acquire()
        pckt.seqno = self.send_seq + len(self.write_buffer) # this has to be replaced with Queue
        if self.debug:
            print(datetime.datetime.now().time())
            print("Packet sent:")
            print(pckt)
        self.write_buffer.append(pckt)  # this has to be replaced with Queue
        self.mut.release()
        self.sock.sendto(pckt.encode(), self.server_addr)
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    def timeout(self):
        if len(self.write_buffer) == 0: # this has to be replaced with Queue
            return
        for pckt in self.write_buffer:  # this has to be replaced with Queue
            if self.debug:
                print(datetime.datetime.now().time())
                print("Packet sent:")
                print(pckt)
            self.sock.sendto(pckt.encode(), self.server_addr)
        self.timer = Timer(self.timeout, TIMEOUT)
        self.timer.start()

    # this is user calling function {done}
    def recv(self, max_bytes):
        if self.closed:
            raise Exception("Socket closed")
        while True:
            if len(self.read_buffer) > 0:   # this has to be replaced with Queue
                l = min(len(self.read_buffer), max_bytes)   # this has to be replaced with Queue
                data = b''.join(list(self.read_buffer)[:l]) # this has to be replaced with Queue
                self.read_buffer = deque(list(self.read_buffer)[l:]) # this has to be replaced with Queue
                return data
            if not self.connected:
                return None
            time.sleep(POLL_INTERVAL)

    # this is user calling function {done}
    def send(self, data):
        '''
        Packetize the data and write
        '''
        if self.closed:
            raise Exception("Socket closed")
        if not self.connected:
            raise Exception("Peer disconnected")
        while len(data) > 0:
            rem = min(len(data), MAX_PCKT_SIZE)
            payload = data[:rem]    # this has to be replaced with Queue
            data = data[rem:]   # this has to be replaced with Queue
            pckt = Packet()
            pckt.payload = payload
            self.write(pckt)

    def finack(self):
        '''
        Assumption is that the server will stay active to send fin-ack even after 
        it has received fin twice
        '''
        self.write_buffer.clear()  # this has to be replaced with Queue
        if self.timer != None and self.timer.running:
            self.timer.finish()
        self.listener.finish()

    # this is user calling function
    def close(self):
        '''
        Close connection (Client initiates closing connection)
        '''
        # TODO: handle case when server disconnects without asking the FIN
        self.read_buffer.clear()  # this has to be replaced with Queue
        self.closed = True
        if self.connected:
            self.connected = False
            # Wait till all data is sent
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
            # send FIN-ACK
            pckt = Packet()
            pckt.fin = 1
            self.write(pckt)
            # Wait for FIN-ACK
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
        if self.timer != None and self.timer.running:
            self.timer.finish()
        self.listener.finish()
        time.sleep(2*POLL_INTERVAL)
