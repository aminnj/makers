import numpy as np

def roc(prices, period=21):
    """
    ROC = [(Close - Close n periods ago) / (Close n periods ago)] * 100
    Input:
      prices ndarray
      period int > 1 and < len(prices) (optional and defaults to 21)

    Output:
      rocs ndarray

    """

    num_prices = len(prices)

    if num_prices < period:
        # show error message
        raise SystemExit('Error: num_prices < period')

    roc_range = num_prices - period

    rocs = np.zeros(roc_range)

    for idx in range(roc_range):
        rocs[idx] = ((prices[idx + period] - prices[idx]) / prices[idx]) * 100

    return rocs


def rsi(prices, period=14):
    """
    Input:
      prices ndarray
      period int > 1 and < len(prices) (optional and defaults to 14)

    Output:
      rsis ndarray

    """

    num_prices = len(prices)

    if num_prices < period:
        # show error message
        raise SystemExit('Error: num_prices < period')

    # this could be named gains/losses to save time/memory in the future
    changes = prices[1:] - prices[:-1]
    #num_changes = len(changes)

    rsi_range = num_prices - period

    rsis = np.zeros(rsi_range)

    gains = np.array(changes)
    # assign 0 to all negative values
    masked_gains = gains < 0
    gains[masked_gains] = 0

    losses = np.array(changes)
    # assign 0 to all positive values
    masked_losses = losses > 0
    losses[masked_losses] = 0
    # convert all negatives into positives
    losses *= -1

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    if avg_loss == 0:
        rsis[0] = 100
    else:
        rs = avg_gain / avg_loss
        rsis[0] = 100 - (100 / (1 + rs))

    for idx in range(1, rsi_range):
        avg_gain = ((avg_gain * (period - 1) + gains[idx + (period - 1)]) /
                    period)
        avg_loss = ((avg_loss * (period - 1) + losses[idx + (period - 1)]) /
                    period)

        if avg_loss == 0:
            rsis[idx] = 100
        else:
            rs = avg_gain / avg_loss
            rsis[idx] = 100 - (100 / (1 + rs))

    return rsis


def sma(prices, period):
    """
      prices ndarray
      period int > 1 and < len(prices)

    Output:
      smas ndarray
    """

    num_prices = len(prices)

    if num_prices < period:
        raise SystemExit('Error: num_prices < period')

    sma_range = num_prices - period
    smas = np.zeros(sma_range)

    for idx in range(num_prices):

        if idx >= period:
            smas[idx-period] = np.mean(prices[idx-period:idx])

    return smas


def wma(prices, period):
    """
    Input:
      prices ndarray
      period int > 1 and < len(prices)

    Output:
      wmas ndarray

    """

    num_prices = len(prices)

    if num_prices < period:
        raise SystemExit('Error: num_prices < period')

    wma_range = num_prices - period + 1

    wmas = np.zeros(wma_range)

    k = (period * (period + 1)) / 2.0

    for idx in range(wma_range):
        for period_num in range(period):
            weight = period_num + 1
            wmas[idx] += prices[idx + period_num] * weight
        wmas[idx] /= k

    return wmas


