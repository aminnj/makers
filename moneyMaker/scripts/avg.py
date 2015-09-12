import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
# stock = gs.getStock("SNDK", (2008, 6, 20), (2015, 11, 7))["days"]
# stock = gs.getStock("SNDK", (2008, 6, 20), (2010, 10, 7))["days"]

stock = gs.getStock("WMT", (2008, 6, 20), (2015, 11, 7))["days"] # for calculating
d1,d2 = (2014,3,10),(2014,6,15) # for plotting


quotes = []
normquotes = []
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

emas = []
for i in [1,3,4,8]:
    emas.append( ind.ematimes(timesclose,10*i) )


# bbands discards early dates since it can't do a moving average for those
# we reshape the other arrays to match up with bbands' size
normquotes = np.array(normquotes[-len(bbands):])
quotes = np.array(quotes[-len(bbands):])

km = skc.KMeans(n_clusters=5)
# add more and more columns to data (c_ just puts columns side by side)
data = np.c_[ normquotes[:,[1,2,3,4]] ]
data = np.c_[ data, bbands[:,1]-quotes[:,1] ] # subtract out opening prices from bbands
data = np.c_[ data, bbands[:,2]-quotes[:,1] ]
data = np.c_[ data, bbands[:,3]-quotes[:,1] ]

clusters = km.fit_predict(data)
colors = list("rbgkcmywrbgkcmyw") # only allows up to 16 colors, but it repeats after 8

clustershading = []
for i,day in enumerate(quotes[:,0]):
    clustershading.append([ day, colors[clusters[i]] ])


crossovershading = []
for day, rising in ind.crossovertimes(emas):
    crossovershading.append([day, 'g' if rising else 'r'])


u.makeCandlestick(quotes, "../plots/candlestick.png", title="WMT (2009)", \
        shadings=[clustershading,crossovershading], \
        bbands=bbands, \
        window=[d1,d2], \
        averages=emas )
u.web("../plots/candlestick.png")

