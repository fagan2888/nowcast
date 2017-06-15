import numpy as np
import pandas as pd
import os
import sys
import logging
from stats import stats
from stateSpaceSystem import stateSpaceSystem


class dynFAMissing(object):
    def __init__(self, Yvar, options):
        self.Yvar = Yvar
        self.options = options
        self.stats = stats()
        self.stateSpaceSystem = stateSpaceSystem()

        ## -- model -- ##
        self.model()

    def model(self):
        ## -- Recover the settings of the model -- ##
        self.qlag = np.int64(self.options["qlag"])
        self.plag = np.int64(self.options["plag"])
        self.Nx = np.int64(self.options["Nx"])
        #self.max_iter = np.int64(self.options["max_iter"])
        self.NyQ = np.int64(self.options["NyQ"])
        self.NyM = np.int64(self.options["NyM"])

        ## - -Pick the minimum lags -- ##
        self.pp = max(5, self.plag, self.qlag)
        self.qq = max(5, self.qlag)

        ## -- Dimensions of the data -- ##
        self.Ty = self.Yvar.shape[0]

        if True:
            logging.debug("\nBalanced Panel PCA and OLS: two stage estimation")
            self.balancedPanelPCA()
        else:
            logging.debug("\nGibbs Sampling")

    def balancedPanelPCA(self):
        parameters = {}

        ## -- Balanced Panel: PCA -- ##
        selectM = self.Yvar.columns[:-self.NyQ]
        selectQ = self.Yvar.columns[-self.NyQ:]

        FILTER = self.Yvar.ix[:, selectM].apply(lambda x: all(np.isfinite(x)), axis=1)
        Yhat = self.Yvar.ix[FILTER, selectM]
        pca = self.stats.PCAfn(X=Yhat)
        fhat =  pca.scores[:, 0:self.Nx]

        ## Store factors
        colNames = ["Factor {0:d}".format(ii) for ii in range(1,self.Nx+1)]
        self.fPCA = pd.DataFrame(columns=colNames, data=fhat, index=self.Yvar[FILTER].index)
        self.filterBalance = FILTER

        ## -- Law of Motion: Factors -- ##
        bbetaFactors, ssigmaFactors = self.stats.varpFunction(Yvar=fhat,  plag=self.plag, constant=False)
        PPhi = bbetaFactors.T
        parameters["PPhi"] = PPhi

        ################
        ## -- Step (1.2) Measurement Equation -- ##
        ## Estimate Monthly Parameters
        Ny = self.NyM + self.NyQ
        Ymean = np.zeros(shape=(1, Ny))*np.nan
        select = self.Yvar.columns
        for num, col in enumerate(self.Yvar.columns):
            FILTER = np.isfinite(self.Yvar.ix[:, col])
            Ymean[:, num] = np.mean(self.Yvar.ix[FILTER, col])

        ## -- Demean the data -- ##
        self.Ymean = Ymean
        Yc = (self.Yvar - np.kron(np.ones(shape=(self.Ty,1)), self.Ymean))
        self.Yc = Yc

        ## -- Monthly Data: Measurement Equation -- ##
        logging.debug("\nOLS Estimate of Monthly parameters")
        llambdaM = np.dot(np.linalg.pinv(fhat), Yc.ix[self.filterBalance, selectM]).T
        if (np.sum(np.isnan(llambdaM)) > 0):
            msg = "Error! llambdaM has NaN values"
            msg += "\n{0}".format(logging.error(llambdaM))
            raise ValueError(msg)

        residualMonthly = Yc.ix[self.filterBalance, selectM] - np.dot(fhat, llambdaM.T)
        tthetaM = np.zeros(shape=(self.NyM, self.NyM * self.qlag))

        for num, col in enumerate(residualMonthly.columns):
            yy = np.expand_dims(residualMonthly.ix[self.qlag:, col], axis=1)
            xx = np.expand_dims(residualMonthly.ix[self.qlag-1:-1, col],axis=1)
            for jj in range(2, self.qlag):
                xx = np.hstack((xx, np.expand_dims(residualMonthly.ix[self.qlag-jj:-jj, col],axis=1)))

            bb = np.dot(np.linalg.pinv(xx), yy)
            select = np.arange(start=num, step=self.NyM, stop=(self.NyM * self.qlag))
            tthetaM[num, select] = bb.T
        parameters["tthetaM"] = tthetaM


        ## -- Quarterly Data: Measurement Equation -- ##
        logging.debug("\nOLS Estimate of Quarterly parameters")
        Iq = np.array([[1/3., 2/3., 1., 2./3., 1./3.]])
        if (self.pp-5 > 0):
            IQuarterlyFactors  = np.kron( np.concatenate( (Iq, np.zeros(shape=(1, self.pp-5))), axis=1), np.eye(self.Nx))
        else:
            IQuarterlyFactors = np.kron(Iq , np.eye(self.Nx))

        if (self.qq-5 >0):
            IQuarterlyResidual = np.kron(np.concatenate((Iq, np.zeros(shape=(1, self.qq-5))), axis=1), np.eye(self.NyQ))
        else:
            IQuarterlyResidual = np.kron(Iq, np.eye(self.NyQ))

        # TStart ??
        # TEnd ??
        Yq = Yc.ix[:, selectQ]

        T, N  = Yq.shape
        FILTER = Yq.ix[:, :].apply(lambda x: all(np.isfinite(x)), axis=1) #np.isfinite(Yq.ix[:,0:])
        selectFilter = FILTER  & self.filterBalance
        selectFilter[0:3] = False

        filterQuarter = Yq[self.filterBalance].index.map(lambda x: (x.month % 3 == 0)) & Yq.ix[self.filterBalance, :].apply(lambda x: all(np.isfinite(x)), axis=1)
        filterQuarter[0:3] = False
        rangeSelect = np.arange(start=0, stop=fhat.shape[0], step=1)

        fGDP = fhat[rangeSelect[filterQuarter.values]]
        for tt in range(1, self.pp):
            fGDP = np.concatenate((fGDP, fhat[rangeSelect[filterQuarter.values] - tt]), axis=1)


        ## Parameters for Quarterly Data Loadings
        llambdaQ = np.dot(np.linalg.pinv(np.dot(fGDP, IQuarterlyFactors.T)), Yq[self.filterBalance][filterQuarter]).T
        if (np.sum(np.isnan(llambdaQ)) > 0):
            msg = "Error! llambdaQ has NaN values"
            raise ValueError(msg)

        parameters["llambdaQ"] = llambdaQ

        ## Initial Guess of idiosyncratic component: Arbitrary
        ## Kill persistance...
        tthetaQ = np.kron(np.ones(shape=(1,self.qlag)), np.eye(self.NyQ)) *0 # OR ZERO
        parameters["tthetaQ"] = tthetaQ

        ## -- The State Transition Equation -- ##
        logging.debug("\nFactor transition equation")

        ## -- Monthly Factors -- ##
        Fstate = fhat[self.pp:, :]
        for ii in range(1, self.pp):
            Fstate = np.concatenate((Fstate, fhat[self.pp-ii:-ii, :]), axis=1)

        Fstate = np.concatenate((Fstate, np.zeros(shape=(Fstate.shape[0], self.NyQ*5))), axis=1)

        ## -- The Variance-Covariance Matrix of the states -- ##
        ## -- Innovation Common Component -- ##
        Q = np.diag(np.diag(ssigmaFactors))
        parameters["Q"] = Q

        ## -- Variance-Covariance Idiosyncratic Component -- ##
        HMonthly = np.diag( np.diag( np.cov( residualMonthly, rowvar=0) ) )
        parameters["HMonthly"] = HMonthly
        HQuarterly = np.eye(self.NyQ)*1e-3 # OBS: NOT ESTIMATED
        parameters["HQuarterly"] = HQuarterly

        ## Store the parameters
        parameters = {
            "llambdaM": llambdaM,
            "llambdaQ": llambdaQ,
            "PPhi": PPhi,
            "tthetaM": tthetaM,
            "tthetaQ": tthetaQ,
            "Q": Q,
            "HMonthly": HMonthly,
            "HQuarterly": HQuarterly
            }

        C, A, Htilde, Qtilde = self.stateSpaceSystem.stateSpace(parameters=parameters, options=self.options)
        Ytilde, self.Ylag = self.stateSpaceSystem.MonthlyLags(Y=self.Yc.values.T, parameters=parameters, options=self.options)
        indexVal = self.Yc.index[self.qlag:]

        tt=0
        Tmax = Ytilde.shape[1]
        runModel = False
        while True:
            if any(np.isfinite(Ytilde[:self.NyM,tt])):
                TStart = tt
                runModel = True
                break
            else:
                tt +=1
            if (tt > Tmax):
                TStart = None
                raise ValueError("Break: TStart not found, all NaN")

        if runModel:
            loglik, Xhat, Phat = self.stats.kalmanFn(Yvar=Ytilde[:, TStart:], Lmbda=C, H=Htilde, A=A, Q=Qtilde)
        else:
            msg = "\nError TStart {0}\nBreak".format(TStart)
            raise ValueError(msg)

        ## -- Uncertainty -- ##
        fhat = Xhat[0:self.Nx,:]
        phat = Phat[0:self.Nx, 0:self.Nx,:]
        XhatHigh = np.zeros(shape=Xhat.shape) * np.NaN
        XhatLow  = np.zeros(shape=Xhat.shape) * np.NaN

        for tt in range(0, Xhat.shape[1]):
            if np.all(np.linalg.eigvals(Phat[:,:,tt]) > 0):
                try:
                    Pvar = np.linalg.cholesky(Phat[:,:,tt])
                except:
                    if np.any(Phat[:,:,tt] < 0):
                        Pvar = np.diag(np.sqrt(np.diag(Phat[:,:,tt])))
                    else:
                        Pvar = np.sqrt(Phat[:,:,tt])
            else:
                logging.debug("\nPhat is not semi-positive definite at t: {0:d}".format(tt))
                if np.any(Phat[:,:,tt] < 0):
                    Pvar = np.diag(np.sqrt(np.diag(Phat[:,:,tt])))
                else:
                    Pvar = np.sqrt(Phat[:,:,tt])

            XhatHigh[:, tt:tt+1]  = np.expand_dims(Xhat[:, tt], axis=1) + np.dot(Pvar, 2*np.ones(shape=(Xhat.shape[0],1)))
            XhatLow[:, tt:tt+1]   = np.expand_dims(Xhat[:, tt], axis=1) - np.dot(Pvar, 2*np.ones(shape=(Xhat.shape[0],1)))

        ## -- Fitted to Observables -- ##
        Yhat = np.dot(self.Ymean.T, np.ones(shape=(1, Xhat.shape[1]))) + self.Ylag[:, TStart:] + np.dot(C, Xhat)

        YhatLow = np.dot(self.Ymean.T, np.ones(shape=(1, Xhat.shape[1]))) + self.Ylag[:, TStart:] + np.dot(C, XhatLow)
        YhatHigh = np.dot(self.Ymean.T, np.ones(shape=(1, Xhat.shape[1]))) + self.Ylag[:, TStart:] + np.dot(C, XhatHigh)
        listVar = list(self.Yvar)
        Yfit = {}
        colName = ["Mean", "Low", "High"]
        listVar = list(self.Yvar)
        for num, name in enumerate(listVar):
            yy = np.concatenate((Yhat[num:num+1,:].T, YhatLow[num:num+1,:].T, YhatHigh[num:num+1,:].T), axis=1)
            Yfit[name] = pd.DataFrame(index=indexVal[TStart:], columns=colName, data=yy)

        self.Yfit = Yfit

        ## -- Individual Components -- ##
        ## Common Component
        Ycommon = np.concatenate((np.dot(llambdaM, Xhat[0:self.Nx ,:]), np.dot(C[-self.NyQ:, 0:self.Nx*self.pp], Xhat[0:self.Nx*self.pp ,:])), axis=0)
        self.Ycommon = pd.DataFrame(data=Ycommon.T, columns=list(Yc), index=indexVal[TStart:])
        ## Idiosyncratic Component
        Yidiosyncratic = Yc.ix[TStart+self.qlag:, :].values.T - Ycommon
        Yidiosyncratic[-self.NyQ:, :] = np.dot(C[-self.NyQ:, -self.NyQ*self.qq:], Xhat[-self.NyQ*self.qq:, :])
        self.Yidiosyncratic = pd.DataFrame(data=Yidiosyncratic.T, columns=list(Yc), index=indexVal[TStart:])

        self.Yhat = pd.DataFrame(data=Yhat.T, columns=list(Yc), index=indexVal[TStart:])

        ## -- DataFrame -- ##
        colName = ["Factor {0} (Mean)".format(ii) for ii in range(1,self.Nx+1)]
        fMean = pd.DataFrame(index=indexVal[TStart:], data=Xhat[:self.Nx,:].T, columns=colName)

        colName = ["Factor {0} (High)".format(ii) for ii in range(1,self.Nx+1)]
        fHigh = pd.DataFrame(index=indexVal[TStart:], data=XhatHigh[:self.Nx,:].T, columns=colName)

        colName = ["Factor {0} (Low)".format(ii) for ii in range(1,self.Nx+1)]
        fLow = pd.DataFrame(index=indexVal[TStart:], data=XhatLow[:self.Nx,:].T, columns=colName)
        self.fData = pd.concat((fMean, fHigh, fLow), axis=1)

        ## -- Store Results -- ##
        self.parameters = parameters; self.Xhat = Xhat; self.fhat = fhat; self.XhatHigh = XhatHigh; self.XhatLow = XhatLow
        self.C = C; self.Htilde = Htilde; self.Qtilde= Qtilde; self.A = A
