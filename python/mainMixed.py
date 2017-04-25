#!/bin/usr/python3
import logging
from datetime import datetime
import socket

if __name__ == "__main__":
    log_filename = 'C:\\Nowcast\\logs\\{1:%Y-%m-%d}_MSP_nowcast_logfile_{0:s}.log'.format(socket.gethostname(), datetime.now())
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

import numpy as np
import pandas as pd
import sys
import os
import configparser

from getData import getData
from dynFAMissing import dynFAMissing
from dfForecast import dfForecast
from insertResultsMySQL import insertResultsMySQL
from outputResults import outputResults
from investigateData import investigateData
from backtesting import backtesting

## -- Main script for the Dynamic Factor Now-Casting Model -- ##
class nowcastModel(object):
    def __init__(self, configPath = "/nowcast/config/", runModel=False):
        self.configPath = configPath
        self.getConfig()

        ## -- run the model -- ##
        if runModel:
            self.runModel()

    def getConfig(self):
        ## -- General Configurations -- ##
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        logging.info(self.config.sections())

    def getData(self):
        ## -- 1) Get the data -- ##
        logging.info("\nStep (1) Retrieve the data from the MySQL MacroSynergy db")
        self.data = getData(configPath =self.configPath)

    def runModel(self):
        ## -- get the data -- ##
        self.getData()

        ## -- 2) Estimate the Dynamic Factor Model -- ##
        logging.info("\nStep (2) Estimate the model")
        self.dfModel = dynFAMissing(Yvar=self.data.dataModel, options=self.data.options)

        ## -- Forecast and Nowcast the variables -- ##
        logging.info("\nForecast the series")
        self.forecast = dfForecast(model=self.dfModel, options=self.data.options)

        ## -- Generate the Output -- ##
        logging.info("\nGenerate the Output")

        ## -- Save the Results -- ##
        if self.config["model1"].getboolean("saveresultstodb"):
            print("\nSave Results")
            self.saveResultsToDb()

    def backTestModel(self, start = datetime.date(datetime(2000, 1, 1))):
        logging.info("\nBack test the model")
        backTest = backtesting( start = start )
        backTest.runBacktest(data = self.data.dataModel, options=self.data.options)
        ## PASS the history of updates / loop through datasets...
        ## resultsBacktest = BackTest(Y, datesData, options, variableNames, VarNames, dataPresent)

    def re_runForecasts(self):
        ## -- Flush all saved forecasts and re-run them all -- ##
        pass

    def saveResultsToDb(self):
            logging.info("\nSave the results to the MySQL database")
            self.saveMySQL = insertResultsMySQL(forecast=self.forecast, configPath = self.configPath)

    def plotResults(self):
        self.output = outputResults()
        self.output.plotAll(forecast=self.forecast, data=self.data, model=self.dfModel)


if __name__ == "__main__":
    print("\n\n=============\nNowCasting Model\n=============\n")
    if (os.getlogin() == "pnash"):
        os.chdir("Z:\\PNash\\My Documents\\Projects\\Nowcast\\")
    elif False:
        os.chdir("C:\\Nowcast\\")
    else:
        os.chdir("C:\\Nowcast\\")

    print("\nCurrent Work Directory: ", os.getcwd())
    model = nowcastModel(runModel=False)
    model.backTestModel()

    ## -- Investigate the data -- ##
    if False:
        investigateData(model.data)

    if False:
        model.plotResults()

    if False:
        ## -- Save data -- ##
        Ycommonf = model.forecast.Ycommonf["usnaac0169"]
        Ycommonf.rename(columns={"usnaac0169":"common"}, inplace=True)

        Yidiosyncraticf = model.forecast.Yidiosyncraticf["usnaac0169"]
        Yidiosyncraticf.rename(columns={"usnaac0169": "diosyncratic"}, inplace=True)

        Yf = model.forecast.Yf["usnaac0169"]
        Yf.rename(columns={"usnaac0169": "Yf"}, inplace=True)

        Ygdp = pd.concat((Yf, Ycommonf, Yidiosyncraticf), axis=1)
        Ygdp.rename(columns={0: "Yf", 1: "Common Component", 2: "Idiosyncratic Component"}, inplace=True)
        print(Ygdp)
        Ygdp.to_csv("tmp/GDP_forecast.csv")


    print("\n\nThat is all for now folks\n")
