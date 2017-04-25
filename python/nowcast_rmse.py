import os
import sys
import logging
import socket
from datetime import datetime
if __name__ == "__main__":
    log_filename = 'C:\\Nowcasting\\logs\\MSP_developmentModel_logfile_{0:s}_{1:%Y%m%d}.log'.format(socket.gethostname(), datetime.now())
    FORMAT = '%(asctime)-15s %(funcName)s %(lineno)d %(message)s'
    logging.basicConfig(filename = log_filename, format=FORMAT, level = logging.INFO)

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import configparser


import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
from matplotlib.ticker import MaxNLocator
my_locater = MaxNLocator(8)

if __name__ == "__main__":
    print("\n\n=============\nNowCasting Model\n=============\n")
    if (os.getlogin() == "pnash"):
        os.chdir("Z:\\PNash\\My Documents\\Projects\\Nowcast\\Model")
    elif False:
        os.chdir("C:\\Nowcasting\\model")
    else:
        os.chdir("C:\\Nowcasting\\DevelopmentModel\\")

sys.path.append(os.getcwd()[:-len("DevelopmentModel")] + "Db\\py\\")
from msDbaseInterface import msDbInterface
from getData import getData

class evalNowCast(msDbInterface):
    __version__ = "0.0.2"
    __name__ = "__insertResultsMySQL__"

    def __init__(self, configPath = "python\\model\\config\\"):
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)

        self.engine = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(self.user, self.password, self.host, self.db_name))

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')
        self.user = self.config["DATABASE"].get("db_user")
        self.password = self.config["DATABASE"].get("db_password")
        self.db_name = self.config["DATABASE"].get("db_name")
        self.host = self.config["DATABASE"].get("db_host")

    def evaluateModel(self):

        ## -- indicator_id -- ##
        query = """
                SELECT
                    indicators.vendor_key AS vendor_key,
                    backtest_dfm_y.indicator_id AS indicator_id,
                    backtest_dfm_y.period_date AS period_date,
                    backtest_dfm_y.forecast_type_id AS forecast_type_id,
                    backtest_dfm_y.run_id AS run_id,
                    backtest_dfm_y.mean_forecast AS mean_forecast
                FROM
                    backtest_dfm_y
                LEFT JOIN
                    indicators
                ON  backtest_dfm_y.indicator_id = indicators.indicator_id
                WHERE   vendor_key = "usnaac0169"
                AND     month(period_date) % 3 = 0;
                """
        data_forecast = pd.read_sql(con=self.cnx, sql=query)

        data_forecast["forecast_date"] = data_forecast.run_id.map(lambda x: datetime.strptime(x.split("_")[0], "%Y-%m-%d"))
        data_forecast["forecast_variable"] = data_forecast.run_id.map(lambda x: np.int64(x.split("_")[1]))
        data_forecast["diff_year"] = data_forecast["period_date"].map(lambda x: x.year) - data_forecast["forecast_date"].map(lambda x: x.year)
        data_forecast["diff_month"] = data_forecast["period_date"].map(lambda x: x.month) - data_forecast["forecast_date"].map(lambda x: x.month)
        data_forecast["diff"] = data_forecast["diff_year"].astype("int64")*12 + data_forecast["diff_month"].astype("int64")
        data_forecast["t_count"] = data_forecast["diff"]*20 + 20 - data_forecast["forecast_variable"]

        FILTER = (data_forecast["diff"] == 12)
        pickDate = datetime.date(datetime(2016,12,1))
        FILTER = data_forecast["period_date"] < pickDate
        gdpF = data_forecast[FILTER].pivot(index="period_date", columns="t_count", values="mean_forecast")

        ## -- Get the data --- ##
        logging.info("\nStep (1) Retrieve the data from the MySQL MacroSynergy db")
        dataObj = getData(configPath =self.configPath)
        data = dataObj.dataModel


        data = pd.merge(data[["usnaac0169"]], gdpF, left_index=True, right_index=True, how='inner')
        ef = data.ix[:, 1:].copy()

        for ii in range(0, ef.shape[1]):
            ef.ix[:, ii] = data.ix[:,"usnaac0169"] - data.ix[:, ii+1]

        rmse = np.sqrt((ef**2).mean(axis=0).sort_index(ascending=False))
        print(rmse)

        fig = plt.figure(num=1, figsize=(10, 2.7))
        ax = fig.add_subplot(111)
        plt.title("\nForecast Comparison 2016 Q4")
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)

        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        plt.grid(False)
        ax.spines['top'].set_linewidth(0.5)
        ax.spines['right'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)

        plt.plot(rmse.index, rmse)
        plt.gca().invert_xaxis()

        plt.xticks(rotation=45)
        #plt.legend(loc=9, ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.25))
        plt.savefig('C:\\Nowcasting\\GDP_nowcast_Evaluation_RMSE_{0:%Y-%m-%d}.png'.format(datetime.today()), dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
        plt.show()
        plt.close()




        """
        FILTER = (data_forecast.vendor_key == "usnaac0169")
        gdpF = data_forecast[FILTER].pivot(index="period_date", columns="run_id", values="mean_forecast")
        pickData = datetime.date(datetime(2016,12,31))
        print(gdpF.ix[(gdpF.index== pickData), :].T)
        """


        #print(data["usnaac0169"])

if __name__ == "__main__":
    print("\n\n=============\nEvaluate NowCasting Model\n=============\n")
    evalNow = evalNowCast()
    evalNow.evaluateModel()
