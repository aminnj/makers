import os, sys, random, json

import numpy as np
import getStocks as gs
import utils as u
import indicators as ind
import tradeReport as tr

class Backtest:
    def __init__(self, symbols, d1, d2, strategy, money=1000.0, filename="temp.txt"):
        self.symbols = symbols
        self.isymbol = 0
        self.nsymbols = len(symbols)

        self.d1 = d1
        self.d2 = d2

        self.strategy = strategy
        self.money = money

        self.filename = filename

        self.report =  { }

        print "[BT] Initialized backtest with $%i over %i stocks between %s and %s" % \
                (self.money, self.nsymbols, u.tuple2string(d1), u.tuple2string(d2))

    def getSymbols(self): return self.symbols
    def getDates(self): return (self.d1, self.d2)
    def getReport(self): return self.report
    def getProgress(self): return 1.0*self.isymbol/self.nsymbols

    def performChecks(self):
        if(self.money < 1.0):
            print "[BT] Give me more money than that"
            return 1
        if(self.nsymbols < 1):
            print "[BT] Give me at least one symbol"
            return 1

        return 0

    def postBenchmark(self):
        # dump report to file for later analysis
        fh = open(self.filename,"w")
        fh.write( json.dumps(self.report) )
        fh.close()



    def doBenchmark(self):
        if self.performChecks():
            print "[BT] Can't benchmark"
            return

        for isymbol,symbol in enumerate(self.symbols):
            self.isymbol = isymbol

            stock = gs.getStock(symbol,self.d1,self.d2)
            quotes = u.dictToList(stock) # [day,o,h,l,c]
            if(len(quotes) < 10): continue

            dBuy, dSell = self.strategy(quotes)
            if(len(dBuy.keys()) < 1): continue # pointless if we don't buy
            if(len(dSell.keys()) < 1): continue # pointless if we don't sell -- then it's just BAH

            # USER STRATEGY
            price = 0
            ledger = tr.Ledger(self.money)
            for quote in quotes:
                day,price,h,l,c = quote
                if(day in dBuy): ledger.buyStock(symbol, price)
                elif(day in dSell): ledger.sellStock(symbol,price)
            ledger.sellStock(symbol, price) # sell outstanding shares to finish up

            # RANDOM STRATEGY
            profits = []
            for i in range(100):
                price = 0
                ledgerRand = tr.Ledger(self.money)
                days = quotes[:,0]
                np.random.shuffle(days)
                # want to do a random trade on avg every 3-10 days
                # so we take the first #days/rand(3,10) random days, then sort them
                days = sorted(days[:len(days)//random.randint(3,10)])
                days = days[len(days)%2:] # even number of entries, so we always sell what we buy
                buy = True # buy initially
                for day in days:
                    if(buy): ledgerRand.buyStock(symbol, price=stock["days"][day]['c'])
                    else: ledgerRand.sellStock(symbol, price=stock["days"][day]['c'])
                    buy = not buy # alternate between buy and sell
                profits.append( ledgerRand.getProfit() )
            profits = np.array(profits)

            # BUY AND HOLD
            ledgerBAH = tr.Ledger(self.money) # buy and hold
            ledgerBAH.buyStock(symbol,quotes[0][4])
            ledgerBAH.sellStock(symbol,quotes[-1][4])

            # fill report. do we want anything else here?
            # second element is the error...only applies to rand, but want to keep compatibility with others
            self.report[symbol] = { }
            self.report[symbol]["user"] = [ledger.getProfit(), 0.0, ledger.getNumTrades()]
            self.report[symbol]["rand"] = [round(np.mean(profits),2), round(np.std(profits)), ledgerRand.getNumTrades()]
            self.report[symbol]["bah"] = [ledgerBAH.getProfit(), 0.0,  ledgerBAH.getNumTrades()]
            self.report[symbol]["ndays"] = len(quotes)

        self.postBenchmark()


