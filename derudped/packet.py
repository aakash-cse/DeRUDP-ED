class Packet:
    """
    Class for packet encoding and decoding with sequence number
    """
    def __init__(self,data=None):
        self.seqno = 0
        self.payload = b''
        self._delim = "|:|:|"
        if data:
            self.decode(data)
    
    def decode(self,data):
        self.seqno = int.from_bytes(data[:4],'big')
        self.payload = data[9:]
        
    def encode(self):
        data = b''
        data+=self.seqno.to_bytes(4,'big')
        data+=bytes(self._delim,"utf-8")
        data+=self.payload
        return data
    
    def __str__(self):
        s = "-" * 30 + "\n" + \
            f"Seqno: {self.seqno}, Payload: {self.payload}" + "\n" + \
            "-" * 30 + "\n"
        return s

def _dontRun():
    p = Packet(b'0001|:|:|Aakash') # this is how the data is manipulated
    print(p.encode())
    print(p.seqno,"\n",p._delim,"\n",p.payload)
    print(p.__str__)

