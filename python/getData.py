#!/bin/usr/python3
import numpy as np
import pandas as pd
import mysql.connector
import sys
import logging
import time
import socket
import configparser
import os
import sys

from msDbaseInterface import msDbInterface



class getData(msDbInterface):
    def __init__(self, configPath='/nowcast/config/'):
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)
        self.getModelData()

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')

        self.user = self.config["DATABASE"].get("db_user")
        self.password = self.config["DATABASE"].get("db_password")
        self.db_name = self.config["DATABASE"].get("db_data")
        self.host = self.config["DATABASE"].get("db_host")

        ## -- Variables -- ##
        self.configVariables = configparser.ConfigParser()
        self.configVariables.read(self.configPath + 'configNowcastingVariables.ini')

        indexVar = [nn for nn in self.configVariables.sections()]
        self.variables = pd.DataFrame(index=indexVar, columns=["Type", "transformationCode", "presentationUnits", "units", "includeModel", "name", "frequency", "retransformation"])
        self.variables["includeModel"] = self.variables["includeModel"].astype('bool')

        for nn in self.configVariables.sections():
            pick = self.configVariables[nn]
            self.variables.ix[nn, "Type"] = pick.get("Type")
            self.variables.ix[nn, "transformationCode"] = pick.get("transformationCode")
            self.variables.ix[nn, "presentationUnits"] = pick.get("presentationUnits")
            self.variables.ix[nn, "units"] = pick.get("units")
            self.variables.ix[nn, "includeModel"] = pick.getboolean("includeModel")
            self.variables.ix[nn, "name"] = pick.get("name")
            self.variables.ix[nn, "frequency"] = pick.get("frequency")
            self.variables.ix[nn, "retransformation"] = pick.get("retransformation")

        self.variables["transformationCode"] = self.variables["transformationCode"].astype('int')
        self.variables["retransformation"] = self.variables["retransformation"].astype('int')

        ## -- Options -- ##
        self.options = {}
        self.options["low"] = self.config["options"].getint("low")
        self.options["high"] = self.config["options"].getint("high")
        self.options["hor"] = self.config["options"].getint("hor")
        self.options["max_iter"] = self.config["options"].getint("max_iter")
        self.options["qlag"] = self.config["options"].getint("qlag")
        self.options["plag"] = self.config["options"].getint("plag")
        self.options["Nx"] = self.config["options"].getint("Nx")

    def getVendorKeys(self):
        ## -- Get the indicators of the series -- ##
        query = """
            SELECT  indicator_id, vendor_key
            FROM    indicators
            WHERE   country_id = {0};
            """.format(self.config["options"].get("country_id"))

        self.vendor_keys = pd.read_sql(sql=query, con=self.cnx)

    def getModelData(self):
        self.getVendorKeys()

        ## -- Get the data --- ##
        query = """SELECT period_date"""

        ## -- The Monthly data -- ##
        FILTER = (self.variables["frequency"] == "M") & (self.variables["includeModel"])
        self.options["nyM"] = self.variables[FILTER].shape[0]

        ## -- OBS: Change how the order is created
        for key in self.variables[FILTER].index:
            query +=  ", MAX(IF(vendor_key = '{0}', value, Null)) AS '{0}'".format(key)

        ## -- The Quarterly data -- ##
        FILTER = (self.variables["frequency"] == "Q") & (self.variables["includeModel"])
        self.options["nyQ"] = self.variables[FILTER].shape[0]
        for key in self.variables[FILTER].index:
            query +=  ", MAX(IF(vendor_key = '{0}', value, Null)) AS '{0}'".format(key)

        query += """
                FROM data_series_v
                WHERE year(period_date) > 1990
                AND latest = True
                GROUP BY period_date
                ORDER BY period_date;
            """
        data = pd.read_sql(sql=query, con=self.cnx)

        ## -- Alternative -- ##
        query = "SELECT period_date, vendor_key, value FROM data_series_v WHERE year(period_date) > 1990 AND latest=True"
        data = pd.read_sql(sql=query, con=self.cnx)
        SELECT = self.variables[self.variables["includeModel"]].index.values
        FILTER = data["vendor_key"].map(lambda x: x in SELECT)
        data = data[FILTER].pivot(index="period_date", columns="vendor_key", values="value")

        for nn in ["Surveys", "Production and Trade", "Labour Market", "Consumption and Income"]:
                filterType = FILTER & (self.variables["Type"] == nn)
        FILTER = (self.variables["frequency"] == "M") & self.variables["includeModel"]
        select = []
        for nn in ["Surveys", "Production and Trade", "Labour Market", "Consumption and Income"]:
                filterType = FILTER & (self.variables["Type"] == nn)
                select = np.concatenate((select, self.variables[filterType].index.values), axis=0)
        dataM = data[select]

        FILTER = (self.variables["frequency"] == "Q") & self.variables["includeModel"]
        select = self.variables[FILTER].index.values

        dataQ = data[select]
        data = pd.merge(dataM, dataQ, left_index=True, right_index=True, how='outer')


        ## -- Release datess -- ##
        query = """
            SELECT  vendor_key,
                max(release_date) AS release_date,
                max(next_release) AS next_release
            FROM data_series_v
            WHERE vintage=1
            GROUP BY vendor_key;
        """

        ## Retrive the data ##
        self.dataNextRelease = pd.read_sql(sql=query, con=self.cnx)

        ## -- Transform the data -- ##
        self.dataRaw = data
        self.dataModel, self.dataPresent = self.transformData(dataFrame=data)
        if (self.dataRaw.shape[1] != self.dataModel.shape[1]):
            logging.error("\nRaw data N: {0:d}\nModel data N: {1:d}".format(self.dataRaw.shape[1], self.dataModel.shape[1]))
            raise ValueError

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


    def transformData(self, dataFrame):
        Ty, Ny = dataFrame.shape
        dataModel = dataFrame.copy()
        dataPresent = dataFrame.copy()

        ## -- Code: 1 log transformation -- ##
        FILTER = (self.variables["transformationCode"] == 1) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataModel[select] = np.log(dataModel[select])

        ## -- Code: 2 Level differences -- ##
        FILTER = (self.variables["transformationCode"] == 2) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataModel[select] = dataModel[select].diff(periods=3, axis=0)


        ## -- Code: 3 Annualised Quarter on Quarter Growth rate -- ##
        FILTER = (self.variables["transformationCode"] == 3) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataModel[select] = 400 * np.log(dataModel[select]).diff(periods=3, axis=0)

        ## -- The Presentation of the Data -- ##
        FILTER = (self.variables["transformationCode"] == 3) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataPresent[select] = 400 * np.log(dataPresent[select]).diff(periods=3, axis=0)

        ## -- Code: 4 3-month growth rate of 12-month difference of log variable -- ##
        FILTER = (self.variables["transformationCode"] == 4) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataModel[select] = 100 * (np.log(dataModel[select]).diff(periods=12, axis=0)).diff(periods=3, axis=0)

        ## -- The Presentation of the Data -- ##
        FILTER = (self.variables["transformationCode"] == 4) & self.variables["includeModel"]
        select = self.variables[FILTER].index.values
        dataPresent[select] = 100 * (np.log(dataPresent[select]).diff(periods=12, axis=0)).diff(periods=3, axis=0)

        return dataModel, dataPresent


if __name__ == "__main__":
    print("\ngetData Main File")
    timestr = time.strftime("%Y%m%d")
    log_filename = '/Nowcast/logs/MS_Investigate_logfile_' + socket.gethostname() + '_' + timestr + '.log'
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

    os.chdir("/Nowcast/")
    data = getData()
    #data.getModelData()
    #data.forecastGDP()
