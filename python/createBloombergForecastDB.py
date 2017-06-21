import os
import sys
import datetime
import logging

from msp_Logging import mspLog
if __name__ == "__main__":
    mspLog(name="msForecast")

import numpy as np
import pandas as pd
import os
import sys
from optparse import OptionParser
import platform
import configparser
import sqlalchemy
import argparse
import calendar

from msp_blpAPI import bloombergAPI
from fcstPlots import fcstPlots

class createBloombergForecastDB(object):
    def __init__(self, path:str = "/repos/Nowcast/", dev:bool=True):
        logging.info("Initiate the Bloomberg API")
        self.path = path
        self.dev = dev

        ## -- Config File -- ##
        self.getConfig()

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
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))
        filename = "{0:s}/data/master-datasource.xlsx".format(self.path)

        # 1) fcst_variables
        dtype = {"fcst_variable_id": int, "fcst_variable_tick":str, "target_variable_id":int}
        fcst_variables = pd.read_excel(io=filename, sheetname="fcst_variables", dtype=dtype)
        query = "SELECT fcst_variable_id, fcst_variable_tick, target_variable_id, 0 AS upload FROM fcst_variables;"
        exists = pd.read_sql(sql=query, con=engine)
        exists.rename(columns={x:"{0:s}_exists".format(x) for x in exists.columns if x != "upload"}, inplace=True)
        if exists.shape[0] > 0:
            fcst_variables = pd.merge(fcst_variables, exists, left_on=["fcst_variable_tick"], right_on=["fcst_variable_tick_exists"], how='left')
            fcst_variables.loc[np.isnan(fcst_variables["upload"]), "upload"] = 1
            fcst_variables["upload"] = fcst_variables["upload"].astype(bool, inplace=True)
            for column in ["fcst_variable_id", "target_variable_id"]:
                select = [column, "{0:s}_exists".format(column)]
                check = fcst_variables.loc[:, select].apply(lambda x: x[column] != x["{0}_exists".format(column)], axis=1)
                if any(check):
                    select = [column, "{0:s}_exists".format(column)]
                    msg = "Failure for column {0:s}, not identical\n{1}".format(column, fcst_variables.loc[check, select])
                    raise ValueError(msg)
            select = [col for col in fcst_variables.columns if "exists" in col]
            fcst_variables.drop(select, axis=1, inplace=True)
        else:
            fcst_variables["upload"] = True

        if any(fcst_variables["upload"]):
            upload = ["({0[fcst_variable_id]:d}, '{0[fcst_variable_tick]:s}', {0[target_variable_id]:d})".format(fcst_variables.loc[index, :]) for index in fcst_variables.loc[fcst_variables["upload"], :].index]
            query = "INSERT INTO fcst_variables (fcst_variable_id, fcst_variable_tick, target_variable_id) VALUES\n\t{0:s}\n\t;".format(",\n\t".join(upload))
            engine.execute(query)

            query  = "UPDATE meta_last_updated SET last_updated = '{0:%Y-%m-%d %H:%M}' WHERE dataset = 'fcst_variables';".format(datetime.datetime.now())
            engine.execute(query)

        # 2) fcst_sources
        dtype = {"fcst_source_id":int, "fcst_source_name":str, "fcst_source_code":str}
        fcst_sources = pd.read_excel(io=filename, sheetname="fcst_sources", dtype=dtype)
        fcst_sources.loc[fcst_sources["fcst_source_id"] == 0, "fcst_source_code"] = ""

        query = "SELECT fcst_source_id, fcst_source_name, fcst_source_code, 0 AS upload FROM fcst_sources"
        exists = pd.read_sql(sql=query, con=engine)
        exists.rename(columns={x:"{0:s}_exists".format(x) for x in exists.columns if x != "upload"}, inplace=True)
        if exists.shape[0] > 0:
            fcst_sources = pd.merge(fcst_sources, exists, left_on=["fcst_source_code"], right_on=["fcst_source_code_exists"], how='left')
            fcst_sources.loc[np.isnan(fcst_sources["upload"]), "upload"] = 1
            fcst_sources["upload"] = fcst_sources["upload"].astype(bool, inplace=True)
            for column in ["fcst_source_id", "fcst_source_name"]:
                check = (fcst_sources[column] != fcst_sources["{0}_exists".format(column)]) & np.isfinite(fcst_sources["fcst_source_id_exists"])
                if any(check):
                    select = [column, "{0:s}_exists".format(column)]
                    msg = "Failure for column {0:s}, not identical\n{1}".format(column, fcst_variables.loc[check, select])
                    raise ValueError(msg)
            select = [col for col in fcst_sources.columns if "exists" in col]
            fcst_sources.drop(select, axis=1, inplace=True)
        else:
            fcst_sources["upload"] = True

        if any(fcst_sources["upload"]):
            upload = ["({0[fcst_source_id]:d}, '{0[fcst_source_name]:s}', '{0[fcst_source_code]:s}')".format(fcst_sources.loc[index, :]) for index in fcst_sources.loc[fcst_sources["upload"], :].index]
            query = "INSERT INTO fcst_sources (fcst_source_id, fcst_source_name, fcst_source_code) VALUES\n\t{0:s}\n\t;".format(",\n\t".join(upload))
            engine.execute(query)

            query  = "UPDATE meta_last_updated SET last_updated = '{0:%Y-%m-%d %H:%M}' WHERE dataset = 'fcst_sources';".format(datetime.datetime.now())
            engine.execute(query)

        # 3) fcst_tickers: own function?

        ## Candidates
        query = "SELECT frequency_id, frequency FROM meta_release_frequencies;"
        frequency = pd.read_sql(sql=query, con=engine)

        query = "SELECT source_id FROM data_sources WHERE source_name= 'BLP';"
        provider = engine.execute(query).fetchone()[0]

        dtype = {"ticker_code":str, "active":bool, "target_period":datetime.date, "fcst_variable_id":int, "fcst_source_id":int, "provider_id":int, "target_frequency":int}
        candidates = pd.DataFrame(columns=list(dtype.keys()))
        target_frequency = frequency.loc[frequency.frequency == "y", "frequency_id"].values[0]
        num = 0
        for yy in range(17, 20):
            for variable_index in fcst_variables.index:
                variable_tick = fcst_variables.loc[variable_index, "fcst_variable_tick"]
                variable_id = fcst_variables.loc[variable_index, "fcst_variable_id"]
                for source_index in fcst_sources.index:
                    source_code =fcst_sources.loc[source_index, "fcst_source_code"]
                    source_id = fcst_sources.loc[source_index, "fcst_source_id"]
                    target_date = datetime.date(2000+yy, 12, 31)
                    target_frequency = frequency.loc[frequency.frequency == "y", "frequency_id"].values[0]
                    if len(source_code) == 0:
                        ticker = "{0:4s} {1:2d} Index".format(variable_tick, yy)
                    else:
                        ticker = "{0:4s} {1:2d} {2:s} Index".format(variable_tick, yy, source_code)
                    num += 1
                    candidates.loc[num, ["ticker_code", "active", "target_period", "fcst_variable_id", "fcst_source_id", "provider_id", "target_frequency"]] = [ticker, False, target_date, variable_id, source_id, provider, target_frequency]
                    target_frequency = frequency.loc[frequency.frequency == "q", "frequency_id"].values[0]
                    for qq in range(1,5):
                        mm = qq*3
                        year = 2000+yy
                        dd = calendar.monthrange(year,mm)[1]
                        target_date = datetime.date(year, mm, dd)
                        if len(source_code) == 0:
                            ticker = "{0:4s} Q{1:1d}{2:2d} Index".format(variable_tick, qq, yy)
                        else:
                            ticker = "{0:4s} Q{1:1d}{2:2d} {3:s} Index".format(variable_tick, qq, yy, source_code)
                        num += 1
                        candidates.loc[num, ["ticker_code", "active", "target_period", "fcst_variable_id", "fcst_source_id", "provider_id", "target_frequency"]] = [ticker, False, target_date, variable_id, source_id, provider, target_frequency]#

        # Test candidates - if success, upload...
        candidates["upload"] = False
        dtype["upload"] = bool
        for key in candidates.columns:
            candidates[key] = candidates[key].astype(dtype[key], inplace=True)

        frame_type = candidates.dtypes
        incorrect = []
        for key in dtype.keys():
            if ((frame_type[key] != dtype[key]) & (dtype[key] != str)) | ((dtype[key] == str) & (frame_type[key] !="object")):
                incorrect.append(key)

        if len(incorrect) > 0:
            msg = "Incorrect data types in candidates:\n{0}".format(frame_type[incorrect])
            raise ValueError(msg)


        # check whether they are already uploaded to DB
        query = "SELECT ticker_code, True AS exist FROM fcst_tickers;"
        exists = pd.read_sql(sql=query, con=engine)
        if exists.shape[0] > 0:
            candidates = pd.merge(candidates, exists, on=["ticker_code"], how='left')
            candidates.drop(candidates[(candidates["exist"].astype(str) != "nan")].index, axis=0, inplace=True)
            candidates.drop(["exist"], axis=1, inplace=True)

        # Check whether valid lines....
        blpAPI = bloombergAPI()
        response = blpAPI.BDP(securitiesNames=candidates["ticker_code"].values, fieldNames=["PX_LAST"])
        response["PX_LAST"] = response["PX_LAST"].astype(np.float64, inplace=True)
        candidates = pd.merge(candidates, response, left_on=["ticker_code"], right_index=True, how='left')
        candidates.loc[np.isfinite(candidates["PX_LAST"]), "upload"] = True


        # upload valid tickers
        if any(candidates["upload"]):
            upload = ["('{0[ticker_code]:s}', {0[active]:b}, '{0[target_period]:%Y-%m-%d}', {0[fcst_variable_id]:d}, {0[fcst_source_id]:d}, {0[provider_id]:d}, {0[target_frequency]:d})".format(
                candidates.loc[index, :]) for index in candidates[candidates["upload"]].index]
            query = "INSERT INTO fcst_tickers (ticker_code, active, target_period, fcst_variable_id, fcst_source_id, provider_id, target_frequency) VALUES\n\t{0}\n\t;".format(",\n\t".join(upload))
            engine.execute(query)
            query  = "UPDATE meta_last_updated SET last_updated = '{0:%Y-%m-%d %H:%M}' WHERE dataset = 'fcst_tickers';".format(datetime.datetime.now())
            engine.execute(query)

            ## Check whether sources are active
            query = """UPDATE fcst_tickers AS tab1 LEFT JOIN ( SELECT t1.ticker_id,
            	CASE WHEN t3.period_date IS NULL THEN DATE('1900-01-01') ELSE t3.period_date END AS period_date
            	FROM fcst_tickers AS t1 LEFT JOIN fcst_variables AS t2 ON t1.fcst_variable_id = t2.fcst_variable_id
            	LEFT JOIN (SELECT d3.variable_id, max(d1.period_date) AS period_date FROM data_values AS d1
            	LEFT JOIN data_indicators AS d2 ON d1.indicator_id = d2.indicator_id LEFT JOIN data_variable_id AS d3
            	ON d2.variable_id = d3.variable_id GROUP BY d3.variable_id) AS t3 ON t2.target_variable_id = t3.variable_id
                ) AS tab2 ON tab2.ticker_id = tab1.ticker_id SET active = tab1.target_period >= tab2.period_date;"""
            engine.execute(query)

        # 4) fcst_data: download data - own function?
        self.fcstDownloadData(downloadAll=True)

    def fcstDownloadData(self, downloadAll:bool=False):
        logging.info("Get Bloomberg Tickers")
        blpAPI = bloombergAPI()
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        if downloadAll:
            extra = None
        else:
            extra = "\n\tWHERE t1.active = True"
        query = """SELECT t1.ticker_id, t1.ticker_code,
            max(CASE
    		    WHEN t2.release_date IS NULL THEN DATE('1900-01-01')
                ELSE DATE_ADD(t2.release_date, INTERVAL 1 DAY)
    	        END) AS start_date
            FROM
    	       fcst_tickers AS t1
            LEFT JOIN
    	       fcst_data AS t2
            ON t1.ticker_id = t2.ticker_id{0}
            GROUP BY t1.ticker_id, t1.ticker_code;""".format(extra)
        ticker = pd.read_sql(sql=query, con=engine, index_col="ticker_code", parse_dates=["start_date"])

        outputNames = {"PX_LAST": {"name": "value", "dtype": np.float64}}
        fieldNames = list(outputNames)
        updated = False
        for tick in ticker.index:
            security = [tick]
            startDateObj = ticker.loc[tick, "start_date"]
            if startDateObj.date() <= datetime.datetime.now().date():
                startDate = "{0:%Y%m%d}".format(startDateObj)
                msg = "Security: {0} - StartDate: {1}".format(security[0], startDate)
                logging.info(msg)
                data = blpAPI.BDH(securitiesNames=security, fieldNames=fieldNames, startDate=startDate)
                if data.shape[0] > 0:
                    updated = True
                    data.rename(columns={"Ticker": "ticker_code", "date": "release_date"}, inplace=True)
                    for key in outputNames.keys():
                        data[key] = data[key].astype(outputNames[key]["dtype"])
                        data.rename(columns={key:outputNames[key]["name"]}, inplace=True)
                    ticker_id = ticker.loc[tick, "ticker_id"]
                    upload = ["({0:d}, '{1[release_date]:%Y-%m-%d}', {1[value]:f})".format(ticker_id, data.loc[index, :]) for index in data.index]
                    query = "INSERT INTO fcst_data (ticker_id, release_date, value) VALUES\n\t{0:s}\n\t;".format(",\n\t".join(upload))
                    engine.execute(query)
        if updated:
            query  = "UPDATE meta_last_updated SET last_updated = '{0:%Y-%m-%d %H:%M}' WHERE dataset = 'fcst_data';".format(datetime.datetime.now())
            engine.execute(query)
        logging.info("All done with the downloads of the forecasts - Plot the data")

        fcst = fcstPlots()
        fcst.getFcstPlots()
        logging.info("Bloomberg Forecasts plotted and uploaded to Intraweb page")

if __name__ == "__main__":
    blp = createBloombergForecastDB()
    blp.getForecastTickers()
    #blp.fcstDownloadData()
