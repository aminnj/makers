import numpy as np
import talib as ta

def rsi(prices, period=14):
    out = ta.RSI(prices, timeperiod=period)
    return out[np.isfinite(out)] # remove nans at beginning when we can't get the MA

def sma(prices, period):
    out = ta.SMA(prices, timeperiod=period)
    return out[np.isfinite(out)]

def ema(prices, period, ema_type=1):
    out = ta.EMA(prices, timeperiod=period)
    return out[np.isfinite(out)]

def bb(prices, period, num_std_dev=2.0):
    upper, middle, lower = ta.BBANDS(prices, period, num_std_dev, num_std_dev)
    # upper, middle, lower bands, bandwidth, range and %B
    bbands = np.c_[ upper, middle, lower, (upper-lower)/middle, upper-lower, (prices-lower)/(upper-lower) ]
    return bbands[np.isfinite(bbands[:,0])]

def kst(prices, roc1=10, roc2=15, roc3=20, roc4=30, sma1=10, sma2=10, sma3=10, sma4=15, smasig=9):
    rcma1 = ta.SMA(ta.ROC(prices,timeperiod=roc1), timeperiod=sma1)
    rcma2 = ta.SMA(ta.ROC(prices,timeperiod=roc2), timeperiod=sma2)
    rcma3 = ta.SMA(ta.ROC(prices,timeperiod=roc3), timeperiod=sma3)
    rcma4 = ta.SMA(ta.ROC(prices,timeperiod=roc4), timeperiod=sma4)
    kst = 1.0*rcma1 + 2.0*rcma2 + 3.0*rcma3 + 4.0*rcma4
    return ta.SMA(kst, timeperiod=smasig)

def hma(prices, period=20):
    # https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average
    step1 = 2.0*ta.WMA(prices, timeperiod=period/2)
    step2 = step1 - ta.WMA(prices, timeperiod=period)
    step3 = ta.WMA(step2, timeperiod=np.sqrt(10))
    return step3



def bbtimes(timeprices, period, num_std_dev=2.0):
    times = timeprices[:,0]
    prices = timeprices[:,1]

    bbands = bb(prices, period, num_std_dev)
    times = times[-len(bbands):] # make sure times and bb output have same length from the end
    return np.c_[ times, bbands ] # add the time back in as a column

def ematimes(timeprices, period, ema_type=0):
    times = timeprices[:,0]
    prices = timeprices[:,1]
    emaprices = ema(prices, period, ema_type) # feed the function only the prices
    times = times[-len(emaprices):] # make sure times and ema output have same length from the end
    return np.c_[ times, emaprices ] # add the time back in as a column

def macdhisttimes(timeprices, period_fast, period_slow, period_signal, ema_type=0):
    times = timeprices[:,0]
    prices = timeprices[:,1]
    emaprices_fast = ema(prices, period_fast, ema_type) # feed the function only the prices
    emaprices_slow = ema(prices, period_slow, ema_type) # feed the function only the prices
    ema_diff = [x - y for x, y in zip(emaprices_fast, emaprices_slow)]# MACD line
    ema_diff = np.array(ema_diff)
    ema_signal = ema(ema_diff, period_signal, ema_type) # Signal line
    hist = [x - y for x, y in zip(ema_diff, ema_signal)]# Histogram of MACD - Signal
    times = times[-len(hist):] # make sure times and hist have same length from the end
    return np.c_[ times, hist ] # add the time back in as a column

def rsitimes(timeprices, period=14):
    # give a ndarray of time,price
    # get the rsi at each time slice
    times = timeprices[:,0]
    prices = timeprices[:,1]
    rsis = rsi(prices, period)
    times = times[-len(rsis):]
    return np.c_[ times, rsis ]

def crossovertimes(matimes):
    # takes a list of moving averages and returns a list where
    # each element is a (day,code) pair. code=1 if trendlines crossed upwards
    # code=0 if trendlines crossed downwards

    # shortest first
    mas = sorted(matimes, key=lambda e: len(e))
    mintimesteps = len(mas[0])
    macrossover = [[] for i in range(mintimesteps)]
    for ima,ma in enumerate(mas):
        ma = ma[-mintimesteps:]
        for it in range(mintimesteps): macrossover[it].append( ma[it] )

    # each element of emacrossover represents one day, meaning it is an array of (time,price) pairs for each MA
    # find out if the prices are increasing or decreasing between the MAs for each day
    macrossover = np.array(macrossover)

    crossover = [] # each element will be a pair (day, code) where code=1 for increasing, -1 for decreasing, or 0 otherwise
    for dayinfo in macrossover:
        prices = dayinfo[:,1]
        day = dayinfo[0][0]
        isIncreasing = all(x<y for x,y in zip(prices, prices[1:]))
        isDecreasing = all(x>y for x,y in zip(prices, prices[1:]))

        if(isIncreasing): crossover.append([day, 1])
        elif(isDecreasing): crossover.append([day, -1])
        else: crossover.append([day, 0])

    prevcode = -999
    crossovertimes = [] # each element will be a pair (day, code) where code=1 if trendlines crossed upwards, or 0 if trendlines crossed downwards
    wasRising = False
    for day, code in crossover:
        day = int(day)
        if   prevcode == 0 and code == 1 and not wasRising: # none to rising
            crossovertimes.append([day,1])
            wasRising = True
        elif prevcode == -1 and code == 1: # falling to rising
            crossovertimes.append([day,1])
            wasRising = True
        elif prevcode == 0 and code == -1 and wasRising:  # none to falling
            crossovertimes.append([day,0])
            wasRising = False
        elif prevcode == 1 and code == -1: # rising to falling
            crossovertimes.append([day,0])
            wasRising = False
        else: pass

        prevcode = code
    return crossovertimes

