import math
import matplotlib.pyplot as plt
from .MainDistribution import Distribution

class Binomial(Distribution):
    def __init__(self, prob= 0.5, size = 100):
        self.p = prob
        self.n = size
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())
    
    def calculate_mean(self):
        self.mean = self.p * self.n
        return self.mean

    def calculate_stdev(self):
        self.stdev = math.sqrt(self.n*self.p*(1-self.p))
        return self.stdev

    def replace_stats_with_data(self):
        self.n = len(self.data)
        self.p = sum(self.data)/len(self.data) *1.0
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()
        return self.n, self.p
