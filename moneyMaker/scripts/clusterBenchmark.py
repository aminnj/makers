import numpy as np
from pprint import pprint
import itertools

import backtestBenchmark as btbm
import utils as u
import indicators as ind
import cluster as cl

def clusterMethod(quotes, params={}):
    timesclose = quotes[:,[0,4]]
    # p1, p2 = params["p1"], params["p2"]
    # p1, p2 = min(p1,p2), max(p1,p2)
    # if(p2 - p1 <= 1): return { }, { }

    nclusters=params["p0"]
    ncandles=params["p1"]
    # times, clusters, clusterCenters = cl.clusterCandles(quotes, nclusters=nclusters, ncandles=ncandles, loadFrom="test.txt")
    times, clusters, clusterCenters = cl.clusterCandles(quotes, nclusters=nclusters, ncandles=ncandles) #  re-train everytime. slow?

    clustersAndProfits = cl.clustersAndTheirNextProfits(clusters,clusterCenters)
    dBuy = {}
    dSell = {}
    for i,clusterIdx in enumerate(clusters[:-2]):
        profit = clustersAndProfits[clusterIdx]

        if(profit > params["p2"]):
            dBuy[times[i+1]] = 1
            dSell[times[i+2]] = 1

    return dBuy, dSell

# symbols = [line.strip() for line in open("../data/nasdaqlisted.txt").readlines()][:4]
d1, d2 = (2005, 1, 15), (2014, 9, 14)

symbols = ["DIS", "AAPL", "WMT", "F", "BAC", "IBM" ]
# symbols = ["DIS"]
bt = btbm.Backtest(symbols, d1, d2, clusterMethod, money=1000.0, filename="test.txt")
params = { "p0" : [ 5, 10, 15, 20, 50 ] , # nclusters
           "p1" : [ 2, 3, 4, 5, 10, 15 ] , # ncandles
           "p2" : [ 0.05, 0.1, 0.2, 0.4, 0.5 ] , # profit value
           }
bt.doScan(params, filename="test_scan.txt")

# bt.doBenchmark( progressBar=True, params={"p0": 0.95, "p1": 1} )
print
pprint(bt.getReport())
