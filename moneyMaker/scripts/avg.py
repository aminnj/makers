import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind
import cluster as cl

plotdir = "../plots/"


# stock = gs.getStock("WMT", (2009, 2, 15), (2014, 5, 3))["days"] # for calculating
# d1,d2 = (2013,8,9),(2014,4,25) # for plotting

stock = gs.getStock("MCD", (2006, 1, 1), (2008, 10, 5))["days"] # for calculating
d1,d2 = (2007,8,1),(2008,3,5) # for plotting

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

quotes = np.array(quotes)
rsis = ind.rsitimes(quotes[:,[0,1]],14)

# bbands discards early dates since it can't do a moving average for those
# we reshape the other arrays to match up with bbands' size
normquotes = np.array(normquotes[-len(bbands):])
quotes = quotes[-len(bbands):]

times, clusters = cl.clusterCandles(normquotes, nclusters=5, ncandles=3)

colors = list("rbgkcmyw") # only allows up to 8
clustershading = []
for i, day in enumerate(times):
    clustershading.append([ day, colors[clusters[i]] ])

crossovershading = []
for day, rising in ind.crossovertimes(emas):
    crossovershading.append([day, 'g' if rising else 'r'])

u.makeCandlestick(quotes, "../plots/candlestick.png", title="WMT (2009)", \
        shadings=[clustershading,crossovershading], \
        bbands=bbands, \
        window=[d1,d2], \
        averages=emas, \
        rsis=rsis, \
        )
u.web("../plots/candlestick.png")
