import socket
import time
import threading, time
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

# constants 
MAX_BYTES = 90000 # 65535 should be less than receiver buffer size
MAX_PCKT_SIZE = 1460
POLL_INTERVAL = 0.1 # 10 polls / sec
HEADER_SIZE = 9
TIMEOUT = 0.2 # seconds
RWND = 10 # Retransmission window size (maximum no of packets to be retransmitted after timeout)

#Packet class
class Packet():
    """
        Class Definition of the packet
    """
    def __init__(self, data=None):
        self.seqno = 0
        self.ackno = 0
        self.syn = 0
        self.ack = 0
        self.fin = 0
        self.payload = b''
        if data:
            self.decode(data)

    def decode(self, data):
        f = data[0]
        self.syn = int((f & 4) > 0)
        self.ack = int((f & 2) > 0)
        self.fin = int((f & 1) > 0)
        self.seqno = int.from_bytes(data[1:5], 'big')
        self.ackno = int.from_bytes(data[5:9], 'big')
        self.payload = data[9:]

    def encode(self):
        '''
        Returns:
            binary encoded packet with required flags
        '''
        # flag format SYN | ACK | FIN
        syn = self.syn
        syn <<= 2
        ack = self.ack
        ack <<= 1
        fin = self.fin
        f = syn | ack | fin
        data = b''
        data += f.to_bytes(1, 'big')
        data += self.seqno.to_bytes(4, 'big')
        data += self.ackno.to_bytes(4, 'big')
        data += self.payload
        return data
    
    def __str__(self):
        s = "-" * 30 + "\n" + \
            f"SYN: {self.syn}, ACK: {self.ack}, FIN: {self.fin}" + "\n" + \
            f"Seqno: {self.seqno}, Ackno: {self.ackno}" + "\n" + \
            "-" * 30 + "\n"
        return s

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
        self.derudp_sock.sock.setblocking(0)
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

class AESCipher():
    """Used to encrypt and decrypt the data send into the packets
    """
    def __init__(self, key="key"): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class Timer(threading.Thread):
    """
        Timer class for the calculation of time using threading
    """
    def __init__(self, callback, seconds):
        """
            Constructor for the timer class
        """
        threading.Thread.__init__(self)
        self.callback = callback
        self.isRunning = True
        self.seconds = seconds

    def run(self):
        """
            Thread function used to initiate the thread => called using start()
        """
        time.sleep(self.seconds)
        if self.isRunning:
            self.callback()
        self.isRunning = False
    
    def done(self):
        """Finish will set the running flag to false
        """
        self.isRunning = False

def writeLog(log_data):
    """Function used to write the log in the log file for debugging

    Args:
        log_data ([string]): data to be written on the logfile.txt
    """
    
    f = open(r'Log.txt', 'a+')
    secondsSinceEpoch = time.time()
    timeObj = time.localtime(secondsSinceEpoch)
    time_stamp = str(('%d/%d/%d %d:%d:%d' % (
        timeObj.tm_mday, timeObj.tm_mon, timeObj.tm_year, timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec)))
    f.write(time_stamp+'  '+log_data+' '+'\n')
    return