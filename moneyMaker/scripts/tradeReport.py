import numpy as np
import utils as u

def tradeReport(ledger):
    """
    ledger is a list where each entry is [symbol, shares, price]
    shares > 0 is a buy, shares < 0 is a sell
    example ledger = [ ["AAPL", 2, 100.00], ["AAPL", -2, 105.32] ]
    """

    sumProfit = {}
    sumShares = {}
    print ''
    print 'list of trades'
    print 'symbol', 'shares', 'price'
    for entry in ledger:
        symbol = entry[0]
        shares = entry[1]
        price = entry[2]
        print symbol, " ", shares, " ", price
        if not sumProfit.has_key(symbol):
            sumProfit[symbol] = 0.0
            sumShares[symbol] = 0
        sumProfit[symbol] += shares * price * -1.0
        sumShares[symbol] += shares

    print ''
    print 'summary for closed trades'
    print 'symbol', ': ', 'profit'
    for symbol, profit in sumProfit.iteritems():
            if sumShares[symbol] == 0: 
              print symbol, ': ', profit

    print ''
    print 'outstanding shares'
    print 'symbol', ': ', 'shares'
    for symbol, shares in sumShares.iteritems():
        if shares != 0:
              print symbol, ': ', shares


class Ledger:
    def __init__(self, money):
        self.money = float(money)
        self.trades = []
        self.assets = {}
        self.profit = 0.0

    def getTrades(self): return self.trades
    def getAssets(self): return self.assets
    def getMoney(self): return self.money
    def getNumTrades(self): return len(self.trades)
    def getProfit(self): 
        self.profitReport(False)
        return round(self.profit,2)

    def getWinPercent(self):
        buys = self.trades[::2]
        sells = self.trades[1::2]
        numWins = 0
        for buy,sell in zip(buys, sells): 
            if buy[1] <= sell[1]: numWins += 1
        return int(100*2*numWins/float(len(self.trades)))

    def getAvgWinProfitPercent(self):
        buys = self.trades[::2]
        sells = self.trades[1::2]
        numWins = 0
        winProfit = 0
        for buy,sell in zip(buys, sells): 
            if buy[1] <= sell[1]:
                numWins += 1
                winProfit += float(sell[1] - buy[1])/float(buy[1])
        if numWins > 0: return round(100*winProfit/float(numWins),1)
        else: return 0
    def getAvgLossProfitPercent(self):
        buys = self.trades[::2]
        sells = self.trades[1::2]
        numLosses = 0
        lossProfit = 0
        for buy,sell in zip(buys, sells): 
            if buy[1] > sell[1]:
                numLosses += 1
                lossProfit += float(sell[1] - buy[1])/float(buy[1])
        if numLosses > 0: return round(100*lossProfit/float(numLosses),1)
        else: return 0

    def buyStock(self, ticker, time, price=None, amount=None):
        if(price is None):
            print "[Ledger] Please specify price for %s" % ticker
            return

        if(amount is None):  # buy as much as possible if unspecified
            amount = int(self.money / price)
        elif(amount*price > self.money):  # buy as much as possible if not rich enough
            amount = int(self.money / price)

        if(amount == 0): return

        if(ticker not in self.assets): self.assets[ticker] = 0

        self.trades.append( [ ticker, price, amount, time ] )
        self.assets[ticker] += amount
        self.money -= price*amount

    def sellStock(self, ticker, time, price=None, amount=None, fraction=1.0):
        if(price is None):
            print "[Ledger] Please specify price for %s" % ticker
            return

        if(ticker not in self.assets):
            self.assets[ticker] = 0
            return

        if(amount is None):  # sell as much as possible if unspecified
            amount = self.assets[ticker]

        amount = min(amount, self.assets[ticker]) # only sell what we have
        amount = int(fraction*amount)

        self.trades.append( [ ticker, price, -amount, time ] )
        self.assets[ticker] -= amount
        self.money += price*amount

    def cleanup(self):
        # delete assets which we don't possess anymore (nstocks == 0)
        for ass in self.assets.keys():
            if self.assets[ass] == 0: del self.assets[ass]

    def profitReport(self, printouts=True):
        d = { }
        totalProfit = 0.0
        for ticker, price, amount, day in self.trades:
            if ticker not in d: d[ticker] = [0, 0.0] # num trades, profit

            d[ticker][0] += 1
            d[ticker][1] -= price*amount
            totalProfit -= price*amount

        self.profit = totalProfit

        if not printouts: return

        print "Total profit: $%.2f" % totalProfit
        print "-"*25
        for ticker in d.keys():
            print "Got $%.2f from %i trades of %s" % (d[ticker][1], d[ticker][0], ticker)
        print
                
    def printLedger(self,showTrades=True):
        self.cleanup()
        print "-"*25
        print "Money remaining: %.2f" % self.money
        print "-"*25
        if(showTrades):
            for t in self.trades:
                date = ", ".join(map(str,list(u.inum2tuple(t[3]))))
                print "[%s] %-4s %i stocks of %s @ $%.2f" % (date,"BUY" if t[2]>0 else "SELL", abs(t[2]), t[0], t[1])
            print "-"*25

        for ass in self.assets.keys():
            print "Have %i stocks of %s" % (self.assets[ass], ass)
        print

if __name__=='__main__':
    l1 = Ledger(1000) # start out with 1 grand
    l1.buyStock("AAPL", 1, price=100) # if you don't specify an amount, it uses the rest of your money
    l1.sellStock("AAPL", 2, price=50,amount=20)

    l1.buyStock("F", 3, price=20,amount=5)
    l1.sellStock("F", 4, price=25) # same with selling...sells all possessed stocks

    l1.buyStock("INTC", 5, price=20)
    l1.sellStock("INTC", 6, price=18)

    l1.printLedger()

    l1.profitReport()
    print l1.getProfit() # if you want to retrieve the profit as a number. also note the other get commands
    print l1.getWinPercent()
    print l1.getAvgWinProfitPercent()
    print l1.getAvgLossProfitPercent()

