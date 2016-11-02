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

    logging.info("Opening Db Connection within Service")

    now = datetime.datetime.now()
    data_correct = True
    incomplete_indicators = mb_up.find_incorrect_release_dates()
    if incomplete_indicators:
        for indicator in incomplete_indicators:
            c = win32com.client.Dispatch("Macrobond.Connection")
            d = c.Database
            ts = d.FetchOneSeries(str(indicator[0]))
            releaseName = ts.Metadata.GetFirstValue("Release")
            releaseEntity = d.FetchOneEntity(releaseName)
            current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
            next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
            success = False
            if next_release:
                success = mb_up.fix_incomplete_indicator(indicator, next_release)
                
            if not success:
                data_correct = False
            if not data_correct:
                timeout = 1000 * 60  * 60 # 1s * 60 * 60 = 1hr

    next_release = mb_up.next_release_date()[0]
    logging.info("Next release: %s", str(next_release))
    if next_release < now:
        indicator_updates = mb_up.available_updates()
    else:
    # No updates, wait until next release time until checking again.
        indicator_updates = []
        time_diff = next_release - now
        error_margin = 600000
        if data_success:
            timeout = time_diff.total_seconds() * 1000 + error_margin


    indicators = mb_up.return_available_series()
    all_series = d.FetchSeries(indicators)
    for num, indicator_key in enumerate(all_series):
        ts = all_series[num]
        releaseName = ts.Metadata.GetFirstValue("Release")
        releaseEntity = d.FetchOneEntity(releaseName)
        current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
        next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
        if not next_release:
            next_release = pywintypes.Time(0).replace(year=1900, month=1, day=1)
        
        mb_up.upload_mb_data(ts, str(indicator_key),  current_release, next_release)

except:
    print ("Unexpected error:", sys.exc_info()[0])
    raise

print("Got through")
