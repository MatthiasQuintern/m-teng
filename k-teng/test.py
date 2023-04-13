readings = [
  4.974127e-10, -1.418591e-12, -1.573563e-12, -1.728535e-12, -1.704693e-12,
 -1.847744e-12, -1.931190e-12, -1.788139e-12, -1.871586e-12, -2.169609e-12,
 -2.074242e-12, -1.895428e-12, -1.895428e-12, -1.776218e-12, -1.990795e-12,
 -1.788139e-12, -1.811981e-12, -1.657009e-12, -1.573563e-12, -2.396107e-12,
 -2.515316e-12, -2.765656e-12, -2.825260e-12, -3.147125e-12, -2.300739e-12,
 -2.825260e-12, -3.278255e-12, -5.257130e-12, -6.818771e-12, -8.916855e-12,
 -7.712841e-12,  6.437302e-12, -1.142025e-11, -1.206398e-11, -4.649043e-10,
 -3.427613e-09, -2.460408e-09, -2.340376e-09, -1.306653e-10,  1.496077e-11,
  2.933741e-11,  1.953280e-09,  8.579970e-10,  9.226799e-12, -1.095533e-11,
 -2.508163e-11, -2.776039e-09, -8.686423e-09,  4.935264e-12,  1.246929e-11,
  3.225744e-09,  2.814472e-09,  1.877034e-09,  2.229273e-09,  1.713574e-09,
  8.355618e-10, -4.332781e-10,  5.896091e-11,  5.762577e-11,  8.129537e-09,
  4.044378e-09,  1.771629e-09,  7.849216e-10,  4.098892e-10,  3.390551e-10,
  2.956390e-10,  3.033876e-10,  1.716256e-10,  1.463890e-11, -5.078316e-12,
 -6.949902e-12, -8.106232e-12, -6.473065e-12, -4.506111e-12,  4.919767e-11,
  3.052297e-08,  1.161162e-08, -9.892106e-09, -3.613818e-09, -5.004287e-09,
 -2.015829e-11, -4.183054e-11, -1.810908e-10, -2.042532e-10, -3.516316e-10,
  5.099773e-11,  1.921976e-08, -1.256589e-08, -4.242897e-10, -1.358986e-12,
 -3.445148e-12, -3.838539e-12, -4.184246e-12, -7.402897e-12, -2.840877e-10,
 -2.872229e-10, -2.730966e-10, -1.134396e-10, -4.376173e-11, -3.576279e-14
]
timestamps = [
 0.      , 0.05    , 0.1     , 0.15,     0.2,      0.25,     0.3,      0.35,
 0.4     , 0.45    , 0.5     , 0.55,     0.6,      0.65,     0.7,      0.75,
 0.8     , 0.85    , 0.9     , 0.95,     1. ,      1.05,     1.1,      1.15,
 1.2     , 1.25    , 1.3     , 1.35,     1.4,      1.45,     1.5,      1.55,
 1.6     , 1.690891, 1.710923, 1.75,     1.8,      1.85,     1.9,      1.95,
 2.      , 2.05    , 2.1     , 2.15,     2.2,      2.25,     2.3,      2.35,
 2.420332, 2.45    , 2.5     , 2.55,     2.6,      2.65,     2.7,      2.75,
 2.820553, 2.890843, 2.910875, 2.95,     3. ,      3.05,     3.1,      3.15,
 3.2     , 3.25    , 3.3     , 3.35,     3.4,      3.45,     3.5,      3.55,
 3.6     , 3.65    , 3.7     , 3.75,     3.8,      3.85,     3.9,      3.95,
 4.      , 4.05    , 4.1     , 4.15,     4.2,      4.25,     4.3,      4.35,
 4.4     , 4.45    , 4.5     , 4.55,     4.6,      4.65,     4.7,      4.75,
 4.8     , 4.85    , 4.9     , 4.95,    ]

import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
df = pd.DataFrame(np.vstack((timestamps, readings)).T)
df.columns = ["Time [s]", "Voltage [V]"]
print(df)
df.to_csv("test.csv", sep=",", header=True, index=False)

df.plot(x='Time [s]', y="Voltage [V]")
plt.show()

