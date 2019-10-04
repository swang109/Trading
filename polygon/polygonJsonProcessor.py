import polygon
import json
import numpy as np
import pytz
import time
import datetime
import pandas as pd
import os
from polygon.polygonQuery import queryHistoricQuotes


def historicQuotesToDFConsolidatedIntoSecond(symbol, date, begin=None, end=None):
    fileName = polygon.constants.fileNameTemplate.format(symbol, date)
    if not os.path.isfile(fileName):
        queryHistoricQuotes(symbol, date)
    HISTORIC_DATA_PATH = "historicData/"
    parsed_json = json.loads(open(HISTORIC_DATA_PATH + 'TSLA-{}.json'.format(date)).read())

    if not begin or not end:
        begin = "09:30:00"
        end = "16:00:00"
    marketOpenDateTime = datetime.datetime.strptime('{} {}'.format(date, begin), '%Y-%m-%d %H:%M:%S')
    marketCloseDateTime = datetime.datetime.strptime('{} {}'.format(date, end), '%Y-%m-%d %H:%M:%S')

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
    # bidSize - askSize, if positive, more people trying to buy
    bidAskInBalance = resultDF['BidSize'] - resultDF['AskSize']
    resultDF['bidAskInBalance'] = bidAskInBalance
    return resultDF

def historicQuotesToDFConsolidatedMilliSecond(symbol, date, begin=None, end=None):
    fileName = polygon.constants.fileNameTemplate.format(symbol, date)
    if not os.path.isfile(fileName):
        queryHistoricQuotes(symbol, date)
    HISTORIC_DATA_PATH = "historicData/"
    parsed_json = json.loads(open(HISTORIC_DATA_PATH + 'TSLA-{}.json'.format(date)).read())
    if not begin or not end:
        begin = "09:30:00"
        end = "16:00:00"
    marketOpenDateTime = datetime.datetime.strptime('{} {}'.format(date, begin), '%Y-%m-%d %H:%M:%S')
    marketCloseDateTime = datetime.datetime.strptime('{} {}'.format(date, end), '%Y-%m-%d %H:%M:%S')

    ticks = parsed_json["ticks"]

    ticksArray = np.array(ticks)
    consolidatedData = []

    currentMilliSecond = divmod(ticksArray[0].get("t"), 1000)[1]
    currentMilliSecondAskSize = ticksArray[0].get("aS") or 0
    currentMilliSecondBidSize = ticksArray[0].get("bS") or 0
    currentMilliSecondBidPrice = ticksArray[0].get("bP") or 0
    currentMilliSecondAskPrice = ticksArray[0].get("aP") or 0
    dateTimeInEDT = None

    for i in range(0, len(ticksArray)):
        second, nextMilliSecond = divmod(ticksArray[i].get("t"), 1000)
        if nextMilliSecond == currentMilliSecond:
            currentMilliSecondAskSize += ticksArray[i].get("aS") or 0
            currentMilliSecondBidSize += ticksArray[i].get("bS") or 0
            currentMilliSecondBidPrice = ticksArray[i].get("bP")
            currentMilliSecondAskPrice = ticksArray[i].get("aP")
            continue
        else:
            dateTimeInGMTString = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(second)), nextMilliSecond)
            gmtTimezone = pytz.timezone("GMT")
            edtTimezone = pytz.timezone("US/Eastern")
            dateTimeInGMT = datetime.datetime.strptime(dateTimeInGMTString, '%Y-%m-%d %H:%M:%S.%f')
            dateTimeInEDT = gmtTimezone.localize(dateTimeInGMT).astimezone(edtTimezone)
            # remove timezone info
            dateTimeInEDT = dateTimeInEDT.replace(tzinfo=None)

            if marketOpenDateTime < dateTimeInEDT < marketCloseDateTime:
                consolidatedData.append(
                    {'Time': dateTimeInEDT, 'AskPrice': currentMilliSecondAskPrice,
                     'BidPrice': currentMilliSecondBidPrice,
                     'AskSize': currentMilliSecondAskSize, 'BidSize': currentMilliSecondBidSize})

            currentMilliSecondAskSize = ticksArray[i].get("aS")
            currentMilliSecondBidSize = ticksArray[i].get("bS")
            currentMilliSecondBidPrice = ticksArray[i].get("bP")
            currentMilliSecondAskPrice = ticksArray[i].get("aP")
            currentMilliSecond = nextMilliSecond

    if dateTimeInEDT < marketCloseDateTime:
        # consolidate the last second but only if it is before market close
        consolidatedData.append(
            {'Time': dateTimeInEDT, 'AskPrice': currentMilliSecondAskPrice, 'BidPrice': currentMilliSecondBidPrice,
             'AskSize': currentMilliSecondAskSize, 'BidSize': currentMilliSecondBidSize})

    resultDF = pd.DataFrame(consolidatedData).set_index('Time')
    # bidSize - askSize, if positive, more people trying to buy
    bidAskInBalance = resultDF['BidSize'] - resultDF['AskSize']
    resultDF['bidAskInBalance'] = bidAskInBalance
    return resultDF


