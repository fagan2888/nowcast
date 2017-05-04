#!/bin/usr/python3
import logging
import datetime
import socket

if __name__ == "__main__":
    now = datetime.datetime.now()
    log_filename = '/repos/Nowcast/logs/ms_forecasts_logfile_{0:s}_{1:%Y%m%d}.log'.format(socket.gethostname(), now)
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
import numpy as np
import pandas as pd
import os
import sys
from optparse import OptionParser
import platform
import configparser
import sqlalchemy
import argparse
import calendar
## Alternative to sqlalchemy
#import mysql.connector

class blpForecasts(object):
    def __init__(self, path:str = "/repos/Nowcast/", dev:bool=False):
        logging.info("Initiate the Bloomberg API")
        self.path = path
        self.dev = dev

        ## -- Config File -- ##
        self.getConfig()

        ## Move into individual files
        self.engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))


    def getConfig(self, path = "/repos/Nowcast/"):
        pathfile = path + 'config/configNowcasting.ini'
        self.config = configparser.ConfigParser()
        self.config.read(pathfile)
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = self.config[dbname].get("db_user")
        self.password = self.config[dbname].get("db_password")
        self.db_name = self.config[dbname].get("db_name")
        self.host = self.config[dbname].get("db_host")

    def getForecastTickers(self):
        query  = """SELECT\n count(*)\n FROM\n\t information_schema.tables"""
        query += """\nWHERE\n\t table_schema = '{0}'""".format(self.db_name)
        query += """\nAND\n\t table_name = '{0}';""".format("blp_fcst_meta")
        response = self.engine.execute(query)
        check = response.fetchall()[0]
        if (sum(check) == 0):
            print("Does not exists")
        elif (sum(check) == 1):
            print("Table exists")
        else:
            print("\nError too many values")




if __name__ == "__main__":
    print("\nMain File")
    try:
        forecasts = blpForecasts(dev=True)
        forecasts.getForecastTickers()
    except:
        msg = "Error in running the ETF program"
        logging.error(msg, exc_info=True)
