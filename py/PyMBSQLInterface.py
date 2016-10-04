import pandas as pd
import sys
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface
import win32com.client
import datetime
#def main():
try:


    #indicator_key = "usnaac0169"
    #c = win32com.client.Dispatch("Macrobond.Connection")
    #d = c.Database
    #ts = d.FetchOneSeries(indicator_key)
    #releaseName = ts.Metadata.GetFirstValue("Release")
    #releaseEntity = d.FetchOneEntity(releaseName)
    #current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
    #next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")

    #ts =  pd.read_csv("U:\\My Documents\\ussurv1459.csv")
    #ts.columns = ['Date', 'value']
    #indicator_key = 'ussurv1459'
    #current_release = '2016-08-01'
    #next_release = '2016-09-01'

    c = win32com.client.Dispatch("Macrobond.Connection")
    d = c.Database
    mb_up = msMBDbInterface(user = 'dbuser', password = 'Melbourne2016', host = 'mslinuxdb01', db_name = 'ms_econ_Db_DEV')
    indicators = mb_up.return_available_series()
    all_series = d.FetchSeries(indicators)
    for num, indicator_key in enumerate(all_series):
        ts = all_series[num]
        releaseName = ts.Metadata.GetFirstValue("Release")
        releaseEntity = d.FetchOneEntity(releaseName)
        current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
        next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
        if 'bea037_76a067rx_m' != str(indicator_key):
            mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)
except:
    print ("Unexpected error:", sys.exc_info()[0])
    raise
