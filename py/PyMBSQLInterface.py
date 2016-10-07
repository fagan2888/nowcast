import pandas as pd
import sys
from msDbaseInterface import msDbInterface
from msDbaseInterface import msMBDbInterface
import win32com.client
import datetime
import logging


from win32timezone import TimeZoneInfo
import time
import pywintypes

try:


    '''    pytime = pywintypes.Time(time.time())
    pytime = (pytime.replace(tzinfo = TimeZoneInfo('GMT Standard Time', True)))

    pytimetuple = (pytime,)
    pytimetuplelist = [pytimetuple, pytimetuple, pytimetuple]
    print(pd.Series([x[0].replace(tzinfo=None) for x in pytimetuplelist]).apply(lambda x: datetime.datetime.strftime(datetime.datetime(x.year, x.month, x.day, x.hour, x.minute), '%Y-%m-%d %H:%M')))
    '''
    #print(map(lambda x: x.replace(tzinfo = None), pytimetuplelist))
    #print(pytimetuplelist.replace(tzinfo = None))
    #print("Done")

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
    print("HEERE!!")
    for num, indicator_key in enumerate(all_series):
        print("Num: {0} Indicator: {1}".format(num, indicator_key))
        ts = all_series[num]
        releaseName = ts.Metadata.GetFirstValue("Release")
        releaseEntity = d.FetchOneEntity(releaseName)

        current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
        print("\nCurrent: {0}".format(current_release))
        next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
        print("\nNext: {0}".format(current_release))
        if 'bea037_76a067rx_m' != str(indicator_key):
            print("\nAccess second part")
            #mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)
            mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)

except:
    print ("Unexpected error:", sys.exc_info()[0])
    raise

print("Got through")
