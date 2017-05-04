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

import matplotlib as mpl
import matplotlib.pyplot as plt

from msDbaseInterface import msDbInterface

class benchmark(object):
    def __init__(self, configPath:str='/repos/Nowcast/config/', dev:bool=False):
        self.dev = dev
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)
        self.getBenchmarks()

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        if self.dev:
            dbname = "DATABASE_DEV"
        else:
            dbname ="DATABASE_UAT"
        self.user = self.config[dbname].get("db_user")
        self.password = self.config[dbname].get("db_password")
        self.db_name = self.config[dbname].get("db_name")
        self.host = self.config[dbname].get("db_host")

    def getBenchmarks(self):
        ## -- Get the indicators of the series -- ##
        query = """
                SELECT
                    CASE
                    	WHEN tb2.provider IS NULL THEN "BLP_mean"
                    	ELSE tb2.provider
                    END as provider,
                    tb2.variable, tb2.forecast_period, tb1.release_date, tb1.value
                FROM blp_fcst_data as tb1
                LEFT JOIN
                	blp_fcst_meta as tb2
                ON tb1.ticker = tb2.ticker
                ORDER BY tb2.variable, tb2.forecast_period, tb2.provider, tb1.release_date;
                """
        fcst = pd.read_sql(sql=query, con=self.cnx)

        ## GET OUR OWN nowcast
        ## GET Atlanta Fed's nowcast
        ## GET NY Fed's nowcast
        ## GET WSJ Econ Forecasting Project (monthly)

        filterVar = (fcst["variable"] == "GDP")
        periods = fcst.ix[filterVar, "forecast_period"].unique()
        yMin = fcst.ix[filterVar, "value"].min()
        yMax = fcst.ix[filterVar, "value"].max()
        xMin = fcst.ix[filterVar, "release_date"].min()
        xMax = fcst.ix[filterVar, "release_date"].max()
        filterCC = filterVar & (fcst["provider"] != "BLP_mean")

        ySeriesMin = pd.pivot_table(data=fcst.ix[filterCC], index="release_date", columns="forecast_period", values="value", aggfunc=np.min)
        ySeriesMax = pd.pivot_table(data=fcst.ix[filterCC], index="release_date", columns="forecast_period", values="value", aggfunc=np.max)
        #ySeriesQ75 = pd.pivot_table(data=fcst.ix[filterCC], index="release_date", columns="forecast_period", values="value", aggfunc=np.percentile)

        fig = plt.figure(1)

        for num, tt in enumerate(periods):
            ax = fig.add_subplot(2,2,num+1)
            plt.title("{0:%Y}-Q{1:d}".format(tt, int(np.ceil(tt.month/3))))
            filterTT = filterVar & (fcst["forecast_period"] == tt)

            FILTER = filterTT & (fcst["provider"] == "BLP_mean")
            plt.plot(fcst.ix[FILTER, "release_date"], fcst.ix[FILTER, "value"], label="BLP Mean", lw=3, c='g', alpha=0.8, zorder=10)
            providers = fcst.ix[filterTT & (fcst["provider"] != "BLP_mean"), "provider"].unique()
            data = fcst[filterTT].pivot(index="release_date", columns="provider", values="value")

            dateRange = sorted(data.index)

            for num, rr in enumerate(dateRange):
                if num > 0:
                    check = np.isnan(data.ix[rr, :])
                    data.ix[rr, check] = data.ix[dateRange[num-1], check]

            #plt.plot(ySeriesMin.ix[:, tt])
            #plt.plot(ySeriesMax.ix[:, tt])
            for nn in providers:
                filterNN = filterTT & (fcst["provider"] == nn)
                #plt.plot(data.index, data[nn], zorder=1, lw=1)
            #ax.fill_between(data.index, data.min(axis=1), data.max(axis=1), alpha=0.05, facecolor='b', edgecolor=None, zorder=1, label="$100\%$")
            ax.fill_between(data.index, data.quantile(q=0.025, axis=1), data.quantile(q=0.975, axis=1), alpha=0.05, facecolor='b', edgecolor=None, zorder=1, label="$95\%$")
            ax.fill_between(data.index, data.quantile(q=0.05, axis=1), data.quantile(q=0.95, axis=1), alpha=0.10, facecolor='b', edgecolor=None, zorder=1, label="$90\%$")
            ax.fill_between(data.index, data.quantile(q=0.10, axis=1), data.quantile(q=0.90, axis=1), alpha=0.15, facecolor='b', edgecolor=None, zorder=1, label="$80\%$")
            ax.fill_between(data.index, data.quantile(q=0.125, axis=1), data.quantile(q=0.875, axis=1), alpha=0.20, facecolor='b', edgecolor=None, zorder=1, label="$75\%$")
            ax.fill_between(data.index, data.quantile(q=0.15, axis=1), data.quantile(q=0.85, axis=1), alpha=0.25, facecolor='b', edgecolor=None, zorder=1, label="$70\%$")
            ax.fill_between(data.index, data.quantile(q=0.25, axis=1), data.quantile(q=0.75, axis=1), alpha=0.3, facecolor='b', edgecolor=None, zorder=1, label="$50\%$")

            dateZero = pd.date_range(start=xMin, end=xMax)
            plt.plot([xMin, xMax], [0,0], c='k', lw=0.5)
            plt.xticks(rotation=45)
            plt.ylim(ymin=yMin, ymax=yMax)
            plt.xlim(xmin=xMin, xmax=xMax)
            plt.legend()

        plt.show()

if __name__ == "__main__":
    print("\nBenchmark Forecasts")
    timestr = time.strftime("%Y-%m-%d")
    log_filename = '/repos/Nowcast/logs/ms_Investigate_logfile_' + socket.gethostname() + '_' + timestr + '.log'
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

    os.chdir("/repos/Nowcast/")
    benchmark = benchmark(dev=True)
    #data.getModelData()
    #data.forecastGDP()
