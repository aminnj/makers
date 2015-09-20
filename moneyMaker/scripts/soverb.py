import os, sys

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import talib as ta

import getStocks as gs
import utils as u
import indicators as ind


def noNaN(v, col=0):
    if(col > 0): return v[np.isfinite(v[:,col])]
    else: return v[np.isfinite(v)]

def filterTimes(d, arr):
    # only take vectors in arr if the first element of the vec is a key in d
    return np.array([e for e in arr if int(e[0]) in d])

def makeSigBkgHist(bkg, sig, filename, title="", nbins=20, norm=1):
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=16)
    bins=np.histogram(np.hstack((sig,bkg)), bins=nbins)[1] #get the bin edges
    ax.hist(bkg,bins,color='r',alpha=1.0,label='bkg', normed=norm, histtype='stepfilled')
    ax.hist(sig,bins,color='b',alpha=1.0,label='sig', normed=norm, histtype='step')
    ax.legend(loc='upper right')
    ax.text(0.015,0.985,"#bkg: "+str(len(bkg)), horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='red')
    ax.text(0.015,0.935,"#sig: "+str(len(sig)), horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='blue')
    ax.text(0.015,0.885,"Normalized" if norm>0 else "Unnormalized", horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='black')
    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)

def findSignals(quotes):
    x = 0.03
    prices = quotes[:,4] # closing values
    times = quotes[:,0]
    sig, bkg = [], []
    for i,p in enumerate(prices[:-3]):
        p0, p1, p2, p3 = p, prices[i+1], prices[i+2], prices[i+3]
        # want stock to go up by x% over 3 days without decreasing at all
        if((p3-p0)/p0 < x or p1 < p0 or p2 < p1 or p3 < p2): bkg.append( [times[i],(p3-p0)/p0] )
        else: sig.append( [times[i],(p3-p0)/p0] )
    return np.array(bkg), np.array(sig)

def normToM1P1(vals):
    # normalize so that min and max are -1 and 1, respectively
    vals += 1.0*np.min(vals)
    vals = 1.0*vals/np.max(vals)
    return vals

def addToSigBkgDict(valtimes, shortname, bkgtimes, sigtimes, longname=None):
    global dInds
    if shortname not in dInds:
        dInds[shortname] = {}
        dInds[shortname]["sig"] = np.array([])
        dInds[shortname]["bkg"] = np.array([])
        dInds[shortname]["longname"] = shortname if not longname else longname

    filtbkg = filterTimes(bkgtimes, valtimes)
    filtsig = filterTimes(sigtimes, valtimes)
    if len(bkgtimes) > 0: 
        dInds[shortname]["bkg"] = np.append(dInds[shortname]["bkg"], filtbkg[:,1])
    if len(sigtimes) > 0:
        dInds[shortname]["sig"] = np.append(dInds[shortname]["sig"], filtsig[:,1])

def addTimes(times, vals):
    return noNaN(np.c_[ times, vals ], 1)



symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:10]
symbols = ["F", "AAL"]


