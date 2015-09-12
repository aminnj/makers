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
#symbol = "NFLX"
symbol = "F"
stock = gs.getStock(symbol, (2014, 6, 1), (2015, 6, 1))["days"] # for calculating
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

previous = 0
position = False
money = 1000.00
shares = 0
price = 0.00
ledger = []
last_quote = 0
for quote, band in zip(quotes, bbands):
    last_quote = quote[1]
    if position == True:
        if quote[1] > 1.10*price or band[6] > 0.6 or quote[1] < 0.95*price or band[6] < -0.03:
            position = False
            money += shares*quote[1]
            ledger.append([symbol, shares*-1, quote[1]])
            shares = 0
    else:
        if band[6] > 0.05 and previous < 0.05:
            position = True
            price = quote[1]
            shares = int(money/price)
            money -= shares*price
            ledger.append([symbol, shares, quote[1]])
    previous = band[6]

if shares > 0:
    money += shares*last_quote
    ledger.append([symbol, shares*-1, last_quote])

tr.tradeReport(ledger)

#previous = 0
#position = False
#money = 1000.00
#shares = 0
#price = 0.00
#ledger = []
#last_quote = 0
#days = 0
#wait = 0
#for quote, band in zip(quotes, bbands):
#    last_quote = quote[1]
#    if position == True:
#            days += 1
#            if days >= wait:
#                pass
#                #position = False
#                #money += shares*quote[1]
#                #ledger.append([symbol, shares*-1, quote[1]])
#                #shares = 0
#    else:
#          position = True
#          price = quote[1]
#          shares = int(money/price)
#          money -= shares*price
#          ledger.append([symbol, shares, quote[1]])
#          wait = random.randrange(1,5)
#          days = 0
#    previous = band[6]
#
#if shares > 0:
#    money += shares*last_quote
#    ledger.append([symbol, shares*-1, last_quote])
#
#tr.tradeReport(ledger)
