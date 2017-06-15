#!/bin/usr/python3
import logging
from datetime import datetime
import socket

from msp_Logging import mspLog
if __name__ == "__main__":
    mspLog(name="msNowcast")

import numpy as np
import pandas as pd
import sys
import os
import configparser
import sqlalchemy

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

        ## -- DATABASE -- ##
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = config[dbname].get("db_user")
        self.password = config[dbname].get("db_password")
        self.db_name = config[dbname].get("db_name")
        self.host = config[dbname].get("db_host")

    def runAllModels(self, saveResults:bool=True, productionCode:int=3):
        for model in self.modelID.keys():
            logging.info("Model {0}: {1}".format(model, self.modelID[model]))
            ## -- 1) Get the data -- ##
            logging.info("Step (1) Retrieve the data from the MySQL MacroSynergy db")
            dataModel, dataPresent, options = self.getData.getModelData(modelID = self.modelID[model])

            ## -- 2) Estimate the Dynamic Factor Model -- ##
            logging.info("Step (2) Estimate the model")
            self.dfModel = dynFAMissing(Yvar=dataModel, options=options)

            ## -- Forecast and Nowcast the variables -- ##
            logging.info("Step (3) Forecast the series")
            self.forecast = dfForecast(model=self.dfModel, options=options)

            ## -- Save the Results -- ##
            if saveResults:
                logging.info("Step (4) Save Results to MySQL")
                ## OBS ADD Model ID
                if self.dev:
                    productionCode = 1
                self.saveMySQL = insertResultsMySQL(forecast=self.forecast, configPath = self.configPath, dev=self.dev, modelID=self.modelID[model], productionCode=productionCode)
            logging.info("Step (5) All done for now")


    def runModel(self, model:str="benchmark", saveResults:bool=True, productionCode:int=3):
        ## -- 1) Get the data -- ##
        logging.info("Step (1) Retrieve the data from the MySQL MacroSynergy db")
        dataModel, dataPresent, options = self.getData.getModelData(modelID = self.modelID[model])

        ## -- 2) Estimate the Dynamic Factor Model -- ##
        logging.info("Step (2) Estimate the model")
        self.dfModel = dynFAMissing(Yvar=dataModel, options=options)

        ## -- Forecast and Nowcast the variables -- ##
        logging.info("Step (3) Forecast the series")
        self.forecast = dfForecast(model=self.dfModel, options=options)

        ## -- Save the Results -- ##
        if saveResults:
            logging.info("Step (4) Save Results to MySQL")
            ## OBS ADD Model ID
            if self.dev:
                productionCode = 1
            self.saveMySQL = insertResultsMySQL(forecast=self.forecast, configPath = self.configPath, dev=self.dev, modelID=self.modelID[model], productionCode=productionCode)
        logging.info("Step (5) All done for now")

    def backTestModel(self, start:datetime.date = datetime.date(datetime(2000, 1, 1))):
        ## PRODUCTION CODE = 2
        ## GET RELEASE DATES TO constrain information set from...
        query = "SELECT DISTINCT release_date FROM data WHERE release_date >= '{0:%Y-%m-%d}'".format(start)
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))
        connection = engine.connect()
        response = connection.execute(query)
        releaseDates = []
        for row in response:
            releaseDates.append(row["release_date"])
        response.close()

        for release in releaseDates:
            print(release)
            query = "SELECT indicator_id, value, period_date, vintage FROM data WHERE release_date = '{0}'".format(release)
            data= pd.read_sql(sql=query, con=engine)
            print(data.head())
            print(data["vintage"].unique())

            #response = connection.execute(query)
            #print(response.fetchone())
            #response.close()
        connection.close()


        ## for dd in release_dates...
        #backTest = backtesting( start = start )
        #backTest.runBacktest(data = self.data.dataModel, options=self.data.options)
        ## PASS the history of updates / loop through datasets...
        ## resultsBacktest = BackTest(Y, datesData, options, variableNames, VarNames, dataPresent)

    def re_runForecasts(self):
        ## -- Flush all saved forecasts and re-run them all -- ##
        pass


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

    if False:
        model.runModel(saveResults=True, model="harddata")
    if True:
        model.runAllModels(saveResults=True)

    print("\n\nThat is all for now folks\n")
