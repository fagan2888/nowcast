import numpy as np
import pandas as pd
import sys
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime
rcParams['axes.labelsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Computer Modern Roman']
rcParams['text.usetex'] = True
from matplotlib.ticker import MaxNLocator
my_locater = MaxNLocator(8)

class outputResults(object):

    def __init__(self):
        pass

    def plotAll(self, model, forecast, data):

        numFig = 0
        for num, ii in enumerate(list(data.dataModel)):
            if True:
                if ii == "usnaac0169":
                    numFig += 1
                    print(ii, numFig)
                    self.plotVariable(plotVar=ii, num=num, numFig=numFig, model=model, forecast=forecast, data=data)
            else:
                numFig += 1
                print(ii, numFig)
                self.plotVariable(plotVar=ii, num=num, numFig=numFig)
        #plt.show()

    def plotVariable(self, plotVar, num, numFig, model, forecast, data):
        fig = plt.figure(num=numFig, figsize=(10, 2.7))
        ax = fig.add_subplot(111)
        self.plotLayout(ax=ax)


        FILTER = (data.dataModel.index >= model.Yhat.index.min())
        plt.scatter(data.dataModel[FILTER].index, data.dataModel[FILTER][plotVar], facecolor='b', edgecolor="None", label="Observed data", zorder=3)

        ## -- Sample (unconditional) Mean -- ##
        Yhigh = model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape)
        Ylow = np.zeros(shape = model.Yhat.index.shape)
        plt.plot(model.Yhat.index, model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape), c='g', ls='--', label=None)
        ax.fill_between(model.Yhat.index, Ylow,  Yhigh, edgecolor="None", facecolor='g', alpha=0.3, label="Unconditional Mean")

        ## -- Common Component -- ##
        plt.plot(model.Yhat.index, model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape) + model.Ycommon[plotVar].values.T, c='r', label=None)
        Yhigh = model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape) + model.Ycommon[plotVar].T
        Ylow = model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape)
        ax.fill_between(model.Yhat.index, Ylow,  Yhigh, edgecolor="None", facecolor='r', alpha=0.3, label="Common Component")

        ## -- Idiosyncratic Component -- ##
        plt.plot(model.Yhat.index, model.Yhat[plotVar].values, c='b', label=None)
        Yhigh = model.Yhat[plotVar]
        Ylow = model.Ymean[0,num]*np.ones(shape = model.Yhat.index.shape) + model.Ycommon[plotVar].T
        ax.fill_between(model.Yhat.index, Ylow,  Yhigh, edgecolor="None", facecolor='b', alpha=0.3, label="Idiosyncratic Component")

        plt.plot(model.Yhat.index, np.zeros(shape = model.Yhat.index.shape), c='k', label=None, lw=0.5)

        ## -- Forecast -- ##
        plt.plot(forecast.Yf.index, np.zeros(shape = forecast.Yf[plotVar].shape), 'k', label=None, lw=0.5)

        ## Mean
        YmeanF = model.Ymean[0,num]*np.ones(shape = forecast.Yf[plotVar].shape)
        plt.plot(forecast.Yf.index, YmeanF, 'g', ls='--', label=None)
        Yhigh = YmeanF
        Ylow = np.zeros(shape = forecast.Yf.index.shape)
        ax.fill_between(forecast.Yf.index, Ylow,  Yhigh, edgecolor="None", facecolor='g',  alpha=0.3, label=None)

        ## Common Component
        plt.plot(forecast.Yf.index, YmeanF + forecast.Ycommonf[plotVar].values, c='r', label=None)
        Yhigh = YmeanF + forecast.Ycommonf[plotVar]
        Ylow = YmeanF
        ax.fill_between(forecast.Yf.index, Ylow,  Yhigh, edgecolor="None", facecolor='r', alpha=0.3, label=None)

        ## Idiosyncratic Component
        plt.plot(forecast.Yf.index, forecast.Yf[plotVar].values, c='b', label=None)
        Yhigh = forecast.Yf[plotVar].values
        Ylow = YmeanF + forecast.Ycommonf[plotVar].values
        ax.fill_between(forecast.Yf.index, Ylow,  Yhigh, edgecolor="None", facecolor='b', alpha=0.3, label=None)


        plt.xlim(xmin = model.Yhat.index.min(), xmax = forecast.Yf.index.max())

        yMax = np.ceil(np.max((forecast.Yf[plotVar].max(), data.dataModel[FILTER][plotVar].max(), model.Yhat[plotVar].max()))/5)*5
        yMin = np.floor(np.min((forecast.Yf[plotVar].min(), data.dataModel[FILTER][plotVar].min(), model.Yhat[plotVar].min()))/5)*5
        ax.fill_between(forecast.Yf.index, yMin*np.ones(shape = forecast.Yf[plotVar].shape),  yMax*np.ones(shape = forecast.Yf[plotVar].shape), facecolor='k', edgecolor="None", alpha=0.3)
        plt.ylim(ymin=yMin, ymax=yMax)

        plt.ylabel(data.variables.ix[plotVar, "presentationUnits"])
        plt.title(data.variables.ix[plotVar, "name"])
        #data.variables.ix[plotVar, "Type"]
        plt.xticks(rotation=45)
        plt.legend(loc=9, ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.25))
        plt.savefig('C:\\GDP_nowcast_{0:%Y-%m-%d}.png'.format(datetime.today()), dpi=1000, frameon=False, transparent=True, bbox_inches='tight')
        plt.close()

    def plotLayout(self, ax):
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(True)

        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        plt.grid(False)
        ax.spines['top'].set_linewidth(0.5)
        ax.spines['right'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)

    def investigateResults(self):
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        fData = self.dfModel.fData
        Nx = self.dfModel.Nx
        print("\nFactors:", Nx)
        fig = plt.figure(1)
        for ii in range(1, Nx+1):
            ax = fig.add_subplot(Nx, 1, ii)
            plt.plot(fData.index, fData["Factor {0} (Mean)".format(ii)], c='b')
            plt.plot(fData.index, fData["Factor {0} (High)".format(ii)], c='r', ls='--')
            plt.plot(fData.index, fData["Factor {0} (Low)".format(ii)], c='r', ls='--')
            plt.plot(fData.index, np.zeros(shape=fData["Factor {0} (Mean)".format(ii)].shape), c='k')

        Yfit = self.dfModel.Yfit

        FILTER = Yfit["usnaac0169"].index.map(lambda x: (x.month % 3 == 0))
        print(Yfit["usnaac0169"][FILTER])
        fig = plt.figure(2)
        ax = fig.add_subplot(111)
        plt.plot(Yfit["usnaac0169"][FILTER].index, Yfit["usnaac0169"][FILTER]["Mean"], c='b')
        plt.plot(Yfit["usnaac0169"][FILTER].index, Yfit["usnaac0169"][FILTER]["Low"], c='r', ls='--')
        plt.plot(Yfit["usnaac0169"][FILTER].index, Yfit["usnaac0169"][FILTER]["High"], c='r', ls='--')
        plt.plot(Yfit["usnaac0169"][FILTER].index, np.zeros(shape=Yfit["usnaac0169"][FILTER]["High"].shape), c='k')
        plt.show()
