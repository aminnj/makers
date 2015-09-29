import os, sys, random

import numpy as np
import talib as ta

import getStocks as gs
import utils as u
import indicators as ind
import pprint


def noNaN(v, col=0):
    if(col > 0): return v[np.isfinite(v[:,col])]
    else: return v[np.isfinite(v)]

def classifyStocks(quotes):
    prices = quotes[:,4] # closing values
    times = quotes[:,0]
    classes = []

    for i,p in enumerate(prices[:-3]):
        p0, p1, p2, p3 = p, prices[i+1], prices[i+2], prices[i+3]
        pGainD1 = (p1-p0)/p0 
        pGainD2 = (p2-p1)/p1

        if(pGainD1 > 0.0125 and pGainD2 > 0.0075): # 1.25% day 1, 0.75% day 2
            classes.append( [times[i],  1, pGainD1, pGainD2] )
        elif(pGainD1 < -0.0125 and pGainD2 < -0.0075): # -1.25% day 1, -0.75% day 2
            classes.append( [times[i],  0, pGainD1, pGainD2] )
        else:
            classes.append( [times[i], -1, pGainD1, pGainD2] )
    
    return np.array(classes)


def addTimes(times, vals):
    return noNaN(np.c_[ times, vals ], 1)

def drawProgressBar(fraction):
    width = 40
    if(fraction > 1): fraction = 1
    if(fraction < 0): fraction = 0
    filled = int(round(fraction*width))
    print "\r[{0}{1}]".format("#" * filled, "-" * (width-filled)),
    print "%d%%" % (round(fraction*100)),
    sys.stdout.flush()


def addToDict(vals, ticker, shortname):
    global mainDict, valNamesDict

    if shortname not in valNamesDict: valNamesDict[shortname] = 1

    for t,v in vals:
        if(t not in mainDict[ticker]): mainDict[ticker][t] = {}

        mainDict[ticker][t][shortname] = round(v,3)


symbols = [line.strip() for line in open("../data/goodstocks.txt").readlines()]
# symbols = ["F", "AAPL"]
nsymbols = len(symbols)
tickerIDs = {} # key is stock name, val is a unique number (I will use iticker for it)

fname = "forBDT_092915.txt"
fh = open(fname,"w")
fhTickers = open(fname.replace(".txt","_tickers.txt"),"w")

valNamesDict, mainDict = {}, {}

