
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
