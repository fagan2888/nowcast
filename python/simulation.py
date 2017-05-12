import os
import sys
import numpy as np

from dynFAMissing import dynFAMissing


class simulateModel(object):
    def __init__(self):
        pass

    def simulate(self, Ny=20, Nx=1, rhoy=1, rhox=1, Ty=100):
        ## Model
        ## Y(t) = mu + Lmbda*f(t) + u(t), u(t) = rho_{u,1} u(t-1) +...+ rho_{u, rhoy}u(t-rhoy) + eps(t), eps(t)~N(0, sigma_eps**2)
        ## f(t) = theta_{1}f(t-1) + ... + theta__{rhox}f(t-rhox) + eta(t), eta(t)~N(0, sigma_eta**2)
        self.sigmaEps = np.random.gamma(scale=1/2, shape=1/(1/2), size=(Ny, Ny))
        self.sigmaEta = np.random.gamma(scale=10/2, shape=1/(10/2), size=(Nx, Nx))
        self.Lmbda = np.random.normal(scale=1, size=(Ny, Nx))
        count = 0
        while True:
            count += 1
            if count > 1000:
                print("No convergence")
                break
            ttheta = np.random.normal(size=(Nx, Nx*rhox))
            

        eeps = np.random.normal(size=(Ny, Ty))
        eeta = np.random.normal(size=(Nx, Ty))

if __name__ == "__main__":
    print("Main file")
    model = simulateModel()
    model.simulate()
