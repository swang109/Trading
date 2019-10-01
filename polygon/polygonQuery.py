import requests
import json
import numpy as np

APIKEY = "AK9NOBR0WZO8EVJ5BWVQ"

#find the last tick quote from historic query
def lastTickFromHistoricQuery(ticks):
    ticksArray = np.array(ticks)
    if ticks and ticksArray.size > 0:
        return ticksArray[len(ticksArray) - 1]
    else:
        return False

#queryHistoricQuotes("TSLA", "2019-09-26")
#each request can only get part of the result so need to call the endpoint multiple times to get the full result of that day
def queryHistoricQuotes(symbol, date):
    #https://polygon.io/docs/#!/Stocks--Equities/get_v1_historic_quotes_symbol_date
    initialQuotesQueryTemplate = "https://api.polygon.io/v1/historic/quotes/{}/{}?apiKey={}"
    followQuotesQueryTemplate = "https://api.polygon.io/v1/historic/quotes/{}/{}?offset={}&limit=5000&apiKey={}"
    resultJson = {}

    quotesQuery = initialQuotesQueryTemplate.format(symbol, date, APIKEY)
    queryResult = requests.get(quotesQuery)
    parsedJson = json.loads(queryResult.content)

    resultJson["day"] = parsedJson["day"]
    resultJson["map"] = parsedJson["map"]
    resultJson["symbol"] = parsedJson["symbol"]

    currentTicks = parsedJson["ticks"]
    lastTick = lastTickFromHistoricQuery(currentTicks)

    allticks = []
    allticks.extend(currentTicks)

    #keep query until get the data of the full day
    while lastTick:
        quotesQuery = followQuotesQueryTemplate.format(symbol, date, lastTick["t"], APIKEY)
        queryResult = requests.get(quotesQuery)
        parsedJson = json.loads(queryResult.content)
        currentTicks = parsedJson["ticks"]
        lastTick = lastTickFromHistoricQuery(currentTicks)
        if currentTicks:
            allticks.extend(currentTicks)

    fileNameTemplate = "../historicData/{}-{}.json"
    fileName = fileNameTemplate.format(symbol, date)

    resultJson['ticks'] = allticks
    with open(fileName, 'w') as file:
        json.dump(resultJson, file)
    file.close()

    return resultJson