for iticker,ticker in enumerate(symbols):
    # stock = gs.getStock(ticker, (2013, 1, 1), (2014, 12, 31))["days"] # for calculating
    stock = gs.getStock(ticker, (2014, 1, 1), (2014, 12, 20))["days"] # for calculating
    # stock = gs.getStock(ticker, (2014, 5, 1), (2014, 12, 20))["days"] # for calculating

    drawProgressBar(1.0*iticker/nsymbols)

    if(len(stock) < 50): continue

    quotes = []
    timesclose = []
    for day in sorted(stock.keys()):
        vals = stock[day]
        o, h, l, c, v = vals["o"], vals["h"], vals["l"], vals["c"], vals["v"]
        quotes.append( [day,o,h,l,c,v] )

    quotes = np.array(quotes)

    if(quotes[-1][4] > 600.0): continue # ignore expensive stocks
    if(quotes[-1][4] < 5.00): continue # ignore "penny" stocks


    times = quotes[:,0]
    inputs = {
        'open': quotes[:,1],
        'high': quotes[:,2],
        'low': quotes[:,3],
        'close': quotes[:,4],
        'volume': quotes[:,5],
    }


    try:

        if(ticker not in tickerIDs): tickerIDs[ticker] = iticker

        mainDict[ticker] = {}

        classStuff = classifyStocks(quotes)
        classVals = classStuff[:,[0,1]]
        gainD1Vals = classStuff[:,[0,2]]
        gainD2Vals = classStuff[:,[0,3]]

        addToDict(classVals, ticker, "class")
        addToDict(gainD1Vals, ticker, "gainD1")
        addToDict(gainD2Vals, ticker, "gainD2")


        #ema5 - ema10
        ema5 = ta.abstract.Function('ema')(inputs, timeperiod=5)
        ema10 = ta.abstract.Function('ema')(inputs, timeperiod=10)
        ematimes510 = noNaN(np.c_[ times, (ema5-ema10)/inputs['close'] ], 1)
        addToDict(ematimes510, ticker, "EMA510")

        # d/dt (ema5-ema10)
        # ematimesd510 = noNaN(np.c_[ times[1:], (ema5[1:]-ema10[:-1])/inputs['close'][1:] ], 1)
        ematimesd510 = noNaN(np.c_[ times[1:], ( (ema5[1:] - ema10[1:])-(ema5[:-1] - ema10[:-1]) ) / inputs['close'][1:] ], 1)
        addToDict(ematimesd510, ticker, "EMAD510")

        # #ema3 - ema7
        # ema3 = ta.abstract.Function('ema')(inputs, timeperiod=3)
        # ema7 = ta.abstract.Function('ema')(inputs, timeperiod=7)
        # ematimes37 = noNaN(np.c_[ times, (ema3-ema7)/inputs['close'] ], 1)
        # addToDict(ematimes37, ticker, "EMA37")

        # # d/dt (ema3-ema7)
        # ematimesd37 = noNaN(np.c_[ times[1:], (ema3[1:]-ema7[:-1])/inputs['close'][1:] ], 1)
        # addToDict(ematimesd37, ticker, "EMAD37")

        # know sure thing http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:know_sure_thing_kst
        ksttimes = noNaN(np.c_[ times, ind.kst(inputs['close']) ], 1)
        addToDict(ksttimes, ticker, "KST")

        # all indicators below
        indicators = ["BBANDS","DEMA","EMA","SAR","SAREXT", "ADX","ADXR","APO","AROON", \
                      "AROONOSC","BOP","CCI","CMO","DX","MACD","MACDEXT", "MACDFIX","MFI", \
                      "MINUS_DI","MINUS_DM","MOM","ROC", "RSI","STOCH","STOCHF","STOCHRSI", \
                      "WILLR","AD","ADOSC","HT_DCPERIOD","HT_DCPHASE", "HT_SINE","NATR","TRANGE" ]

        functiongroups = ta.get_function_groups()
        for fname in indicators:
            fn = ta.abstract.Function(fname)

            # skip candlesticks crap
            if(fname in functiongroups['Pattern Recognition']): continue

            params = {}

            outputs = fn(inputs, **params)
            numoutputs = len(fn.info['output_names'])
            norm = 1.0

            if(fname in functiongroups['Overlap Studies']): norm = inputs['close'] # normalize these indicators via closing price
            if(fname in functiongroups['Price Transform']): norm = inputs['close']


            if(numoutputs == 1):
                valtimes = addTimes(times,outputs/norm)
                addToDict(valtimes, ticker, fname)


            elif(numoutputs > 1):
                for i in range(numoutputs):
                    valtimes = addTimes(times,outputs[i]/norm)
                    shortname = fname+"_"+fn.info['output_names'][i]
                    addToDict(valtimes, ticker, shortname)

    except Exception,e:
        # so many failure modes. dont care to debug them if we have 3k stocks. just skip 'em
        print str(e)
        print ticker
        continue


valNames = valNamesDict.keys()
nvalNames = len(valNames)


ignore = ['class', 'gainD1', 'gainD2', 'tickerID']
fh.write( "# : Class Day gainD1 gainD2 tickerID " )
for name in valNames:
    if(name not in ignore): fh.write( "%s " % name )
fh.write("\n")

for stock in mainDict.keys():
    cnt = 0
    for t in mainDict[stock]:
        vals = mainDict[stock][t]
        if(len(vals) < nvalNames): continue

        cnt += 1

        fh.write( "%i %i %.3f %.3f %i " % (vals['class'], t, vals['gainD1'], vals['gainD2'], tickerIDs[stock]) )
        for name in valNames:
            if(name not in ignore): fh.write( "%.3f " % vals[name] )
        fh.write( "\n" )

    print "Stock", stock, "ended up with", cnt, "days of data"

fhTickers.write( "# : tickerName tickerID\n" )
for ticker in tickerIDs:
    fhTickers.write( "%s %i\n" % (ticker, tickerIDs[ticker]) )
fhTickers.close()

# print tickerIDs

fh.close()
