import numpy as np

def line(x, m=1, b=0):
    return x*m+b
    
def parabola(x, a=1, b=0, c=0):
    return a*x**2 + b*x + c

def cubic(x, a=1, b=0, c=0, d=0):
    return a*x**3 + b*x**2 + c*x + d

def sinusoid(x, phase=0, amplitude=1, period=2*np.pi):
    return amplitude*np.sin(period*x+phase)

def uniform(x, shift=0, scale=1):
    return scale * np.random.rand(len(x)) + shift

def gaussian(x, mean, stdev):
    return np.random.normal(loc=mean, scale=stdev, size=x)

def poisson(x, lam):
    return np.random.poisson(lam=lam, size=x)