dInds = {}
for ticker in symbols:
# for ticker in ["F"]:
    stock = gs.getStock(ticker, (2010, 1, 1), (2014, 12, 31))["days"] # for calculating

    if(len(stock) < 50): continue


    quotes = []
    timesclose = []
    for day in sorted(stock.keys()):
        vals = stock[day]
        o, h, l, c, v = vals["o"], vals["h"], vals["l"], vals["c"], vals["v"]
        quotes.append( [day,o,h,l,c,v] )

    quotes = np.array(quotes)

    inputs = {
        'open': quotes[:,1],
        'high': quotes[:,2],
        'low': quotes[:,3],
        'close': quotes[:,4],
        'volume': quotes[:,5],
    }


    times = quotes[:,0]
    bkg, sig = findSignals(quotes)
    # dict for const. lookup
    bkgtimes = { int(bkg[:,0][i]):1 for i in range(len(bkg[:,0])) }
    sigtimes = { int(sig[:,0][i]):1 for i in range(len(sig[:,0])) }

    ### PLOTS BEGIN

    ema5 = ta.abstract.Function('ema')(inputs, timeperiod=5)
    ema10 = ta.abstract.Function('ema')(inputs, timeperiod=10)
    ematimes = noNaN(np.c_[ times, (ema5-ema10)/inputs['close'] ], 1)
    addToSigBkgDict(ematimes, "ema5minus10", bkgtimes, sigtimes, longname="(ema5-ema10)/close")

    ema3 = ta.abstract.Function('ema')(inputs, timeperiod=3)
    ema7 = ta.abstract.Function('ema')(inputs, timeperiod=7)
    ematimes = noNaN(np.c_[ times, (ema3-ema7)/inputs['close'] ], 1)
    addToSigBkgDict(ematimes, "ema3minus7", bkgtimes, sigtimes, longname="(ema3-ema7)/close")

    # all indicators below

    indicators = ["BBANDS","DEMA","EMA","HT_TRENDLINE","KAMA","MA","MAMA","MIDPOINT","MIDPRICE","SAR","SAREXT","SMA","T3","TEMA","TRIMA","WMA","ADX","ADXR","APO","AROON","AROONOSC","BOP","CCI","CMO","DX","MACD","MACDEXT","MACDFIX","MFI","MINUS_DI","MINUS_DM","MOM","PLUS_DI","PLUS_DM","PPO","ROC","ROCP","ROCR","ROCR100","RSI","STOCH","STOCHF","STOCHRSI","TRIX","ULTOSC","WILLR","AD","ADOSC","OBV","HT_DCPERIOD","HT_DCPHASE","HT_PHASOR","HT_SINE","HT_TRENDMODE","AVGPRICE","MEDPRICE","TYPPRICE","WCLPRICE","ATR","NATR","TRANGE","CDL2CROWS","CDL3BLACKCROWS","CDL3INSIDE","CDL3LINESTRIKE","CDL3OUTSIDE","CDL3STARSINSOUTH","CDL3WHITESOLDIERS","CDLABANDONEDBABY","CDLADVANCEBLOCK","CDLBELTHOLD","CDLBREAKAWAY","CDLCLOSINGMARUBOZU","CDLCONCEALBABYSWALL","CDLCOUNTERATTACK","CDLDARKCLOUDCOVER","CDLDOJI","CDLDOJISTAR","CDLDRAGONFLYDOJI","CDLENGULFING","CDLEVENINGDOJISTAR","CDLEVENINGSTAR","CDLGAPSIDESIDEWHITE","CDLGRAVESTONEDOJI","CDLHAMMER","CDLHANGINGMAN","CDLHARAMI","CDLHARAMICROSS","CDLHIGHWAVE","CDLHIKKAKE","CDLHIKKAKEMOD","CDLHOMINGPIGEON","CDLIDENTICAL3CROWS","CDLINNECK","CDLINVERTEDHAMMER","CDLKICKING","CDLKICKINGBYLENGTH","CDLLADDERBOTTOM","CDLLONGLEGGEDDOJI","CDLLONGLINE","CDLMARUBOZU","CDLMATCHINGLOW","CDLMATHOLD","CDLMORNINGDOJISTAR","CDLMORNINGSTAR","CDLONNECK","CDLPIERCING","CDLRICKSHAWMAN","CDLRISEFALL3METHODS","CDLSEPARATINGLINES","CDLSHOOTINGSTAR","CDLSHORTLINE","CDLSPINNINGTOP","CDLSTALLEDPATTERN","CDLSTICKSANDWICH","CDLTAKURI","CDLTASUKIGAP","CDLTHRUSTING","CDLTRISTAR","CDLUNIQUE3RIVER","CDLUPSIDEGAP2CROWS","CDLXSIDEGAP3METHODS"]

    functiongroups = ta.get_function_groups()
    for fname in indicators:
        fn = ta.abstract.Function(fname)

        # skip candlesticks
        if(fname in functiongroups['Pattern Recognition']): continue

        outputs = fn(inputs)
        numoutputs = len(fn.info['output_names'])
        norm = 1.0

        if(fname in functiongroups['Overlap Studies']): norm = inputs['close'] # normalize these indicators via closing price
        if(fname in functiongroups['Price Transform']): norm = inputs['close']



        if(numoutputs == 1):
            valtimes = addTimes(times,outputs/norm)
            addToSigBkgDict(valtimes, fname, bkgtimes, sigtimes, longname=fn.info['display_name'])
        elif(numoutputs > 1):
            for i in range(numoutputs):
                valtimes = addTimes(times,outputs[i]/norm)
                addToSigBkgDict(valtimes, fname+"_"+fn.info['output_names'][i], bkgtimes, sigtimes, longname=fn.info['display_name']+" ("+fn.info['output_names'][i]+")")

    ### PLOTS END


plotdir = "../plots/"
for key in dInds.keys():
    makeSigBkgHist(dInds[key]["bkg"], dInds[key]["sig"], plotdir+key+".png", dInds[key]["longname"], nbins=30)
    # u.web(plotdir+key+".png")

bkg, sig = findSignals(quotes)
makeSigBkgHist(bkg[:,1], sig[:,1], plotdir+"sig_definition.png", "% increase over 3 days", norm=0)
u.web(plotdir+"sig_definition.png")
