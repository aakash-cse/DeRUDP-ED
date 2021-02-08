from threading import Thread
import time

class Timer(Thread):
    """
        Timer class for the calculation of time using threading
    """
    def __init__(self, callback, seconds):
        """
            Constructor for the timer class
        """
        Thread.__init__(self)
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