import time, datetime
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.finance as mf
from matplotlib.dates import date2num, num2date
from matplotlib.cbook import iterable

### TIME MANIPULATIONS ###
def date2inum(dt):
    # takes datetime object
    # return #days+1 since 01-01-01
    return int(date2num(dt))
def tuple2inum(dt):
    # takes (y,m,d) tuple
    # return #days+1 since 01-01-01
    dt = datetime.datetime(*dt)
    return int(date2num(dt))
def inum2date(dt):
    # takes #days+1 since 01-01-01
    # return datetime object
    return int(num2date(dt))

### PLOTTING ###
def web(filename,user="namin"):
    os.system("scp %s %s@uaf-6.t2.ucsd.edu:~/public_html/dump/" % (filename, user))
    print "Copied to uaf-6.t2.ucsd.edu/~%s/dump/%s" % (filename, user)

def makeHist(vals, filename, title=None, nbins=50):
    if not title:
        title = filename.split("/")[-1]
        title = ".".join(title.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    ax.hist(vals,nbins,color='green',alpha=0.8)
    fig.savefig("%s" % (filename), bbox_inches='tight')
    print "Saved hist %s" % filename

def makeCandlestick(quotes, filename, title=None, shading={}):
    # each element of quotes is [day, open, high, low, close]
    if not title:
        title = filename.split("/")[-1]
        title = ".".join(title.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    fig.subplots_adjust(bottom=0.2)

    mondays = md.WeekdayLocator(md.MONDAY)    # major ticks on the mondays
    alldays = md.DayLocator()                 # minor ticks on the days
    weekFormatter = md.DateFormatter('%b %d') # e.g., Jan 12
    dayFormatter = md.DateFormatter('%d')     # e.g., 12
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    mf.candlestick_ohlc(ax, quotes, width=0.6)
    ax.xaxis_date()
    ax.autoscale_view()

    if(shading):
        # keys are the days, vals are the shade color
        for day in shading.keys():
            plt.axvspan(day-0.5,day+0.5, color=shading[day], alpha=0.2,lw=0)


    fig.savefig("%s" % (filename), bbox_inches='tight')
