
# ---------------------------------------------------------
#    ____          __      ___     
#   |  _ \         \ \    / (_)    
#   | |_) | __ _ _ _\ \  / / _ ____
#   |  _ < / _` | '__\ \/ / | |_  /
#   | |_) | (_| | |   \  /  | |/ / 
#   |____/ \__,_|_|    \/   |_/___|  SimplexBuilder class
# ---------------------------------------------------------                            
# SIMaP / Jean-Luc Parouty 2022                  

import numpy as np
import math, random
from math import sqrt, cos, sin, acos

from barviz.version        import __version__


class SimplexBuilder:

    version = __version__

    def __init__(self, m=10, q=10, ks=10, s0=2, kd=4):
        self.m    = m        # mass
        self.q    = q        # charge        
        self.ks   = ks       # spring coefficient
        self.s0   = s0       # spring elongation at rest
        self.kd   = kd       # damping factor
        self.ee   = 0.001    # epsilon to avoid /0


    def add_points(self, nbp=10, mode='fibonacci'):
        self.__set_random_uniform_points(nbp)
        if mode=='fibonacci': self.__set_fibonacci_points(nbp)
        if mode=='spherical': self.__set_random_spherical_points(nbp)


    @property
    def nbp(self):
        return len(self.points)


    def get_simplex(self):
        # Import here, to avoid circular reference..
        from barviz.Simplex import Simplex
        nbp=self.nbp
        return Simplex( name     = f'{nbp-1}-simplex', 
                        points   = self.points,
                        labels   = None,
                        colors   = None ) 


    def iterate(self, max_dp=0.01, max_i=5000, dt=0.01, epsilon=0.001):
        done      = False
        iteration = 0
        p         = self.points           # points
        nbp       = self.nbp              # nb points
        dp        = np.zeros( (nbp,3) )   # speeds

        trace_dp  = []

        while done is False:

            # ---- Force : Spring to origin / F = -ks * ( d - s0 )

            fs = np.zeros((nbp,3))
            for i in range(nbp):
                pi=p[i]
                di = np.sqrt(pi.dot(pi))
                fs[i] = -self.ks * ( di - self.s0 ) * pi

            # ---- Force : Electric repulsion / Fij = q * ij / d*d*d
            #
            fq = np.zeros((nbp,3))
            for i in range(nbp):
                for j in range(nbp):
                    if i==j : next
                    ij     = p[j] - p[i]
                    d      = np.sqrt(ij.dot(ij))            
                    fq[i] += -self.q * ij / ( d*d*d + epsilon )
                    
            # ---- Force : Damping / F = -kd * dp
            #
            fd = -self.kd * dp

            # ---- Fine, now, we can update our points / F=m.a => a=F/m => dp += (F/m).dt
            #
            dp += ( fs + fq + fd) * dt / self.m

            p += dp * dt

            # ---- Sum of the speeds 
            sum_dp=0
            for dpi in dp:
                sum_dp+= np.sqrt(dpi.dot(dpi) )
            trace_dp.append(sum_dp)

            # ---- Stop condition
            #
            iteration += 1
            if iteration>max_i or sum_dp<max_dp: done=True

        self.trace_dp = trace_dp
        return sum_dp, iteration


    def __set_fibonacci_points(self, nbp=10):
        points = []
        phi = math.pi * (3. - sqrt(5.))
        for i in range(nbp):
            y = 1 - (i / float(nbp - 1)) * 2
            radius = sqrt(1 - y * y)
            theta = phi * i
            x = cos(theta) * radius
            z = sin(theta) * radius
            points.append((x, y, z))
        self.points = np.array(points)

    def __set_random_uniform_points(self, nbp=10):
        self.points = np.random.uniform(low=-1, high=1, size=(nbp,3))


    def __set_random_spherical_points(self, nbp=10):
        points=[]
        for i in range(nbp):
            theta = 2 * math.pi * random.random()
            phi = acos(random.uniform(-1, 1))
            x = cos(theta) * sin(phi)
            y = sin(theta) * sin(phi)
            z = cos(phi)
            points.append((x, y, z))
        self.points = np.array(points)
