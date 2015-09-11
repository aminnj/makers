import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("SNDK", (2008, 6, 20), (2010, 10, 7))["days"]

quotes = []
normquotes = []
fractions = []
timesclose = []
for day in sorted(stock.keys()):
    vals = stock[day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]

    # "normalize" values (subtract out open price)
    no = round(o-o,2)
    nh = round(h-o,2)
    nl = round(l-o,2)
    nc = round(c-o,2)

    quotes.append( [day,o,h,l,c] )
    normquotes.append( [day,no,nh,nl,nc] )
    timesclose.append([day,c])

timesclose = np.array(timesclose)
bbands = ind.bbtimes(timesclose, 20)

ema1 = ind.ematimes(timesclose, 10)
ema2 = ind.ematimes(timesclose, 20)
ema3 = ind.ematimes(timesclose, 30)
ema4 = ind.ematimes(timesclose, 40)
ema5 = ind.ematimes(timesclose, 50)

# bbands discards early dates since it can't do a moving average for those
# we reshape the other arrays to match up with bbands' size
normquotes = np.array(normquotes[-len(bbands):])
quotes = np.array(quotes[-len(bbands):])

km = skc.KMeans(precompute_distances='auto',max_iter=600,n_clusters=6)
# add more and more columns to data
# subtract out opening prices from bbands
data = np.c_[ normquotes[:,[1,2,3,4]] ]
data = np.c_[ data, bbands[:,1]-quotes[:,1] ]
data = np.c_[ data, bbands[:,2]-quotes[:,1] ]
data = np.c_[ data, bbands[:,3]-quotes[:,1] ]
clusters = km.fit_predict(data)
colors = list("rbgkcmyw") # only allows up to 8 colors :(

shading = []
for i,day in enumerate(quotes[:,0]): shading.append([ day, colors[clusters[i]] ])

u.makeCandlestick(quotes, "../plots/candlestick.png", title="SNDK (2009)", shading=shading, bbands=bbands, window=[(2009,6,10),(2009,9,15)], averages=[ema1,ema2,ema3,ema4,ema5])
u.web("../plots/candlestick.png")

