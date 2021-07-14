import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler
standardscaler = StandardScaler()

scale_data = np.array([0, 150, 130, 120 ,110])
scale_data.reshape(-1, 1)
print(standardscaler.fit_transform(scale_data.reshape(-1, 1)))


scale_data
minmaxscaler = MinMaxScaler()
minmaxscaler.fit_transform(scale_data.reshape(-1, 1))
