import numpy as np

def testcurve(x, frequency=10, peak_width=2, amplitude=20, bias=0):
    # 0 = pk - width
    # 2pi = pk + width
    # want peak at n*time == frequency
    nearest_peak = np.round(x / frequency, 0)
    # if not peak at 0 and within peak_width
    if nearest_peak > 0 and np.abs((x - nearest_peak * frequency)) < peak_width:
        # return sin that does one period within 2*peak_width
        return amplitude * np.sin(2*np.pi * (x - nearest_peak * frequency - peak_width) / (2*peak_width)) + bias
    else:
        return bias

def get_testcurve(frequency=10, peak_width=2, amplitude=20, bias=0):
    return np.vectorize(lambda x: testcurve(x, frequency=frequency, peak_width=peak_width, amplitude=amplitude, bias=bias))

