import logging
import time
import socket
import datetime
import os

## -- Set-up log -- ##
def mspLog(name:str, dev:bool=True):
    path = os.getcwd()
    if os.path.split(path)[1] != "Nowcast":
        path = os.path.split(path)[0]
        if os.path.split(path)[1] != "Nowcast":
            msg = "Error at {0}".format(path)
            raise ValueError(msg)
    now = datetime.datetime.now()

    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    if dev:
        log_filename = path + '\\logs\\{0:%Y-%m-%d}_{1:s}_DEV_logfile_{2:s}.log'.format(now, name, socket.gethostname())
        logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO, filemode='w')
    else:
        log_filename = path + '\\logs\\{0:%Y-%m-%d}_{1:s}_UAT_logfile_{2:s}.log'.format(now, name, socket.gethostname())
        logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
