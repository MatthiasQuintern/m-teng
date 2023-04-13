import numpy as np
import matplotlib.pyplot as plt

def testcurve(x, frequency=10, peak_width=2, amplitude=20, bias=0):
    # want peak at n*time == frequency
    nearest_peak = np.round(x / frequency, 0)
    # if not peak at 0 and within peak_width
    # print(x, nearest_peak)
    if nearest_peak > 0 and abs((x - nearest_peak * frequency)) < peak_width:
        # return sin that does one period within 2*peak_width
        return amplitude * np.sin(2*np.pi * (x - nearest_peak * frequency - peak_width) / (2*peak_width)) + bias
    else:
        return bias

    # 0 = pk - width
    # 2pi = pk + width

def baseline(data):
    # find the value where the most values with low gradients are closest to
    gradients = np.abs(np.gradient(data))
    # consider the values where the absolute gradient is in the bottom 20%
    n_gradients = len(data) // 20
    consider_indices = np.argsort(gradients)[:n_gradients]
    # of those, only consider values where the value 
    consider_values = data[consider_indices]


xdata = np.arange(0, 100, 0.01)
ydata = np.vectorize(testcurve)(xdata)


plt.plot(xdata, ydata)
plt.show()
