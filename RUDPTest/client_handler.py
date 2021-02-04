import socket
import time
from packet import Packet
from listener import Listener
from constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from timer import Timer
from collections import deque

class ClientHandler:
    # need to add the list for the queue number to be send 

    # this method is from read_data from the sender and calls the send_synack()
    def __init__(self, rudp, client_addr, debug):
        self.rudp = rudp
        self.sock = rudp.sock
        self.send_seq = 1
        self.recv_seq = 1
        self.write_buffer = deque()  # this has to be replaced with Queue {done}
        self.read_buffer = deque()  # this has to be replaced with Queue {done}
        self.timer = None
        self.client_addr = client_addr
        self.connected = True
        self.closed = False
        self.debug = debug
        self.send_synack()

    # this method is being called by init and create a packet and send the packet to client
    def send_synack(self):
        pckt = Packet()
        pckt.syn = 1
        pckt.ack = 1
        self.sock.sendto(pckt.encode(), self.client_addr)

    # this method is called to send the fin&ack packet to the client address
    def send_finack(self):
        self.connected = False
        self.write_buffer.clear() # this has to be replaced with Queue { clearing the queue}
        pckt = Packet()
        pckt.fin = 1
        pckt.ack = 1
        self.sock.sendto(pckt.encode(), self.client_addr)

    # this method is responsible for calling the send_synack, send_finack and finack
    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener and process
        '''
        if self.debug:
            print(pckt)
        # Handle SYN
        if pckt.syn: # if it get syn packet from the client it should send the ack for that syn
            self.send_synack()
            return
        
        # Handle FIN-ACK
        if pckt.fin and pckt.ack:  # fin and ack then it should terminate i guess..{got right} and make buffer to zero
            self.finack()
            return

        # Handle FIN
        if pckt.fin: # if it gets the fin packet from the client it should send the ack for that fin
            self.send_finack()
            return

        # If ACK packet (no piggy backed ack for now)
        # Discarding out of order packets for now
        if pckt.ack:
            count = pckt.ackno - self.send_seq
            self.write_buffer = deque(list(self.write_buffer)[count:]) # this has to be replaced with Queue { done}
            self.send_seq = pckt.ackno
        else:
            if pckt.seqno == self.recv_seq:
                self.read_buffer.append( pckt.payload )# this has to be replaced with Queue {done}
                self.recv_seq += 1
            pckt = Packet()
            pckt.ack = 1
            pckt.ackno = self.recv_seq
            self.sock.sendto(pckt.encode(), source_addr)
    
    # this function is same as the write function in the client{}
    def write(self, pckt):
        pckt.seqno = self.send_seq + len(self.write_buffer) # this has to be replaced with Queue
        self.sock.sendto(pckt.encode(), self.client_addr)
        self.write_buffer.append(pckt) # this has to be replaced with Queue {done}
        if self.timer == None or not self.timer.running:
            self.timer = Timer(self.timeout, TIMEOUT)
            self.timer.start()

    # this function is same as the timeout function in the client{}
    def timeout(self):
        if len(self.write_buffer) == 0: # this has to be replaced with Queue
            return
        for pckt in self.write_buffer:  # this has to be replaced with Queue
            self.sock.sendto(pckt.encode(), self.client_addr)
        self.timer = Timer(self.timeout, TIMEOUT)
        self.timer.start()

    # this function is same as the recv function in the client{}
    def recv(self, max_bytes):
        if self.closed:
            raise Exception("Socket closed")
        while True:
            if len(self.read_buffer) > 0:
                l = min(len(self.read_buffer), max_bytes) # this has to be replaced with Queue
                #data = self.read_buffer[:l]
                #self.read_buffer = self.read_buffer[l:] # this has to be replaced with Queue
                data = self.read_buffer.popleft()
                return data
            if not self.connected:
                return None
            time.sleep(POLL_INTERVAL)

    # this function is same as the send function in the client{}
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
            payload = data[:rem]
            data = data[rem:]
            pckt = Packet()
            pckt.payload = payload
            self.write(pckt)

    # this method just clears the write buffer and terminate the connection
    def finack(self):
        print('Received FIN-ACK')
        self.write_buffer.clear() # this has to be replaced with Queue {done}
        if self.timer != None and self.timer.running:
            self.timer.finish()

    # this function is same as the close function in the client{}
    def close(self):
        '''
        Close connection and release client handler
        '''
        self.read_buffer.clear() # this has to be replaced with Queue {done}
        self.closed = True
        if self.connected:
            self.connected = False
            # Wait till all data is sent
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
            pckt = Packet()
            pckt.fin = 1
            self.write(pckt)
            # Wait for fin-ack
            while len(self.write_buffer) > 0:
                time.sleep(POLL_INTERVAL)
        self.rudp.close_connection(self.client_addr)
