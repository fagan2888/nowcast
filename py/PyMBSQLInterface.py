import numpy as np
import pandas as pd
import datetime
import mysql.connector
import win32com.client
import sys
import os.path
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface



''' try:
    cnx = mysql.connector.connect(user = 'dbuser', password = 'Melbourne2016', host =   'mslinuxdb01' , database = 'economic_database')
    cursor = cnx.cursor(buffered = True)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
'''

try:
    '''list = []
    query = """SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'economic_database' AND TABLE_NAME = 'data';"""
    cursor.execute(query)
    for column_name, in cursor:
        list.append(str(column_name))
        '''
    ts =  pd.read_csv("U:\\My Documents\\ussurv1459_mddle.csv")

    ts.columns = ['Date', 'value']  
   # tuple = [tuple(x) for x in ts.values]
  #  print(tuple)
   
    indicator_key = 'ussurv1459'
    current_release = '2016-09-01'
    next_release = '2016-10-01'
    mb_up = msMBDbInterface(user = 'dbuser', password = 'Melbourne2016', host = 'mslinuxdb01', db_name = 'economic_database')
    mb_up.upload_mb_data(ts, indicator_key,  current_release, next_release)

except:
    print ("Unexpected error:", sys.exc_info()[0])
    raise

