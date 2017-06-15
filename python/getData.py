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
        query  = """SELECT t1.indicator_id, t3.frequency_id, t2.transformation_code, t2.presentation_code
                FROM data_indicators AS t1
                LEFT JOIN model_indicators AS t2
                ON t1.indicator_id = t2.indicator_id
				LEFT JOIN data_variable_id AS t3
				ON t1.variable_id = t3.variable_id
                WHERE t2.model_id = {0}
                AND t2.indicator_id IS NOT NULL
                ORDER BY t3.frequency_id ASC, t1.indicator_id ASC
                ;""".format(modelID)

        meta = pd.read_sql(sql=query, con=engine, index_col="indicator_id")

        ## -- Model options -- ##
        query  = """SELECT t2.variable_name, t1.control_values
                FROM model_controls AS t1
                LEFT JOIN meta_control_variables AS t2
                ON t1.control_id = t2.variable_id
                WHERE t1.model_id = {0};""".format(modelID)
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
        query  = """SELECT t1.indicator_id, t1.period_date, t1.value
                FROM data_values AS t1 LEFT JOIN model_indicators AS t2
                ON t1.indicator_id = t2.indicator_id
                WHERE t2.model_id = {0}
                AND t2.indicator_id IS NOT NULL AND t1.latest = 1
                AND year(t1.period_date) > 1990;""".format(modelID)
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
        #data.ix[:, select] = 100*np.log(data.ix[:, select]).diff(periods=1, axis=0)
        data.ix[:, select] = 100*data.ix[:, select].pct_change(periods=1)

        ## -- Code 6: QoQ annualised (400\Delta_{3}\log(x_{t})) -- ##
        select = meta[(meta["transformation_code"] == 6)].index
        #data.ix[:, select] = 400*np.log(data.ix[:, select]).diff(periods=3, axis=0)
        data.ix[:, select] = 400*data.ix[:, select].pct_change(periods=3)

        ## -- Code 7: Change of change (100 \Delta_{3}\Delta_{12}\log(x_{t})) -- ##
        select = meta[(meta["transformation_code"] == 7)].index
        #data.ix[:, select] = 100*np.log(data.ix[:, select]).diff(periods=12, axis=0).diff(periods=3, axis=0)
        data.ix[:, select] = 100*data.ix[:, select].pct_change(periods=12).diff(periods=3, axis=0)

        return data

    def forecastGDP(self):
        query = """
        SELECT
            t1.run_id, t1.period_date, t1.mean_forecast,
            t2.vendor_key,
            t3.variable_name,
            t4.forecast_type,
            t5.timestamp,
            t6.timestamp
        FROM
            output_forecast_data AS t1
            LEFT JOIN
                (SELECT max(run_id) as run_id, max(timestamp) as timestamp, date_format(timestamp, '%Y-%m-%d') AS run_date FROM output_run_table GROUP BY run_date) AS t6 ON (t6.run_id = t1.run_id)
            LEFT JOIN (data_indicators AS t2) ON (t2.indicator_id = t1.indicator_id)
            LEFT JOIN (data_variable_id AS t3) ON (t3.variable_id = t2.variable_id)
            LEFT JOIN (meta_forecast_types AS t4) ON (t4.forecast_type_id = t1.forecast_type_id)
            LEFT JOIN (output_run_table AS t5) ON (t5.run_id = t1.run_id)
        WHERE
            t2.vendor_key = 'usnaac0169'
        AND
            t5.timestamp is not NULL
        ORDER BY
            t6.run_date desc;"""
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
