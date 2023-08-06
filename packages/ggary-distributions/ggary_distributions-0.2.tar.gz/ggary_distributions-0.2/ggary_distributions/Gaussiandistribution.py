import math
import matplotlib.pyplot as plt
from .MainDistribution import Distribution

class Gaussian(Distribution):
    def __init__(self, mu = 0, sigma = 1):
        Distribution.__init__(self, mu, sigma)
    
    def calculate_mean(self):
        self.mean = 1.0*sum(self.data)/len(self.data)
        return self.mean

    def calculate_stdev(self, sample = True):
        if sample:
            n = len(self.data) -1
        else:
            n = len(self.data)
        sigma = 0
        mean = self.mean
        for d in self.data:
            sigma += (d-mean)**2
        sigma = math.sqrt(sigma/n)
        self.stdev = sigma            
        return self.stdev

