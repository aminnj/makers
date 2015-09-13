import os, sys, random

import numpy as np
import getStocks as gs
import utils as u
import indicators as ind
import tradeReport as tr

#symbol = "WMT"
symbol = "NFLX"
# symbol = "F"
stock = gs.getStock(symbol, (2011, 6, 1), (2015, 6, 1)) # for calculating
quotes = u.dictToList(stock) # [day,o,h,l,c]

timesclose = quotes[:,[0,3]]
emas = []
for i in [1,2]: emas.append( ind.ematimes(timesclose,10*i) )

crossovertimes = ind.crossovertimes(emas)
dCrossovers = {} # turn into dict for fast lookup
for time,rising in crossovertimes: dCrossovers[time] = rising


# CROSSOVER STRATEGY
price = 0
ledger = tr.Ledger(1000)
for quote in quotes:
    day,price,h,l,c = quote
    if(day in dCrossovers): 
        rising = dCrossovers[day]

        if(rising): ledger.buyStock(symbol, price)
        else: ledger.sellStock(symbol,price)
        
ledger.sellStock(symbol, price) # sell outstanding shares to finish up
# ledger.printLedger()
print ledger.getProfit(), ledger.getNumTrades()


# RANDOM STRATEGY

profits = []
for i in range(100):
    price = 0
    ledgerRand = tr.Ledger(1000)
    days = quotes[:,0]
    np.random.shuffle(days)
    # want to do a random trade on avg every 3-10 days
    # so we take the first #days/rand(3,10) random days, then sort them
    days = sorted(days[:len(days)//random.randint(3,10)])
    days = days[len(days)%2:] # even number of entries, so we always sell what we buy
    buy = True # buy initially
    for day in days:
        if(buy): ledgerRand.buyStock(symbol, price=stock["days"][day]['c'])
        else: ledgerRand.sellStock(symbol, price=stock["days"][day]['c'])
        buy = not buy # alternate between buy and sell
    # print ledgerRand.getProfit(), ledgerRand.getNumTrades()
    profits.append( ledgerRand.getProfit() )

profits = np.array(profits)
print np.mean(profits), np.std(profits)



# BUY AND HOLD
ledgerBAH = tr.Ledger(1000) # buy and hold
ledgerBAH.buyStock(symbol,quotes[0][4])
ledgerBAH.sellStock(symbol,quotes[-1][4])
print ledgerBAH.getProfit(), ledgerBAH.getNumTrades()
