import numpy as np
#from scipy.optimize import minimize
import os
import sys
import logging

class stats(object):
    def kalmanFn(self, Yvar, Lmbda, H, A, Q, R=None, initX=None, initP=None):
        Ny, Ty = Yvar.shape
        Nx = A.shape[0]

        if not R:
            R = np.eye(Q.shape[0])

        ## -- Save Paraemeters -- ##
        self.Lmbda=Lmbda; self.H=H; self.A=A; self.R=R; self.Q=Q

        ## -- Initial Values -- ##
        if not initX:
            initX = np.zeros(shape=(Nx, 1))

        if not initP:
            initP = np.dot(R, np.dot(Q, R.T))

        ## -- Potential for having better guess for the initial values -- ##
        if True:
            loglik = self.kalmanFilter(Yvar=Yvar, Lmbda=Lmbda, H=H, A=A, R=R, Q=Q, initX=initX, initP=initP)
        else:
            self.kalmanFilterSquareRoot()

        ## -- Kalman Smoother -- ##
        #self.kalmanSmoother()
        return loglik, self.Xtt, self.Ptt

    def PCAfn(self, X, normalise=True):
        return PCAfunction(X=X, normalise=normalise)

    def kalmanFilter(self, Yvar, Lmbda, H, A, R, Q, initX, initP):
        Ny, Ty = Yvar.shape
        Nx = A.shape[0]

        yPlus = Yvar.copy()
        yPlus[np.isnan(Yvar)] = 0

        vv = np.zeros(shape=(Ny, Ty))*np.nan

        ## -- Xtt = E[X(t)|t], Ptt = E[X(t) - E[X(t)|t]]*E[X(t) - E[X(t)|t]].T-- ##
        ## For X(0|0) to X(T|T)
        Xtt = np.zeros(shape=(Nx, Ty))
        Ptt = np.zeros(shape=(Nx, Nx, Ty))

        ## -- E[X(t)|t-1] -- ##
        ## For X(0|-1) to X(T+1|T)
        Xtm = np.hstack((initX, np.zeros(shape=(Nx, Ty+1)) ))
        Ptm = np.zeros(shape=(Nx, Nx, Ty+1))
        Ptm[:,:,0] = initP

        ll = np.zeros(shape=(1, Ty))*np.NaN

        for tt in np.arange(0, Ty):

            ## -- Adjustment Missing Values -- ##
            Wt    = np.eye(Ny)[np.isfinite(Yvar[:,tt]),:]
            yStar = np.dot(Wt, yPlus[:,tt])

            if np.ndim(yStar) == 1:
                yStar = np.expand_dims(yStar, axis=1)
            HStar = np.dot(Wt, np.dot(H, Wt.T))
            LmbdaStar = np.dot(Wt, Lmbda)

            ## -- Prediction Error -- ##
            ee = yStar - np.dot(LmbdaStar, np.expand_dims(Xtm[:,tt], axis=1))
            vv[np.isfinite(Yvar[:,tt]), tt] = ee[:,0]

            ## -- Filtering -- ##
            ## F(t): Variance of Observable
            try:
                F = np.dot(LmbdaStar, np.dot(Ptm[:,:,tt], LmbdaStar.T)) + HStar
                Finv = np.linalg.pinv(F)
            except:
                print("\n\n{0:d}\n\nF:\n".format(tt))

                print("\n\nLmbdaStar")
                print(LmbdaStar)
                print("\n\nLmbda")
                print(Lmbda)
                print("\n\nWt")
                print(Wt)
                sys.exit(0)

            ## -- Kalman Gain -- ##
            #K = np.dot(A, np.dot(Ptm[:,:,tt], np.dot(Lmbda.T, Finv)))

            ## -- Update Current State: Xtt -- ##
            Xtt[:,tt:tt+1] = np.expand_dims(Xtm[:,tt], axis=1) + np.dot(Ptm[:,:,tt], np.dot(LmbdaStar.T, np.dot(Finv, ee)))

            ## -- Forecast next periods State -- ##
            Xtm[:, tt+1] = np.dot(A, Xtt[:,tt])

            ## -- Ptt: Variance-Covariance Matrix -- ##
            Ptt[:,:,tt] = Ptm[:,:,tt] - np.dot(np.dot(Ptm[:,:,tt], np.dot(LmbdaStar.T, np.dot(Finv, LmbdaStar))), Ptm[:,:,tt])

            ## -- Ptm: Forecasted Variance-Covaraince Matrix -- ##
            Ptm[:,:,tt+1] = np.dot(np.dot(A, Ptt[:,:,tt]), A.T) + np.dot(R, np.dot(Q, R.T))

            ## -- Log-likelihood -- ##
            ll[0,tt] = np.log(np.linalg.det(F)) + np.dot(ee.T, np.dot(Finv, ee))


        loglik = -Ty*Ny/2*np.log(2*np.pi) - np.sum(ll, axis=1)/2

        logging.info("\n{0:20s}{1:10.2f}\n{2:20s}{3:10.2f}".format("log-likelihood:", loglik[0], "likelihood:", np.exp(loglik[0])))

        self.vv = vv; self.Xtt = Xtt; self.Ptt=Ptt; self.Xtm = Xtm; self.Ptm = Ptm
        return loglik

    def kalmanFilterNormal(self):
        pass

    def kalmanFilterSquareRoot(self):
        Yvar = self.Yvar
        Ny, Ty = Yvar.shape
        Nx = self.A.shape[0]

        vv = np.zeros(shape=(self.Ny, self.Ty))

        ## -- Xtt = E[X(t)|t], Ptt = E[X(t) - E[X(t)|t]]*E[X(t) - E[X(t)|t]].T-- ##
        ## For X(0|0) to X(T|T)
        Xtt = np.zeros(shape=(self.Nx, self.Ty))
        Ptt = np.zeros(shape=(self.Nx, self.Nx, self.Ty))

        ## -- E[X(t)|t-1] -- ##
        ## For X(0|-1) to X(T+1|T)
        Xtm = np.hstack((self.initX, np.zeros(shape=(self.Nx, self.Ty+1)) ))
        Ptm = np.zeros(shape=(self.Nx, self.Nx, self.Ty+1))
        Ptm[:,:,0] = self.initP

        ll = np.zeros(shape=(1,self.Ty))*np.NaN

        for tt in np.arange(0, Ty):
            ## -- Prediction Error -- ##
            vv[:, tt] = Yvar[:,tt] - np.dot(self.Lmbda, Xtm[:,tt])

            ## -- Filtering -- ##
            ## F(t): Variance of Observable
            F = np.dot(self.Lmbda, np.dot(Ptm[:,:,tt], self.Lmbda.T)) + np.dot(self.ssigmaY, self.ssigmaY.T)
            Finv = np.linalg.pinv(F)

            ## -- Kalman Gain -- ##
            K = np.dot(self.A, np.dot(Ptm[:,:,tt], np.dot(self.Lmbda.T, Finv)))

            ## -- Update Current State: Xtt -- ##
            Xtt[:,tt] = Xtm[:,tt] + np.dot(Ptm[:,:,tt], np.dot(self.Lmbda.T, np.dot(Finv, vv[:,tt])))

            ## -- Forecast next periods State -- ##
            Xtm[:, tt+1] = np.dot(self.A, Xtt[:,tt])

            ## -- Square Root Form -- ##
            Ptilde = np.linalg.cholesky(Ptm[:,:,tt])
            Htilde = self.ssigmaY
            RQtilde = self.ssigmaX
            U = np.vstack((
                    np.hstack((np.dot(self.Lmbda, Ptilde), Htilde, np.zeros(shape=(self.Ny, self.Nx)))),
                    np.hstack((np.dot(self.A, Ptilde), np.zeros(shape=(self.Nx, self.Ny)), RQtilde ))
                    ))
            q, r = np.linalg.qr(U)

            ## -- Ptt: Variance-Covariance Matrix -- ##
            Ptt[:,:,tt] = Ptm[:,:,tt] - np.dot(np.dot(Ptm[:,:,tt], np.dot(self.Lmbda.T, np.dot(Finv, self.Lmbda))), Ptm[:,:,tt])

            ## -- Ptm: Forecasted Variance-Covaraince Matrix -- ##
            Ptm[:,:,tt+1] = np.dot(np.dot(self.A, Ptt[:,:,tt]), self.A) + np.dot(self.ssigmaX, self.ssigmaX.T)

            ## -- Log-likelihood -- ##
            ll[0,tt] = np.log(np.linalg.det(F)) + np.dot(vv[:,tt:tt+1].T, np.dot(Finv, vv[:,tt:tt+1]))

        loglik = -Ty*Ny/2*np.log(2*np.pi) - np.sum(ll, axis=1)/2

        logging.info("log-likelihood: {0}, likelihood: {1}".format(loglik, np.exp(loglik[0])))

        self.vv = vv; self.Xtt = Xtt; self.Ptt=Ptt; self.Xtm = Xtm; self.Ptm = Ptm; self.loglik = loglik

    def kalmanSmoother(self):
        Yvar = self.Yvar
        Ny, Ty = Yvar.shape
        Nx = self.A.shape[0]

        XtT = np.zeros(shape=(Nx,Ty))
        XmT = np.zeros(shape=(Nx,Ty))
        for tt in np.arange(start=Ty-1, stop=0, step=-1):
            pass

    def OLSfn(self, yy, xx, constant=True):
        if yy.ndim == 1:
            yy = np.expand_dims(yy, axis=1)
        elif yy.ndim > 2:
            logging.error("\nError: Too many dimension of {0}".format(yy.ndim))
            raise ValueError

        if xx.ndim == 1:
            xx = np.expand_dims(xx, axis=1)
        elif xx.ndim > 2:
            logging.error("\nError: Too many dimension of {0}".format(xx.ndim))
            raise ValueError

        Ty, Ny = yy.shape
        Tx, Nx = xx.shape
        if Ty != Tx:
            raise ValueError("Ty ({0:d}) not equal to Tx ({1:d})".format(Ty, Tx))


        if constant:
            xx = np.concatenate((np.ones(shape=(Ty, 1)), xx), axis=1)

        bbeta = np.dot(np.linalg.pinv(xx), yy)
        ee = yy - np.dot(xx, bbeta)  # VAR residuals
        ssigma = np.dot(ee.T, ee)/(Ty - bbeta.size)
        ssigmaY = np.var(yy, axis=0)

        R2 = np.zeros(shape=(Nx, 1))
        for ii in range(0,Nx):
            R2[ii,0] = 1 - ssigma[ii,ii]/ssigmaY[ii]
        return bbeta, R2, ssigma, ee

    def varpFunction(self, Yvar,  plag, constant=True):
        if Yvar.ndim == 1:
            Yvar = np.expand_dims(Yvar, axis=1)
        elif Yvar.ndim > 2:
            logging.error("\nError: Too many dimension of {0}".format(Yvar.ndim))
            raise ValueError

        Ty, Ny = Yvar.shape
        if (Ty < Ny):
            flip = True
            Yvar = Yvar.T
        else:
            flip = False

        YY = Yvar[plag:,:]


        if constant:
            XX = np.ones(shape=(Yvar.shape[0]-plag,1))
            for ii in range(1, plag+1):
                XX = np.concatenate((XX, Yvar[0+plag-ii:-ii, :]), axis=1)
        else:
            XX = Yvar[plag-1:-1, :]
            for ii in range(2, plag+1):
                XX = np.concatenate((XX, Yvar[0+plag-ii:-ii, :]), axis=1)

        bbeta = np.dot(np.linalg.pinv(XX), YY)
        ee = YY - np.dot(XX, bbeta)  # VAR residuals
        ssigma = np.dot(ee.T, ee)/(Ty - bbeta.size)

        #ssigma = np.cov(ee, rowvar=0)       # VAR covariance matrix

        if flip:
            bbeta = bbeta.T; ssigma = ssigma.T
        return bbeta, ssigma


