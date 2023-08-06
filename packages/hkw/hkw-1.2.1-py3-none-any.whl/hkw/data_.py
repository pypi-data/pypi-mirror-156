import numpy as np
import pandas as pd
def hkw() :
	ppd = pd.read_csv('./rdata_/exam.csv')
	lat= np.loadtxt('./rdata_/exam.csv', delimiter = ',', skiprows = 1, dtype = 'str')
	print(lat)
	print(ppd)
