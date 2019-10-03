import polygon
import json
import numpy as np
import pytz
import time
import datetime
import pandas as pd
import os
from polygon.polygonQuery import queryHistoricQuotes


def historicQuotesToDF(symbol, date):
    fileName = polygon.constants.fileNameTemplate.format(symbol, date)
    if not os.path.isfile(fileName):
        queryHistoricQuotes(symbol, date)
    HISTORIC_DATA_PATH = "historicData/"
    parsed_json = json.loads(open(HISTORIC_DATA_PATH + 'TSLA-{}.json'.format(date)).read())

    marketOpenDateTime = datetime.datetime.strptime('{} 09:30:00'.format(date), '%Y-%m-%d %H:%M:%S')
    marketCloseDateTime = datetime.datetime.strptime('{} 16:00:00'.format(date), '%Y-%m-%d %H:%M:%S')

    ticks = parsed_json["ticks"]

    ticksArray = np.array(ticks)
    consolidatedData = []

    currentSecond = divmod(ticksArray[0].get("t"), 1000)[0]
    currentSecondAskSize = ticksArray[0].get("aS") or 0
    currentSecondBidSize = ticksArray[0].get("bS") or 0
    currentSecondBidPrice = ticksArray[0].get("bP") or 0
    currentSecondAskPrice = ticksArray[0].get("aP") or 0
    dateTimeInEDT = None

    for i in range(1, len(ticksArray)):
        nextSecond, milliseconds = divmod(ticksArray[i].get("t"), 1000)
        if nextSecond == currentSecond:
            currentSecondAskSize += ticksArray[i].get("aS") or 0
            currentSecondBidSize += ticksArray[i].get("bS") or 0
            currentSecondBidPrice = ticksArray[i].get("bP")
            currentSecondAskPrice = ticksArray[i].get("aP")
            continue
        else:
            # dateTimeInGMTString = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(second)), milliseconds)
            dateTimeInGMTString = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(currentSecond))
            gmtTimezone = pytz.timezone("GMT")
            edtTimezone = pytz.timezone("US/Eastern")
            dateTimeInGMT = datetime.datetime.strptime(dateTimeInGMTString, '%Y-%m-%d %H:%M:%S')
            dateTimeInEDT = gmtTimezone.localize(dateTimeInGMT).astimezone(edtTimezone)
            # remove timezone info
            dateTimeInEDT = dateTimeInEDT.replace(tzinfo=None)

            if marketOpenDateTime < dateTimeInEDT < marketCloseDateTime:
                consolidatedData.append(
                    {'Time': dateTimeInEDT, 'AskPrice': currentSecondAskPrice, 'BidPrice': currentSecondBidPrice,
                     'AskSize': currentSecondAskSize, 'BidSize': currentSecondBidSize})

            currentSecondAskSize = ticksArray[i].get("aS")
            currentSecondBidSize = ticksArray[i].get("bS")
            currentSecondBidPrice = ticksArray[i].get("bP")
            currentSecondAskPrice = ticksArray[i].get("aP")
            currentSecond = nextSecond

    if dateTimeInEDT < marketCloseDateTime:
        # consolidate the last second but only if it is before market close
        consolidatedData.append(
            {'Time': dateTimeInEDT, 'AskPrice': currentSecondAskPrice, 'BidPrice': currentSecondBidPrice,
             'AskSize': currentSecondAskSize, 'BidSize': currentSecondBidSize})
    resultDF = pd.DataFrame(consolidatedData).set_index('Time')
    #bidSize - askSize, if positive, more people trying to buy
    bidAskInBalance = resultDF['BidSize'] - resultDF['AskSize']
    resultDF['bidAskInBalance'] = bidAskInBalance
    return resultDF
