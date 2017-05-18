import numpy as np
import pandas as pd
import os
import sys
import logging
import calendar
import datetime
from stateSpaceSystem import stateSpaceSystem

def add_month(dateIn):
    mm = dateIn.month + 1
    if mm > 12:
        yy = int(dateIn.year + np.floor((mm-1)/12))
        mm = 1
    else:
        yy = int(dateIn.year)
    dd = calendar.monthrange(yy, mm)[1]
    dateOut = datetime.date(yy, mm, dd)
    return dateOut

def subtract_month(dateIn):
    mm = int(dateIn.month) - 1
    if mm == 0:
        yy = int(dateIn.year) -1
        mm = 1
    else:
        yy = int(dateIn.year)
    dd = calendar.monthrange(yy, mm)[1]
    dateOut = datetime.date(yy, mm, dd)
    print("\ndateOut: {0:%Y-%m-%d}".format(dateOut))
    return dateOut

class dfForecast(object):
    __name__ = "__forecast__"
    __version__ = "0.0.1"

    def __init__(self, model, options):
        self.stateSpaceSystem = stateSpaceSystem()
        NyQ = options["NyQ"]
        self.options = options
        self.model   = model

        ## -- Start date of Forecast -- ##
        FILTER = self.model.Yc.ix[:, -NyQ:].apply(lambda x: all(np.isfinite(x)), axis=1).values
        self.Tmax = self.model.Yc[FILTER].index.max()
        self.Tnow = self.model.Yc.index.max()
        self.hor = self.options["hor"]

        ## -- Run the forecast -- ##
        logging.debug("Forecast the dynamic factor model")
        self.forecastDFM()

    def forecastDFM(self):
        ## -- Options -- ##
        NyQ =self.options["NyQ"]
        NyM =self.options["NyM"]
        Nx = self.options["Nx"]
        plag = self.options["plag"]
        pp = max(5, plag)
        qlag = self.options["qlag"]
        qq = max(5, qlag)

        ## -- Parameters of the Model -- ##
        C = self.model.C
        Htilde = self.model.Htilde
        Qtilde= self.model.Qtilde
        A = self.model.A
        tthetaM   = self.model.parameters["tthetaM"]

        ## -- Observables and In-Sample factors -- ##
        Yobs = self.model.Yc.copy()
        Xhat = self.model.Xhat

        ## -- State-Space and Estimate of observables -- ##
        Tdelta = (self.Tnow.year - self.Tmax.year)*12 + self.Tnow.month - self.Tmax.month

        ## -- Forecast of States and dating of forecasts -- ##
        if Tdelta > 0:
            ## -- In-Sample fit -- ##
            Xf = Xhat[: , -Tdelta:]
            Ytilde = np.dot(C, Xf)

            ## -- Dates -- ##
            datesForecast = self.model.Yc[-Tdelta:].index.values
            datesStarted = True
        else:
            datesStarted = False

        if self.hor - Tdelta > 0:
            for hh in np.arange(1, self.hor - Tdelta+1):
                if datesStarted:
                    dNew = add_month(dateIn=max(datesForecast))
                    datesForecast = np.concatenate((datesForecast,  np.array([dNew])), axis=0)
                    Xf = np.concatenate((Xf, np.dot(A, Xf[:, -1:])), axis=1)
                    Ytilde = np.concatenate((Ytilde, np.dot(C, Xf[:, -1:])), axis=1)
                else:
                    dNew = add_month(dateIn=Yobs.index.max())
                    datesForecast = np.array([dNew])
                    datesStarted = True
                    Xf = np.dot(A, Xhat[:, -1:])
                    Ytilde = np.dot(C, Xf[:, -1:])

        ## -- Lagged Values -- ##
        FILTER = self.model.Yc.ix[:, 0:NyM].apply(lambda x: all(np.isfinite(x)), axis=1).values
        Ylag = self.stateSpaceSystem.revertMonthlyLags(Y=Yobs.values.T, tthetaM=tthetaM, qlag=qlag, NyM=NyM)

        dateLags = add_month(dateIn=self.model.Yc[FILTER].index.max())
        diffLags = (self.Tnow.year - dateLags.year)*12 + self.Tnow.month - dateLags.month

        Yf = pd.DataFrame(columns=list(self.model.Yc), index=datesForecast, dtype=np.float64)

        if (Tdelta > 0):
            Yf.ix[0:Tdelta, :] = np.dot(self.model.Ymean.T, np.ones(shape=(1, Tdelta))).T + Ylag[:,-Tdelta:].T + Ytilde[:,0:Tdelta].T
            FILTER = Yf.apply(lambda x: all(np.isfinite(x)), axis=1)
            if np.sum(FILTER) > 0:
                Tall = Yf[FILTER].index.max()
            else:
                Tall = subtract_month(Yf.index.min())
            Tlag = Tall
        else:
            Tall = subtract_month(Yf.index.min())
            Tlag = Tall

        TyMax = Yobs.index.max()

        ## -- Insert the Forecasts, Nowcasts, and Backcasts -- ##
        for tt in Yf[Yf.index > Tall].index:
            num = Yf[Yf.index <= tt].shape[0]
            logging.debug("tt: {0}, Tlag: {1}, num: {2:d}".format(tt, Tlag, num))
            if (Tlag > TyMax):
                Yobs.loc[Tlag] = Yf.ix[Tlag, :] # np.nan* np.ones(shape=(1,NyM+NyQ))
            elif any(np.isnan(Yobs.ix[Tlag, 0:NyM])):
                FILTER = np.isnan(Yobs.ix[Tlag, 0:NyM])
                select = [x for x in FILTER[FILTER].index]
                Yobs.ix[Tlag, select] = Yf.ix[Tlag, select]

            FILTER = (Yobs.index < tt)
            Ylag = self.stateSpaceSystem.revertMonthlyLags(Y=Yobs[FILTER].values.T, tthetaM=tthetaM, qlag=qlag, NyM=NyM)
            yf = self.model.Ymean.T + Ylag[:, -1:] + Ytilde[:, num-1:num]
            Yf.ix[tt, :] = yf.T
            if np.sum(np.isnan(Yf.ix[tt, ::].values)) > 0:
                raise ValueError("Yf[tt,:] is NaN for {0:%Y-%m-%d}".format(tt))
            Tlag = tt

        if np.sum(np.isnan(Yf.values)) > 0:
            msg = "Yf contains NaN values"
            raise ValueError(msg)

        ## -- Individual Components -- ##
        ## Common Component
        llambdaM = self.model.parameters["llambdaM"]
        Ycommonf = np.concatenate((np.dot(llambdaM, Xf[0:Nx ,:]), np.dot(C[-NyQ:, 0:Nx*pp], Xf[0:Nx*pp ,:])), axis=0)

        ## Mean
        Ymean = np.dot(self.model.Ymean.T, np.ones(shape=(1, Xf.shape[1])))

        ## Idiosyncratic Component
        Yidiosyncraticf = Yf.values.T  - Ymean - Ycommonf
        Yidiosyncraticf[-NyQ:, :] = np.dot(C[-NyQ:, -NyQ*qq:], Xf[-NyQ*qq:, :])

        ## -- Save to DataFrame -- ##
        self.Ymeanf = Ymean
        self.Yf = Yf
        #pd.DataFrame(data=Yf.T, columns=list(self.model.Yc), index=datesForecast)

        self.Ycommonf = pd.DataFrame(data=Ycommonf.T, columns=list(self.model.Yc), index=datesForecast)
        self.Yidiosyncraticf = pd.DataFrame(data=Yidiosyncraticf.T, columns=list(self.model.Yc), index=datesForecast)
        self.Xf = pd.DataFrame(data=Xf.T, columns=["xf_{0:d}".format(ii+1) for ii in range(0,Xf.shape[0])], index=datesForecast)
        #return Yf, Ymeanf, YcommonF, Yidiosyncraticf, Xf
    """
    def forecastPresent(self):
        function reTransformData(yf, yPresent, datesData, datesForecast, TransformCode, Tnow, Tmax)

        ## transformation code .== 1
        if all(TransformCode .==1)
        print("\nTransform code 1: exp(x)")
        ## -- Re-transform for a log of the variables -- ##
        yf = exp(yf)
        elseif all(TransformCode .== 2) | all(TransformCode .== 4)
        print("\nTransform code 2 or 4: y(t)= ytilde(t) +y(t-3)")
        for tt in 1:size(yf,1)
        if (tt  <= Tnow)

        ## -- There should be data -- ##
        if all(isfinite(yPresent[end-Tnow-4+tt,:]))
        yf[tt,:] = yf[tt, :] + yPresent[end-Tmax-4+tt, :]
        print("\nHistorical data: $tt, ytilde($(tt)): $(yf[tt,:]-yPresent[end-Tmax-4+tt, :]), yPresent($(tt-3)): $(yPresent[end-Tmax-4+tt, :]),  yf($tt): $(yf[tt,:])")
        else
        print("\nError: No Values for $(tt)!", yPresent[end-Tmax-4+tt,:])
        quit()
        end
        elseif (tt > Tnow) & (tt-4-Tmax <= 0)
        ## -- There May be data -- ##
        if all(isfinite(yPresent[end-Tmax-4+tt,:]))
        yf[tt,:] = yf[tt,:] + yPresent[end-Tmax-4+tt, :]
        print("\nHistorical data: $tt, ytilde($(tt)): $(yf[tt,:]-yPresent[end-Tmax-4+tt, :]), yPresent($(tt-3)): $(yPresent[end-Tmax-4+tt, :]),  yf($tt): $(yf[tt,:])")
        else
        yf[tt,:] = yf[tt,:] + yf[tt-3, :]
        print("\nForecasted data: $tt, ytilde($tt): $(yf[tt,:]-yf[tt-3, :]), yf($(tt-3)): $(yf[tt-3, :]),  yf($tt): $(yf[tt,:])")
        end
        elseif (tt-Tmax-4 > 0)
        ## -- There is only past forecasted data -- ##
        yf[tt,:] = yf[tt,:] + yf[tt-3,:]
        print("\nForecasted data: $tt, ytilde($tt): $(yf[tt,:]-yf[tt-3, :]), yf($(tt-3)): $(yf[tt-3, :]),  yf($tt): $(yf[tt,:])")
        else
        print("\nShould not reach this level: Error")
        quit()
        end
        end
        end

        return yf
        end
    """
