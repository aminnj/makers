import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("DIS", (2009, 6, 20), (2009, 10, 7))["days"]

prices = []
days = []
fractions = []
for day in stock.keys():
    vals = stock[day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]

    days.append(day)
    prices.append( [o-o,h-o,l-o,c-o] )
    # fractions.append( abs(o-c)/(h-l) ) # what fraction of (high-low) is |open-close|?
    fractions.append( ((o+c)/2 - l)/(h-l) ) # how far from the low is the center of the body?

# makeHist(prices[:,0], "openhist.png")

u.makeHist(fractions, "../plots/fractions.png", title="|o-c|/(h-l)", nbins=50)



prices = np.array(prices)
# print prices
km = skc.KMeans(n_clusters=2)
clusters = km.fit_predict(prices)
print clusters
# print days

shading = {}
colors = list("bgrcmykw") # only allows up to 8 colors :(
# print colors
for i,day in enumerate(days):
    shading[day] = colors[clusters[i]]

# print shading




u.makeCandlestick(stock, "../plots/candlestick.png", shading=shading)

