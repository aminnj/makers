import numpy as np
import sklearn.cluster as skc

# def clusterCandles(normquotes, nclusters=5, ncandles=2, shift=0):
def clusterCandles(quotes, nclusters=5, ncandles=2, loadFrom=None, saveTo=None, improve=False):
    """
    - takes quotes object
    - returns:
      a 1D array of start times for candles 
      a 1D array of cluster numbers
      an array of cluster centers (array of vectors)
    - specify filename in loadFrom to load initial centroids
    - specify saveTo to save centroids
    - specify improve=True when you have loadFrom to load centroids, and train further
    """

    # remove the first few elements so that the size is a multiple of ncandles; ignore dates
    forfit = quotes[:,[1,2,3,4]][len(quotes)%ncandles:] 
    times = quotes[:,0][len(quotes)%ncandles:] 
    forfit = forfit.ravel() # flattens n-dim to 1-dim
    # group candles together in groups of size ncandles
    # turn it into [ [o h l c o h l c ... ] # 4*ncandles elements
    #                [o h l c o h l c ... ]  ... ]
    rows, cols = int(np.ceil(len(forfit)/(ncandles*4))),4*ncandles
    forfit.resize(rows, cols)
    times = times.ravel()
    times.resize(rows,cols//4)
    times = times[:,0]
    # now subtract the first open price from all elements (within each group)
    # and normalize so that highest-lowest=1
    normforfit = []
    for group in forfit: 
        maxp, minp = np.max(group), np.min(group)
        normforfit.append( (group - group[0])/(maxp - minp) )
    normforfit = np.array(normforfit)
    
    if(loadFrom is not None):
        if(not improve): km = skc.KMeans(n_clusters=nclusters,max_iter=1,init=np.loadtxt(loadFrom))
        else: km = skc.KMeans(n_clusters=nclusters,max_iter=600,init=np.loadtxt(loadFrom))
    else:
        km = skc.KMeans(n_clusters=nclusters,max_iter=600,n_init=20)

    data = np.c_[ normforfit ]
    clusters = km.fit_predict(data)
    clusterCenters = km.cluster_centers_

    if(saveTo is not None):
        np.savetxt(saveTo,clusterCenters)

    return times, clusters, clusterCenters

def clusterCentersForPlotting(clusterCenters):
    """
    - takes array of cluster centers (from above function)
    - returns quotes object and vlines object to directly feed into candlestick plotting function
    - dates don't matter (they're just dummy values) as this is only for visualization of cluster geometry
    """
    clusterCenters = np.c_[ clusterCenters ]
    nclusters, ncandles = len(clusterCenters), len(clusterCenters[0])//4
    clusterCenters = clusterCenters.reshape(nclusters*ncandles,4)
    clusterQuotes = np.c_[ np.array(range(1000,1000+len(clusterCenters))), clusterCenters ]
    vlines = range(1000,1000+len(clusterQuotes[:,0]),ncandles)

    return clusterQuotes, vlines

def dictToSortedList(d, reverse=True):
    """
    takes a dict with key,vals
    returns an array with elements [key,val] sorted with descending value
    """
    sortedkeys = sorted(d, key=d.get, reverse=reverse)
    sortedvals = [d[k] for k in sortedkeys]
    return np.array(zip(sortedkeys, sortedvals))

def profitFromCluster(cluster):
    # returns NORMALIZED profit for a given cluster vector
    # want close of last day - open of first day
    # since it is O h l c o h l C
    return cluster[-1]-cluster[0]

def clustersAndTheirProfits(clusters, clusterCenters):
    # give me an array of clusters codes (1D) and an array of clusterCenters
    # I will give you a dict of clusters and their normalized profits
    # due to a weighted average of all possible following clusters

    # want to find which cluster follows another cluster most of the time
    clusterpairs = zip(clusters[:-1], clusters[1:]) 
    # make histogram dict
    dpairs = {}
    for one,two in clusterpairs:
        if one not in dpairs: dpairs[one] = { }
        if two not in dpairs[one]: dpairs[one][two] = 0

        dpairs[one][two] += 1

    clusterProfits = {}
    for one in sorted(dpairs.keys()):
        twos = dictToSortedList(dpairs[one])
        if(len(twos) > 0): tot = np.sum(twos[:,1])
        else: tot = 1
        # for each cluster pattern, figure out the cluster patterns that follow
        s = 0.0
        for two in twos:
            # sum up the profit from the following cluster pattern weighted by it's probability
            # to follow the initial cluster pattern
            frac = 1.0*two[1]/tot
            s += frac*profitFromCluster(clusterCenters[two[0]])
        clusterProfits[one] = s

    return clusterProfits

