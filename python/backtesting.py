import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime

from dynFAMissing import dynFAMissing
from dfForecast import dfForecast
from backtestSaveResultsMySQL import backtestResultsMySQL

class backtesting(object):
    def __init__(self, configPath = "python\\model\\config\\", start = datetime.date(datetime(2000,1,1))):
        self.start = start
        self.configPath = configPath
        self.uploadMySQL = backtestResultsMySQL()

    def getConfig(self):
        ## -- General Configurations -- ##
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        logging.info(self.config.sections())

    def runBacktest(self, data, options):
        nyM = options["nyM"]
        datatmp = data.copy()
        datatmp[datatmp.index >= self.start] = np.nan


        for TT in data[data.index >= self.start].index:
            print("\n\n{0}\nDate: {1:%Y-%m-%d}\n{0}".format("-"*50, TT))
            for num, nn in enumerate(list(data)):
                run_id = "{0:%Y-%m-%d}_{1}".format(TT, num+1)
                print("\nrun_id: {0:s}".format(run_id))
                runModel = False
                FILTER = (data.index <= TT)

                if (num+1 <= nyM):
                    datatmp.ix[TT, nn] = data.ix[TT, nn]
                    runModel = True
                    #print("{0}, {1:d}, {2:s}: {3:d}".format(TT, num+1, nn, data[FILTER].shape[0]))
                elif (num+1 > nyM) & (TT.month % 3 == 0):
                    datatmp.ix[TT, nn] = data.ix[TT, nn]
                    runModel = True

                if runModel:
                    print("Model ran: {0}, {1:s}: {2:d}".format(TT, nn, data[FILTER].shape[0]))
                    dfModel = dynFAMissing(Yvar=datatmp[FILTER], options=options)
                    forecast = dfForecast(model=dfModel, options=options)
                    self.uploadMySQL.uploadResults(forecast=forecast, run_id=run_id, options=options)

if __name__ =="__main__":
    print("Main file: {0}".format(__file__))
    bt = backtesting()
    print(bt.start)
