import numpy as np
from pprint import pprint
import itertools

import backtestBenchmark as btbm
import utils as u
import indicators as ind
import getStocks as gs

def crossover(quotes):

    timesclose = quotes[:,[0,4]]

    emas = [ ind.ematimes(timesclose,i) for i in [5, 10] ]
    crossovertimes = ind.crossovertimes(emas)
    dCrossovers = {} # turn into dict for fast lookup
    for time,rising in crossovertimes: dCrossovers[time] = rising
    dBuy = { }

    hasBought = False
    boughtPrice = -1.0
    for i,day in enumerate(quotes[:,0]):
        #print day
        if(day in dCrossovers): 
            rising = dCrossovers[day]
            if(rising):
                dBuy[day] = 1
                hasBought = True
                boughtPrice = quotes[i][4]

    return dBuy

symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:1000]

for symbol in symbols:
    stock = gs.getStock(symbol, (2015, 8, 1), (2015, 9, 16))
    quotes = u.dictToList(stock) # [day,o,h,l,c]
    array_quotes = np.array(quotes)
    if(len(quotes) < 25): continue
    if np.mean(quotes[:,4]) > 20: continue
    buys = crossover(quotes)
    if 735856.0 in buys: print symbol
