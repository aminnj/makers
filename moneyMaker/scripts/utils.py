import time, datetime, os
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
    return num2date(dt)
def inum2tuple(dt):
    # takes #days+1 since 01-01-01
    # return (y,m,d) tuple
    dt = inum2date(dt)
    return (dt.year, dt.month, dt.day)

### PLOTTING ###
def web(filename,user="namin"):
    os.system("scp %s %s@uaf-6.t2.ucsd.edu:~/public_html/dump/" % (filename, user))
    print "Copied to uaf-6.t2.ucsd.edu/~%s/dump/%s" % (user, filename.split("/")[-1])

def makeHist(vals, filename, title=None, nbins=50):
    # vals is a 1d array of values
    if not title:
        title = filename.split("/")[-1]
        title = ".".join(title.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    ax.hist(vals,nbins,color='green',alpha=0.8)
    fig.savefig("%s" % (filename), bbox_inches='tight')
    print "Saved hist %s" % filename

def makePlot(vx, vy, filename, title=None):
    # vx, vy are 1D arrays of x,y vals
    if not title:
        title = filename.split("/")[-1]
        title = ".".join(title.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    ax.plot(vx,vy,'r',lw=2,alpha=0.8)
    fig.savefig("%s" % (filename), bbox_inches='tight')
    print "Saved plot %s" % filename

def keepIfBetween(vals, tuple1, tuple2, idx=0):
    # return the elements in vals for which the date (val[idx]) is in specified range
    day1, day2 = tuple2inum(tuple1), tuple2inum(tuple2)

    # ndarray
    if(type(vals) is np.ndarray): return vals[ (day1 <= vals[:,0]) & (vals[:,0] <= day2) ]

    # list
    return [val for val in vals if day1 <= val[0] <= day2]


def makeCandlestick(quotes, filename, title=None, shadings=None, bbands=None, window=None, averages=None):
    if window:
        quotes = keepIfBetween(quotes, window[0], window[1])
        if shadings is not None: shadings = [keepIfBetween(shading, window[0], window[1]) for shading in shadings]
        if bbands is not None: bbands = keepIfBetween(bbands, window[0], window[1])
        if averages is not None: averages = [keepIfBetween(avg, window[0], window[1]) for avg in averages]

    # each element of quotes is [day, open, high, low, close]
    if not title:
        title = filename.split("/")[-1]
        title = ".".join(title.split(".")[:-1])

    fig, ax = plt.subplots( nrows=1, ncols=1 , figsize=(12,8) )  # create figure & 1 axis
    fig.suptitle(title, fontsize=20)
    fig.subplots_adjust(bottom=0.2)

    # mondays = md.WeekdayLocator(md.MONDAY)    # major ticks on the mondays
    # alldays = md.DayLocator()                 # minor ticks on the days
    # weekFormatter = md.DateFormatter('%b %d') # e.g., Jan 12
    # dayFormatter = md.DateFormatter('%d')     # e.g., 12
    # ax.xaxis.set_major_locator(mondays)
    # ax.xaxis.set_minor_locator(alldays)
    # ax.xaxis.set_major_formatter(weekFormatter)
    mf.candlestick_ohlc(ax, quotes, width=0.6)

    ax.xaxis_date()
    ax.autoscale_view()

    ax.xaxis.set_major_formatter(md.DateFormatter("%d %b"))
    fig.autofmt_xdate()

    if shadings is not None:
        for i,shading in enumerate(shadings):
            for j in range(len(shading)):
                dayleft = shading[j][0]
                if(j == len(shading)-1): dayright = dayleft+1
                else: dayright = shading[j+1][0]

                # bottom 90% for shading 1
                if(i == 0):
                    plt.axvspan(dayleft-0.5,dayright-0.5, 0.0,0.9, color=shading[j][1], alpha=0.35,lw=0)
                elif(i == 1):
                    plt.axvspan(dayleft-0.5,dayright-0.5, 0.9,1.0, color=shading[j][1], alpha=0.35,lw=0)
                else:
                    pass
    
    if bbands is not None:
        ax.plot(bbands[:,0],bbands[:,1],'r',lw=1,alpha=0.7) # upper
        ax.plot(bbands[:,0],bbands[:,2],'k--',lw=1,alpha=0.5) # middle
        ax.plot(bbands[:,0],bbands[:,3],'r',lw=1,alpha=0.7) # lower

    if averages is not None:
        for i,avg in enumerate(averages):
            # ax.plot(avg[:,0],avg[:,1],color=(0.1*i,0,0.4+0.08*i),lw=1,alpha=0.7) # upper
            ax.plot(avg[:,0],avg[:,1],color=(1.0,1.0-0.1*i,0.0),lw=1,alpha=0.7) # upper

    fig.savefig("%s" % (filename), bbox_inches='tight')
