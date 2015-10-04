import numpy as np
import matplotlib as mpl
import itertools
mpl.use('Agg')
from sklearn.svm import *
from sklearn.ensemble import *
from sklearn.lda import *
from sklearn.tree import *
from sklearn.neural_network import *
import sklearn.preprocessing as skp
from matplotlib import pyplot as plt
import utils as u
import sys

def printImportances(imps, inds):
    importances = {}
    for i, imp in enumerate(imps):
        importances[inds[i]] = imp

    print "---- BEGIN ----"
    for w in sorted(importances, key=importances.get, reverse=True):
        print "%-20s %.2f" % (w, importances[w])
    print "---- END ----"

def projectionX(xvals, yvals, nselect=250):
    nbins = 25
    with np.errstate(all='ignore'):
        n,  edges = np.histogram(xvals, bins=nbins)
        w,  edges = np.histogram(xvals, bins=nbins,  weights=yvals)
        w2, edges = np.histogram(xvals, bins=nbins,  weights=yvals*yvals)
        mean = w/n
        std = np.sqrt(w2/n - mean*mean)/np.sqrt(n)
        bincenters = map(np.mean,zip(edges[:-1], edges[1:]))

    # at what point do we have ~360 evts to the right of the line
    cutoff = 0.0
    nright = 0
    cumsum = np.cumsum(n[::-1])
    for i,val in enumerate(cumsum):
        if(val >= nselect):
            nright = val
            cutoff = edges[::-1][i+1]
            break
    nleft = len(xvals)-nright
            
    return bincenters, mean, std, cutoff, nleft, nright

def saveTrades(testingdata, classifiersTest, cutoffTest, printToScreen=False):
    goodTrades = testingdata[classifiersTest > cutoffTest][:,[1,2,3,4,5]] # FIXME FIXME FIXME
    # goodTrades = testingdata[testingdata[:,0] > 0.5][classifiersTest[testingdata[:,0] > 0.5] > cutoffTest][:,[1,2,3,4,5]]
    goodClassifiers = classifiersTest[classifiersTest > cutoffTest] # FIXME FIXME FIXME
    # goodClassifiers = classifiersTest[testingdata[:,0] > 0.5][classifiersTest[testingdata[:,0] > 0.5] > cutoffTest]
    for itrade, trade in enumerate(goodTrades):
        day, gain1, gain2, iticker, close0 = trade
        day, iticker, close0 = int(day), int(iticker), float(close0)
        if printToScreen:
            print dTickers[iticker], u.inum2tuple(day), close0, gain1, gain2, gain1+gain2
        else:
            dt = "%04i-%02i-%02i" % u.inum2tuple(day)
            fhTrades.write("%s %s %.3f %.2f\n" % (dTickers[iticker], dt, goodClassifiers[itrade], close0))


def doubleHist(sig, bkg, filename="test.png", name="", nbins=80):
    maximum = max( np.max(sig) , np.max(bkg) )
    minimum = min( np.min(sig) , np.min(bkg) )
    histsig = np.histogram(sig,bins=nbins,range=(minimum,maximum))
    histbkg = np.histogram(bkg,bins=nbins,range=(minimum,maximum))
    bin_edges = histsig[1]
    bin_centers = ( bin_edges[:-1] + bin_edges[1:]  ) /2.
    bin_widths = (bin_edges[1:] - bin_edges[:-1])
    ax1 = plt.subplot(111)
    ax1.bar(bin_centers-bin_widths/2.,histsig[0],facecolor='blue',linewidth=0,width=bin_widths,label='S',alpha=0.5)
    ax1.bar(bin_centers-bin_widths/2.,histbkg[0],facecolor='red',linewidth=0,width=bin_widths,label='B',alpha=0.5)
    plt.title(name)
    plt.xlabel("Value")
    plt.ylabel("Counts/Bin")
    legend = ax1.legend(loc='upper right', shadow=False,ncol=1)
    plt.savefig(filename)
    plt.clf()
    
def plotFeatureDistributions(Xtrain, Ytrain, name, idx):
    sig = Xtrain[:,[idx]][Ytrain>0.5]
    bkg = Xtrain[:,[idx]][Ytrain<0.5]
    doubleHist(sig, bkg, basedir+"feature_%i.png"%idx, name="Training distributions: "+name, nbins=50)

def makeHist2D(valsx, valsy, filename, title="", nbins=50):
    # vals is a 1d array of values
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    plt.title(title)
    ax.hist2d(valsx,valsy,bins=nbins,norm=mpl.colors.LogNorm(), cmap='Blues')
    fig.savefig("%s" % (filename))
    print ">>> Saved %s" % filename
    plt.clf()

