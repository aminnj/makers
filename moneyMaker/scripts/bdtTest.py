import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.svm import NuSVC
from sklearn.svm import LinearSVC
from sklearn.lda import LDA
from sklearn.ensemble import AdaBoostClassifier
from matplotlib import pyplot as plt
import utils as u

filename = "forBDT_3000_unprescaled_newsb.txt"
# filename = "forBDT_1000.txt"
basedir = "../bdtplots2/"
fhinput = open(filename,"r")
firstline = fhinput.readline()
columnlabels = firstline.split(":")[1].strip().split()
indicators = columnlabels[2:]
fhinput.close()

dataset = np.loadtxt(filename)
np.random.shuffle(dataset)
# dataset = dataset[:1000]
# print dataset[:,0]

def to01(array):
    a = array.min()
    # ignore the Runtime Warning
    with np.errstate(divide='ignore'):
        b = 1. /(array.max() - array.min())
    if not(np.isfinite(b)):
        b = 0
    return np.vectorize(lambda x: b * (x - a))(array)

def scaleMatrix(mat):
    # separately scale each column of mat
    return np.column_stack( [ to01(mat[:,[icol]]) for icol in range(len(mat[0]))] )

def featureDistributions(Xtrain, Ytrain, name, idx):
    sig = Xtrain[:,[idx]][Ytrain>0.5]
    bkg = Xtrain[:,[idx]][Ytrain<0.5]
    histsig = np.histogram(sig,bins=80,range=(-1.5,1.5))
    histbkg = np.histogram(bkg,bins=80,range=(-1.5,1.5))
    AllHistos= [histsig, histbkg]
    h_max = max([histo[0].max() for histo in AllHistos])*1.2
    h_min = max([histo[0].min() for histo in AllHistos])
    bin_edges = histsig[1]
    bin_centers = ( bin_edges[:-1] + bin_edges[1:]  ) /2.
    bin_widths = (bin_edges[1:] - bin_edges[:-1])
    ax1 = plt.subplot(111)
    ax1.bar(bin_centers-bin_widths/2.,histsig[0],facecolor='blue',linewidth=0,width=bin_widths,label='S',alpha=0.5)
    ax1.bar(bin_centers-bin_widths/2.,histbkg[0],facecolor='red',linewidth=0,width=bin_widths,label='B',alpha=0.5)
    ax1.axis([-1.5, 1.5, h_min, h_max])
    plt.title("Training distributions: %s" % name)
    plt.xlabel("Value")
    plt.ylabel("Counts/Bin")
    legend = ax1.legend(loc='upper right', shadow=False,ncol=1)
    for alabel in legend.get_texts(): alabel.set_fontsize('small')
    plt.savefig(basedir+"feature_%i.png" % idx)
    plt.clf()


balances = ["balance", "nobalance"]
# algorithms = ["LDA", "LDAshrinkage", "SVR", "BDT", "SVC", "NuSVC", "LinearSVC", "SVC_gamma0p08"]

# balances = ["balance"]
algorithms = ["LDA", "SVR", "SVC"]
# algorithms = ["LDA"]


