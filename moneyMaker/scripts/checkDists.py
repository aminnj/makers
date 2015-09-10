import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.finance as mf

import os, sys
import getStocks as gs

plotdir = "../plots/"

def web(filename):
    os.system("scp %s/%s namin@uaf-6.t2.ucsd.edu:~/public_html/dump/" % (plotdir, filename))
    print "Copied to uaf-6.t2.ucsd.edu/~namin/dump/%s" % filename

def makeHist(vals, filename, title=None, nbins=50):
    if not title: title = ".".join(filename.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    ax.hist(vals,nbins,color='green',alpha=0.8)
    fig.savefig("%s/%s" % (plotdir, filename), bbox_inches='tight')
    print "Saved hist %s" % filename
    # web(filename)

    
def makeCandlestick(stock, filename, title=None):
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    # fig.subplots_adjust(bottom=0.2)
    quotes = []
    for day in stock["days"].keys():
        vals = stock["days"][day]
        o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]
        quotes.append( [day, o,h,l,c] )



    mondays = md.WeekdayLocator(md.MONDAY)        # major ticks on the mondays
    alldays = md.DayLocator()              # minor ticks on the days
    weekFormatter = md.DateFormatter('%b %d')  # e.g., Jan 12
    dayFormatter = md.DateFormatter('%d')      # e.g., 12
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)

    mf.candlestick_ohlc(ax, quotes, width=0.6)

    ax.xaxis_date()
    ax.autoscale_view()

    fig.savefig("%s/%s" % (plotdir, filename), bbox_inches='tight')

    # web(filename)


# stock = gs.getStock("AAPL", 2005, 2010)
stock = gs.getStock("DIS", (2009, 8, 15), (2009, 9, 15))
print len(stock["days"].keys())

prices = []
fractions = []
for day in stock["days"].keys():
    vals = stock["days"][day]
    o, h, l, c = vals["o"], vals["h"], vals["l"], vals["c"]
    prices.append( [o,h,l,c] )
    # fractions.append( abs(o-c)/(h-l) ) # what fraction of (high-low) is |open-close|?
    fractions.append( ((o+c)/2 - l)/(h-l) ) # how far from the low is the center of the body?


prices = np.array(prices)

# makeHist(prices[:,0], "openhist.png")
makeHist(fractions, "fractions.png", title="|o-c|/(h-l)", nbins=50)
makeCandlestick(stock, "candlestick.png")


