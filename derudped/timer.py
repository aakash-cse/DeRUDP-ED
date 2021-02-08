<<<<<<< HEAD
import threading
import time

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
=======
import threading
import time

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
>>>>>>> 62fb2c8b4db22d5730f02d5abe185771a52773d3
