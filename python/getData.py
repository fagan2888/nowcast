#!/bin/usr/python3
import logging
import socket
import datetime
import os
if __name__ == "__main__":
    now = datetime.datetime.now()
    os.chdir("/repos/Nowcast/")
    log_filename = '/repos/Nowcast/logs/{0:%Y-%m-%d}_MS_Investigate_logfile_{1}.log'.format(now, socket.gethostname())
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

import numpy as np
import pandas as pd
import mysql.connector
import sys
import configparser
import traceback
import sqlalchemy

## MSP modules
from msDbaseInterface import msDbInterface


class getData(msDbInterface):
    def __init__(self, configPath:str='/repos/nowcast/config/', dev:bool=False):
        ## retweek to give model_id:int as input?
        self.configPath = configPath
        self.dev = dev
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)

    def getConfig(self):
        config = configparser.ConfigParser()
        config.read(self.configPath + 'configNowcasting.ini')

        ## -- DATABASE -- ##
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = config[dbname].get("db_user")
        self.password = config[dbname].get("db_password")
        self.db_name = config[dbname].get("db_name")
        self.host = config[dbname].get("db_host")

        ## -- MODELS -- ##
        self.modelID = {}
        for key in config["MODELS"]:
            self.modelID[key] = config["MODELS"].getint(key)

    def getModelData(self, modelID:int =1):
        ## OBS: Add model_id as input variable!
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        ## -- Get the Frequencies -- ##
        query  = "SELECT\n\tt1.indicator_id, t1.frequency_id, t2.transformation_code, t2.presentation_code"
        query += "\nFROM\n\tindicators AS t1"
        query += "\nLEFT JOIN\n\tmodel_indicators AS t2"
        query += "\nON\n\tt1.indicator_id = t2.indicator_id"
        query += "\nWHERE\n\t t2.model_id = {0}".format(modelID)
        query += "\nAND\n\tt2.indicator_id IS NOT NULL"
        query += "\nORDER BY\n\tt1.frequency_id ASC, t1.indicator_id ASC"
        query += "\n;"
        meta = pd.read_sql(sql=query, con=engine, index_col="indicator_id")

        ## -- Model options -- ##
        query  = "SELECT\nt2.variable_name, t1.control_values"
        query += "\nFROM\n\tmodel_controls AS t1"
        query += "\nLEFT JOIN\n\tcontrol_variables AS t2"
        query += "\nON\n\tt1.control_id = t2.variable_id\nWHERE\n\tt1.model_id =1\n;"
        response = engine.execute(query)
        options = {}
        for row in response:
            if (row["variable_name"] == "high") | (row["variable_name"] == "low"):
                options[row["variable_name"]] = row["control_values"]
            else:
                options[row["variable_name"]] = int(row["control_values"])
        options["NyQ"] = np.int64(np.sum(meta["frequency_id"] == 10))
        options["NyM"] = np.int64(np.sum(meta["frequency_id"] == 7))

        ## -- Get the data -- ##
        query  = """SELECT\n\t t1.indicator_id, t1.period_date, t1.value"""
        query += "\nFROM\n\tdata AS t1\nLEFT JOIN\n\tmodel_indicators AS t2"
        query += "\nON\n\tt1.indicator_id = t2.indicator_id"
        query += "\nWHERE\n\t t2.model_id = {0}".format(modelID)
        query += "\nAND\n\tt2.indicator_id IS NOT NULL\nAND\n\tt1.latest = 1"
        query += "\nAND\n\tyear(t1.period_date) > 1990\n;"
        data = pd.read_sql(sql=query, con=engine)
        data = data.pivot(columns="indicator_id", index="period_date", values="value")[meta.index.values]


        ## -- Transform the data -- ##
        dataModel = self.transformData(dataFrame=data, meta=meta, transform="transformation_code")
        dataPresent = self.transformData(dataFrame=data, meta=meta, transform="presentation_code")

        return dataModel, dataPresent, options

    def transformData(self, dataFrame:pd.core.frame.DataFrame, meta:pd.core.frame.DataFrame, transform:str="transformation_code"):
        data = dataFrame.copy()
        ## -- code 0: No transform (x_{t})-- ##

        ## -- code 1: log-transform (log(x_{t})-- ##
        select = meta[(meta[transform] == 1)].index
        data.ix[:, select] = np.log(data.ix[:, select])

        ## -- Code 2: 1month level differences (\Delta_{1}x_{t}) -- ##
        select = meta[(meta["transformation_code"] == 2)].index
        data.ix[:, select] = data.ix[:, select].diff(periods=1, axis=0)

        ## -- Code 3: 1month level differences (\Delta_{3}x_{t}) -- ##
        select = meta[(meta["transformation_code"] == 3)].index
        data.ix[:, select] = data.ix[:, select].diff(periods=3, axis=0)

        ## -- Code 4: 1month level differences (\Delta_{12}x_{t}) -- ##
        select = meta[(meta["transformation_code"] == 4)].index
        data.ix[:, select] = data.ix[:, select].diff(periods=12, axis=0)

        ## -- Code 5: MoM Growth rate (100 \Delta_{1}\log(x_{t})) -- ##
        select = meta[(meta["transformation_code"] == 5)].index
        data.ix[:, select] = 100*np.log(data.ix[:, select]).diff(periods=1, axis=0)

        ## -- Code 6: QoQ annualised (400\Delta_{3}\log(x_{t})) -- ##
        select = meta[(meta["transformation_code"] == 6)].index
        data.ix[:, select] = 400*np.log(data.ix[:, select]).diff(periods=3, axis=0)

        ## -- Code 7: Change of change (100 \Delta_{3}\Delta_{12}\log(x_{t})) -- ##
        select = meta[(meta["transformation_code"] == 7)].index
        data.ix[:, select] = 100*np.log(data.ix[:, select]).diff(periods=12, axis=0).diff(periods=3, axis=0)

        return data

    def forecastGDP(self):
        query = """
                SELECT
                    t1.period_date,
                    t1.mean_forecast,
                    t2.vendor_key,
                    t2.indicator_short_info, t3.forecast_type, t1.run_id, t6.presentation_unit, t5.timestamp, t5.run_date
                FROM
                    forecast_data t1
                    LEFT JOIN
                        (SELECT max(run_id) as run_id,max(timestamp) as timestamp, date_format(timestamp, '%Y-%m-%d') as run_date from run_table group by run_date) t5 ON (t5.run_id = t1.run_id)
                    LEFT JOIN (indicators t2) ON (t2.indicator_id = t1.indicator_id)
                    LEFT JOIN (forecast_types t3) ON (t3.forecast_type_id = t1.forecast_type_id)
                    LEFT JOIN (presentation_units t6) ON (t2.indicator_presentation = t6.unit_id)
                WHERE
                    vendor_key = 'usnaac0169'
                AND
                    t5.timestamp is not NULL
                ORDER BY
                    t5.run_date desc;
                """
        dataForecast = pd.read_sql(sql=query, con=self.cnx)
        return dataForecast

if __name__ == "__main__":
    print("main file")
    try:
        data = getData(dev=True)
        dataModel, dataPresent, options= data.getModelData()
        print(dataModel)
    except Exception as e:
        logging.info("Error in init: %s", e)
        raise

    #data.getModelData()
    #data.forecastGDP()
