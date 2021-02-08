import socket
from threading import Thread
import time
from .const import MAX_BYTES,POLL_INTERVAL
from .packet import Packet
class Listener(Thread):
    """
        Listener class used to read the data from the socket and 
        return to its higher level implementation
    """
    def __init__(self, derudp_sock):
        Thread.__init__(self)
        self.derudpSock = derudp_sock
        self.isRunning = True
        
    def run(self):
        # make the socket to unblock for connection
        self.derudpSock.sock.setblocking(False)
        # start listener
        while True:
            # Receive datagram
            try:
                msg, source_addr = self.derudpSock.sock.recvfrom(MAX_BYTES)
                pckt = Packet(msg)
                self.derudpSock.__readData(pckt, source_addr)
            except socket.error:
                time.sleep(POLL_INTERVAL)
            if not self.isRunning:
                return

    def done(self):
        self.isRunning = False

