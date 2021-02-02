import time

def writeLog(log_data):        # writes log
    f = open(r'Log.txt', 'a+')
    secondsSinceEpoch = time.time()
    timeObj = time.localtime(secondsSinceEpoch)
    time_stamp = str(('%d/%d/%d %d:%d:%d' % (
        timeObj.tm_mday, timeObj.tm_mon, timeObj.tm_year, timeObj.tm_hour, timeObj.tm_min, timeObj.tm_sec)))
    f.write(time_stamp+'  '+log_data+' '+'\n')
    return

"""
class ThreeWayHandshake:

    def __init__(self, twh=None):

        self.status = None
        self.connected = False

    def Connection(self):
        if self.status == None:
            print("starting 3-way handshake", "status: sync", sep="\n")
            self.status = "sync"
        elif self.status == "sync":
            print("sync received", "status: ack-sync", sep="\n")
            self.status = "ack-sync"
        elif self.status == "ack-sync":
            print("ack-sync received", "status: ack", sep="\n")
            self.status = "ack"
        elif self.status == "ack":
            self.connected = True
            print("connected.", "ready to received data.", sep="\n")

    def IsConnected(self):
        return self.connected

    def Reset(self):
        self.status = None
        self.connected = False

    def __str__(self):
        return f"status: {self.status}, connection established: {self.connected}."


'''
flag = threewayhandshake()
if flag:
    loadData() => it will load the data into the queue and ready to send the packets
    sendData()
    terminate()
terminate():
    if data lost:
        get lost data number
        sendData()
        terminate()
    else:
        reorganise()
        exit()
'''
"""
