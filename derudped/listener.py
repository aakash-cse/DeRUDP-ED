import socket
import threading,time
from .const import MAX_BYTES,POLL_INTERVAL
from .packet import Packet
class Listener(threading.Thread):
    """
        Listener class used to read the data from the socket and 
        return to its higher level implementation
    """
    def __init__(self, derudp_sock):
        threading.Thread.__init__(self)
        self.derudp_sock = derudp_sock
        self.isRunning = True
        
    def run(self):
        # make the socket to unblock for connection
        self.derudp_sock.sock.setblocking(False)
        # start listener
        while True:
            # Receive datagram
            try:
                msg, source_addr = self.derudp_sock.sock.recvfrom(MAX_BYTES)
                pckt = Packet(msg)
                self.derudp_sock.__readData(pckt, source_addr)
            except socket.error:
                time.sleep(POLL_INTERVAL)
            if not self.isRunning:
                return

    def done(self):
        self.isRunning = False

