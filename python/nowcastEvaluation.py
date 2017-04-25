## Python Script to Download Data from Macrobond
import numpy as np
import pandas as pd
import datetime

import sys
import os
import configparser

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
#rcParams['font.family'] = 'serif'
#rcParams['font.serif'] = ['Computer Modern Roman']
#rcParams['text.usetex'] = True
from matplotlib.ticker import MaxNLocator
my_locater = MaxNLocator(8)


print(os.getcwd())
#sys.path.append(os.getcwd()+'\\DevelopmentModel\\python\\model\\')
#sys.path.append(os.getcwd()+'\\DevelopmentModel\\python\\model\\')
from macrobondAPI import MacrobondInterface
from stats import stats

sys.path.append(os.getcwd()[:-len('DevelopmentModel\\python\\model\\')] + "\\Db\\py\\")
print(os.getcwd()[:-len('DevelopmentModel\\python\\model\\')] + "\\Db\\py\\")

#sys.path.append(os.getcwd() + "\\Db\\py\\")
from msDbaseInterface import msDbInterface
from fredapi import Fred
os.chdir("C:\\Nowcasting\\")



class nowcastEvaluate(msDbInterface):
    def __init__ (self, configPath=os.getcwd() + '\\DevelopmentModel\\python\\model\\config\\'):
        self.mbAPI = MacrobondInterface()
        self.configPath = configPath
        self.getConfig()
        msDbInterface.__init__(self, user=self.user, password=self.password, host=self.host, db_name=self.db_name)

    def getConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath + 'configNowcasting.ini')

        self.user = self.config["DATABASE"].get("db_user")
        self.password = self.config["DATABASE"].get("db_password")
        self.db_name = self.config["DATABASE"].get("db_data")
        self.host = self.config["DATABASE"].get("db_host")
        self.fred_api_key = self.config["fred"].get("api_key")

    def getFRED(self):
        fred  = Fred(api_key = self.fred_api_key)
        data = fred.get_series_all_releases("GDP")
        print(data)


    def getNowcast(self):
        listNow = ["usfcst1846", "usfcst1884"]#, "usfcst1969"]
        store = []
        for ii in listNow:
            print("\nData series: {0:s}".format(ii))
            exists, tmp = self.mbAPI.GetData(ii)
            tmp.rename(columns={"value": ii}, inplace=True)

            if exists & ("data" in locals()):
                data = pd.merge(data, tmp, on="period_date", how='outer')
            elif exists:
                data = tmp
        data["forecast_date"] = data["period_date"].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
        data.drop("period_date", inplace=True, axis=1)

        ## -- Get Our own forecasts -- ##
        query = """
                SELECT  run_date, run_id, mean_forecast AS msp_nowcast
                FROM    gdp_fcst_per_day_v
                WHERE   period_date = "2016-12-31"
                ORDER BY run_date
                """
        mspNow = pd.read_sql(sql=query, con=self.cnx)
        mspNow["forecast_date"] = mspNow.run_date.map( lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))


        data = pd.merge(data, mspNow[["forecast_date", "msp_nowcast"]], on='forecast_date', how='outer')
        data.sort_values(by="forecast_date", inplace=True)
        data.set_index("forecast_date", inplace=True)

        minDate = data.index.min()
        maxDate = data.index.max()
        date = pd.date_range(start=minDate, end=maxDate, freq="D")
        dateRange = pd.DataFrame(index=date, columns=["Merged"], data=True)
        data = pd.merge(data, dateRange, left_index=True, right_index=True, how='outer')
        data.drop(["Merged"], inplace=True, axis=1)

        for num, tt in enumerate(data.index[1:]):
            tlag = tt - datetime.timedelta(1)
            FILTER = np.isnan(data.ix[tt, :])
            data.ix[tt, FILTER] = data.ix[tlag, FILTER]
        return data


    def __del__(self):
        self.mbAPI.closeMacrobond

if __name__ == "__main__":
    print('\nScript to download data')
    nowcast = nowcastEvaluate()

    #nowcast.getFRED()


    data = nowcast.getNowcast()


    stats = stats()
    FILTER = np.isfinite(data.msp_nowcast) & np.isfinite(data.usfcst1846)
    bbeta, R2, ssigma, ee = stats.OLSfn(yy=data.msp_nowcast[FILTER].values, xx=data.usfcst1846[FILTER].values)
    print("\n\nNew York Fed")
    print(bbeta[0,0])
    print("{0:<15s}{1:6.2f}\n{2:<15s}{3:6.2f}\n{4:15s}{5:6.3f}".format(
            "Constant:", bbeta[0,0],
            "New York Fed:", bbeta[1,0],
            "R2:", R2[0,0]
        ))


    FILTER = np.isfinite(data.msp_nowcast) & np.isfinite(data.usfcst1884)
    bbeta, R2, ssigma, ee = stats.OLSfn(yy=data.msp_nowcast[FILTER].values, xx=data.usfcst1884[FILTER].values)
    print("\n\nAtlanta Fed GDPNow")
    print("{0:<15s}{1:6.2f}\n{2:<15s}{3:6.2f}\n{4:15s}{5:6.3f}".format(
        "Constant:", bbeta[0,0],
        "Atlanta Fed:", bbeta[1,0],
        "R2:", R2[0,0])
        )

    if True:
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

        plt.plot(data.index, data.msp_nowcast, c="b", label="MSP Nowcast")
        plt.plot(data.index, data.usfcst1846, c="g", label="New York Fed Nowcast")
        plt.plot(data.index, data.usfcst1884, c="r", label="Atlanta Fed GDPNow")

        plt.xticks(rotation=45)
        plt.legend(loc=9, ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.25))
        plt.savefig('C:\\Nowcasting\\GDP_nowcast_Evaluation_{0:%Y-%m-%d}.png'.format(datetime.datetime.today()), dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
        plt.show()
        plt.close()
