import os, sys

import numpy as np
import sklearn.cluster as skc

import getStocks as gs
import utils as u
import indicators as ind

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("DIS", (2008, 6, 20), (2010, 10, 7))["days"]

quotes = []
normquotes = []
fractions = []
close = []
for day in stock.keys():
    vals = stock[day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]

    # "normalize" values (subtract out open price)
    no = round(o-o,2)
    nh = round(h-o,2)
    nl = round(l-o,2)
    nc = round(c-o,2)

    quotes.append( [day,o,h,l,c] )
    normquotes.append( [day,no,nh,nl,nc] )
    # fractions.append( abs(o-c)/(h-l) ) # what fraction of (high-low) is |open-close|?
    fractions.append( ((o+c)/2 - l)/(h-l) ) # how far from the low is the center of the body?
    close.append(c)

# makeHist(prices[:,0], "openhist.png")

u.makeHist(fractions, "../plots/fractions.png", title="|o-c|/(h-l)", nbins=50)

close = np.array(close)
bbands = ind.bb(close, 14)
u.makeHist(bbands[:,0], "../plots/bbands_upper.png", title="Bollinger Bands", nbins=50)
u.makeHist(bbands[:,2], "../plots/bbands_lower.png", title="Bollinger Bands", nbins=50)

normquotes = np.array(normquotes)
quotes = np.array(quotes)

km = skc.KMeans(n_clusters=5)
clusters = km.fit_predict( normquotes[:,[1,2,3,4]] )

shading = []
colors = list("krbgcmyw") # only allows up to 8 colors :(

for i,day in enumerate(quotes[:,0]):
    shading.append([ day, colors[clusters[i]] ])




u.makeCandlestick(quotes, "../plots/candlestick.png", shading=shading, window=[(2009,7,10),(2009,8,10)])

