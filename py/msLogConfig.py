import logging

log_filename = 'C:\\Windows\\Temp\\ms_Db_logfile.log'
FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

