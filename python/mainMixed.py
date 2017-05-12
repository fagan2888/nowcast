#!/bin/usr/python3
import logging
from datetime import datetime
import socket

if __name__ == "__main__":
    log_filename = '/repos/Nowcast/logs\\{1:%Y-%m-%d}_MSP_nowcast_logfile_{0:s}.log'.format(socket.gethostname(), datetime.now())
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

import numpy as np
import pandas as pd
import sys
import os
import configparser

## 00 Own Modules
from getData import getData
from dynFAMissing import dynFAMissing
from dfForecast import dfForecast
from insertResultsMySQL import insertResultsMySQL
from backtesting import backtesting

## -- Main script for the Dynamic Factor Now-Casting Model -- ##
class nowcastModel(object):
    def __init__(self, configPath:str = "/repos/Nowcast/config/", runModel:bool=False, dev:bool=False):
        self.configPath = configPath
        self.dev = dev
        self.getConfig()
        self.getData = getData(configPath =self.configPath, dev=dev)

    def getConfig(self):
        ## -- General Configurations -- ##
        config = configparser.ConfigParser()
        config.read(self.configPath + 'configNowcasting.ini')

        ## -- MODELS -- ##
        self.modelID = {}
        for key in config["MODELS"]:
            self.modelID[key] = config["MODELS"].getint(key)

    def runModel(self, model:str="benchmark", saveResults:bool=True):
        ## -- 1) Get the data -- ##
        logging.info("\nStep (1) Retrieve the data from the MySQL MacroSynergy db")
        dataModel, dataPresent, options = self.getData.getModelData(modelID = self.modelID[model])
        
        ## -- 2) Estimate the Dynamic Factor Model -- ##
        logging.info("\nStep (2) Estimate the model")
        self.dfModel = dynFAMissing(Yvar=dataModel, options=options)

        ## -- Forecast and Nowcast the variables -- ##
        logging.info("\nForecast the series")
        self.forecast = dfForecast(model=self.dfModel, options=options)

        ## -- Generate the Output -- ##
        logging.info("\nGenerate the Output")

        ## -- Save the Results -- ##
        if saveResults:
            logging.info("Save Results")
            self.saveResultsToDb()

    def backTestModel(self, start:datetime.date = datetime.date(datetime(2000, 1, 1))):
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
    else:
        os.chdir("/repos/Nowcast/")

    print("\nCurrent Work Directory: ", os.getcwd())
    model = nowcastModel(dev=True)

    if False:
        model.backTestModel()

    if True:
        model.runModel()

    print("\n\nThat is all for now folks\n")
