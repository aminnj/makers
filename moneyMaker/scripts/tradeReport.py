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