# default type = 1 matches up with mathematica's ema with alpha=2/(1+period)
def ema(prices, period, ema_type=1):
    """
    EMA type 0
    EMAn = w.Pn + (1 - w).EMAn-1
    EMAn = EMAn-1 + w.(Pn - EMAn-1)
    EMAn = w.Pn + w.(1 - w).Pn-1 + w.(1 - w)^2.Pn-2 + ... +
    w.(1 - w)^(n-1).P1 + w.(1 - w)^n.EMA0
    where w = 2 / (n + 1) and EMA0 = mean(oldest period)
    or
    EMAn = w.EMAn-1 + (1 - w).Pn
    where w = 1 - 2 / (n + 1) and Pn is the most recent price
    and EMA0 = mean(oldest period)

    EMA type 1
    The above formulas with EMA0 = P1 (oldest price)

    EMA type 2
    EMA = (Pn + w.Pn-1 + w^2.Pn-2 + w^3.Pn-3 + ... ) / K
    where K = 1 + w + w^2 + ... = 1 / (1 - w) and Pn is the most recent price
    and w = 2 / (N + 1)

    """

    num_prices = len(prices)

    if num_prices < period:
        # show error message
        raise SystemExit('Error: num_prices < period')

    if ema_type == 0:  # 1st value is the average of the period
        ema_range = num_prices - period + 1

        emas = np.zeros(ema_range)

        emas[0] = np.mean(prices[:period])

        w = 2 / float(period + 1)

        for idx in range(1, ema_range):
            emas[idx] = w * prices[idx + period - 1] + (1 - w) * emas[idx - 1]


    elif ema_type == 1:  # 1st value is the 1st price
        ema_range = num_prices

        emas = np.zeros(ema_range)

        emas[0] = prices[0]

        w = 2 / float(period + 1)


        for idx in range(1, ema_range):
            emas[idx] = w * prices[idx] + (1 - w) * emas[idx - 1]

    else:
        ema_range = num_prices - period + 1

        emas = np.zeros(ema_range)

        w = 2 / float(period + 1)

        k = 1 / float(1 - w)

        for idx in range(ema_range):
            for period_num in range(period):
                # this runs the prices backwards to comply with the formula
                emas[idx] += w**period_num * \
                    prices[idx + period - period_num - 1]
            emas[idx] /= k

    return emas


def ma_env(prices, period, percent, ma_type=0):
    """
    Input:
      prices ndarray
      period int > 1 and < len(prices)
      percent float > 0.00 and < 1.00
      ma_type 0=EMA type 0, 1=EMA type 1, 2=EMA type 2, 3=WMA, 4=SMA

    Output:
      ma_envs ndarray with upper, middle, lower bands, range and %B

    """

    num_prices = len(prices)

    if num_prices < period:
        # show error message
        raise SystemExit('Error: num_prices < period')

    ma_env_range = num_prices - period + 1

    # 3 bands, range and %B
    ma_envs = np.zeros((ma_env_range, 5))

    if 0 <= ma_type <= 2:  # EMAs
        ma = ema(prices, period, ema_type=ma_type)

    elif ma_type == 3:  # WMA
        ma = wma(prices, period)

    else:  # SMA
        ma = sma(prices, period)

    for idx in range(ma_env_range):
        # upper, middle, lower bands, range and %B
        ma_envs[idx, 0] = ma[idx] + (ma[idx] * percent)
        ma_envs[idx, 1] = ma[idx]
        ma_envs[idx, 2] = ma[idx] - (ma[idx] * percent)
        ma_envs[idx, 3] = ma_envs[idx, 0] - ma_envs[idx, 2]
        ma_envs[idx, 4] = (prices[idx] - ma_envs[idx, 2]) / ma_envs[idx, 3]

    return ma_envs


def bb(prices, period, num_std_dev=2.0):
    """
    Input:
      prices ndarray
      period int > 1 and < len(prices)
      num_std_dev float > 0.0 (optional and defaults to 2.0)

    Output:
      bbs ndarray with upper, middle, lower bands, bandwidth, range and %B

    """

    num_prices = len(prices)

    if num_prices < period:
        # show error message
        raise SystemExit('Error: num_prices < period')

    bb_range = num_prices - period + 1

    # 3 bands, bandwidth, range and %B
    bbs = np.zeros((bb_range, 6))

    simple_ma = sma(prices, period)

    for idx in range(num_prices):
        if idx >= period:

            index = idx - period
            std_dev = np.std(prices[index:index + period])

            # upper, middle, lower bands, bandwidth, range and %B
            bbs[index, 0] = simple_ma[index] + std_dev * num_std_dev
            bbs[index, 1] = simple_ma[index]
            bbs[index, 2] = simple_ma[index] - std_dev * num_std_dev
            bbs[index, 3] = (bbs[index, 0] - bbs[index, 2]) / bbs[index, 1]
            bbs[index, 4] = bbs[index, 0] - bbs[index, 2]
            bbs[index, 5] = (prices[idx-1] - bbs[index, 2]) / bbs[index, 4]

    return bbs

def bbtimes(timeprices, period, num_std_dev=2.0):
    times = timeprices[:,0]
    prices = timeprices[:,1]
    bbprices = bb(prices, period, num_std_dev) # feed the function only the prices
    times = times[-len(bbprices):] # make sure times and bb output have same length from the end
    return np.c_[ times, bbprices ] # add the time back in as a column

