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
        for yy in range(17, 18):
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
        print(candidates.head())
        print(candidates.dtypes)

        candidates.loc[np.isfinite(candidates["PX_LAST"]), "upload"] = True
        print(candidates)

        # upload valid tickers
        if any(candidates["upload"]):
            upload = ["('{0[ticker_code]:s}', {0[active]:b}, '{0[target_period]:%Y-%m-%d}', {0[fcst_variable_id]:d}, {0[fcst_source_id]:d}, {0[provider_id]:d}, {0[target_frequency]:d})".format(
                candidates.loc[index, :]) for index in candidates[candidates["upload"]].index]
            query = "INSERT INTO fcst_tickers (ticker_code, active, target_period, fcst_variable_id, fcst_source_id, provider_id, target_frequency) VALUES\n\t{0}\n\t;".format(",\n\t".join(upload))
            engine.execute(query)



        #= {"ticker_id":str, "active":bool, "target_period":datetime.date, "fcst_variable_id":int, "fcst_source_id":int, "provider_id":int, "target_frequency":int}
        # 4) fcst_data: download data - own function?



if __name__ == "__main__":
    blp = createBloombergForecastDB()
    blp.getForecastTickers()
