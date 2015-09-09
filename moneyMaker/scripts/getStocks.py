import urllib2, time, datetime
import pickle, gzip

storageDir = "../data/"

def saveStock(stock, yearStart, yearEnd):
    pickleFile = "%s/%s.pklz" % (storageDir, stock)

    dOld = { }
    alreadyExists = False

    # try to open an already existing pickle file for this stock
    try:
        fh = gzip.open(pickleFile, "rb")
        dOld = pickle.load(fh)
        fh.close()
        alreadyExists = True
    except:
        print "[MM] %s: No existing data file. Making one now." % stock

    # check to see if the requested dates are already within datafile, to reduce API calls
    if(alreadyExists):
        # move firstDay back 4 days and lastDay up 4 days to account for weekends and holidays
        firstDay = datetime.date(yearStart,1,1)+datetime.timedelta(days=3)
        lastDay = datetime.date(yearEnd,12,31)-datetime.timedelta(days=3)
        timeFirstDay = time.mktime(firstDay.timetuple())
        timeLastDay = time.mktime(lastDay.timetuple())

        if ( timeFirstDay > dOld["firstTime"] and timeLastDay < dOld["lastTime"] ):
            print "[MM] %s: Already saved specified time period (%i-%i)." % (stock, yearStart, yearEnd)
            return




    # start on Jan 1st of yearStart, end on Dec 31st of yearEnd
    url="http://ichart.yahoo.com/table.csv?s=%s&a=0&b=1&c=%i&d=11&e=31&f=%i&g=d&ignore=.csv" % (stock,yearStart,yearEnd)
    try:
        csv = urllib2.urlopen(url).read()
    except:
        print "[MM] %s: No data available for part of specified time period (%i-%i)." % (stock, yearStart, yearEnd)
        return

    lines = csv.split()[2:] # first 2 lines are just the column names 
    numDays = len(lines)

    d = {}

    d["stock"] = stock
    d["yearStart"] = yearStart
    d["yearEnd"] = yearEnd

    for i,line in enumerate(lines):
        line = line.strip()
        # print line
        date, openPrice, highPrice, lowPrice, closePrice, volume, adjustedClosePrice = line.split(",")
        openPrice = round(float(openPrice),2)
        closePrice = round(float(closePrice),2)
        highPrice = round(float(highPrice),2)
        lowPrice = round(float(lowPrice),2)
        adjustedClosePrice = round(float(adjustedClosePrice),2)
        volume = int(volume)
        date = time.strptime(date,"%Y-%m-%d") # looks like 2001-01-17
        unixtime = int(time.mktime(date))
        d[unixtime] = { 
                "open": openPrice,
                "high": highPrice,
                "low": lowPrice,
                "close": closePrice,
                "adjustedclose": adjustedClosePrice,
                "volume": volume
                }

        # save first and last times for this API call for range checking later
        if(i == numDays-1): d["firstTime"] = unixtime
        if(i == 0): d["lastTime"] = unixtime
        


    # if data already exists, then add the new dates to it
    if(alreadyExists):
        for date in d.keys():
            if( not( dOld["firstTime"] <= date <= dOld["lastTime"] ) ):
                dOld[date] = d[date]
    else: dOld = d

    fh = gzip.open(pickleFile, "wb")
    pickle.dump(dOld, fh)
    fh.close()

    print "[MM] %s: Successfully saved data for time period (%i-%i)." % (stock, yearStart, yearEnd)



# saveStock("AAPL", 2001, 2015)
# saveStock("AAPL", 2002, 2004)

