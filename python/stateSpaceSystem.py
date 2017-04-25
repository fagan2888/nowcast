import numpy as np
import pandas as pd
import logging
import os
import sys

class stateSpaceSystem(object):
    __name__ = "__StateSpace__"
    __version__ = "0.0.1"

    def __init__(self):
        pass

    def stateSpace(self, parameters, options):
        qlag      = options["qlag"]
        plag      = options["plag"]
        Nx        = options["Nx"]
        nyQ       = int(options["nyQ"])
        nyM       = options["nyM"]

        ## -- Adjusting of Quaterly variables -- ##
        qq = max(5, qlag)
        pp = max(5, plag, qlag+1)

        ## -- Recover the parameters -- ##
        llambdaM    = parameters["llambdaM"]
        llambdaQ    = parameters["llambdaQ"]
        PPhi        = parameters["PPhi"]
        tthetaM     = parameters["tthetaM"]
        tthetaQ     = parameters["tthetaQ"]
        Q           = parameters["Q"]
        HMonthly    = parameters["HMonthly"]
        HQuarterly  = parameters["HQuarterly"]

        ## -- The Measurement Equation: C e.g. Factor Loadings -- ##
        ## Monthly
        cMonthlyF = np.concatenate((np.dot(np.concatenate((np.eye(nyM), -tthetaM) ,axis=1), np.kron(np.eye(qlag+1), llambdaM)),  np.zeros(shape=(nyM, (pp - qlag - 1)*Nx))),axis=1)
        cMonthlyU = np.zeros(shape=(nyM, qq*nyQ))

        ## Quarterly
        Iqq = np.array([[1/3., 2/3., 1., 2./3., 1./3.]])
        Iqq = np.concatenate((Iqq, np.zeros(shape=(1, qq - 5))), axis=1)
        IQuarterlyResidual = np.kron(Iqq, np.eye(nyQ))
        cQuarterlyU = IQuarterlyResidual

        ## Quarterly: Factor loadings
        Ipp = np.array([[1/3., 2/3., 1., 2./3., 1./3.]])
        Ipp = np.concatenate((Ipp, np.zeros(shape=(1, pp - 5))), axis=1)
        IQuarterlyFactors = np.kron(Ipp, np.eye(Nx))
        cQuarterlyF = np.dot(llambdaQ, IQuarterlyFactors)

        ## Combine
        C = np.concatenate((np.concatenate((cMonthlyF, cMonthlyU), axis=1), np.concatenate((cQuarterlyF, cQuarterlyU), axis=1)),axis=0)

        ## Measurement Equation: H - Noise ---#
        # arbitrary small variance for quarterly variables
        Htilde = np.concatenate((np.concatenate((HMonthly, np.zeros(shape=(nyM, nyQ))), axis=1), np.concatenate((np.zeros(shape=(nyQ, nyM)), np.eye(nyQ)*1e-8), axis=1)), axis=0)

        ## -- State Equation: A - Transition Dynamics -- ##
        # Dynamics: Common Component
        aFF = np.concatenate((PPhi, np.zeros(shape=(Nx, (pp-plag)*Nx))), axis=1)
        aFF = np.concatenate((aFF, np.concatenate((np.eye((pp - 1)*Nx), np.zeros(shape=((pp - 1)*Nx, Nx))), axis=1)), axis=0)

        aFU = np.zeros(shape=(pp*Nx, nyQ*qq))
        aUF = np.zeros(shape=(nyQ*qq, pp*Nx))

        ## Idiosyncratic Component
        aQu = np.concatenate((tthetaQ, np.zeros(shape=(nyQ, (qq - qlag)*nyQ))), axis=1)
        aQu = np.concatenate((aQu, np.concatenate((np.eye(nyQ*(qq - 1)), np.zeros(shape=(nyQ*(qq-1), nyQ))), axis=1)), axis=0)
        aUU = aQu

        A = np.concatenate((np.concatenate((aFF, aFU), axis=1), np.concatenate((aUF, aUU), axis=1)), axis=0)

        ## -- State Equation: State Innovations -- ##
        ## Factors
        Qtilde = np.concatenate((np.concatenate((Q, np.zeros(shape=(Nx, (pp-1)*Nx + qq*nyQ))), axis=1),  np.zeros(shape=((pp-1)*Nx, pp*Nx + qq*nyQ))), axis=0)
        ## Quarterly
        Qtilde = np.concatenate((Qtilde, np.concatenate((np.zeros(shape=(nyQ, pp*Nx)), HQuarterly, np.zeros(shape=(nyQ, (qq-1)*nyQ))), axis=1), np.zeros(shape=((qq-1)*nyQ, pp*Nx + qq*nyQ))), axis=0)

        ## -- Properties of the State Space System -- ##
        # Stability: Transition matrix
        if True:
            w, v = np.linalg.eig(A)
            if (np.max(abs(w)) >= 1):
                logging.error("\nUnstable system\nMax Eigen Value: {0:6.2f}".format(np.max(abs(w))))
                #raise ValueError
            else:
                logging.info("\nSystem Stable\nMax Eigen Value: {0:6.2f}".format(np.max(abs(w))))

        return C, A, Htilde, Qtilde

    def MonthlyLags(self, Y, parameters, options):
        ## Inputs
        # Y: Ny.T data matrix
        ## Outputs
        # Ytilde
        # Ylag

        Ny, Ty = Y.shape
        if (Ny > Ty):
            Y = Y.T
            Ny, Ty = Y.shape
            flip = True
        else:
            flip = False

        ## -- Parameters and model -- ##
        nyM       = options["nyM"]
        nyQ       = options["nyQ"]
        Ny        = nyM + nyQ
        qlag      = options["qlag"]
        tthetaM   = parameters["tthetaM"]

        ## -- De-lag -- ##
        Ylag = np.nan * np.zeros(shape=(nyM+nyQ, Ty-qlag))
        for nn in range(0, nyM):
            xx = np.expand_dims(Y[nn, qlag-1:-1], axis=0)
            select = np.array((nn))
            for jj in range(1,qlag):
                select.append(nyM*jj+nn)
                xx = np.concatenate((xx, np.expand_dims(Y[nn, qlag-jj-1:-jj-1], axis=0)))
            Ylag[nn, :] = np.dot(tthetaM[nn, select], xx)
        Ylag[-nyQ:, :] = 0

        ## -- Clean out the lags -- ##
        Ytilde = Y[:, qlag:] - Ylag

        if flip:
            Ytilde = Ytilde.T
            Ylag   = Ylag.T

        return Ytilde, Ylag

    def revertMonthlyLags(self, Y, tthetaM, nyM, qlag):
        Ty = Y.shape[1]
        nyQ = Y.shape[0] - nyM

        Ylag = np.nan * np.zeros(shape=(nyM+nyQ, Ty-qlag))
        for nn in range(0, nyM):
            xx = np.expand_dims(Y[nn, qlag:], axis=0)
            select = np.array([nn])
            for jj in range(1, qlag):
                select = np.concatenate((select, np.array([nyM*jj+nn])), axis=0)
                xx = np.concatenate((xx, np.expand_dims(Y[nn, qlag-jj:-jj], axis=0)))
            Ylag[nn, :] = np.dot(tthetaM[nn, select], xx)
        Ylag[-nyQ:, :] = 0

        return Ylag
