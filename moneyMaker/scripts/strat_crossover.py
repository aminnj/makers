import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind
import tradeReport as tr
import random

plotdir = "../plots/"

#symbol = "WMT"
symbol = "NFLX"
# symbol = "F"
stock = gs.getStock(symbol, (2011, 6, 1), (2015, 6, 1))["days"] # for calculating
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
quotes = np.array(quotes[-len(bbands):])

emas = []
for i in [1,8]:
    emas.append( ind.ematimes(timesclose,10*i) )

crossovertimes = ind.crossovertimes(emas)
# turn into dict for fast lookup
dCrossovers = {}
for time,rising in crossovertimes:
    dCrossovers[time] = rising

money = 1000.0
ledger = []
shares = 0

lastprice = 0
for quote in quotes:
    day,o,h,l,c = quote
    price = o
    lastprice = price
    if(day in dCrossovers): 
        rising = dCrossovers[day]

        if(rising): # buy
            nshares = money//price
            ledger.append([symbol,  nshares, price])
            money -= nshares*price
            shares += nshares

        else: # sell
            nshares = shares
            ledger.append([symbol, -nshares, price])
            money += nshares*price
            shares -= nshares
        
# sell outstanding shares to finish up
ledger.append([symbol, -shares, lastprice])
print tr.tradeReport(ledger)