def historicQuotesToDF(symbol, date, begin=None, end=None):
    fileName = polygon.constants.fileNameTemplate.format(symbol, date)
    if not os.path.isfile(fileName):
        queryHistoricQuotes(symbol, date)
    HISTORIC_DATA_PATH = "historicData/"
    parsed_json = json.loads(open(HISTORIC_DATA_PATH + 'TSLA-{}.json'.format(date)).read())
    if not begin or not end:
        begin = "09:30:00"
        end = "16:00:00"
    marketOpenDateTime = datetime.datetime.strptime('{} {}'.format(date, begin), '%Y-%m-%d %H:%M:%S')
    marketCloseDateTime = datetime.datetime.strptime('{} {}'.format(date, end), '%Y-%m-%d %H:%M:%S')

    ticks = parsed_json["ticks"]

    ticksArray = np.array(ticks)
    data = []
    currentAskSize = None
    currentBidSize = None
    currentBidPrice = None
    currentAskPrice = None
    dateTimeInEDT = None

    for i in range(0, len(ticksArray)):
        currentAskSize = ticksArray[i].get("aS") or 0
        currentBidSize = ticksArray[i].get("bS") or 0
        currentBidPrice = ticksArray[i].get("bP") or 0
        currentAskPrice = ticksArray[i].get("aP") or 0
        second, milliseconds = divmod(ticksArray[i].get("t"), 1000)
        dateTimeInGMTString = '{}.{:03d}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(second)), milliseconds)
        gmtTimezone = pytz.timezone("GMT")
        edtTimezone = pytz.timezone("US/Eastern")
        dateTimeInGMT = datetime.datetime.strptime(dateTimeInGMTString, '%Y-%m-%d %H:%M:%S.%f')
        dateTimeInEDT = gmtTimezone.localize(dateTimeInGMT).astimezone(edtTimezone)
        # remove timezone info
        dateTimeInEDT = dateTimeInEDT.replace(tzinfo=None)

        if marketOpenDateTime < dateTimeInEDT < marketCloseDateTime:
            data.append(
                {'Time': dateTimeInEDT, 'AskPrice': currentAskPrice, 'BidPrice': currentBidPrice,
                 'AskSize': currentAskSize, 'BidSize': currentBidSize})

    if dateTimeInEDT < marketCloseDateTime:
        # consolidate the last second but only if it is before market close
        data.append(
            {'Time': dateTimeInEDT, 'AskPrice': currentAskPrice, 'BidPrice': currentBidPrice,
             'AskSize': currentAskSize, 'BidSize': currentBidSize})

    resultDF = pd.DataFrame(data)
    # bidSize - askSize, if positive, more people trying to buy
    bidAskInBalance = resultDF['BidSize'] - resultDF['AskSize']
    resultDF['bidAskInBalance'] = bidAskInBalance
    return resultDF