"""

###########################################################
function pickTnow(datesData, Y)
  ## -- Define time periods -- ##
  lastYear = Dates.year(datesData[end,end])
  lastMonth = Dates.month(datesData[end,end])


  if all(isfinite(Y[maximum((1:size(Y,1))[isfinite(Y[:,end])]),1:end-1]))
    datesMaxGDP = datesData[maximum((1:size(Y,1))[isfinite(Y[:,end])])]
  else
    datesMaxGDP = datesData[maximum((1:size(Y,1))[isfinite(Y[:,end])])-3]
  end
  lastYearGDP = Dates.year(datesMaxGDP)
  lastMonthGDP = Dates.month(datesMaxGDP)

  ## -- Time In-sample, Nowcast and Forecast -- ##
  if (lastMonth - lastMonthGDP > 3)
    Tnow = 3
    Tmax = lastMonth - lastMonthGDP
  else
    if (lastMonth % 3 == 0)
      Tnow = 3
    elseif (lastMonth % 3 == 2)
      Tnow = 2
    elseif (lastMonth % 3 == 1)
      Tnow = 1
    else
      print("\nError: Can't recognise Tpick: exit")
      quit()
    end
    Tmax = Tnow
  end

  return Tnow, Tmax, lastMonth, lastYear
end
"""
