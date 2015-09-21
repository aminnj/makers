import os, sys, random

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

def removeBelowSize(d,sizeThreshold=1):
    newd = { }
    for key in d:
        if not d[key]: continue
        if len(d[key].keys()) < sizeThreshold: continue

        newd[key] = d[key]
            
    return newd

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

def findSignals(quotes, ignoretimes=None):
    x = 0.04
    prices = quotes[:,4] # closing values
    times = quotes[:,0]
    sig, bkg = [], []
    dCuts = {}
    if ignoretimes is not None: dCuts = { int(t):1 for t in ignoretimes } # for lookup

    for i,p in enumerate(prices[:-3]):
        if int(times[i]) in dCuts: continue

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


symbols = [line.strip() for line in open("../data/goodstocks.txt").readlines()]
# symbols = ["F", "AAL"]
nsymbols = len(symbols)

print "FILLING HISTOGRAMS!"

extraParams = {
        "BBANDS": { "timeperiod": 20 }
        }

doCuts = False
writeBDTtext = True 
makePlots = False
fh = None
dInds = {}
bkgPercentinc = np.array([])
sigPercentinc = np.array([])

if(writeBDTtext):
    fh = open("forBDT.txt","w")

for iticker,ticker in enumerate(symbols):
    # stock = gs.getStock(ticker, (2013, 1, 1), (2014, 12, 31))["days"] # for calculating
    stock = gs.getStock(ticker, (2014, 1, 1), (2014, 12, 20))["days"] # for calculating

    drawProgressBar(1.0*iticker/nsymbols)

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


    times = quotes[:,0]
    inputs = {
        'open': quotes[:,1],
        'high': quotes[:,2],
        'low': quotes[:,3],
        'close': quotes[:,4],
        'volume': quotes[:,5],
    }

    ### CUTS BEGIN

    ignoretimes = np.array([])

    if doCuts:
        outputs = ta.abstract.Function("WILLR")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > -85][:,0] )

        outputs = ta.abstract.Function("HT_DCPHASE")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > 75][:,0] )

        outputs = ta.abstract.Function("CCI")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > -90][:,0] )

        outputs = ta.abstract.Function("AROONOSC")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > -60][:,0] )

        outputs = ta.abstract.Function("NATR")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] < 3][:,0] )

        outputs = ta.abstract.Function("SAREXT")(inputs)
        timevals = addTimes(quotes[:,0]/inputs['close'], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > 0][:,0] )

        outputs = ta.abstract.Function("SAR")(inputs)
        timevals = addTimes(quotes[:,0]/inputs['close'], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] < 1.1][:,0] )

        outputs = ta.abstract.Function("DX")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] < 40][:,0] )

        outputs = ta.abstract.Function("RSI")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > 35][:,0] )

        outputs = ta.abstract.Function("BOP")(inputs)
        timevals = addTimes(quotes[:,0], outputs)
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > 0][:,0] )

        outputs = ta.abstract.Function("STOCHF")(inputs)
        timevals = addTimes(quotes[:,0], outputs[1]) # fastd is the second one
        ignoretimes = np.append( ignoretimes, timevals[timevals[:,1] > 18][:,0] )
    ### CUTS END


    bkg, sig = findSignals(quotes, ignoretimes)
    # dicts for const. lookup
    bkgtimes = { int(bkg[:,0][i]):1 for i in range(len(bkg[:,0])) } if len(bkg) > 0 else { }
    sigtimes = { int(sig[:,0][i]):1 for i in range(len(sig[:,0])) } if len(sig) > 0 else { }

    ### PLOTS BEGIN

    try:

        # % increase over 3 days
        if(len(bkg) > 0): bkgPercentinc = np.append( bkgPercentinc, bkg[:,1] )
        if(len(sig) > 0): sigPercentinc = np.append( sigPercentinc, sig[:,1] )

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
                      "HT_PHASOR","HT_SINE","HT_TRENDMODE","AVGPRICE","MEDPRICE","TYPPRICE","WCLPRICE","ATR","NATR","TRANGE" ]
        # indicators = ["WILLR", "DX", "BBANDS", "MOM"]
        fullIndicators = []

        forBDTsig = {}
        forBDTbkg = {}

        nIndicators = 0
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

            nIndicators += numoutputs

            if(numoutputs == 1):
                valtimes = addTimes(times,outputs/norm)
                fullIndicators.append(fname)

                for t,v in valtimes:
                    t = int(t)
                    if t not in forBDTsig: forBDTsig[t] = {}
                    if t not in forBDTbkg: forBDTbkg[t] = {}
                    if t in sigtimes: forBDTsig[t][fname] = v
                    if t in bkgtimes: forBDTbkg[t][fname] = v

                addToSigBkgDict(valtimes, fname, bkgtimes, sigtimes, longname=fn.info['display_name'])
            elif(numoutputs > 1):
                for i in range(numoutputs):
                    valtimes = addTimes(times,outputs[i]/norm)
                    shortname = fname+"_"+fn.info['output_names'][i]
                    fullIndicators.append(shortname)

                    for t,v in valtimes:
                        t = int(t)
                        if t not in forBDTsig: forBDTsig[t] = {}
                        if t not in forBDTbkg: forBDTbkg[t] = {}
                        if t in sigtimes: forBDTsig[t][shortname] = v
                        if t in bkgtimes: forBDTbkg[t][shortname] = v

                    addToSigBkgDict(valtimes, shortname, bkgtimes, sigtimes, longname=fn.info['display_name']+" ("+fn.info['output_names'][i]+")")

        assert(len(fullIndicators) == nIndicators), "ERROR: len(fullIndicators) != nIndicators (%i != %i)" % (len(fullIndicators), nIndicators)



        forBDTsig = removeBelowSize(forBDTsig, nIndicators)
        forBDTbkg = removeBelowSize(forBDTbkg, nIndicators)

        if writeBDTtext:
            # if( iticker == 0 ): print "# ["+ticker+"]: SB Day "+" ".join(fullIndicators)
            prescale = 1
            fh.write( "# ["+ticker+"]: SB Day "+" ".join(fullIndicators) +"\n" )
            for t in random.sample(forBDTsig.keys(), len(forBDTsig.keys())//prescale): #  "prescale" the events by 10
                # we should have all indicators in here if we've done removeBelowSize properly
                # 1 for sig, 0 for bkg
                fh.write("1 %i " % int(t))
                for indic in fullIndicators: 
                    fh.write("%.2f " % forBDTsig[t][indic])
                fh.write("\n")

                # print "1", t,
                # for indic in fullIndicators: print forBDTsig[t][indic],
                # print
            for t in random.sample(forBDTbkg.keys(), len(forBDTbkg.keys())//prescale):
                fh.write("0 %i " % int(t))
                for indic in fullIndicators: 
                    fh.write("%.2f " % forBDTbkg[t][indic])
                fh.write("\n")

                # print "0", t,
                # for indic in fullIndicators: print forBDTbkg[t][indic],
                # print


    except Exception,e:
        # so many failure modes. dont care to debug them if we have 3k stocks. just skip 'em
        print str(e)
        print ticker
        continue

    ### PLOTS END

if(writeBDTtext): fh.close()


if(makePlots):
    print "PLOTTING!"
    plotdir = "../sb4/"
    nkeys = len(dInds.keys())
    for i,key in enumerate(dInds.keys()):
        continue
        drawProgressBar(1.0*i/nkeys)
        try:
            makeSigBkgHist(dInds[key]["bkg"], dInds[key]["sig"], plotdir+key+".png", dInds[key]["longname"], nbins=60)
        except:
            # try-except all the things!
            continue
        # u.web(plotdir+key+".png")

    makeSigBkgHist(bkgPercentinc, sigPercentinc, plotdir+"sig_definition.png", "% increase over 3 days", norm=0, nbins=60)
    # u.web(plotdir+"sig_definition.png")

