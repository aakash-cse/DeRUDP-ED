class Packet():
    def __init__(self,payload):
        self.payload = payload
        self.seqno = 0

    # need to define the packet header(i think just seq no should be added) and udp to it...

class derudp():
    def __init__(self,sock):
        self.sock = sock
        self.connected = self.threewayhandshake()
        self.readQueue = []
        self.writeQueue = []
    
    def threewayhandshake(self):
        return True

    def loaddata(self):
        pass

    def terminate(self):
        pass

    def confirmPacket(self):
        pass
    
    def isLost(self):
        pass
    