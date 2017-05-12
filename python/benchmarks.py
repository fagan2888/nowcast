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
        # OBS: Remove back cast??? Or change how they are presented...
        query = """
            SELECT
            	d1.period_date AS forecast_period, date(d1.timestamp) AS release_date, d1.mean_forecast
            FROM
            	(
            	SELECT
            		tb4.period_date, tb4.indicator_id, tb4.mean_forecast, tb4.run_id, tb4.indicator_short_info, tb4.forecast_type, tb5.timestamp
            	FROM
            	(
            		SELECT
            			tb1.period_date, tb1.indicator_id, tb1.mean_forecast, tb1.run_id, tb2.indicator_short_info, tb3.forecast_type
            		FROM
            			forecast_data as tb1
            		LEFT JOIN
            			indicators as tb2
            		ON tb1.indicator_id = tb2.indicator_id
            		LEFT JOIN
            			forecast_types AS tb3
            		ON tb1.forecast_type_id = tb3.forecast_type_id
            	) AS tb4
            	LEFT JOIN
            		run_table AS tb5
            	ON
            		tb4.run_id = tb5.run_id
            	WHERE
            		indicator_id = 20
            	AND
            		month(tb4.period_date) % 3 = 0
            	) AS d1
            LEFT JOIN
            	(SELECT date(timestamp) AS datestamp, max(run_id) AS run_id FROM run_table GROUP BY date(timestamp)) AS d2
            ON
            	date(d1.timestamp) = d2.datestamp
            WHERE
            	d1.run_id = d2.run_id
            ;
            """
        nowcast= pd.read_sql(sql=query, con=self.cnx)
        nowcastPlot = nowcast.pivot(index="release_date", columns="forecast_period", values="mean_forecast")

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

        for num, tt in enumerate(periods):
            fig = plt.figure(num=1, figsize=(5, 5))
            ax = fig.add_subplot(111)
            lines=[]; labels=[];

            filterTT = filterVar & (fcst["forecast_period"] == tt)
            FILTER = filterTT & (fcst["provider"] == "BLP_mean")
            ax.plot(fcst.ix[FILTER, "release_date"], fcst.ix[FILTER, "value"], label="Bloomberg Mean Forecast", lw=1, c='g', zorder=10)

            ax.plot(nowcastPlot[tt].index, nowcastPlot[tt], label="MSP Nowcast Model", lw=3, c='r', zorder=20)

            data = fcst[filterTT & (fcst["provider"] != "BLP_mean")].pivot(index="release_date", columns="provider", values="value")
            yMin = data.min().min()
            yMax = data.max().max()

            xMin = min((data.index.min().date(), fcst.ix[FILTER, "release_date"].min().date(), nowcastPlot[tt].index.min()))
            xMax = max((data.index.max().date(), fcst.ix[FILTER, "release_date"].max().date(), nowcastPlot[tt].index.max()))

            dateRange = sorted(data.index)
            for num, rr in enumerate(dateRange):
                if num > 0:
                    check = np.isnan(data.ix[rr, :])
                    data.ix[rr, check] = data.ix[dateRange[num-1], check]
            aalpha = 0.
            for qq in [5, 10, 20, 25, 30, 50]:
                aalpha += 0.05
                ax.fill_between(
                    data.index, data.quantile(q=qq/200, axis=1), data.quantile(q=1-qq/200, axis=1),
                    alpha=aalpha, facecolor='b', edgecolor=None, zorder=1, label="Bloomberg ${0}\%$".format(100-qq)
                    )
            FILTER = filterTT & (fcst["provider"] != "BLP_mean")
            ax.plot([xMin, xMax], [0,0], c='k', lw=0.5, zorder=5)

            ax.set_ylim(ymin=yMin, ymax=yMax)
            ax.set_xlim(xmin=xMin, xmax=xMax)
            hh, ll = ax.get_legend_handles_labels()
            lines += hh; labels += ll

            titleName = "Forecast: {0:%Y}-Q{1:d}".format(tt, int(np.ceil(tt.month/3)))
            ax = self.plotLayout(ax=ax, titleName=titleName)

            by_label = dict(zip(labels, lines))
            plt.legend(by_label.values(), by_label.keys(), loc = 'lower center', ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.1), bbox_transform = plt.gcf().transFigure)
            plt.tight_layout()

            filename = "tmp/benchmark_{0:%Y}-Q{1:d}.png".format(tt, int(np.floor(tt.month/3)))
            plt.savefig(filename, dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
            plt.close()


    def plotLayout(self, ax, titleName:str, ylabelName:str="$\%$-SAAR"):
        ax.set_title(titleName, fontsize=12)

        ax.spines['top'].set_linewidth(0.5)
        ax.spines['right'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.get_xaxis().tick_bottom()

        ax.spines['right'].set_visible(False)
        ax.get_yaxis().tick_left()
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
    benchmark = benchmark(dev=False)
    #data.getModelData()
    #data.forecastGDP()
