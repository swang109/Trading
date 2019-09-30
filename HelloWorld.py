import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#setting figure size
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,20

#for normalizing data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

df = pd.read_csv('NSE-TATAGLOBAL11.csv')
#print the head
print(df.head(5))

#setting index as date
df['Date'] = pd.to_datetime(df.Date,format='%Y-%m-%d')

df.index = df['Date']

#plot
plt.figure(figsize=(16,8))
plt.plot(df['Close'], label='Close Price history')
# plt.plot(df['High'], label='High Price history')
plt.show()