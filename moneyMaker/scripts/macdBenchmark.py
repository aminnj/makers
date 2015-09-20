import numpy as np
from pprint import pprint
import itertools

import backtestBenchmark as btbm
import utils as u
import indicators as ind

def macd(quotes, d1, d2, params = {}):
    # define a function that takes a quotes object, so it is an array with elements [day,o,h,l,c]
    # and returns a dictionary with keys of buy and sell times
    # values are not used (1 here), so that gives us room to pack in more information with this function

    timesclose = quotes[:,[0,4]]
    macdhisttimes = ind.macdhisttimes(timesclose, 12, 26, 9)
    dmacdhisttimes = {} # turn into dict for fast lookup
    for time,value in macdhisttimes: dmacdhisttimes[time] = value
    dBuy = { }
    dSell = { }

    hasBought = False
    boughtPrice = -1.0
    for i,day in enumerate(quotes[:,0]):
        if(day in dmacdhisttimes and quotes[i-1][0] in dmacdhisttimes): 
            value = dmacdhisttimes[day]
            previous_value = dmacdhisttimes[quotes[i-1][0]]
            if(hasBought):
                if(value > 0 and value < 0.9*previous_value):
                    dSell[day] = 1
                    hasBought = False
                elif(quotes[i][4] < 0.97*boughtPrice):
                    dSell[day] = 1
                    hasBought = False
                elif(quotes[i][4] > 1.25*boughtPrice):
                    dSell[day] = 1
                    hasBought = False
            else:
                if(value < 0 and value > previous_value):
                    dBuy[day] = 1
                    hasBought = True
                    boughtPrice = quotes[i][4]

    return dBuy, dSell

symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()]
symbols = symbols[:100]
d0, d1, d2 = (2013, 5, 15), (2014, 1, 15), (2015, 9, 15)
            

bt = btbm.Backtest(symbols, d0, d1, d2, macd, money=1000.0, filename="test.txt")
#bt.doScan(params, filename="test_scan.txt")
bt.doBenchmark( progressBar=False, params={} )
pprint(bt.getReport())
