import numpy as np
from pprint import pprint

import backtestBenchmark as btbm
import utils as u
import indicators as ind

def bbstrat(quotes, params={}):
    # define a function that takes a quotes object, so it is an array with elements [day,o,h,l,c]
    # and returns a dictionary with keys of buy and sell times
    # values are not used (1 here), so that gives us room to pack in more information with this function

    timesclose = quotes[:,[0,4]]
    timesclose = np.array(timesclose)
    bbands = ind.bbtimes(timesclose, 20)
    quotes = np.array(quotes[-len(bbands):])

    dBuy = { }
    dSell = { }

    previous = 0
    price = 0
    position = False
    for quote, band in zip(quotes, bbands):
        last_quote = quote[1]
        if position == True:
            if quote[1] > 1.20*price or band[6] > 0.7 or quote[1] < 0.93*price or band[6] < -0.03:
                position = False
                dSell[quote[0]] = 1
        else:
            if band[6] > 0.06 and previous < 0.06:
                position = True
                dBuy[quote[0]] = 1
                price = quote[1]
                
        previous = band[6]

    return dBuy, dSell

#symbols = ["NFLX", "WMT"]
symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()]
symbols = symbols[:100]
d1, d2 = (2013, 6, 1), (2015, 6, 1)

bt = btbm.Backtest(symbols, d1, d2, bbstrat, money=1000.0, filename="test.txt")
bt.doBenchmark()
#pprint(bt.getReport())
