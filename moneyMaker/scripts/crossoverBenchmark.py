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
    # p1, p2 = params["p1"], params["p2"]
    # p1, p2 = min(p1,p2), max(p1,p2)
    # if(p2 - p1 <= 1): return { }, { }

    emas = [ ind.ematimes(timesclose,i) for i in [5, 10] ]
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

        # if price is x% lower than what we bought for, get the hell out and sell a certain %
        if( hasBought and (0.0 < quotes[i][4] / boughtPrice < params["p0"]) ):
            dSell[day] = params["p1"]
            hasBought = False

    return dBuy, dSell

# symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:4]
d1, d2 = (2006, 1, 15), (2015, 9, 14)

# symbols = ["DIS", "AAPL", "WMT", "F", "BAC", "IBM" ]
symbols = ["DIS"]
bt = btbm.Backtest(symbols, d1, d2, crossover, money=1000.0, filename="test.txt")
params = { "p0" : [ 0.95, 0.8, 0.7, 0.3 ] ,
           "p1" : [ 0.1, 0.3, 0.5, 0.7, 0.9 ] ,
           # "p1" : [ 5, 10, 15, 20 ] ,
           # "p2" : [ 10, 15, 20, 30 ] ,
           }
# bt.doScan(params, filename="test_scan.txt")

bt.doBenchmark( progressBar=True, params={"p0": 0.95, "p1": 1} )
print
pprint(bt.getReport())
