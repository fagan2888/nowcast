import os
import sys
import datetime
import logging

from msp_Logging import mspLog
if __name__ == "__main__":
    mspLog(name="msFcstPlots")

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

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
from matplotlib.ticker import MaxNLocator
my_locater = MaxNLocator(8)

from paramiko import SSHClient
from paramiko import AutoAddPolicy
from  scp import SCPClient

class fcstPlots(object):
    def __init__(self, path:str = "/repos/Nowcast/", dev:bool=True):
        logging.info("Initiate the plotting of Bloomberg Forecasts")
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

        ## -- Server settings -- ##
        self.webuser = self.config["webpage"].get("user")
        self.webhost = self.config["webpage"].get("host")
        self.webpassword = self.config["webpage"].get("password")

    def getFcstPlots(self):
        now = datetime.datetime.now()
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

        ## Bloomberg Mean:
        query = """SELECT
        	release_date, target_period, value
        FROM
        	fcst_data AS t1
        LEFT JOIN
        	fcst_tickers AS t2
        ON t1.ticker_id = t2.ticker_id
        LEFT JOIN
        	fcst_variables AS t3
        ON t3.fcst_variable_id = t2.fcst_variable_id
        LEFT JOIN
        	fcst_sources AS t4
        ON t4.fcst_source_id = t2.fcst_source_id
        WHERE t3.target_variable_id = 40
        AND t2.target_frequency = 9
        AND t4.fcst_source_id = 0
        AND t2.active = 1;"""
        mean = pd.read_sql(sql=query, con=engine)
        mean = mean.pivot(index="release_date", columns="target_period", values="value")

        # Dispersion:
        query = """SELECT
        	release_date, target_period, fcst_source_code, value
        FROM
        	fcst_data AS t1
        LEFT JOIN
        	fcst_tickers AS t2
        ON t1.ticker_id = t2.ticker_id
        LEFT JOIN
        	fcst_variables AS t3
        ON t3.fcst_variable_id = t2.fcst_variable_id
        LEFT JOIN
        	fcst_sources AS t4
        ON t4.fcst_source_id = t2.fcst_source_id
        WHERE t3.target_variable_id = 40
        AND t2.target_frequency = 9
        AND t4.fcst_source_id > 0
        AND t2.active = 1;"""
        data = pd.read_sql(sql=query, con=engine)

        num = 0
        ## Check amount of lags...
        for dd in mean.columns:
            FILTER = (data.loc[:, "target_period"] == dd)
            microdata = data.loc[FILTER, :].pivot(columns="fcst_source_code", index="release_date", values="value")
            periods = microdata.index.values
            for num, index in enumerate(periods):
                if num > 0:
                    microdata.loc[index, np.isnan(microdata.loc[index, :])] = microdata.loc[periods[num-1], np.isnan(microdata.loc[index, :])]
            num += 1
            fig = plt.figure(num)
            ax = fig.add_subplot(111)
            lines=[]; labels=[];

            isfinite = np.isfinite(mean.loc[:, dd])
            plt.plot(mean.loc[isfinite, dd].index, mean.loc[isfinite, dd], c='r',label="Bloomberg Average")
            aalpha = 0.
            for qq in [5, 10, 20, 25, 30, 50]:
                aalpha += 0.05
                ax.fill_between(
                    microdata.index, microdata.quantile(q=qq/200, axis=1), microdata.quantile(q=1-qq/200, axis=1),
                    alpha=aalpha, facecolor='b', edgecolor=None, zorder=1, label="Bloomberg ${0}\%$".format(100-qq)
                    )

            # OBS: missing Own Model, Atlanta Fed and New York Fed
            #ax.plot(nowcastPlot[tt].index, nowcastPlot[tt], label="MSP Nowcast Model", lw=3, c='r', zorder=20)
            FILTER = microdata.apply(lambda x: any(np.isfinite(x)), axis=1)

            xMin = min(microdata.loc[FILTER, :].index.min(), mean.loc[isfinite, dd].index.min())
            xMax = max(microdata.loc[FILTER, :].index.max(), mean.loc[isfinite, dd].index.max())
            ax.set_xlim(xmin=xMin, xmax=xMax)
            plt.plot([xMin, xMax], [0, 0], c='k', lw=0.5, zorder=5)
            titleName = "Forecast Real GDP (SAAR) {0:%Y}-Q{1:d}\nUpdated: {2:%H:%M %d-%m-%Y}".format(dd, int(dd.month/3), now)
            ax = self.plotLayout(ax=ax, titleName=titleName)
            hh, ll = ax.get_legend_handles_labels()
            lines += hh; labels += ll
            by_label = dict(zip(labels, lines))
            plt.legend(by_label.values(), by_label.keys(), loc = 'lower center', ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.1), bbox_transform = plt.gcf().transFigure)
            plt.tight_layout()
            if (dd.month/3 < now.month/3) | (dd.year < now.year):
                diff = int((now.month/3 - dd.month/3) - (now.year -dd.year)*4)
                filename = "/repos/Nowcast/tmp/benchmarks/benchmark-period-lag{0:d}.svg".format(diff)
            elif (dd.month/3 == now.month/3) & (dd.year == now.year):
                filename = "/repos/Nowcast/tmp/benchmarks/benchmark-period-current.svg"
            else:
                diff = int((dd.month/3 - now.month/3) - (dd.year - now.year)*4)
                filename = "/repos/Nowcast/tmp/benchmarks/benchmark-period-lead{0:d}.svg".format(diff)
            plt.savefig(filename, dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
            plt.close()
        self.transferFiles()

            self.transferFiles()

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

    def transferFiles(self):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=self.webhost, username=self.webuser, password=self.webpassword)

        filedir = "/repos/Nowcast/tmp/benchmarks/"
        files = os.listdir(filedir)
        print(type(ssh))
        for ff in files:
            if ".svg" in ff:
                filename = "{0:s}{1:s}".format(filedir, ff)
                self.transfer(filepath=filename, ssh=ssh)
                print(filename)

    def transfer(self, filepath:str, ssh:SSHClient):
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(files=filepath, remote_path='/var/www/html/nowcast/public_html/img/Nowcast/')

if __name__ == "__main__":
    fcst = fcstPlots()
    fcst.getFcstPlots()
