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


        # row and column sharing: Fixed to three period forecast or current year forecast?
        fig, axarr = plt.subplots(2, 2, num=1)
        """
        ax1.plot(x, y)
        ax1.set_title('Sharing x per column, y per row')
        ax2.scatter(x, y)
        ax3.scatter(x, 2 * y ** 2 - 1, color='r')
        ax4.plot(x, 2 * y ** 2 - 1, color='r')
        """
        #fig = plt.figure(num=1, figsize=(5,5))
        lines=[]; labels=[];
        #for num, ii in enumerate(range(0,4)):
        #    print("num: {0}, row: {1}, col: {2}".format(num, row, col))
        #    print(axarr[row, col])

        for num, tt in enumerate(periods):
            row = int(np.floor(num/2))
            col = int(num - 2*row)
            ax = axarr[row, col]
            # 0: {np.floor(num/2), num - np.floor(num/2)}, 1: {0,1}, 2: {1,0}, 3: {1,1}
            filterTT = filterVar & (fcst["forecast_period"] == tt)
            FILTER = filterTT & (fcst["provider"] == "BLP_mean")
            ax.plot(fcst.ix[FILTER, "release_date"], fcst.ix[FILTER, "value"], label="Bloomberg Mean Forecast", lw=3, c='g', zorder=10)

            data = fcst[filterTT].pivot(index="release_date", columns="provider", values="value")
            dateRange = sorted(data.index)
            for num, rr in enumerate(dateRange):
                if num > 0:
                    check = np.isnan(data.ix[rr, :])
                    data.ix[rr, check] = data.ix[dateRange[num-1], check]

            ax.fill_between(data.index, data.quantile(q=0.025, axis=1), data.quantile(q=0.975, axis=1), alpha=0.05, facecolor='b', edgecolor=None, zorder=1, label="$95\%$")
            ax.fill_between(data.index, data.quantile(q=0.05, axis=1), data.quantile(q=0.95, axis=1), alpha=0.10, facecolor='b', edgecolor=None, zorder=1, label="$90\%$")
            ax.fill_between(data.index, data.quantile(q=0.10, axis=1), data.quantile(q=0.90, axis=1), alpha=0.15, facecolor='b', edgecolor=None, zorder=1, label="$80\%$")
            ax.fill_between(data.index, data.quantile(q=0.125, axis=1), data.quantile(q=0.875, axis=1), alpha=0.20, facecolor='b', edgecolor=None, zorder=1, label="$75\%$")
            ax.fill_between(data.index, data.quantile(q=0.15, axis=1), data.quantile(q=0.85, axis=1), alpha=0.25, facecolor='b', edgecolor=None, zorder=1, label="$70\%$")
            ax.fill_between(data.index, data.quantile(q=0.25, axis=1), data.quantile(q=0.75, axis=1), alpha=0.3, facecolor='b', edgecolor=None, zorder=1, label="$50\%$")

            ax.plot([xMin, xMax], [0,0], c='k', lw=0.5)

            ax.set_ylim(ymin=yMin, ymax=yMax)
            ax.set_xlim(xmin=xMin, xmax=xMax)
            hh, ll = ax.get_legend_handles_labels()
            lines += hh; labels += ll
            titleName = "{0:%Y}-Q{1:d}".format(tt, int(np.ceil(tt.month/3)))
            if row == 1:
                bottomAxis = True
            else:
                bottomAxis=False
            if col == 0:
                leftAxis = True
            else:
                leftAxis = False
            plt.xticks(rotation=45)
            ax = self.plotLayout(ax=ax, titleName=titleName, bottomAxis=bottomAxis, leftAxis=leftAxis)

        by_label = dict(zip(labels, lines))
        plt.legend(by_label.values(), by_label.keys(), loc = 'lower center', ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.1), bbox_transform = plt.gcf().transFigure)
        plt.tight_layout()
        #plt.legend()
        filename = "benchmark.svg"
        plt.savefig(filename, dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
        plt.show()

    def plotLayout(self, ax, titleName:str, leftAxis:bool=True, bottomAxis:bool=True, ylabelName:str="$\%$-SAAR"):
        ax.set_title(titleName, fontsize=12)


        ax.spines['top'].set_linewidth(0.5)
        ax.spines['right'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.get_xaxis().tick_bottom()

        #if leftAxis:
        ax.spines['right'].set_visible(False)
        ax.get_yaxis().tick_left()
        if leftAxis:
            ax.set_ylabel(ylabelName)
        plt.grid(False)
        plt.xticks(rotation=45)

        return ax


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
