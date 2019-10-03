from polygon import polygonJsonProcessor
import pylab
from tradingLib import peakdetection
import numpy as np

resultDF = polygonJsonProcessor.historicQuotesToDF("TSLA","2019-09-26")

# Settings: lag = 10 minutes, threshold = 5, influence = 0
lag = 5
threshold = 5
influence = 0.8

inputArray = resultDF['AskPrice']
peakDetectionResult = peakdetection.thresholding_algo(resultDF['AskPrice'],lag=lag, threshold=threshold, influence=influence)

pylab.figure(figsize=(16, 8))

pylab.subplot(311)
pylab.plot(resultDF['AskPrice'], label='Ask Price history', color="green")

pylab.subplot(313)
pylab.plot(np.arange(1, len(inputArray) + 1),
           peakDetectionResult["avgFilter"], color="cyan", lw=2)

#超过这条线就是peak
pylab.plot(np.arange(1, len(inputArray) + 1),
           peakDetectionResult["avgFilter"] + threshold * peakDetectionResult["stdFilter"], color="green", lw=2)

#低于这条线也是peak
pylab.plot(np.arange(1, len(inputArray) + 1),
           peakDetectionResult["avgFilter"] - threshold * peakDetectionResult["stdFilter"], color="red", lw=2)

# pylab.plot(resultDF['bidAskInBalance'], label='bid Ask In Balance', color = "blue")

pylab.subplot(312)
pylab.step(np.arange(1, len(inputArray) + 1), peakDetectionResult["signals"], color="red", lw=2)
pylab.ylim(-1.5, 1.5)
pylab.show()
