import numpy as np
import pandas as pd
import mysql.connector
import mysql
from sqlalchemy import create_engine
import sys
import logging
import time
import socket
import configparser
import os
import sys
import re
import logging

sys.path.append(os.getcwd()[:-len("DevelopmentModel\\python\\model")] + "Db\\py\\")
from msDbaseInterface import msDbInterface

class insertResultsMySQL (msDbInterface):
    __version__ = "0.0.2"
    __name__ = "__insertResultsMySQL__"

    def __init__(self, forecast, configPath = "python\\model\\config\\"):
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)
        self.uploadResults(forecast=forecast)

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        self.user = self.config["DATABASE"].get("db_user")
        self.password = self.config["DATABASE"].get("db_password")
        self.db_name = self.config["DATABASE"].get("db_name")
        self.host = self.config["DATABASE"].get("db_host")

    def uploadResults(self, forecast):
        ## -- Results: Mean Forecast -- ##
        Yf = forecast.Yf.unstack().reset_index()
        Yf.rename(columns={"level_0": "vendor_key", "level_1": "period_date", 0: "mean_forecast"}, inplace=True)

        ## -- Low forecast -- ##
        #Yf_low = forecast.Yf.unstack().reset_index()
        #Yf_low.rename(columns={"level_0": "vendor_key", "level_1": "period_date", 0: "mean_forecast"}, inplace=True)
        Yf["low_forecast"] = 0

        ## -- High Forecast -- ##
        Yf["hi_forecast"] = 0

        ## -- forecast_type_id -- ##
        # 1: Backcast, 2: Nowcast, 3: Forecast
        forecast_type = pd.DataFrame(index=list(forecast.model.Yc), columns=["forecast_type_date"])
        for ii in forecast_type.index:
            FILTER = np.isfinite(forecast.model.Yc[ii])
            date = forecast.model.Yc.ix[FILTER, ii].index.max()
            forecast_type.ix[ii, "forecast_type_date"] = date
        forecast_type["max_date"] = forecast.model.Yc.index.max()

        Yf = pd.merge(Yf, forecast_type, how='left', left_on=["vendor_key"], right_index=True)

        Yf["forecast_type_id"] = np.nan
        Yf.ix[Yf["period_date"] > Yf["max_date"] , "forecast_type_id"] = 3
        Yf.ix[Yf["period_date"] <= Yf["forecast_type_date"] , "forecast_type_id"] = 1
        Yf.ix[(Yf["period_date"] > Yf["forecast_type_date"]) & (Yf["period_date"] <= Yf["max_date"]) , "forecast_type_id"] = 2
        if any(np.isnan(Yf["forecast_type_id"])):
            msg  = "\nBreak: Not all forecasts given a forecast_type_id"
            msg += "{0}".format(Yf[np.isnan(Yf["forecast_type_id"])])
            logging.info(msg)
            raise
        Yf.drop(["forecast_type_date", "max_date"], axis=1, inplace=True)

        ## -- Update the run_id of the forecast -- ##
        query = """
            INSERT INTO run_table VALUES();
            """
        self.cursor.execute(query)
        self.cnx.commit()

        query = """
            SELECT max(run_id) FROM run_table;
            """
        self.cursor.execute(query)
        run_id = self.cursor.fetchall()[0][0]
        Yf["run_id"] = run_id

        ## -- indicator_id -- ##
        query = """
            SELECT  vendor_key, indicator_id
            FROM    indicators
            """
        indicators = pd.read_sql(con=self.cnx, sql=query)
        Yf = pd.merge(Yf, indicators, how='left', on=["vendor_key"])

        ## -- SQL MySQL-connector Engine -- ##
        engine = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        ## -- Upload the data -- ##
        select = ["indicator_id", "period_date", "forecast_type_id", "run_id", "low_forecast", "mean_forecast", "hi_forecast"]
        Yf[select].to_sql(name="forecast_data_python", con=engine, if_exists="append", index=False)

        ## -- Upload the factors -- ##
        Xf = forecast.Xf.ix[:, 0:3].unstack().reset_index()
        Xf.rename(columns={"level_0": "factor", "level_1": "period_date", 0: "value"}, inplace=True)
        Xf["run_id"] = run_id
        Xf.to_sql(name="factors_python", con=engine, if_exists="append", index=False)

        ## -- Update the run_ifo table -- ##
        query = """CREATE TABLE IF NOT EXISTS run_info_python (
                    run_id INTEGER,
                    variable_id INTEGER,
                    variable_value INTEGER);"""
        self.cursor.execute(query)
        self.cnx.commit()

        query = """SELECT variable_id, variable_name FROM control_variables;"""
        control_variables = pd.read_sql(con=self.cnx, sql=query, index_col=["variable_name"])
        control_variables["run_id"] = run_id

        control_variables["variable_value"] = 0
        FILTER = (control_variables.index != "modelType")

        ## -- Get Subversion Version of model -- ##
        modelType = os.popen("svnversion").read().strip("\n")
        control_variables.ix[~FILTER,  "variable_value"]  = modelType
        query = """INSERT INTO run_info_python(run_id, variable_id, variable_value) VALUES({0}, {1}, {2});""".format(run_id, control_variables.ix["modelType", "variable_id"], modelType)
        #self.cursor.execute(query)
        #self.cnx.commit()

        for ii in control_variables[FILTER].index:
            control_variables.ix[ii, "variable_value"] = int(forecast.options[ii])
            query = """INSERT INTO run_info_python(run_id, variable_id, variable_value) VALUES({0}, {1}, {2});""".format(run_id, control_variables.ix[ii, "variable_id"], forecast.options[ii])
            self.cursor.execute(query)
            self.cnx.commit()