def makeScatter2D(valsx, valsy, sigbkg, filename, title=""):
    # vals is a 1d array of values
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    plt.title(title)
    cols = 100.0-100.0*sigbkg
    ax.scatter(valsx,valsy,c=cols,alpha=0.6,lw=0)
    fig.savefig("%s" % (filename))
    print ">>> Saved %s" % filename
    plt.clf()

def plotTrainTest(Xtrain, Ytrain, Xtest, Ytest, trainingdata, testingdata, title="test title", filename="test.png"):
    # shamelessly stolen from https://dbaumgartel.wordpress.com/2014/03/14/machine-learning-examples-scikit-learn-versus-tmva-cern-root/
    Classifier_training_S = alg.decision_function(Xtrain[Ytrain>0.5]).ravel()
    Classifier_training_B = alg.decision_function(Xtrain[Ytrain<0.5]).ravel() 
    Classifier_testing_S = alg.decision_function(Xtest[Ytest>0.5]).ravel()
    Classifier_testing_B = alg.decision_function(Xtest[Ytest<0.5]).ravel()

    classifiersTrain = alg.decision_function(Xtrain).ravel()
    classifiersTest = alg.decision_function(Xtest).ravel()

    gainsTrain = trainingdata[:,2]+trainingdata[:,3]
    gainsTest = testingdata[:,2]+testingdata[:,3]
        
    c_min, c_max = -1.5, 1.5
    if("NuSVC" in title): c_min, c_max = -150.0, 150.0
    elif("LDA" in title): c_min, c_max = -1.0, 1.0
    elif("BDT" in title and not "BDTG" in title): c_min, c_max = -0.1, 0.1
    elif("LinearSVC" in title): c_min, c_max = -0.5, 0.5

    Histo_training_S = np.histogram(Classifier_training_S,bins=40,range=(c_min,c_max))
    Histo_training_B = np.histogram(Classifier_training_B,bins=40,range=(c_min,c_max))
    Histo_testing_S = np.histogram(Classifier_testing_S,bins=40,range=(c_min,c_max))
    Histo_testing_B = np.histogram(Classifier_testing_B,bins=40,range=(c_min,c_max))
    AllHistos= [Histo_training_S,Histo_training_B,Histo_testing_S,Histo_testing_B]
    h_max = max([histo[0].max() for histo in AllHistos])*1.2
    h_min = max([histo[0].min() for histo in AllHistos])
    bin_edges = Histo_training_S[1]
    bin_centers = ( bin_edges[:-1] + bin_edges[1:]  ) /2.
    bin_widths = (bin_edges[1:] - bin_edges[:-1])
    ErrorBar_testing_S = np.sqrt(Histo_testing_S[0])
    ErrorBar_testing_B = np.sqrt(Histo_testing_B[0])
    ax1 = plt.subplot(111)
    ax1.bar(bin_centers-bin_widths/2.,Histo_training_S[0],facecolor='blue',linewidth=0,width=bin_widths,label='S (Train)',alpha=0.5)
    ax1.bar(bin_centers-bin_widths/2.,Histo_training_B[0],facecolor='red',linewidth=0,width=bin_widths,label='B (Train)',alpha=0.5)
    ax1.errorbar(bin_centers, Histo_testing_S[0], yerr=ErrorBar_testing_S, xerr=None, ecolor='blue',c='blue',fmt='o',label='S (Test)')
    ax1.errorbar(bin_centers, Histo_testing_B[0], yerr=ErrorBar_testing_B, xerr=None, ecolor='red',c='red',fmt='o',label='B (Test)')
    ax1.axvspan(0.0, c_max, color='blue',alpha=0.08)
    ax1.axvspan(c_min,0.0, color='red',alpha=0.08)
    ax1.axis([c_min, c_max, h_min, h_max])
    plt.title(title)
    plt.xlabel("Classifier")
    plt.ylabel("Counts/Bin")
    legend = ax1.legend(loc='upper center', shadow=False,ncol=2)
    for alabel in legend.get_texts(): alabel.set_fontsize('small')
    plt.savefig(filename)
    print ">>> Saved %s" % filename
    plt.clf()
        


    cutoffTrain = plot2DGainClassifier(gainsTrain, classifiersTrain, title+" Training", filename.replace(".png", "_gainsTrain.png"), lims=[c_min, c_max])
    cutoffTest = plot2DGainClassifier(gainsTest, classifiersTest, title+" Testing", filename.replace(".png", "_gainsTest.png"), lims=[c_min, c_max])
    saveTrades(testingdata, classifiersTest, cutoffTest, printToScreen=False)



