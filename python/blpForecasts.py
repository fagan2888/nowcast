#!/bin/usr/python3
import logging
import datetime
import socket

if __name__ == "__main__":
    now = datetime.datetime.now()
    log_filename = '/Nowcast/Logs/ms_forecasts_logfile_{0:s}_{1:%Y%m%d}.log'.format(socket.gethostname(), now)
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)
import numpy as np
import pandas as pd
import os
import sys
from optparse import OptionParser
import platform
import configparser
import sqlalchemy
from msp_blpAPI import bloombergAPI
import argparse
import calendar
## Alternative to sqlalchemy
#import mysql.connector

class blpForecasts(object):
    def __init__(self, path:str = "/repos/Nowcast/", dev:bool=False):
        logging.info("Initiate the Bloomberg API")
        self.path = path
        self.dev = dev

        ## -- Config File -- ##
        self.getConfig()

        ## Move into individual files
        self.engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))
        self.blpAPI = bloombergAPI()

    def getConfig(self, path = "/repos/Nowcast/"):
        pathfile = path + 'config/configNowcasting.ini'
        self.config = configparser.ConfigParser()
        self.config.read(pathfile)
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname = "DATABASE_UAT"
        self.user = self.config[dbname].get("db_user")
        self.password = self.config[dbname].get("db_password")
        self.db_name = self.config[dbname].get("db_name")
        self.host = self.config[dbname].get("db_host")

    def getForecastTickers(self):
        filename = self.path + "data/Bloomberg Forecasts.xlsx"
        tickers = pd.read_excel(io=filename, sheetname="Sheet1")
        ## Check if relevant providers are active!
        tickers["tick"] = tickers["Code"].map(lambda x: "ECGDUS Q117 {0} Index".format(x))

        ## -- Codes for the Variables in Bloomberg -- ##
        ## Link up codes(variables) with indicator_id in our database
        codes = {"GD": "GDP", "PI": "CPI", "UP": "Unemployment", "BB": "Budget Balance", "CA": "Current Account", "3M": "3-Month rate", "CB": "Central Bank Rate"}
        #codes = {"GD": "GDP", "PI": "CPI", "UP": "Unemployment"} # Restrcit variables of interest
        country = {"US": "USA", "GB": "United Kingdom", "DK": "Denmark", "AR":"Argentina"} ## OBS: Only active codes... ISO alpha-2 codes???
        #country = {"US": "USA"}

        now = datetime.datetime.now()

        qrange = [int(now.month/3)]
        yrange = [int("{0:%y}".format(now))]
        for ii in range(1, 4):
            qrange.append(qrange[ii-1]+1)
            if qrange[ii] > 4:
                qrange[ii] = 1
                yrange.append(yrange[ii-1]+1)
            else:
                yrange.append(yrange[ii-1])
        dates = zip(qrange, yrange)
        providers =  np.concatenate(([""], tickers["Code"].values))
        tickerTable = pd.DataFrame(columns=["variable", "forecast_period", "frequency", "country", "provider"])
        tickerTable.index.name = "ticker"
        for var in codes.keys():
                for cc in country.keys():
                    ## Forecasts of Quarterly data
                    for qq, yy in zip(qrange, yrange):
                        for ii in providers:
                            tick = "EC{0}{1} Q{2}{3} {4} Index".format(var, cc, qq, yy, ii)
                            dd = datetime.date(2000+yy, qq*3, calendar.monthrange(2000+yy, qq*3)[1])
                            tickerTable.loc[tick] = [codes[var], dd, "q", country[cc], ii]

                    ## Forecasts of Annual data
                    #for yy in yrange:
                    #    tick = "EC{0}{1} Q{2}{3} Index".format(var, cc, qq, yy)

        tickerTable.ix[(tickerTable["provider"] == ""), "provider"] = None

        ## -- Upload to SQL Tables -- ##
        query = "SELECT ticker, 0 AS upload FROM blp_fcst_meta;"
        upload = pd.read_sql(sql=query, con=self.engine, index_col="ticker")
        if upload.shape[0] == 0:
            tickerTable.to_sql(name="blp_fcst_meta", con=self.engine, if_exists="append")
        elif upload.shape[0] > 0:
            tickerTable = pd.merge(tickerTable, upload, left_index=True, right_index=True, how="left")
            tickerTable.ix[np.isnan(tickerTable["upload"]), "upload"] = 1
            select = ["variable", "forecast_period", "frequency", "country", "provider"]
            tickerTable.ix[(tickerTable["upload"] == 1), select].to_sql(name="blp_fcst_meta", con=self.engine, if_exists="append")

        ## -- Change 'active' codes of the tables -- ##
        query = """UPDATE blp_fcst_meta SET active=False WHERE forecast_period < date('{0:%Y-%m-%d}');""".format(tickerTable["forecast_period"].min())
        self.engine.execute(query)
        query = """UPDATE blp_fcst_meta SET active=True WHERE forecast_period >= date('{0:%Y-%m-%d}');""".format(tickerTable["forecast_period"].min())
        self.engine.execute(query)

    def resetDatabase(self):
        query = "DROP TABLE IF EXISTS blp_fcst_data;"
        self.engine.execute(query)

        query = "DROP TABLE IF EXISTS blp_fcst_meta CASCADE;"
        self.engine.execute(query)

        ## -- Reset meta Table -- ##
        query = "CREATE TABLE\n\tblp_fcst_meta ("
        query += "\n\t\tticker varchar(25) NOT NULL UNIQUE"
        query += ",\n\t\tvariable varchar(15) NOT NULL"
        query += ",\n\t\tforecast_period date NOT NULL"
        query += ",\n\t\tfrequency varchar(1) NOT NULL"
        query += ",\n\t\tcountry varchar(3) NOT NULL"
        query += ",\n\t\tprovider varchar(3)"
        query += ",\n\t\tactive bool"
        query += ",\n\t\tPRIMARY KEY (ticker)"
        query += ")\nCHARACTER SET=utf8\n;"
        self.engine.execute(query)

        ## -- Reset data Table -- ##
        query = "CREATE TABLE blp_fcst_data\n\t("
        query += "\n\t\tticker varchar(25) NOT NULL"
        query += ",\n\t\trelease_date datetime NOT NULL"
        query += ",\n\t\tvalue real NOT NULL"
        query += ",\n\t\tPRIMARY KEY (ticker, release_date)"
        query += ",\n\t\tFOREIGN KEY (ticker) REFERENCES blp_fcst_meta (ticker)"
        #query += ",\n\t\tFOREIGN KEY (forecast_period) REFERENCES blp_fcst_meta (forecast_period)"
        query += "\n\t)\nCHARACTER SET=utf8\n;"
        self.engine.execute(query)

    def runDaily(self):
        logging.info("get Meta data")
        self.getForecastTickers()

        logging.info("Get data")
        self.getData()

    def resetAllData(self):
        logging.info("Reset DB")
        self.resetDatabase()
        self.runDaily()
        logging.info("All done")

    def getData(self, newTable:bool=False):
        ## Move to config file???
        outputNames = {}
        outputNames["PX_LAST"] = {"name": "value", "dtype": np.float64}
        fieldNames = list(outputNames)

        ## Only get the latest data and active forecasts
        query = "SELECT\n\ttb1.ticker AS ticker,"
        query += "\n\tCASE\n\t\tWHEN max(tb2.release_date) IS NULL THEN date('1900-01-01')"
        query += "\n\t\tELSE DATE(DATE_ADD(max(tb2.release_date), INTERVAL 1 DAY))\n\tEND AS startdate"
        query += "\nFROM\n\tblp_fcst_meta AS tb1"
        query += "\nLEFT JOIN\n\tblp_fcst_data AS tb2"
        query += "\nON\n\ttb1.ticker = tb2.ticker"
        query += "\nWHERE\n\ttb1.active = 1"
        query += "\nGROUP BY tb1.ticker"
        query += "\n;"

        response = self.engine.execute(query)

        for row in response:
            security = [row["ticker"]]
            startDateObj = row["startdate"]
            if not startDateObj:
                startDateObj = datetime.date(year=1900, month=1, day=1)
            if startDateObj <= datetime.datetime.now().date():
                startDate = "{0:%Y%m%d}".format(startDateObj)
                msg = "Security: {0} - StartDate: {1}".format(security[0], startDate)
                logging.info(msg)
                data = self.blpAPI.BDH(securitiesNames=security, fieldNames=fieldNames, startDate=startDate)
                data.rename(columns={"Ticker": "ticker", "date": "release_date"}, inplace=True)
                for key in outputNames.keys():
                    data[key] = data[key].astype(outputNames[key]["dtype"])
                    data.rename(columns={key:outputNames[key]["name"]}, inplace=True)
                data.to_sql(name="blp_fcst_data", con=self.engine, if_exists="append", index=False)

        ## Update table of meta-meta data
        #now = datetime.datetime.now()
        #query = """UPDATE blp_fcst_data SET last_update={0} WHERE tablename = 'etf_blp_data' """

        msg = "That is all folks: All data uploaded"
        logging.info(msg)


if __name__ == "__main__":
    print("\nMain File")
    parser = argparse.ArgumentParser(description='Reset DB?')
    parser.add_argument('--newdb', dest='newdb', default=0, type=int, help='Reset the database T/F')
    args = parser.parse_args()
    try:
        forecasts = blpForecasts(dev=True)
        if False:
            forecasts.resetAllData()
        else:
            forecasts.runDaily()
    except:
        msg = "Error in running the ETF program"
        logging.error(msg, exc_info=True)