def ematimes(timeprices, period, ema_type=0):
    times = timeprices[:,0]
    prices = timeprices[:,1]
    emaprices = ema(prices, period, ema_type) # feed the function only the prices
    times = times[-len(emaprices):] # make sure times and ema output have same length from the end
    return np.c_[ times, emaprices ] # add the time back in as a column

def macdhisttimes(timeprices, period_fast, period_slow, period_signal, ema_type=0):
    times = timeprices[:,0]
    prices = timeprices[:,1]
    emaprices_fast = ema(prices, period_fast, ema_type) # feed the function only the prices
    emaprices_slow = ema(prices, period_slow, ema_type) # feed the function only the prices
    ema_diff = [x - y for x, y in zip(emaprices_fast, emaprices_slow)]# MACD line
    ema_signal = ema(ema_diff, period_signal, ema_type) # Signal line
    hist = [x - y for x, y in zip(ema_diff, ema_signal)]# Histogram of MACD - Signal
    times = times[-len(hist):] # make sure times and hist have same length from the end
    return np.c_[ times, hist ] # add the time back in as a column

def rsitimes(timeprices, period=14):
    # give a ndarray of time,openprice,closeprice
    # get the rsi at each time slice
    times = timeprices[:,0]
    prices = timeprices[:,1]

    # rsis = rsi(closeprices)
    # differences = prices[1:]-prices[:-1]
    # up = np.copy(differences)
    # up[up <= 0] = 0
    # down = np.copy(differences)
    # down[down >= 0] = 0
    # down = np.abs(down)
    # rss = ema(up,period)/ema(down,period)
    # rsis = 100.0 - 100.0/(1+rss)
    rsis = rsi(prices, period)

    times = times[-len(rsis):]
    return np.c_[ times, rsis ]

def crossovertimes(matimes):
    # takes a list of moving averages and returns a list where
    # each element is a (day,code) pair. code=1 if trendlines crossed upwards
    # code=0 if trendlines crossed downwards

    # shortest first
    mas = sorted(matimes, key=lambda e: len(e))
    mintimesteps = len(mas[0])
    macrossover = [[] for i in range(mintimesteps)]
    for ima,ma in enumerate(mas):
        ma = ma[-mintimesteps:]
        for it in range(mintimesteps): macrossover[it].append( ma[it] )

    # each element of emacrossover represents one day, meaning it is an array of (time,price) pairs for each MA
    # find out if the prices are increasing or decreasing between the MAs for each day
    macrossover = np.array(macrossover)

    crossover = [] # each element will be a pair (day, code) where code=1 for increasing, -1 for decreasing, or 0 otherwise
    for dayinfo in macrossover:
        prices = dayinfo[:,1]
        day = dayinfo[0][0]
        isIncreasing = all(x<y for x,y in zip(prices, prices[1:]))
        isDecreasing = all(x>y for x,y in zip(prices, prices[1:]))

        if(isIncreasing): crossover.append([day, 1])
        elif(isDecreasing): crossover.append([day, -1])
        else: crossover.append([day, 0])

    prevcode = -999
    crossovertimes = [] # each element will be a pair (day, code) where code=1 if trendlines crossed upwards, or 0 if trendlines crossed downwards
    wasRising = False
    for day, code in crossover:
        day = int(day)
        if   prevcode == 0 and code == 1 and not wasRising: # none to rising
            crossovertimes.append([day,1])
            wasRising = True
        elif prevcode == -1 and code == 1: # falling to rising
            crossovertimes.append([day,1])
            wasRising = True
        elif prevcode == 0 and code == -1 and wasRising:  # none to falling
            crossovertimes.append([day,0])
            wasRising = False
        elif prevcode == 1 and code == -1: # rising to falling
            crossovertimes.append([day,0])
            wasRising = False
        else: pass

        prevcode = code
    return crossovertimes

# timeprices = np.array([ [1,86.16], [2,89.09], [3,88.78], [4,90.32], [5,89.07], [6,91.15], [7,89.44] ])
# print bbtimes(timeprices,3)
