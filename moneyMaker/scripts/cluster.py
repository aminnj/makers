import numpy as np
import sklearn.cluster as skc

def clusterCandles(normquotes, nclusters=5, ncandles=2, shift=0):
    """
    - takes normalizedquotes (e.g., subtract open price from everything), which is
    a list of [day,o,h,l,c] vals. shift is the offset.
    - returns a 1D array of start times for candles and a 1D array of cluster numbers
    """
    # each candle is described by 3 values
    forfit = normquotes[:,[2,3,4]][shift:] # no need for low because we subtracted that out...always 0
    times = normquotes[:,0][shift:]

    forfit = forfit[len(forfit)%ncandles:] # drop excess candles so we have a multiple of ncandles
    times = times[len(times)%ncandles:]

    forfit = forfit.ravel() # flattens n-dim to 1-dim
    times = times.ravel()
    rows, cols = int(np.ceil(len(forfit)/(ncandles*3))),3*ncandles # rows is num of candle clumps
    forfit.resize(int(np.ceil(len(forfit)/(ncandles*3))),3*ncandles)
    times.resize(rows,cols//3)
    times = times[:,0]

    km = skc.KMeans(n_clusters=nclusters)
    # add more and more columns to data (c_ just puts columns side by side)
    # data = np.c_[ normquotes[:,[2,3,4]] ] # no need for low because we subtracted that out...always 0
    data = np.c_[ forfit ] # no need for low because we subtracted that out...always 0
    # data = np.c_[ data, bbands[:,1]-quotes[:,1] ] # subtract out opening prices from bbands
    # data = np.c_[ data, bbands[:,2]-quotes[:,1] ]
    # data = np.c_[ data, bbands[:,3]-quotes[:,1] ]

    clusters = km.fit_predict(data)
    return times, clusters
