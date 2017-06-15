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
import datetime

#sys.path.append(os.getcwd()[:-len("DevelopmentModel\\python\\model")] + "Db\\py\\")
# Own Modules
from msDbaseInterface import msDbInterface

class insertResultsMySQL (msDbInterface):
    __version__ = "0.0.2"
    __name__ = "__insertResultsMySQL__"

    def __init__(self, forecast, modelID:int, configPath = "/repos/Nowcast/config/", dev=False, productionCode:int=3):
        self.dev = dev
        self.modelID = modelID
        self.configPath = configPath
        self.getConfig()
        ## OBS: Change to SQLAlchemy or MySQLConnector???
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)
        self.uploadResults(forecast=forecast, productionCode=productionCode)

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = self.config[dbname].get("db_user")
        self.password = self.config[dbname].get("db_password")
        self.db_name = self.config[dbname].get("db_name")
        self.host = self.config[dbname].get("db_host")
        msg = "SaveResults to\nUser: {0}, DB Name: {1}, Host: {2}".format(self.user, self.db_name, self.host)
        logging.info(msg)

    def uploadResults(self, forecast, informationSet=None, productionCode:int=3):
        ## -- Results: Mean Forecast -- ##
        Yf = forecast.Yf.unstack().reset_index()
        Yf.rename(columns={"level_0": "indicator_id", "level_1": "period_date", 0: "mean_forecast"}, inplace=True)

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

        Yf = pd.merge(Yf, forecast_type, how='left', left_on=["indicator_id"], right_index=True)

        Yf["forecast_type_id"] = 0
        Yf.ix[Yf["period_date"] > Yf["max_date"] , "forecast_type_id"] = 3
        Yf.ix[Yf["period_date"] <= Yf["forecast_type_date"] , "forecast_type_id"] = 1
        Yf.ix[(Yf["period_date"] > Yf["forecast_type_date"]) & (Yf["period_date"] <= Yf["max_date"]) , "forecast_type_id"] = 2
        if any(Yf["forecast_type_id"] == 0):
            msg  = "\nBreak: Not all forecasts given a forecast_type_id"
            msg += "{0}".format(Yf[np.isnan(Yf["forecast_type_id"])])
            raise ValueError(msg)
        Yf.drop(["forecast_type_date", "max_date"], axis=1, inplace=True)

        ## -- Update the run_id of the forecast -- ##
        query = """
            INSERT INTO output_run_table VALUES ();
            """
        self.cursor.execute(query)
        self.cnx.commit()

        query = """SELECT max(run_id) FROM output_run_table;"""
        self.cursor.execute(query)
        run_id = self.cursor.fetchall()[0][0]
        # Link run_id to model_id...
        ## run_id (unique), model_id (foreign constraint), svn root repository URL (varchar), svn revision (integer)
        for line in os.popen("svn info").readlines():
            if "Repository Root" in line:
                repository = ":".join(line.strip("\n").split(":")[1:]).strip()
            if "Revision" in line:
                revision = int(line.strip("\n").split(":")[1])

        ## OBS NEEDS MODEL ID
        if informationSet:
            query = "INSERT INTO output_run_info (run_id, model_id, run_type, information_set, svn_repository, svn_revision) VALUES ({0}, {1}, {2}, '{3}', '{4}', {5})".format(
                run_id, self.modelID, productionCode, informationSet, repository, revision)
        else:
            query = "INSERT INTO output_run_info (run_id, model_id, run_type, svn_repository, svn_revision) VALUES ({0}, {1}, {2}, '{3}', {4})".format(run_id, self.modelID, productionCode, repository, revision)
        self.cursor.execute(query)
        self.cnx.commit()

        ## -- SQL MySQL-connector Engine -- ##
        ## OBS...
        Yf["run_id"] = run_id
        #engine = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        ## -- Upload the data: Forecasts -- ##
        select = ["indicator_id", "period_date", "forecast_type_id", "run_id", "low_forecast", "mean_forecast", "hi_forecast"]
        query = """INSERT INTO output_forecast_data (indicator_id, period_date, forecast_type_id, run_id, low_forecast, mean_forecast, hi_forecast) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        Yf['period_date'] = Yf["period_date"].apply(lambda x: datetime.datetime.strftime(datetime.datetime(x.year, x.month, x.day), '%Y-%m-%d'))
        df_to_tuple = [tuple((row["indicator_id"], row["period_date"], row["forecast_type_id"], row["run_id"], row["low_forecast"], row["mean_forecast"], row["hi_forecast"])) for index, row in Yf.iterrows()]
        self.cursor.executemany(query, df_to_tuple)
        #self.cursor.execute(query)
        self.cnx.commit()

        ## -- Upload the factors -- ##
        ## OBS: Store History of factors...
        Xf = forecast.Xf.ix[:, 0:3].unstack().reset_index()
        Xf.rename(columns={"level_0": "factor", "level_1": "period_date", 0: "value"}, inplace=True)
        Xf["run_id"] = run_id
        Xf["factor_id"] = Xf["factor"].map(lambda x: int(x.split("_")[1]))

        Xf["forecast_type_id"] = 0
        dateMin = forecast_type["forecast_type_date"].min()
        dateMax = forecast_type["forecast_type_date"].min()

        ## 1. Back-Cast
        FILTER = (Xf["period_date"] <= dateMin)
        Xf.ix[FILTER, "forecast_type_id"] = 1
        ## 2. Nowcast
        FILTER = (Xf["period_date"] <= dateMax) & (Xf["period_date"] > dateMin)
        Xf.ix[FILTER, "forecast_type_id"] = 2
        ## 3. Forecast
        FILTER = (Xf["period_date"] > dateMax)
        Xf.ix[FILTER, "forecast_type_id"] = 3

        if any(Xf["forecast_type_id"] == 0):
            msg = "Error: Zero values in factors forecast type"
            msg += "\n{0}".format(Xf[Xf["forecast_type_id"] == 0])
            raise ValueError(msg)

        query = "INSERT INTO output_factors (factor_id, period_date, forecast_type_id, run_id, factor_value) VALUES (%s, %s, %s, %s, %s);"
        df_to_tuple = [tuple((row["factor_id"], '{0:%Y-%m-%d}'.format(row["period_date"]), row["forecast_type_id"], row["run_id"], row["value"])) for index, row in Xf.iterrows()]
        self.cursor.executemany(query, df_to_tuple)
        self.cnx.commit()