def plot2DGainClassifier(gains, classifiers, title, filename, lims=[-1.5,1.5]):
    nselect = 1000
    # at what classifier value do we have nselect points to the right?
    xvals, yvals, yerr, cutoff, nleft, nright = projectionX(classifiers, gains, nselect=nselect)
    # what is the average fractional gain to the right of this cutoff line
    avgPctGainRight = np.mean(gains[classifiers >= cutoff]) * 100.0
    avgPctGainLeft = np.mean(gains[classifiers < cutoff]) * 100.0

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    plt.title(title)
    ax.hist2d(classifiers,gains,bins=[100,150],norm=mpl.colors.LogNorm(),cmap='Purples')
    ax.text(0.985,0.985,"%i evts (right side)" % nright, horizontalalignment='right', verticalalignment='top',transform=ax.transAxes,color='black')
    ax.text(0.985,0.925,"avg %% gain: %.3f%%" % avgPctGainRight, horizontalalignment='right', verticalalignment='top',transform=ax.transAxes,color='black')

    ax.text(0.015,0.985,"%i evts (left side)" % nleft, horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='black')
    ax.text(0.015,0.925,"avg %% gain: %.3f%%" % avgPctGainLeft, horizontalalignment='left', verticalalignment='top',transform=ax.transAxes,color='black')
    ax.errorbar(xvals, yvals, yerr=yerr, xerr=None, ecolor='r',c='r',fmt='o',label='Mean')
    ax.axvline(cutoff, color='r',alpha=0.5)
    plt.ylim([-0.5,0.5])
    plt.xlim(lims)
    plt.ylabel('2-day fractional gain')
    plt.xlabel('Classifier')
    fig.savefig(filename)
    plt.clf()
    print ">>> Saved %s" % filename
    return cutoff

filename = "forBDT_092915.txt"
if(len(sys.argv)>1): filename = sys.argv[1]
# filename = "forBDT_093015_short.txt"
# tickerfile = "forBDT_092915_tickers.txt"
tickerfile = filename.replace(".txt","_tickers.txt")
tradefile = "trades_"+filename

print ">>> Input file:", filename
print ">>> Input tickers file:", tickerfile
print ">>> Output trades file:", tradefile

# tradefile = "trades_092915.txt"
basedir = "../bdtplots5/"
if(len(sys.argv)>3): basedir = sys.argv[3]
fhinput = open(filename,"r")
firstline = fhinput.readline()
columnlabels = firstline.split(":")[1].strip().split()
# indicators = columnlabels
fhinput.close()

datasetOriginal = np.loadtxt(filename)

dataset = np.copy(datasetOriginal)
# np.random.shuffle(dataset)

# re-compute class on the fly
change1, change2 = 1.25/100, 0.75/100
for i in range(len(dataset)):
    sb, gainD1, gainD2 = -1, dataset[i][2], dataset[i][3]

    if(  gainD1 >  change1 and gainD2 >  change2): sb = 1
    elif(gainD1 < -change1 and gainD2 < -change2): sb = 0

    dataset[i][0] = sb

dataset = dataset[dataset[:,2]+dataset[:,3] < 1.0] # ignore 100% gains!

fhTicker = open(tickerfile, "r")
lines = fhTicker.readlines()
fhTicker.close()
dTickers = {}
for line in lines:
    line = line.strip()
    if("#" in line): continue
    if(len(line) < 3): continue
    ticker = line.split()[0]
    iticker = int(line.split()[1])
    dTickers[iticker] = ticker
fhTrades = open(tradefile, "w")

alg = None
inclusive = True
plotFeatures = False
plotFeatures2D = False
fracTrain = 0.6
print ">>> Training with first %.0f%% and testing with latter %.0f%%" % (100.0*fracTrain, 100.0*(1.0-fracTrain))
if(inclusive):

    trainingdata = dataset[:int(fracTrain*len(dataset))] # train with first half (s and b only)
    testingdata = dataset[-int((1.0-fracTrain)*len(dataset)):] # test with second half (inclusive)

    trainingdata = trainingdata[trainingdata[:,0] > -0.5] # ignore non sig and non bkg

else:
    dataset = dataset[dataset[:,0] > -0.5] # ignore non sig and non bkg
    trainingdata = dataset[:int(fracTrain*len(dataset))] # train with first half (s and b only)
    testingdata = dataset[-int((1.0-fracTrain)*len(dataset)):] # test with second half

# mix things up to keep the learner on its toes
np.random.shuffle(trainingdata) 
np.random.shuffle(testingdata)

