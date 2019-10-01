import pandas as pd
import matplotlib.pyplot as plt
import json
from tradingLib import peakdetection

#setting figure size
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,20

#for normalizing data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))


HISTORIC_DATA_PATH = "historicData/"
parsed_json = json.loads(open(HISTORIC_DATA_PATH+'TSLA-2019-09-26.json').read())

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

peakdetection.thresholding_algo()