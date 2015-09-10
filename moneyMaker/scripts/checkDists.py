import os, sys
import getStocks as gs
import utils as u

plotdir = "../plots/"

# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("DIS", (2009, 8, 20), (2009, 10, 7))["days"]

prices = []
fractions = []
for day in stock.keys():
    vals = stock[day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]
    prices.append( [o,h,l,c] )
    # fractions.append( abs(o-c)/(h-l) ) # what fraction of (high-low) is |open-close|?
    fractions.append( ((o+c)/2 - l)/(h-l) ) # how far from the low is the center of the body?

# prices = np.array(prices)
# makeHist(prices[:,0], "openhist.png")

u.makeHist(fractions, "../plots/fractions.png", title="|o-c|/(h-l)", nbins=50)
u.makeCandlestick(stock, "../plots/candlestick.png")


