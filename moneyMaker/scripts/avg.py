import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("SNDK", (2008, 6, 20), (2015, 11, 7))["days"]
# stock = gs.getStock("SNDK", (2008, 6, 20), (2010, 10, 7))["days"]

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

emas = []
for i in range(1,9):
    emas.append( ind.ematimes(timesclose,10*i) )

# bbands discards early dates since it can't do a moving average for those
# we reshape the other arrays to match up with bbands' size
normquotes = np.array(normquotes[-len(bbands):])
quotes = np.array(quotes[-len(bbands):])

km = skc.KMeans(n_clusters=5)
# add more and more columns to data
# subtract out opening prices from bbands
data = np.c_[ normquotes[:,[1,2,3,4]] ]
data = np.c_[ data, bbands[:,1]-quotes[:,1] ]
data = np.c_[ data, bbands[:,2]-quotes[:,1] ]
data = np.c_[ data, bbands[:,3]-quotes[:,1] ]

clusters = km.fit_predict(data)
colors = list("rbgkcmywrbgkcmyw") # only allows up to 16 colors, but it repeats after 8

clustershading = []
for i,day in enumerate(quotes[:,0]): clustershading.append([ day, colors[clusters[i]] ])

# maxemalength = np.max([len(ema) for ema in emas])
# for ema in emas:
#     print maxemalength, len(ema)
#     zeros = np.array([0,0]*(maxemalength-len(ema)))
#     # np.append( zeros, ema )
#     padded = np.concatenate( zeros, ema )
#     # zeros = np.append( np.array([0 for e in range(maxemalength-len(ema))]), ema )
#     # test = zeros.extend(ema)
#     print padded
#     print len(padded)
#     # print len(ema)
#     # print ema[:,1]
# # crossovershading = []
# # for i,day in enumerate(emas[0][:,0]):
# #     print emas[j][:,1]

#     crossovershading.append([ day, "r" ])

# shortest first
emas = sorted(emas, key=lambda e: len(e))
mintimesteps = len(emas[0])
emacrossover = [[] for i in range(mintimesteps)]
for iema,ema in enumerate(emas):
    ema = ema[-mintimesteps:]
    for it in range(mintimesteps): emacrossover[it].append( ema[it] )

emacrossover = np.array(emacrossover)
# each element of emacrossover represents one day, meaning it is an array of (time,price) pairs for each EMA
# find out if the prices are increasing or decreasing between the EMAs for each day

crossover = [] # each element will be a pair (day, code) where code=1 for increasing, -1 for decreasing, or 0 otherwise
for dayinfo in emacrossover:
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

print crossovertimes

crossovershading = []
for day, rising in crossovertimes:
    if(rising):
        crossovershading.append([day,'g'])
    else:
        crossovershading.append([day,'r'])

u.makeCandlestick(quotes, "../plots/candlestick.png", title="SNDK (2009)", shadings=[clustershading,crossovershading], bbands=bbands, window=[(2009,2,10),(2015,9,15)], averages=emas)
# u.web("../plots/candlestick.png")

