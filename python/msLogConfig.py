import logging
import time
import socket

timestr = time.strftime("%Y%m%d")
log_filename = 'C:\\Windows\\Temp\\MS_MacroB_Db_logfile_' + socket.gethostname() + '_' + timestr + '.log'
FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
