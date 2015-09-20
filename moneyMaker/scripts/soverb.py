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
    # remove >5 sigma vals
    stdbkg, stdsig = np.std(bkg), np.std(sig)
    meanbkg, meansig = np.mean(bkg), np.mean(sig)
    bkg = bkg[np.abs(meanbkg - bkg) <= stdbkg*5]
    sig = sig[np.abs(meansig - sig) <= stdsig*5]
    nbkg = len(bkg)
    nsig = len(sig)

    # find cut value for which s/b is maximum
    valstotry = np.linspace(np.min(sig),np.max(sig),num=50,endpoint=False)
    
    # # want to maximize eff*purity (eff=nsig/ntotnocut, purity=nsig/ntotwithcut)
    # maxratioleft, maxratioright = -1., -1.
    # leftval, rightval = -1000., -1000.
    # for val in valstotry:
    #     try:
    #         nbkgleft = len(bkg[bkg < val])
    #         nsigleft = len(sig[sig < val])
    #         nbkgright = nbkg - nbkgleft
    #         nsigright = nsig - nsigleft
    #         effleft, purleft = 1.0*nsigleft/(nbkg+nsig),1.0*nsigleft/(nsigleft+nbkgleft), 
    #         ratioleft = effleft*purleft
    #         effright, purright = 1.0*nsigright/(nbkg+nsig),1.0*nsigright/(nsigright+nbkgright), 
    #         ratioright = effright*purright

    #         eff, pur = 1.0*nsigleft/(nbkg+nsig),1.0*nsigleft/(nsigleft+nbkgleft), 
    #         # print val, nbkgleft, nsigleft, nbkgright, nsigright, "eff:", eff, "pur:",pur, "eff*pur:",eff*pur
    #         if(ratioleft > maxratioleft):
    #             maxratioleft = ratioleft
    #             leftval = val
    #         if(ratioright > maxratioright):
    #             maxratioright = ratioright
    #             rightval = val
    #     except:
    #         pass
    #         # probably div by zero, ignore it. who cares?

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=16)
    bins=np.histogram(np.hstack((sig,bkg)), bins=nbins)[1] #get the bin edges
    ax.hist(bkg,bins,color='r',alpha=1.0,label='bkg', normed=norm, histtype='stepfilled')
    ax.hist(sig,bins,color='b',alpha=1.0,label='sig', normed=norm, histtype='step')
    ax.legend(loc='upper right')
    ax.text(0.015,0.985,"#bkg: "+str(len(bkg)), horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='red')
    ax.text(0.015,0.935,"#sig: "+str(len(sig)), horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='blue')
    ax.text(0.015,0.885,"Normalized" if norm>0 else "Unnormalized", horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='black')
    # xr = 1.0*(ax.get_xlim()[1]-ax.get_xlim()[0])
    # if(maxratioleft > maxratioright): # left side wins with cut value of leftval
    #     ax.axvline(x=leftval,c="black",linewidth=0.5)
    #     ax.arrow(leftval, ax.get_ylim()[1]*0.95, -xr*0.04, 0, fc='k',ec='k',head_width=ax.get_ylim()[1]*0.01,head_length=xr*0.01,width=0.0001)
    # else: # right side wins with cut value of rightval
    #     ax.axvline(x=rightval,c="black",linewidth=0.5)
    #     ax.arrow(rightval, ax.get_ylim()[1]*0.95,  xr*0.04, 0, fc='k',ec='k',head_width=ax.get_ylim()[1]*0.01,head_length=xr*0.01,width=0.0001)

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
        # if((p3-p0)/p0 < x or p1 < p0 or p2 < p1 or p3 < p2): bkg.append( [times[i],(p3-p0)/p0] ) # FIXME
        if((p3-p0)/p0 < x): bkg.append( [times[i],(p3-p0)/p0] )
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
    if len(bkgtimes) > 0 and len(filtbkg) > 0: 
        dInds[shortname]["bkg"] = np.append(dInds[shortname]["bkg"], filtbkg[:,1])
    if len(sigtimes) > 0 and len(filtsig) > 0:
        dInds[shortname]["sig"] = np.append(dInds[shortname]["sig"], filtsig[:,1])

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


symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:]
# symbols = ["F", "AAL"]
nsymbols = len(symbols)

print "FILLING HISTOGRAMS!"

extraParams = {
        "BBANDS": { "timeperiod": 20 }
        }

dInds = {}
bkgPercentinc = np.array([])
sigPercentinc = np.array([])
for i,ticker in enumerate(symbols):
# for ticker in ["F"]:
    stock = gs.getStock(ticker, (2013, 1, 1), (2014, 12, 31))["days"] # for calculating

    drawProgressBar(1.0*i/nsymbols)

    if(len(stock) < 50): continue

    quotes = []
    timesclose = []
    for day in sorted(stock.keys()):
        vals = stock[day]
        o, h, l, c, v = vals["o"], vals["h"], vals["l"], vals["c"], vals["v"]
        quotes.append( [day,o,h,l,c,v] )

    quotes = np.array(quotes)

    if(quotes[-1][4] > 300.0): continue # ignore expensive stocks
    if(quotes[-1][4] < 1.00): continue # ignore "penny" stocks

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
    bkgtimes = { int(bkg[:,0][i]):1 for i in range(len(bkg[:,0])) } if len(bkg) > 0 else { }
    sigtimes = { int(sig[:,0][i]):1 for i in range(len(sig[:,0])) } if len(sig) > 0 else { }

    ### PLOTS BEGIN

    try:

        # % increase over 3 days
        bkgPercentinc = np.append( bkgPercentinc, bkg[:,1] )
        sigPercentinc = np.append( sigPercentinc, sig[:,1] )

        #ema5 - ema10
        ema5 = ta.abstract.Function('ema')(inputs, timeperiod=5)
        ema10 = ta.abstract.Function('ema')(inputs, timeperiod=10)
        ematimes510 = noNaN(np.c_[ times, (ema5-ema10)/inputs['close'] ], 1)
        addToSigBkgDict(ematimes510, "ema5minus10", bkgtimes, sigtimes, longname="(ema5-ema10)/close")

        #ema3 - ema7
        ema3 = ta.abstract.Function('ema')(inputs, timeperiod=3)
        ema7 = ta.abstract.Function('ema')(inputs, timeperiod=7)
        ematimes37 = noNaN(np.c_[ times, (ema3-ema7)/inputs['close'] ], 1)
        addToSigBkgDict(ematimes37, "ema3minus7", bkgtimes, sigtimes, longname="(ema3-ema7)/close")

        # know sure thing http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:know_sure_thing_kst
        ksttimes = noNaN(np.c_[ times, ind.kst(inputs['close']) ], 1)
        addToSigBkgDict(ksttimes, "KST", bkgtimes, sigtimes, longname="Know Sure Thing (KST)")

        # know sure thing with hull moving average
        ksthmatimes = noNaN(np.c_[ times, ind.hma(ind.kst(inputs['close'])) ], 1)
        addToSigBkgDict(ksthmatimes, "KSTHMA", bkgtimes, sigtimes, longname="Know Sure Thing (KST) with HMA")

        # diff b/w KST with HMA and KST without HMA
        kstdiff = noNaN(np.c_[ times, ind.kst(inputs['close'])-ind.hma(ind.kst(inputs['close'])) ], 1)
        addToSigBkgDict(kstdiff, "KSTDIFF", bkgtimes, sigtimes, longname="KST HMA - KST")

        # all indicators below

        indicators = ["BBANDS","DEMA","EMA","HT_TRENDLINE","KAMA","MA","MAMA","MIDPOINT","MIDPRICE","SAR","SAREXT","SMA", \
                      "T3","TEMA","TRIMA","WMA","ADX","ADXR","APO","AROON","AROONOSC","BOP","CCI","CMO","DX","MACD","MACDEXT", \
                      "MACDFIX","MFI","MINUS_DI","MINUS_DM","MOM","PLUS_DI","PLUS_DM","PPO","ROC","ROCP","ROCR","ROCR100", \
                      "RSI","STOCH","STOCHF","STOCHRSI","TRIX","ULTOSC","WILLR","AD","ADOSC","OBV","HT_DCPERIOD","HT_DCPHASE", \
                      "HT_PHASOR","HT_SINE","HT_TRENDMODE","AVGPRICE","MEDPRICE","TYPPRICE","WCLPRICE","ATR","NATR","TRANGE", \
                      "CDL2CROWS","CDL3BLACKCROWS","CDL3INSIDE","CDL3LINESTRIKE","CDL3OUTSIDE","CDL3STARSINSOUTH", \
                      "CDL3WHITESOLDIERS","CDLABANDONEDBABY","CDLADVANCEBLOCK","CDLBELTHOLD","CDLBREAKAWAY","CDLCLOSINGMARUBOZU", \
                      "CDLCONCEALBABYSWALL","CDLCOUNTERATTACK","CDLDARKCLOUDCOVER","CDLDOJI","CDLDOJISTAR","CDLDRAGONFLYDOJI", \
                      "CDLENGULFING","CDLEVENINGDOJISTAR","CDLEVENINGSTAR","CDLGAPSIDESIDEWHITE","CDLGRAVESTONEDOJI","CDLHAMMER", \
                      "CDLHANGINGMAN","CDLHARAMI","CDLHARAMICROSS","CDLHIGHWAVE","CDLHIKKAKE","CDLHIKKAKEMOD","CDLHOMINGPIGEON", \
                      "CDLIDENTICAL3CROWS","CDLINNECK","CDLINVERTEDHAMMER","CDLKICKING","CDLKICKINGBYLENGTH","CDLLADDERBOTTOM", \
                      "CDLLONGLEGGEDDOJI","CDLLONGLINE","CDLMARUBOZU","CDLMATCHINGLOW","CDLMATHOLD","CDLMORNINGDOJISTAR", \
                      "CDLMORNINGSTAR","CDLONNECK","CDLPIERCING","CDLRICKSHAWMAN","CDLRISEFALL3METHODS","CDLSEPARATINGLINES", \
                      "CDLSHOOTINGSTAR","CDLSHORTLINE","CDLSPINNINGTOP","CDLSTALLEDPATTERN","CDLSTICKSANDWICH","CDLTAKURI", \
                      "CDLTASUKIGAP","CDLTHRUSTING","CDLTRISTAR","CDLUNIQUE3RIVER","CDLUPSIDEGAP2CROWS","CDLXSIDEGAP3METHODS"]

        functiongroups = ta.get_function_groups()
        for fname in indicators:
            fn = ta.abstract.Function(fname)

            # skip candlesticks crap
            if(fname in functiongroups['Pattern Recognition']): continue

            params = {}
            if(fname in extraParams): params = extraParams[fname]

            outputs = fn(inputs, **params)
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

    except:
        # so many failure modes. dont care to debug them if we have 3k stocks. just skip 'em
        print ticker
        continue

    ### PLOTS END


print "PLOTTING!"
plotdir = "../sb3/"
nkeys = len(dInds.keys())
for i,key in enumerate(dInds.keys()):
    drawProgressBar(1.0*i/nkeys)
    try:
        makeSigBkgHist(dInds[key]["bkg"], dInds[key]["sig"], plotdir+key+".png", dInds[key]["longname"], nbins=60)
    except:
        # try-except all the things!
        continue
    # u.web(plotdir+key+".png")

makeSigBkgHist(bkgPercentinc, sigPercentinc, plotdir+"sig_definition.png", "% increase over 3 days", norm=0, nbins=60)
# u.web(plotdir+"sig_definition.png")
