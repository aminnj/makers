import urllib2, base64, json


username="sk_live_w3Q4bCJVB8xgyeIKJmTC4DS5"
password=""


def sortFunc(v): return sum([60**(2-ie) * int(e) for ie, e in enumerate(v.split("-"))])

def saveStock(ticker):
    startDate="01-01-2013"
    fnameout = "data/sentiment_%s.txt" % ticker
    url1="https://open.marketprophit.com/historical/daily-market-prophit-sentiment-chart-data?start_date=%s&ticker=%s" % (startDate,ticker)
    url2="https://open.marketprophit.com/historical/daily-crowd-sentiment-chart-data?start_date=%s&ticker=%s" % (startDate,ticker)

    data1 = None
    data2 = None

    # url 1
    request = urllib2.Request(url1)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)
    data1 = result.read()

    # url 2
    request = urllib2.Request(url2)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)
    data2 = result.read()

    d = {}

    # market prophit
    for dLine in json.loads(data1):
        ymd = dLine["ts"].split("T")[0]
        if(ymd not in d): d[ymd] = {}

        d[ymd]["mp_sent"] = dLine["mp_sentiment"]
        d[ymd]["mp_sent_z"] = dLine["mp_sentiment_z_score"]
        d[ymd]["mp_sent_ma"] = dLine["mp_sentiment_moving_average"]
        d[ymd]["mp_sent_zma"] = dLine["mp_sentiment_z_score_moving_average"]

    # crowd
    for dLine in json.loads(data2):
        ymd = dLine["ts"].split("T")[0]
        if(ymd not in d): d[ymd] = {}

        d[ymd]["crowd_sent"] = dLine["crowd_sentiment"]
        d[ymd]["crowd_sent_z"] = dLine["crowd_sentiment_z_score"]
        d[ymd]["crowd_sent_ma"] = dLine["crowd_sentiment_moving_average"]
        d[ymd]["crowd_sent_zma"] = dLine["crowd_sentiment_z_score_moving_average"]
        d[ymd]["volume"] = dLine["volume"]
        d[ymd]["buzz"] = dLine["buzz"]


    names = ["mp_sent","mp_sent_z","mp_sent_ma","mp_sent_zma","crowd_sent","crowd_sent_z","crowd_sent_ma","crowd_sent_zma","volume","buzz"]

    fh = open(fnameout,"w") 
    # print "# " + ",".join(names)
    fh.write("# date " + ",".join(names) + "\n")
    for ymd in sorted(d.keys(), key=sortFunc):
        lineStr = ""
        lineStr += "%s," % ymd
        for name in names:
            val = ""
            try: val = d[ymd][name].strip()
            except: pass

            if(len(val.strip()) < 1): val = "-999.0"

            lineStr += "%s," % val

        if(lineStr[-1]==","): lineStr = lineStr[:-1]

        # print lineStr
        fh.write( lineStr + "\n" )
    fh.close()




tickers = [line.strip() for line in open("../../data/goodstocks_vol.txt").readlines()]
ntickers = len(tickers)

# ticker = "AAPL"
for i,ticker in enumerate(tickers):
    print "[%s] %.1f%%" % (ticker, 100.0*i/ntickers)
    try: saveStock(ticker)
    except: print ">>>> ERROR WITH STOCK: ", ticker
