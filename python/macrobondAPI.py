## Python Script to Download Data from Macrobond
import numpy as np
import pandas as pd
import win32com.client
import sys
import os
import datetime
from win32timezone import TimeZoneInfo
import time
import pywintypes
import logging
import traceback

class MacrobondInterface(object):
    __name__ = "MacrobondAPI"

    def __init__(self):
        self.connectMacrobond()

    def connectMacrobond(self):
        self.c = win32com.client.Dispatch("Macrobond.Connection")
        self.d = self.c.Database

    def closeMacrobond(self):
        self.c.Close()

    def GetData(self, indicator):
        logging.info("\nIndicator: {0}".format(indicator))
        exists = False
        try:
            ts = self.d.FetchOneSeries(str(indicator))
            tmp = self.TimeSeries(timeseries=ts, col_name="value")

            releaseName = ts.Metadata.GetFirstValue("Release")
            releaseEntity = self.d.FetchOneEntity(releaseName)
            current_release = releaseEntity.Metadata.GetFirstValue("LastReleaseEventTime")
            next_release = releaseEntity.Metadata.GetFirstValue("NextReleaseEventTime")
            if not next_release:
                next_release = pywintypes.Time(0).replace(year=1900, month=1, day=1)
            exists = True
            return exists, tmp
        except:
            logging.info("\nTime series {0} does not exists".format(indicator))
            logging.warning(traceback.format_exc())
            return exists, None

    def TimeSeries(self, timeseries, col_name):
        tmp = pd.DataFrame()
        tmp[col_name] = pd.Series(timeseries.Values)
        tmp['period_date'] = pd.Series([t.replace(tzinfo=None) for t in timeseries.DatesAtEndOfPeriod]).apply(lambda x: datetime.datetime.strftime(datetime.datetime(x.year, x.month, x.day), '%Y-%m-%d'))
        return tmp

    def getBoPBalance(self):
        listNames = [
        	"gbbopa00102", # Current Account, UK, ONS, GBP, SA
        	"gbbopa00692", # Capital Account, UK, ONS, GBP, SA
            "gbbopa00982", # Financial Account, Net Transactions, UK, ONS
            "gbbopa00792", # Financial Account, Reserves, UK, ONS
        	"gbbopa02022"  # Errors and Omissions, UK, ONS, GBP
        	]

        store = []
        exists = []
        for ii in listNames:
            dataExists, data  = self.GetData(indicator = ii)

            if dataExists:
                store.append(data)
            exists.append(dataExists)

        data = pd.concat(store)

        data.set_index("period_date", inplace=True)
        #data["gbbopa00982"] = - data["gbbopa00982"]
        #data["gbbopa00792"] = - data["gbbopa00792"]
        logging.info("\nCheck Balance")
        logging.info(data.sum(axis=1))
        logging.info(all(exists))
        return data

if __name__ == "__main__":
    print("\nMain file")
    api = MacrobondInterface()
    data = api.getBoPBalance()
    print(data)
