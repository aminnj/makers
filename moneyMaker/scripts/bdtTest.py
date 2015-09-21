import numpy as np
import sklearn.ensemble as ske
import pickle

# X = [ [0.1, 0.2, 0.3], [0.6, 1.3, -1.0], [-7.3, 2.7, 9.1], [-9.9, -9.0, -0.1] ] # vector for each sample
# y = [       1,               0,                 0,               1            ] # classification

# bdt = ske.AdaBoostClassifier()
# bdt = bdt.fit(X, y)

# fh = open("bdt.pkl","wb")
# pickle.dump(bdt, fh)
# fh.close()


# fh = open("bdt.pkl","rb")
# bdt = pickle.load(fh)
# fh.close()


# print np.round(bdt.predict_proba( [0.9, -0.1, 0.1] ), 1)

# print bdt.estimator_weights_
# print bdt.classes_
# print bdt.feature_importances_


filename = "forBDT_1000.txt"
fhinput = open(filename,"r")
firstline = fhinput.readline()
columnlabels = firstline.split(":")[1].strip().split()
indicators = columnlabels[2:]
fhinput.close()

dataset = np.loadtxt(filename)
np.random.shuffle(dataset) # does this matter?
# dataset = dataset[:1000]
# print dataset[:,0]

trainingdata = dataset[:len(dataset)//2] # train with first half
testingdata = dataset[-len(trainingdata)-1:] # test with second half
print "* Length of training dataset is", len(trainingdata)
print "* Length of testing dataset is", len(testingdata)
print "* There are",len(trainingdata[np.round(trainingdata[:,0])==0]),"bkg events in the training dataset"
print "* There are",len(trainingdata[np.round(trainingdata[:,0])==1]),"sig events in the training dataset"
print "* There are",len(testingdata[np.round(testingdata[:,0])==0]),"bkg events in the testing dataset"
print "* There are",len(testingdata[np.round(testingdata[:,0])==1]),"sig events in the testing dataset"
print

whichIndicators = ["AROONOSC", "TRIX", "NATR", "SAR", "WILLR", "HT_SINE_leadsine", "MOM"]
# whichIndicators = ["AROONOSC"]
# whichIndicators = indicators
# whichIndicators = ["EMA"]
indices = [columnlabels.index(indi) for indi in whichIndicators]

print "Training with the indicators: %s" % " ".join(whichIndicators)
print

bdt = ske.AdaBoostClassifier()

### TRAIN

X = trainingdata[:,indices]
y = np.round(trainingdata[:,0]) # make sure that we have 0 and 1 as ints
bdt.fit(X, y)


### TEST

X = testingdata[:,indices]
y = np.round(testingdata[:,0])
score = bdt.score(X, y) 
predictions = [bdt.predict(x)[0] for x in X]
nsignalPredictions = np.sum(predictions) # this is why it's handy to use 1 and 0 instead of 1 and -1 ;)
signalSuccesses = [prediction == ytruth for prediction,ytruth in zip(predictions,y) if ytruth==1]
signalScore = np.mean(signalSuccesses)
predictionsForSignal = np.array([ytruth for prediction,ytruth in zip(predictions,y) if prediction==1])
fcorrect = np.mean(predictionsForSignal == 1)

print "- We predicted \"signal\" %i times and \"background\" %i times" % (nsignalPredictions, len(predictions)-nsignalPredictions)
print """- We have a training success fraction of %.1f%%, but this is for bkg+sig combined (so 
if we have 90%% background, and we predict background 100%% of the time, we'll have a success rate 
of 90%%, which seems misleading)!""" % (100.0*score)
print "- Of all the signal events, we correctly classify %.1f%% of them as signal" % (signalScore)
print "- When we predict that we have a signal event, it is actually signal %.1f%% of the time (%i out of %i)" % (100.0*fcorrect, int(fcorrect*len(predictionsForSignal)), len(predictionsForSignal))

