import numpy as np

def add(y1, y2):
    "Return y1 + y2. "
    return np.add(y1, y2)

def multiply(y1, y2):
    "Return y1 * y2. "
    return np.multiply(y1, y2)

def subtract(y1, y2):
    "Return y1 - y2. "
    return np.subtract(y1, y2)

def divide(y1, y2):
    "Return y1 / y2. "
    return np.divide(y1, y2)

def convolve(y1, y2):
    "Return convolution of y1 and y2"
    return np.convolve(y1, y2, "same")