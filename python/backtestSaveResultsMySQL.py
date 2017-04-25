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

sys.path.append(os.getcwd()[:-len("DevelopmentModel\\python\\model")] + "Db\\py\\")
from msDbaseInterface import msDbInterface

class backtestResultsMySQL (msDbInterface):
    __version__ = "0.0.2"
    __name__ = "__insertResultsMySQL__"

    def __init__(self, configPath = "python\\model\\config\\"):
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)

        ## -- indicator_id -- ##
        query = """
            SELECT  vendor_key, indicator_id
            FROM    indicators
            """
        self.indicators = pd.read_sql(con=self.cnx, sql=query)

        query = """
                DROP TABLE IF EXISTS backtest_dfm_y;
                """
        self.cursor.execute(query)
        self.cnx.commit()
        query = """
                DROP TABLE IF EXISTS backtest_dfm_x;
                """
        self.cursor.execute(query)
        self.cnx.commit()

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        self.user = self.config["DATABASE"].get("db_user")
        self.password = self.config["DATABASE"].get("db_password")
        self.db_name = self.config["DATABASE"].get("db_name")
        self.host = self.config["DATABASE"].get("db_host")

    def uploadResults(self, forecast, run_id, options):
        Nx = options["Nx"]
        ## -- Results: Mean Forecast -- ##
        Yf = forecast.Yf.unstack().reset_index()
        Yf.rename(columns={"level_0": "vendor_key", "level_1": "period_date", 0: "mean_forecast"}, inplace=True)
        if np.sum(np.isnan(Yf["mean_forecast"].values)) > 0:
            logging.error("Yf in insertResultsMySQL contains NaN")
            raise ValueError

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
            print("\nBreak: Not all forecasts given a forecast_type_id")
            print(Yf[np.isnan(Yf["forecast_type_id"])])
            raise ValueError("Forecast type ID not recognised")

        Yf.drop(["forecast_type_date", "max_date"], axis=1, inplace=True)

        ## -- Update the run_id of the forecast -- ##
        Yf["run_id"] = run_id

        Yf = pd.merge(Yf, self.indicators, how='left', on=["vendor_key"])

        ## -- SQL MySQL-connector Engine -- ##
        engine = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        ## -- Upload the data -- ##
        select = ["indicator_id", "period_date", "forecast_type_id", "run_id", "mean_forecast"]
        Yf[select].to_sql(name="backtest_dfm_y", con=engine, if_exists="append", index=False)

        ## -- Upload the factors -- ##
        Xf = forecast.Xf.ix[:, 0:Nx].unstack().reset_index()
        Xf.rename(columns={"level_0": "factor", "level_1": "period_date", 0: "value"}, inplace=True)
        Xf["run_id"] = run_id
        Xf.to_sql(name="backtest_dfm_x", con=engine, if_exists="append", index=False)