first = True
for balance in balances:
    for algorithm in algorithms:
            
            np.random.shuffle(dataset)
            # dataset = dataset[:100000]



            print "Classification with scikit-learn %s %s" % (balance, algorithm)

            # whichIndicators = ["AROONOSC", "TRIX", "NATR", "SAR", "WILLR", "HT_SINE_leadsine", "MOM"]
            # whichIndicators = ["AROONOSC", "BOP", "CCI", "CMO", "HT_DCPHASE", "HT_SINE_sine", "NATR", "RSI", "SAREXT", "STOCHF_fastd", "STOCHRSI_fastd", "WILLR"]
            whichIndicators = ["AROONOSC", "WILLR", "HT_DCPHASE", "NATR", "STOCHF_fastd"]
            # whichIndicators = ["NATR", "AROONOSC"]
            # whichIndicators = ["AROONOSC"]
            # whichIndicators = indicators
            # whichIndicators = ["NATR"]
            indices = [columnlabels.index(indi) for indi in whichIndicators]

            print "Training with the indicators: %s" % " ".join(whichIndicators)
            print

            ### ALGORITHM

            alg = None
            if algorithm == "BDT":
                alg = AdaBoostClassifier()
            elif algorithm == "SVC_gamma0p08":
                alg = SVC(kernel = 'rbf',tol=0.001, gamma=0.08) 
            elif algorithm == "NuSVC":
                alg = NuSVC() 
            elif algorithm == "SVC":
                alg = SVC() 
            elif algorithm == "SVR":
                alg = SVR() 
            elif algorithm == "LinearSVC":
                alg = LinearSVC() 
            elif algorithm == "LDA":
                alg = LDA()
            elif algorithm == "LDAshrinkage":
                alg = LDA(solver="lsqr",shrinkage='auto')

            ### TRAIN

            trainingdata = dataset[:len(dataset)//2] # train with first half
            testingdata = dataset[-len(trainingdata)-1:] # test with second half

            if balance == "balance":
                # for the training dataset, we want 50% signal 50% bkg approximately
                sigpart = trainingdata[trainingdata[:,0]==1]
                bkgpart = trainingdata[trainingdata[:,0]==0]
                bkgpart = bkgpart[:len(sigpart)]
                trainingdata = np.concatenate([sigpart, bkgpart])

            print "* Length of training dataset is", len(trainingdata)
            print "* Length of testing dataset is", len(testingdata)
            print "* There are",len(trainingdata[np.round(trainingdata[:,0])==0]),"bkg events in the training dataset"
            print "* There are",len(trainingdata[np.round(trainingdata[:,0])==1]),"sig events in the training dataset"
            print "* There are",len(testingdata[np.round(testingdata[:,0])==0]),"bkg events in the testing dataset"
            print "* There are",len(testingdata[np.round(testingdata[:,0])==1]),"sig events in the testing dataset"
            print

            Xtrain = scaleMatrix(trainingdata[:,indices])
            Ytrain = np.round(trainingdata[:,0]) # make sure that we have 0 and 1 as ints

            try:
                alg.fit(Xtrain, Ytrain)
            except:
                print "skipping"
                continue


            ### TEST

            Xtest = scaleMatrix(testingdata[:,indices])
            Ytest = np.round(testingdata[:,0])
            score = alg.score(Xtest, Ytest) 
            predictions = [alg.predict(x)[0] for x in Xtest]
            nsignalPredictions = np.sum(predictions) # this is why it's handy to use 1 and 0 instead of 1 and -1 ;)
            signalSuccesses = [prediction == ytruth for prediction,ytruth in zip(predictions,Ytest) if ytruth==1]
            signalScore = np.mean(signalSuccesses)
            predictionsForSignal = np.array([ytruth for prediction,ytruth in zip(predictions,Ytest) if prediction==1])
            fcorrect = 0
            if(len(predictionsForSignal) > 1):
                fcorrect = np.mean(predictionsForSignal == 1)

            print "- We predicted \"signal\" %i times and \"background\" %i times" % (nsignalPredictions, len(predictions)-nsignalPredictions)
            print """- We have a training success fraction of %.1f%%, but this is for bkg+sig combined (so 
            if we have 90%% background, and we predict background 100%% of the time, we'll have a success rate 
            of 90%%, which seems misleading)!""" % (100.0*score)
            print "- Of all the signal events, we correctly classify %.1f%% of them as signal" % (signalScore)
            print "- When we predict that we have a signal event, it is actually signal %.1f%% of the time (%i out of %i)" % (100.0*fcorrect, int(fcorrect*len(predictionsForSignal)), len(predictionsForSignal))


            ### PLOT

            # plot feature distributions
            if first:
                first = False
                for idx, indicator in enumerate(whichIndicators):
                    featureDistributions(Xtrain, Ytrain, indicator, idx)


            # shamelessly stolen from https://dbaumgartel.wordpress.com/2014/03/14/machine-learning-examples-scikit-learn-versus-tmva-cern-root/

            Classifier_training_S = alg.decision_function(Xtrain[Ytrain>0.5]).ravel()
            Classifier_training_B = alg.decision_function(Xtrain[Ytrain<0.5]).ravel() 
            Classifier_testing_S = alg.decision_function(Xtest[Ytest>0.5]).ravel()
            Classifier_testing_B = alg.decision_function(Xtest[Ytest<0.5]).ravel()
            
            # This will be the min/max of our plots
            c_max = 1.5
            c_min = -1.5
             
            # Get histograms of the classifiers
            Histo_training_S = np.histogram(Classifier_training_S,bins=40,range=(c_min,c_max))
            Histo_training_B = np.histogram(Classifier_training_B,bins=40,range=(c_min,c_max))
            Histo_testing_S = np.histogram(Classifier_testing_S,bins=40,range=(c_min,c_max))
            Histo_testing_B = np.histogram(Classifier_testing_B,bins=40,range=(c_min,c_max))
             
            # Lets get the min/max of the Histograms
            AllHistos= [Histo_training_S,Histo_training_B,Histo_testing_S,Histo_testing_B]
            h_max = max([histo[0].max() for histo in AllHistos])*1.2
            h_min = max([histo[0].min() for histo in AllHistos])
             
            # Get the histogram properties (binning, widths, centers)
            bin_edges = Histo_training_S[1]
            bin_centers = ( bin_edges[:-1] + bin_edges[1:]  ) /2.
            bin_widths = (bin_edges[1:] - bin_edges[:-1])
             
            # To make error bar plots for the data, take the Poisson uncertainty sqrt(N)
            ErrorBar_testing_S = np.sqrt(Histo_testing_S[0])
            ErrorBar_testing_B = np.sqrt(Histo_testing_B[0])
             
            # Draw objects
            ax1 = plt.subplot(111)
             
            # Draw solid histograms for the training data
            ax1.bar(bin_centers-bin_widths/2.,Histo_training_S[0],facecolor='blue',linewidth=0,width=bin_widths,label='S (Train)',alpha=0.5)
            ax1.bar(bin_centers-bin_widths/2.,Histo_training_B[0],facecolor='red',linewidth=0,width=bin_widths,label='B (Train)',alpha=0.5)
             
            # # Draw error-bar histograms for the testing data
            ax1.errorbar(bin_centers, Histo_testing_S[0], yerr=ErrorBar_testing_S, xerr=None, ecolor='blue',c='blue',fmt='o',label='S (Test)')
            ax1.errorbar(bin_centers, Histo_testing_B[0], yerr=ErrorBar_testing_B, xerr=None, ecolor='red',c='red',fmt='o',label='B (Test)')
             
            # Make a colorful backdrop to show the clasification regions in red and blue
            ax1.axvspan(0.0, c_max, color='blue',alpha=0.08)
            ax1.axvspan(c_min,0.0, color='red',alpha=0.08)
             
            # Adjust the axis boundaries (just cosmetic)
            ax1.axis([c_min, c_max, h_min, h_max])

            # Make labels and title
            plt.title("Classification with scikit-learn %s %s" % (balance, algorithm))
            plt.xlabel("Classifier")
            plt.ylabel("Counts/Bin")
             
            # Make legend with smalll font
            legend = ax1.legend(loc='upper center', shadow=False,ncol=2)
            for alabel in legend.get_texts():
                alabel.set_fontsize('small')
             
            # Save the result to png
            plt.savefig(basedir+"Sklearn_example_%s_%s.png" % (balance, algorithm))
            plt.clf()
            # u.web(basedir+"Sklearn_example.png")

