#!/usr/bin/env python
# Implementation of algorithm from https://stackoverflow.com/a/22640362/6029703
import numpy as np
import pylab


# lag = the lag of the moving window,
# threshold = the z-score at which the algorithm signals
# influence = the influence (between 0 and 1) of new signals on the mean and standard deviation.

def thresholding_algo(input, lag, threshold, influence):
    #return a new array of zero in float64
    signals = np.zeros(len(input))

    filteredY = np.array(input)

    #平均值
    avgFilter = [0]*len(input)

    #标准差
    stdFilter = [0]*len(input)

    #计算第一个平均值 input 0 to lag的平均值
    avgFilter[lag - 1] = np.mean(input[0:lag])

    #计算第一个标准差
    stdFilter[lag - 1] = np.std(input[0:lag])

    for i in range(lag, len(input)):
        if abs(input[i] - avgFilter[i - 1]) > threshold * stdFilter [i - 1]:
            if input[i] > avgFilter[i - 1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * input[i] + (1 - influence) * filteredY[i - 1]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = input[i]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))
#
# inputArray = np.array([1, 1, 1.1, 1, 0.9, 1, 1, 1.1, 1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1, 1.1, 1, 1, 1, 1, 1.1, 0.9, 1, 1.1, 1, 1, 0.9,
#                        1, 1.1, 1, 1, 1.1, 1, 0.8, 0.9, 1, 1.2, 0.9, 1, 1, 1.1, 1.2, 1, 1.5, 1, 3, 2, 5, 3, 2, 1, 1, 1, 0.9, 1, 1, 3,
#                        2.6, 4, 3, 3.2, 2, 1, 1, 0.8, 4, 4, 2, 2.5, 1, 1, 1])
#
# inputArray = np.array([198,200,201,198,200,198,200,198,201,200,200,200,200,200,200,198,200,201,198,200,198,200,198,201,200,200,200,198,200,201,198,200,198,200,198,201,200,200,200,198,200,201,198,200,198,200,198,201,198,200,201,198,200,198,200,198,201,200,200,200,200,200
#                        ,200,200,200,200,200,200,201,200,200,200,200,200,200,200,200,200,200,500,200,200,200,200,200,200,200,200,200,200,200,200,200])
#
# # Settings: lag = 30, threshold = 5, influence = 0
# lag = 30
# threshold = 5
# influence = 0
#
# result = thresholding_algo(inputArray, lag=lag, threshold=threshold, influence=influence)
#
# pylab.subplot(211)
# pylab.plot(np.arange(1, len(inputArray) + 1), inputArray)
#
# pylab.plot(np.arange(1, len(inputArray) + 1),
#            result["avgFilter"], color="cyan", lw=2)
#
# #超过这条线就是peak
# pylab.plot(np.arange(1, len(inputArray) + 1),
#            result["avgFilter"] + threshold * result["stdFilter"], color="green", lw=2)
#
# #低于这条线也是peak
# pylab.plot(np.arange(1, len(inputArray) + 1),
#            result["avgFilter"] - threshold * result["stdFilter"], color="red", lw=2)
#
# pylab.subplot(212)
# pylab.step(np.arange(1, len(inputArray) + 1), result["signals"], color="red", lw=2)
# pylab.ylim(-1.5, 1.5)
# pylab.show()