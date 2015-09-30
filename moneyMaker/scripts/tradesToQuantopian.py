import sys


fname = "trades_092915.txt"
if len(sys.argv) > 1: fname = sys.argv[-1]

fh = open(fname,"r")
lines = fh.readlines()
fh.close()

dDays = {}
for line in lines:
    line = line.strip()
    if ("#" in line): continue
    if (len(line) < 3): continue

    parts = line.split()
    ticker = parts[0]
    timeStr = parts[1]
    disc = float(parts[2])
    close = float(parts[3])

    if timeStr not in dDays:
        dDays[timeStr] = {}
        dDays[timeStr]["ticker"] = ticker
        dDays[timeStr]["disc"] = disc
    else:
        if disc >= dDays[timeStr]["disc"]:
            dDays[timeStr]["ticker"] = ticker
            dDays[timeStr]["disc"] = disc


# tickers = { dDays[day]['ticker'] for day in dDays } # set
# print tickers
# print len(tickers)

def sortFunc(v):
    # print sum([60**(2-ie) * int(e) for ie, e in enumerate(v.split("-"))])
    return sum([60**(2-ie) * int(e) for ie, e in enumerate(v.split("-"))])

def stupidDate(dt):
    year, month, day = dt.split("-")
    return "%s/%s/%s" % (month, day, year)


print "symbol,date,day,score"
for day in sorted(dDays, key=sortFunc):
    # print day, dDays[day]['ticker'], dDays[day]['disc']
    print "%s,%s,%s,%.3f" % (dDays[day]['ticker'], stupidDate(day), day, dDays[day]['disc'])
