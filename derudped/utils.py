<<<<<<< HEAD
import time
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
=======
import time
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
>>>>>>> 62fb2c8b4db22d5730f02d5abe185771a52773d3
    return