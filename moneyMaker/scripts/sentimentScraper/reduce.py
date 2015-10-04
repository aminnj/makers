# do some data reduction (Find the good stocks)
# in particular, we want to get rid of the -999s somehow
import numpy as np
from matplotlib.dates import date2num
import datetime

ticker = "YHOO"
filename = "data/sentiment_%s.txt" % ticker

def maxContiguousGood(v):
    goodIdx = 0
    for ie,e in enumerate(v):
        if e<-990.0:
            goodIdx = ie 
            break
    return goodIdx

# convert from yyyy-mm-dd to the inum that matplotlib likes
convertDate = lambda x: float(date2num(datetime.datetime(*map(int,x.split("-")))))
data = np.genfromtxt(filename, delimiter=",", converters={0: convertDate}, names=True)[::-1]

print data["date"]
for name in data.dtype.names:
    print name, maxContiguousGood(name)

print data["mp_sent"]
# print data[0]
# print data[:,0]