class PCAfunction(object):
    def __init__(self, X, normalise=True):
        if (np.ndim(X) == 1):
            X = np.expand_dims(X, axis=1)
        elif (np.ndim(X) > 2):
            logging.error("\nError too many dimensions: ", np.ndim(X))
            raise ValueError

        Ty, Ny = X.shape
        if Ny > Ty:
            X = X.T
            self.flip = True
        else:
            self.flip = False

        self.X = X
        if normalise:
            self.Xc, self.Xmean, self.Xstd =self.normalise(X)
        else:
            self.Xc = X

        self.PCAsvd(Xc=self.Xc)

    def PCAsvd(self, Xc):
        ## -- Singular Value Decomposition -- ##
        u, s, v = np.linalg.svd(a = Xc, full_matrices=False)

        pcsd = s/np.sqrt(Xc.shape[0])
        pcv = pcsd**2
        pcvsum = np.sum(pcv)

        # re-scale back principal components if scaling used
        #self.rotation = scale ? make_cols_unit_norm!(v.* self.Xstd.T) : Xsvd[:V]
        if self.flip:
            self.scores = np.dot(u, np.diag(s)).T
            self.standard_deviations = pcsd.T
            self.proportion_of_variance = pcv/pcvsum.T
            self.cumulative_variance = np.cumsum(pcv)/pcvsum.T
        else:
            self.scores = np.dot(u, np.diag(s))
            self.standard_deviations = pcsd
            self.proportion_of_variance = pcv/pcvsum
            self.cumulative_variance = np.cumsum(pcv)/pcvsum


    def normalise(self, X):
        Xmean = np.expand_dims(np.mean(X, axis=0), axis=0)
        Xstd  = np.std(X, axis=0)
        Xc = np.dot((X - np.dot(np.ones(shape=(X.shape[0],1)), Xmean)), np.diag(1./Xstd))
        return Xc, Xmean, Xstd


if __name__ == "__main__":
    stats = stats()
    Xvar = np.random.normal(size=(100,10))
    pca = stats.PCAfn(X=Xvar)
    print(pca.scores.shape)
    print(pca.proportion_of_variance)
    print(pca.cumulative_variance)
