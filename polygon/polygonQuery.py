import requests
import polygon.polygonJsonProcessor

APIKEY = "AK9NOBR0WZO8EVJ5BWVQ"

#queryHistoricQuotes("TSLA", "2019-09-26")
def queryHistoricQuotes(symbol, date):
    #https://polygon.io/docs/#!/Stocks--Equities/get_v1_historic_quotes_symbol_date
    initialQuotesQueryTemplate = "https://api.polygon.io/v1/historic/quotes/{}/{}?apiKey={}"
    followQuotesQueryTemplate = "https://api.polygon.io/v1/historic/quotes/{}/{}?offset={}&limit=5000&apiKey={}"
    quotesQuery = initialQuotesQueryTemplate.format(symbol, date, APIKEY)
    queryResult = requests.get(quotesQuery)

    lastTick = polygon.polygonJsonProcessor.lastTickFromHistoricQuery(queryResult.content)

    fileNameTemplate = "{}-{}.json"
    fileName = fileNameTemplate.format(symbol,date)

    #"x" create file
    file = open(fileName, "wb")

    while lastTick:
        quotesQuery = followQuotesQueryTemplate.format(symbol, date, lastTick["t"], APIKEY)
        queryResult = requests.get(quotesQuery)

        file.write(queryResult.content)
        lastTick = polygon.polygonJsonProcessor.lastTickFromHistoricQuery(queryResult.content)

    file.close()