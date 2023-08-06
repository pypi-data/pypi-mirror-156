import numpy as np
import pandas as pd
ppd = pd.read_csv('exam.csv')
lat= np.loadtxt('exam.csv', delimiter = ',', skiprows = 1, dtype = 'str')
print(lat)
print(ppd)
