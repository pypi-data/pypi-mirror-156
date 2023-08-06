import numpy as np
import pandas as pd
import os
rdata_ = os.path.join(os.path.dirname(__file__), 'rdata_', 'exam.csv')
def hkw() :
	ppd = pd.read_csv(rdata_)
	lat= np.loadtxt(rdata_, delimiter = ',', skiprows = 1, dtype = 'str')
#	print(lat)
#	print(ppd)
	return ppd
