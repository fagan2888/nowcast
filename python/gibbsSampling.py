import numpy as np
#from scipy import stats
import os
import sys
if __name__ == "__main__":
    import matplotlib as mpl
    import matplotlib.pyplot as plt

class bayesianEstimation(object):
    __name__ = "__bayesian__"
    __version__ = "0.0.1"

    def __init__(self, Nx:int=2, Ny:int=1):
        self.Nx = Nx
        self.Ny = Ny
        self.Ty = 100
        self.cons = True

        ## -- Hyper parameters -- ##
        ## bbeta
        self.B0 = np.zeros(shape=(self.Nx + self.cons, self.Ny))
        self.ssigmaB0 = np.eye(self.Nx+self.cons)
        self.ssigmaB0Inv = np.linalg.pinv(self.ssigmaB0)
        self.ssigmaB0Chol = np.linalg.cholesky(self.ssigmaB0)

        ## ssigmaY
        self.ddelta0 = 1
        self.nnu0 = 1

        ## Exogenous Parameters
        self.ssigmaX = 1e4*np.linalg.pinv(np.random.gamma(shape=1, scale=1, size=(self.Nx, self.Nx)))
        self.mmuX = np.random.normal(size=(1,self.Nx))
        self.mmuX = np.zeros(shape=(1,self.Nx))


        ## -- Draw Parameters -- ##
        self.bbeta = self.bbetaPrior()
        self.ssigmaY = self.ssigmaYPrior()

        ## -- Monte Carlo Sample -- ##
        self.monteCarloSample()

    def bbetaPrior(self):
        #bbeta = self.B0 + np.dot(self.ssigmaB0Chol, np.random.normal(size=(self.Nx+self.cons, self.Ny)))
        bbeta = np.ones(shape=(self.Nx+1, self.Ny)) + np.random.normal(size=(self.Nx+self.cons, self.Ny))
        return bbeta

    def bbetaPosterior(self, ssigmaY, Yvar, Xvar):
        ssigmaYInv = 1.0/ssigmaY
        B1 = (self.ssigmaB0Inv + ssigmaYInv *np.dot(Xvar.T, Xvar))
        B1 = np.dot(np.linalg.pinv(B1), (np.dot(self.ssigmaB0Inv, self.B0) + ssigmaYInv* np.dot(Xvar.T, Yvar)) )
        ssigmaB1 = np.linalg.pinv(self.ssigmaB0Inv + ssigmaYInv * np.dot(Xvar.T, Xvar))

        bbeta =  B1 + np.dot(np.linalg.cholesky(ssigmaB1), np.random.normal(size=(Xvar.shape[1], Yvar.shape[1])))

        return bbeta

    def ssigmaYPrior(self):
        ssigmaInv = np.random.gamma(scale=self.nnu0/2, shape=1/(self.ddelta0/2), size=(self.Ny, self.Ny))
        ssigma = 1/ssigmaInv
        return ssigma

    def ssigmaYPosterior(self, bbeta, Yvar, Xvar):
        Ty, Ny = Yvar.shape

        nnu1 = (self.nnu0 + self.Ty )/2
        ddelta1 = (self.ddelta0  + np.dot((Yvar - np.dot(Xvar, bbeta)).T, (Yvar - np.dot(Xvar, bbeta))))/2
        ssigmaInv =  np.random.gamma(shape=nnu1, scale=1/ddelta1, size=(self.Ny, self.Ny))
        ssigma = 1/ssigmaInv
        return ssigma

    def monteCarloSample(self):
        eepsX = np.dot(np.random.normal(size=(self.Ty, self.Nx)), self.ssigmaX)
        self.Xsim = np.dot(np.ones(shape=(self.Ty,1)), self.mmuX) + eepsX
        Xvar = np.hstack((np.ones(shape=(self.Ty,1)), self.Xsim))

        self.eeps = np.random.normal(size=(self.Ty, self.Ny), scale= self.ssigmaY)
        self.Ysim = np.dot(Xvar, self.bbeta) + self.eeps


    def gibbsSampling(self, Yvar, Xvar, L:int=1000, M:int=10000, cons:bool=True):
        if cons:
            Xvar = np.hstack((np.ones(shape=(Yvar.shape[0],1)), Xvar))

        ssigmaY0 = self.ssigmaYPrior()
        bbeta0 = self.bbetaPrior()

        Bhat = np.ones(shape=(self.Nx+cons, self.Ny, L+M+1))
        ssigmaY = np.ones(shape=(self.Nx+cons, self.Nx+cons, L+M+1))

        Bhat[:,:,0] = bbeta0
        ssigmaY[:,:,0]= ssigmaY0

        for jj in range(0, L+M):
            ## 1) Draw bbeta1 | ssigmaY0, Yvar, Xvar ##
            bbeta1 = self.bbetaPosterior(ssigmaY=ssigmaY0, Yvar=Yvar, Xvar=Xvar)

            ## 2) Draw ssigmaY | bbeta1, Yvar, Xvar ##
            ssigmaY1 = self.ssigmaYPosterior(bbeta=bbeta1, Yvar=Yvar, Xvar=Xvar)

            ## 3) Store Results and Update B0 and ssigmaY0 ##
            Bhat[:,:, jj+1] = bbeta1
            ssigmaY[:,:,jj+1] = ssigmaY1

            bbeta0 = bbeta1
            ssigmaY0 = ssigmaY1

        return Bhat[:, :, L:], ssigmaY[:, :, L:]


    def OLS(self, Yvar, Xvar, cons=True):
        if cons:
            Xvar = np.hstack((np.ones(shape=(Yvar.shape[0],1)), Xvar))
        bbetahat = np.dot(np.linalg.pinv(Xvar), Yvar)
        return bbetahat

if __name__ == "__main__":
    print("\nMain file: MonteCarlo")
    obj = bayesianEstimation()
    bhatOLS = obj.OLS(Yvar=obj.Ysim, Xvar=obj.Xsim)
    bhatGibbs, ssigmaYGibbs = obj.gibbsSampling(Yvar=obj.Ysim, Xvar=obj.Xsim)



    print("\n\n{0:4s}|{1:10s}|{2:10s}|{3:10s}|{4:10s}|{5:15s}|{6:10s}|".format("", "Truth", "OLS", "Gibbs Mean", "Gibbs High","Gibbs Median", "Gibbs Low"))
    print("-"*(4+10*5+6))
    fig = plt.figure(1)
    for ii in range(0, bhatOLS.shape[0]):
        print("{0:4s}|{1:10.3f}|{2:10.3f}|{3:10.3f}|{4:10.3f}|{5:15.3f}|{6:10.3f}|".format(
            "B{0}".format(ii+1), obj.bbeta[ii][0], bhatOLS[ii][0],
            np.mean(bhatGibbs[ii,0,:]), np.percentile(a=bhatGibbs[ii,0,:], q=97.5),np.median(bhatGibbs[ii,0,:]), np.percentile(a=bhatGibbs[ii,0,:], q=2.5)
            ))
        ## -- Figure -- ##
        ax = fig.add_subplot(bhatOLS.shape[0], 1, ii+1)
        plt.plot(bhatGibbs[ii,0,:], c='b')
        plt.plot(np.ones(shape=(bhatGibbs[ii,0,:].shape[0],1))*obj.bbeta[ii], c='r')
    print("-"*(4+10*5+6))

    plt.figure(2)
    plt.plot(ssigmaYGibbs[0,0,:], c='b')
    plt.plot(np.ones(shape=(ssigmaYGibbs[0,0,:].shape[0],1))*obj.ssigmaY, c='r')
    plt.show()
