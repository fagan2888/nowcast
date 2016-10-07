import logging
import time
timestr = time.strftime("%Y%m%d-%H%M%S")
log_filename = 'C:\\Windows\\Temp\\MS_MacroB_Db_logfile_' + timestr + '.log'
FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

