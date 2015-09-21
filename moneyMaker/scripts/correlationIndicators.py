import os, sys, itertools

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


def drawProgressBar(fraction):
    width = 40
    if(fraction > 1): fraction = 1
    if(fraction < 0): fraction = 0
    filled = int(round(fraction*width))
    print "\r[{0}{1}]".format("#" * filled, "-" * (width-filled)),
    print "%d%%" % (round(fraction*100)),
    sys.stdout.flush()

def correlation(v1, v2):
    v1 = noNaN(v1)
    v2 = noNaN(v2)
    v1 = v1[-min(len(v1),len(v2)):]
    v2 = v2[-min(len(v1),len(v2)):]
    # Pearson correlation
    # http://stackoverflow.com/questions/3949226/calculating-pearson-correlation-and-significance-in-python
    return np.abs(np.corrcoef(v1,v2)[0,1])


N = 1000
dInds = {}

# indicators = ["BBANDS","DEMA","EMA","HT_TRENDLINE","KAMA","MA","MAMA","MIDPOINT","MIDPRICE","SAR","SAREXT","SMA", \
#               "T3","TEMA","TRIMA","WMA","ADX","ADXR","APO","AROON","AROONOSC","BOP","CCI","CMO","DX","MACD","MACDEXT", \
#               "MACDFIX","MFI","MINUS_DI","MINUS_DM","MOM","PLUS_DI","PLUS_DM","PPO","ROC","ROCP","ROCR","ROCR100", \
#               "RSI","STOCH","STOCHF","STOCHRSI","TRIX","ULTOSC","WILLR","AD","ADOSC","OBV","HT_DCPERIOD","HT_DCPHASE", \
#               "HT_PHASOR","HT_SINE","HT_TRENDMODE","AVGPRICE","MEDPRICE","TYPPRICE","WCLPRICE","ATR","NATR","TRANGE"]
# moving averages correlated amongst themselves, so I took them out because then the plot has a stupid block
indicators = ["ADX","ADXR","APO","AROON","AROONOSC","BOP","CCI","CMO","DX","MACD","MACDEXT", \
              "MACDFIX","MFI","MINUS_DI","MINUS_DM","MOM","PLUS_DI","PLUS_DM","PPO","ROC", \
              "RSI","STOCH","TRIX","ULTOSC","WILLR","AD","ADOSC","OBV","HT_DCPERIOD","HT_DCPHASE", \
              "HT_PHASOR","HT_SINE","HT_TRENDMODE","AVGPRICE","MEDPRICE","TYPPRICE","WCLPRICE","ATR","NATR","TRANGE"]
# indicators = ["WILLR", "HT_SINE"]
fullindicators = [] # will get filled with all the indicators and subindicators (like BBANDS_low, etc.)

closeprices = np.abs(np.random.random(N))
openprices = closeprices*(0.1*np.abs(np.random.random(N))+0.95)
highprices = closeprices*1.06
lowprices = closeprices*0.94
vols = np.floor(10000*np.abs(np.random.random(N)))

inputs = {
    'open': openprices,
    'high': highprices,
    'low': lowprices,
    'close': closeprices,
    'volume': vols,
}

### PLOTS BEGIN



functiongroups = ta.get_function_groups()
for fname in indicators:
    fn = ta.abstract.Function(fname)

    outputs = fn(inputs)
    numoutputs = len(fn.info['output_names'])
    norm = 1.0

    if(fname in functiongroups['Overlap Studies']): norm = inputs['close'] # normalize these indicators via closing price
    if(fname in functiongroups['Price Transform']): norm = inputs['close']

    if(numoutputs == 1):
        fullindicators.append(fname)
        dInds[fname] = outputs/norm
    elif(numoutputs > 1):
        for i in range(numoutputs):
            fullindicators.append(fname+"_"+fn.info['output_names'][i])
            dInds[fname+"_"+fn.info['output_names'][i]] = outputs[i]/norm

data = np.zeros((len(fullindicators),len(fullindicators)))
for i,one in enumerate(fullindicators):
    for j,two in enumerate(fullindicators):
        # if(i>=j): continue # factor of 2 speedup, but then the plot looks dumb
        data[i,j] = correlation(dInds[one], dInds[two])

plotdir = "../plots/"

fig, ax = plt.subplots( nrows=1, ncols=1, figsize=(14.5,11) )  # create figure & 1 axis
plt.pcolor(data)
plt.colorbar()
ax.set_xticks( np.arange(0.5,0.5+len(fullindicators)) )
ax.set_xticklabels( fullindicators, rotation=90 )
ax.set_yticks( np.arange(0.5,0.5+len(fullindicators)) )
ax.set_yticklabels( fullindicators )

fig.savefig(plotdir+"correlation.png", bbox_inches='tight')
u.web(plotdir+"correlation.png")

