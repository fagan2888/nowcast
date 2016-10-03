import pandas as pd
import sys
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface

def main():
    try:
        ts =  pd.read_csv("U:\\My Documents\\ussurv1459.csv")

        ts.columns = ['Date', 'value']  
   
        indicator_key = 'ussurv1459'
        current_release = '2016-08-01'
        next_release = '2016-09-01'
        mb_up = msMBDbInterface(user = 'dbuser', password = 'Melbourne2016', host = 'mslinuxdb01', db_name = 'economic_database')
        mb_up.upload_mb_data(ts, indicator_key,  current_release, next_release)

    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise

