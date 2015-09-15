import numpy as np
from pprint import pprint
import itertools

import backtestBenchmark as btbm
import utils as u
import indicators as ind

def crossover(quotes, params={}):
    # define a function that takes a quotes object, so it is an array with elements [day,o,h,l,c]
    # and returns a dictionary with keys of buy and sell times
    # values are not used (1 here), so that gives us room to pack in more information with this function

    timesclose = quotes[:,[0,4]]
    emas = [ ind.ematimes(timesclose,i) for i in [5, params["p1"] ] ]
    crossovertimes = ind.crossovertimes(emas)
    dCrossovers = {} # turn into dict for fast lookup
    for time,rising in crossovertimes: dCrossovers[time] = rising
    dBuy = { }
    dSell = { }

    hasBought = False
    boughtPrice = -1.0
    for i,day in enumerate(quotes[:,0]):
        if(day in dCrossovers): 
            rising = dCrossovers[day]
            if(rising):
                dBuy[day] = 1
                hasBought = True
                boughtPrice = quotes[i][4]
            else:
                if(hasBought): # don't sell if we already sold
                    dSell[day] = 1
                    hasBought = False

        # if price is 5% lower than what we bought for, get the hell out and sell
        if( hasBought and (0.0 < quotes[i][4] / boughtPrice < params["p0"]) ):
            dSell[day] = 1
            hasBought = False

    return dBuy, dSell

symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:1]
d1, d2 = (2014, 1, 15), (2015, 9, 14)

bt = btbm.Backtest(symbols, d1, d2, crossover, money=1000.0, filename="test.txt")
params = { "p0" : [ 0.95, 0.9 ] ,
           "p1" : [ 10, 12 ] ,
           "p2" : [ 10, 12 ] ,
           }
bt.doScan(params, filename="test_scan.txt")

# bt.doBenchmark( progressBar=False, params={"p0": 0.95, "p1": 10} )
# pprint(bt.getReport())
