import polygon
import json
import numpy as np
import pytz
import time
import datetime
import pylab
import pandas as pd

from polygon.polygonQuery import queryHistoricQuotes

#queryHistoricQuotes("TSLA", "2019-09-26")

HISTORIC_DATA_PATH = "historicData/"
parsed_json = json.loads(open(HISTORIC_DATA_PATH+'TSLA-2019-09-26.json').read())
ticks = parsed_json["ticks"]

ticksArray = np.array(ticks)
bidPriceArray = np.zeros(len(ticks))
askPriceArray = np.zeros(len(ticks))
dateTimeArray = []

new_data = pd.DataFrame(columns=['DateTime', 'askPrice'])

for i in range(0,len(ticksArray)):
    bidPriceArray[i] = ticksArray[i].get("bP")
    # get better handle none
    askPriceArray[i] = ticksArray[i].get("aP")

    second, milliseconds = divmod(ticksArray[i].get("t"), 1000)

    dateTimeInGMTString = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(second)), milliseconds)

    gmtTimezone = pytz.timezone("GMT")
    edtTimezone = pytz.timezone("US/Eastern")

    dateTimeInGMT = datetime.datetime.strptime(dateTimeInGMTString, '%Y-%m-%d %H:%M:%S.%f')

    dateTimeInEDT = gmtTimezone.localize(dateTimeInGMT).astimezone(edtTimezone)

    dateTimeArray.append(dateTimeInEDT)

lastTimeStamp = ticksArray[len(ticks)-1].get("t")

print(bidPriceArray)
print(askPriceArray)

pylab.plot(bidPriceArray)
pylab.plot(askPriceArray)
pylab.show()