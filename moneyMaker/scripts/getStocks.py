import urllib2, time, datetime
import pickle, gzip
from matplotlib.dates import date2num, num2date
from matplotlib.cbook import iterable

# conventions: d1, d2 are 3-tuples of year,month,day
#              dt1, dt2, are datetime objects
#              day1, day2, are ints, given by #days+1 since 01-01-01
# => http://matplotlib.org/api/dates_api.html#matplotlib.dates.date2num

storageDir = "../data/"

def date2inum(dt): return int(date2num(dt))

def saveStock(ticker, d1, d2):
    ticker = ticker.upper()
    pickleFile = "%s/%s.pklz" % (storageDir, ticker)


    if iterable(d1): d1 = (d1[0], d1[1], d1[2])
    else: d1 = (d1.year, d1.month, d1.day)

    if iterable(d2): d2 = (d2[0], d2[1], d2[2])
    else: d2 = (d2.year, d2.month, d2.day)

    dOld = { }
    alreadyExists = False

    # try to open an already existing pickle file for this ticker
    try:
        fh = gzip.open(pickleFile, "rb")
        dOld = pickle.load(fh)
        fh.close()
        alreadyExists = True
    except:
        print "[MM] %s: No existing data file. Making one now." % ticker

    # check to see if the requested dates are already within datafile, to reduce API calls
    if(alreadyExists):
        # monday is 0, friday is 4
        dt1, dt2 = datetime.datetime(*d1), datetime.datetime(*d2)
        # print dt1, dt2, dt1.weekday(), dt2.weekday()
        # move d1 up to be monday
        if(dt1.weekday() > 4): dt1 += datetime.timedelta(days=7-dt1.weekday())
        if(dt2.weekday() > 4): dt2 -= datetime.timedelta(days=dt2.weekday()-4)

        
        d1new, d2new = date2inum(dt1), date2inum(dt2)

        # print dt1, dt2, dt1.weekday(), dt2.weekday()
        # print d1new, d2new, dOld["day1"], dOld["day2"]
        # print num2date(dOld["day1"])
        # print num2date(dOld["day1"]).weekday()

        if ( (d1new >= dOld["day1"]) and (d2new <= dOld["day2"]) ):
            print "[MM] %s: Already saved specified time period [(%i,%i,%i)-(%i,%i,%i)]." % (ticker, d1[0],d1[1],d1[2], d2[0],d2[1],d2[2])
            return

    urlFmt = 'http://ichart.yahoo.com/table.csv?a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&s=%s&y=0&g=%s&ignore=.csv'
    url = urlFmt % (d1[1]-1, d1[2], d1[0], d2[1]-1, d2[2], d2[0], ticker, 'd')

    try:
        csv = urllib2.urlopen(url).read()
    except:
        print "[MM] %s: No data available for part of specified time period [(%i,%i,%i)-(%i,%i,%i)]." % (ticker, d1[0],d1[1],d1[2], d2[0],d2[1],d2[2])
        return

    lines = csv.split()[2:] # first 2 lines are just the column names 
    numDays = len(lines)

    d = {}

    d["ticker"] = ticker
    minday, maxday = 9e7, 0
    for i,line in enumerate(lines):
        line = line.strip()
        dateString, openPrice, highPrice, lowPrice, closePrice, volume, adjClosePrice = line.split(",")
        openPrice,closePrice,highPrice,lowPrice,adjustedClosePrice = map(lambda x: round(float(x),2), (openPrice,closePrice,highPrice,lowPrice,adjClosePrice))
        volume = int(volume)
        date = datetime.datetime.strptime(dateString,"%Y-%m-%d") # looks like 2001-01-17
        day = date2inum(date)
        
        d[day] = { 
                "open": openPrice,
                "high": highPrice,
                "low": lowPrice,
                "close": closePrice,
                "adjustedclose": adjClosePrice,
                "volume": volume
                }

        # save first and last times for this API call for range checking later
        if(day <= minday):
            minday = day
            d["day1"] = day
            d["d1"] = date.timetuple()
        if(day >= maxday):
            maxday = day
            d["day2"] = day
            d["d2"] = date.timetuple()

    # if data already exists, then add only the new dates to it
    if(alreadyExists):
        for day in d.keys():
            if ( not (date2inum(datetime.datetime(*d1)) <= day <= date2inum(datetime.datetime(*d2))) ): dOld[day] = d[day]

        # stretch out the ranges when adding the new dates, if needed
        if(dOld["day1"] <= d["day1"]):
            d["day1"] = dOld["day1"]
            d["d1"] = dOld["d1"]
        if(dOld["day2"] <= d["day2"]):
            d["day2"] = dOld["day2"]
            d["d2"] = dOld["d2"]
    else: dOld = d

    fh = gzip.open(pickleFile, "wb")
    pickle.dump(dOld, fh)
    fh.close()

    d1, d2 = d["d1"], d["d2"]
    print "[MM] %s: Successfully saved data for time period [(%i,%i,%i)-(%i,%i,%i)]." % (ticker, d1[0],d1[1],d1[2], d2[0],d2[1],d2[2])

def getStock(ticker, d1, d2):
    saveStock(ticker, d1, d2)

    pickleFile = "%s/%s.pklz" % (storageDir, ticker)

    fh = gzip.open(pickleFile, "rb")
    dOld = pickle.load(fh)
    fh.close()

    day1, day2 = dOld["day1"], dOld["day2"]

    d = { }
    for day in dOld.keys():
        if( day1 <= day <= day2 ):
            d[day] = dOld[day]

    return d

# saveStock("INTC", (2005,1,11), (2015,2,17))
# getStock("INTC", (2006,1,8), (2006,2,8))

