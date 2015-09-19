import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind
import cluster as cl

plotdir = "../plots/"

stock = gs.getStock("F", (2010, 1, 1), (2011, 10, 5))["days"] # for calculating
d1,d2 = (2010,8,1),(2011,3,5) # for plotting

quotes = []
timesclose = []
for day in sorted(stock.keys()):
    vals = stock[day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]

    quotes.append( [day,o,h,l,c] )
    timesclose.append([day,c])

timesclose = np.array(timesclose)
bbands = ind.bbtimes(timesclose, 20)

emas = [ ind.ematimes(timesclose,i) for i in [5,10] ]

quotes = np.array(quotes)
rsis = ind.rsitimes(quotes[:,[0,1]],14)

# bbands discards early dates since it can't do a moving average for those
# we reshape the other arrays to match up with bbands' size
quotes = quotes[-len(bbands):]


nclusters=5
ncandles=10 # remember to change to "saveTo" below when you change these values
times, clusters, clusterCenters = cl.clusterCandles(quotes, nclusters=nclusters, ncandles=ncandles, loadFrom="test.txt")
clusterQuotes, vlines = cl.clusterCentersForPlotting(clusterCenters)

clustersAndProfits = cl.clustersAndTheirNextProfits(clusters,clusterCenters)
dBuy = {}
dSell = {}
for i,clusterIdx in enumerate(clusters[:-2]):
    profit = clustersAndProfits[clusterIdx]

    if(profit > 0.03):
        dBuy[times[i+1]] = 1
        dSell[times[i+2]] = 1

    

print clustersAndProfits
print dBuy, dSell



# colors = list("rbgkcmyw") # only allows up to 8
# clustershading = []
# for i, day in enumerate(times):
#     clustershading.append([ day, colors[clusters[i]] ])

crossovershading = []
for day, rising in ind.crossovertimes(emas):
    crossovershading.append([day, 'g' if rising else 'r'])


u.makeCandlestick(clusterQuotes, "../plots/candlestick.png",title="cluster centers",vlines=vlines)

# u.makeCandlestick(quotes, "../plots/candlestick.png", title="WMT (2009)", \
#         shadings=[clustershading,crossovershading], \
#         bbands=bbands, \
#         window=[d1,d2], \
#         averages=emas, \
#         rsis=rsis, \
#         )

# u.web("../plots/candlestick.png")
