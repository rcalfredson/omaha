"""General-use mathematical functions.
"""
import numpy as np

def exp_moving_average(values, period):
    """
    Returns calculated exponential moving average for an array of numbers.

    Source: https://codereview.stackexchange.com/a/166640
    Arguments:
      - values: array of type float
      - period: integer specifying window of moving average
    """
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    convolved_array = np.convolve(values, weights, mode='full')[:len(values)]
    convolved_array[:period] = convolved_array[period]
    return convolved_array
