import urllib2
import getStocks as gs


csv = urllib2.urlopen("ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt").read()
for line in csv.split("\n"):
    try:
        stock = line.split("|")[0]
        # print stock
        gs.saveStock(stock,2005,2015)
    except:
        continue


    

