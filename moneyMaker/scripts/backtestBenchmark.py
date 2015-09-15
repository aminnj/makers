import os, sys, random, json, itertools

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

    def drawProgressBar(self):
        width = 40
        fraction = 1.0*self.isymbol/self.nsymbols
        if(fraction > 1): fraction = 1
        if(fraction < 0): fraction = 0
        filled = int(round(fraction*width))
        print "\r[{0}{1}]".format("#" * filled, "-" * (width-filled)),
        print "%d%%" % (round(fraction*100)),
        sys.stdout.flush()

    def performChecks(self):
        if(self.money < 1.0):
            print "[BT] Give me more money than that"
            return 1
        if(self.nsymbols < 1):
            print "[BT] Give me at least one symbol"
            return 1

        return 0

    def cleanVars(self):
        self.isymbol = 0
        self.report = { }

    def postBenchmark(self):
        # dump report to file for later analysis
        fh = open(self.filename,"w")
        fh.write( json.dumps(self.report) )
        fh.close()

    def doScan(self, paramsAndRanges, filename="test_scan.txt"):
        pass
        # each key in paramsAndRanges is a parameter (ROOT syntax): "p0","p1", etc.
        # each value is a list of values for that parameter
        # e.g., paramsAndRanges["p0"] = [0.1,0.2,0.9,1.0]
        
        fhscan = open(filename, "w")

        keys = sorted(paramsAndRanges.keys())
        keyString = "(%s)" % ", ".join(keys)
        vals = tuple([paramsAndRanges[key] for key in keys])
        combinations = list(itertools.product(*vals))
        combinationResults = { }
        for combination in combinations:
            valString = "(%s)" % ", ".join(map(str,combination))
            params =  { keys[i]: combination[i] for i in range(len(keys)) }
            self.doBenchmark(params, progressBar=False, userOnly=True)
            profit = np.mean([self.report[sym]["user"][0] for sym in self.report.keys()])
            ntrades = np.mean([self.report[sym]["user"][2] for sym in self.report.keys()])
            # ntrades = self.report["user"][2]
            fhscan.write("%s = %s: %.2f,%i\n" % (keyString, valString, profit, ntrades) )
            print "%s = %s: %.2f,%i" % (keyString, valString, profit, ntrades)
            combinationResults[combination] = [ profit, ntrades ]

        maxprofit, winningCombination, winningResult = -1, -1, -1
        for res in combinationResults.keys():
            if(combinationResults[res][0] > maxprofit):
                maxprofit = combinationResults[res][0]
                winningCombination = res
                winningResult = combinationResults[res]

        winningString = "%s = (%s) with profit = %.2f and ntrades = %i" % (keyString, ", ".join(map(str,winningCombination)), winningResult[0], winningResult[1])
        fhscan.write("# WINNER:\n%s\n" %  winningString)
        fhscan.close()
        print "WINNER:", winningString


    def doBenchmark(self, params={}, progressBar=True, userOnly=False):
        self.cleanVars()

        if self.performChecks():
            print "[BT] Can't benchmark"
            return

        for isymbol,symbol in enumerate(self.symbols):
            self.isymbol = isymbol
            if(progressBar): self.drawProgressBar()

            stock = gs.getStock(symbol,self.d1,self.d2)
            quotes = u.dictToList(stock) # [day,o,h,l,c]
            if(len(quotes) < 25): continue

            try:
                dBuy, dSell = self.strategy(quotes, params)
            except Exception as e:
                print "[BT] Problem running user strategy"
                print e
                continue

            if(len(dBuy.keys()) < 1): continue # pointless if we don't buy
            if(len(dSell.keys()) < 1): continue # pointless if we don't sell -- then it's just BAH

            try:
                self.report[symbol] = { }
                self.report[symbol]["ndays"] = len(quotes)

                # USER STRATEGY
                price = 0
                ledger = tr.Ledger(self.money)
                for quote in quotes:
                    day,price,h,l,c = quote
                    if(day in dBuy): ledger.buyStock(symbol, price)
                    elif(day in dSell): ledger.sellStock(symbol,price)
                ledger.sellStock(symbol, price) # sell outstanding shares to finish up
                self.report[symbol]["user"] = [ledger.getProfit(), 0.0, ledger.getNumTrades()]

                if(not userOnly): 
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

                    self.report[symbol]["rand"] = [round(np.mean(profits),2), round(np.std(profits)), ledgerRand.getNumTrades()]
                    self.report[symbol]["bah"] = [ledgerBAH.getProfit(), 0.0,  ledgerBAH.getNumTrades()]
            except:
                print "[BT] Some other error"
                continue

        self.postBenchmark()


