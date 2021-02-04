import socket
import time
from packet import Packet
from listener import Listener
from constants import MAX_PCKT_SIZE, POLL_INTERVAL, TIMEOUT
from timer import Timer
from client_handler import ClientHandler

class RUDPServer:
    # Nothing to change the queue in this only rudp_client.py and client_handler.py
    '''
    Server class to:
        1. listen for connection requests
        2. demultiplex data to different connections
        3. open new connections
    '''
    def __init__(self, debug=False):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = {}
        self.binded = False
        self.listening = False
        self.closed = False
        self.new_connections = []
        self.debug = debug

    # able to understand the code of read_data => read_data calls new_connection 
                                    # if syn packet is received {done}
    def read_data(self, pckt, source_addr):
        '''
        Receive data from listener and process
        '''
        # FIN packet from previous connections (?)
        # if pckt.fin and not pckt.ack:
        #     pckt = Packet()
        #     pckt.fin = 1
        #     pckt.ack = 1
        #     self.sock.sendto(pckt.encode(), source_addr)
        #     return
        
        # Forward packet to handler if connection is already present
        if source_addr in self.connections:
            self.connections[source_addr].read_data(pckt, source_addr)
            return

        # New connection
        if pckt.syn:
            if not self.listening:
                return
            self.new_connection(source_addr)
            return

    # this is user calling function {done}
    def bind(self, address):
        self.sock.bind(address)
        self.binded = True

    # this is user calling function => activate listener and calls read_data{done}
    def listen(self):
        if not self.binded:
            raise Exception("Socket not binded")
        self.listening = True
        self.listener = Listener(self)
        # Start listening
        self.listener.start()

    # this function add the entry to the connection dictionary and create a client handler object
    def new_connection(self, client_addr):
        '''
        Handle new connection
        Args:
            client_addr: Address of new client
        '''
        self.connections[client_addr] = ClientHandler(self, client_addr, debug=self.debug)
        self.new_connections.append(client_addr)

    # this is user calling function    {done}
    def accept(self):
        '''
        Accepts new connection
        Returns:
            handler, client address
        '''
        while True:
            if len(self.new_connections) > 0:
                addr = self.new_connections[0]
                self.new_connections = self.new_connections[1:]
                return self.connections[addr], addr
            time.sleep(POLL_INTERVAL)

    # this is user calling function
    def close(self):
        '''
        stop listening for new connections
        '''
        self.listening = False
        self.closed = False
        # close all unaccepted connections
        for addr in self.new_connections:
            nc = self.connections[addr]
            nc.close()
        self.listener.finish()
        
    def close_connection(self, addr):
        '''
        Handle close upcall from client handler. Remove connection from data structure
        '''
        del self.connections[addr]
        