import numpy as np
from pprint import pprint

import backtestBenchmark as btbm
import utils as u
import indicators as ind

def crossover(quotes):
    # define a function that takes a quotes object, so it is an array with elements [day,o,h,l,c]
    # and returns a dictionary with keys of buy and sell times
    # values are not used (1 here), so that gives us room to pack in more information with this function

    timesclose = quotes[:,[0,4]]
    emas = [ ind.ematimes(timesclose,10*i) for i in [1,2] ]
    crossovertimes = ind.crossovertimes(emas)
    dCrossovers = {} # turn into dict for fast lookup
    dBuy = { }
    dSell = { }

    for time,rising in crossovertimes:
        if(rising): dBuy[time] = 1
        else: dSell[time] = 1

    return dBuy, dSell

symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()]
symbols = ["NFLX", "WMT"]
d1, d2 = (2011, 6, 1), (2015, 6, 1)

bt = btbm.Backtest(symbols, d1, d2, crossover, money=1000.0, filename="test.txt")
bt.doBenchmark()
pprint(bt.getReport())