# first = True
# whichIndicators = ["AROONOSC", "WILLR", "HT_DCPHASE", "NATR", "STOCHF_fastd", "SAREXT", \
#                    "SAR", "HT_SINE_leadsine","CMO","RSI","BOP", "CCI", "EMAD510","AD", \
#                    "KST","ADXR","MACDEXT_macdhist","MOM","MINUS_DI","ROC"]
# whichIndicators = [i for i in indicators if "gain" not in i]

whichIndicators = ["BOP","KST","STOCHF_fastk","MACDEXT_macdhist","ADOSC","NATR","MFI","AD","SAREXT","MOM","AROON_aroondown","ADXR","STOCHRSI_fastd","WILLR"]
# print whichIndicators
print ">>> Training with the indicators: %s" % " ".join(whichIndicators)
# whichIndicators = ["gainD1", "gainD2"]
indices = [columnlabels.index(indi) for indi in whichIndicators]

Xtrain = trainingdata[:,indices]
Ytrain = trainingdata[:,0]

Xtest = testingdata[:,indices]
Ytest = testingdata[:,0]

if(plotFeatures):
    for idx, indicator in enumerate(whichIndicators):
        plotFeatureDistributions(Xtrain, Ytrain, indicator, idx)

if(plotFeatures2D):
    for idx1, indicator1 in enumerate(whichIndicators):
        for idx2, indicator2 in enumerate(whichIndicators):
            if( idx1 == idx2 ): continue

            v1 = Xtrain[:,[idx1]].ravel()
            v2 = Xtrain[:,[idx2]].ravel()
            makeScatter2D(v1, v2, Ytrain, basedir+"feature_2d_%s_%s.png" % (indicator1, indicator2), title="%s vs %s" % (indicator1, indicator2))

Xtrain = skp.StandardScaler().fit_transform(Xtrain)
Xtest = skp.StandardScaler().fit_transform(Xtest)

# for algorithm in ["SVC", "BDTG", "BDT2", "BDT"]:
# for algorithm in ["SVC", "BDT", "BDTG", "SVC_gamma0p08", "NuSVC", "SVR", "LinearSVC", "LDA", "LDAshrinkage"]:
algorithms = ["BDT2"]
if(len(sys.argv)>2): algorithms = [sys.argv[2]]

for algorithm in algorithms:
# for algorithm in ["BDTG", "BDT2", "BDT"]:

    print ">>> ALG: %s" % (algorithm)

    if algorithm == "BDT": alg = AdaBoostClassifier(n_estimators=200, learning_rate=0.1)
    if algorithm == "BDT2": alg = AdaBoostClassifier( DecisionTreeClassifier(max_depth=3,min_samples_leaf=0.05*len(Xtrain)), algorithm='SAMME', n_estimators=800, learning_rate=0.5)
    elif algorithm == "BDTG": alg = GradientBoostingClassifier()
    elif algorithm == "Tree": alg = DecisionTreeClassifier()
    elif algorithm == "SVC_gamma0p08": alg = SVC(kernel = 'rbf',tol=0.001, gamma=0.08) 
    elif algorithm == "NuSVC": alg = NuSVC() 
    elif algorithm == "SVC": alg = SVC() 
    elif algorithm == "SVR": alg = SVR() 
    elif algorithm == "LinearSVC": alg = LinearSVC() 
    elif algorithm == "LDA": alg = LDA()
    elif algorithm == "LDAshrinkage": alg = LDA(solver="eigen",shrinkage='auto')
    elif algorithm == "ExtraTrees": alg = ExtraTreesClassifier()
    elif algorithm == "RandomForest": alg = RandomForestClassifier()
    elif algorithm == "Bagging": alg = BaggingClassifier()

    alg.fit(Xtrain, Ytrain)

    # try: printImportances(alg.feature_importances_, whichIndicators)
    # except: pass
    # try: printImportances(alg.coef_, whichIndicators)
    # except: pass

    minday = int(np.min(testingdata[:,[1]]))
    maxday = int(np.max(testingdata[:,[1]]))
    mind, maxd = u.inum2tuple(minday), u.inum2tuple(maxday)
    fhTrades.write("# %s %i to %i (%i-%i-%i to %i-%i-%i) \n" % (algorithm, minday, maxday, mind[0], mind[1], mind[2], maxd[0], maxd[1], maxd[2]) )

    plotTrainTest(Xtrain, Ytrain, Xtest, Ytest, trainingdata, testingdata, \
        # title = "%s LR: %.3f N-estimators: %i" % (algorithm, rate, nest), \
        title = "%s" % (algorithm), \
        # filename = basedir+"TrainTest_%s_%s_%s.png" % (algorithm, ("%.4f" % rate).replace(".",""), ("%i" % nest).replace(".","")) \
        filename = basedir+"TrainTest_%s.png" % (algorithm) \
    )

fhTrades.close()
