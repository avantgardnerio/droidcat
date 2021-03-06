# Import all classification package
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier

from sklearn.cross_validation import cross_val_score
from sklearn.metrics import precision_score,recall_score,f1_score,roc_auc_score,accuracy_score
from sklearn import cross_validation

from sklearn.metrics import confusion_matrix

import numpy
import random
import os
import sys
import string

from configs import *
from featureLoader import *

# 10-fold cross-validation
def cv(model, features, labels):
    sr=len(features)
    #sr=features.shape[0]
    #k=10
    k=sr
    subsize = sr/k
    subsamples=list()
    sublabels=list()

    predicted_labels=list()
    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    for j in range(0,k):
        subsamples.append( (features[j*subsize:(j+1)*subsize]) )
        sublabels.append( (labels[j*subsize:(j+1)*subsize]) )

    for j in range(0,k):
        testFeatures = subsamples[j]
        testLabels = sublabels[j]

        trainFeatures = list()
        trainLabels = list()
        for r in range(0,k):
            if r==j:
                continue
            #trainFeatures.append( subsamples[r] )
            #trainLabels.append( sublabels[r] )
            for fl in subsamples[r]:
                trainFeatures.append(fl)
            for lal in sublabels[r]:
                trainLabels.append( lal )

        model.fit( trainFeatures, trainLabels )
        y_pred = model.predict( testFeatures )
        print >> sys.stderr, "j=%d, testLabels: %s" % (j, str(testLabels))
        print >> sys.stderr, "j=%d, predicted: %s" % (j, str(y_pred))

        predicted_labels.append ( y_pred )

    '''
    for i in range(0, len(predicted_labels)):
        #print type(predicted_labels[i])
        if predicted_labels[i][0] not in big_families:
            predicted_labels[i] = numpy.array(['MALICIOUS'])
    '''

    #print "%s\n%s\n" % (str(sublabels), str(predicted_labels))
    big_families=["DroidKungfu", "ProxyTrojan/NotCompatible/NioServ", "GoldDream", "Plankton", "FakeInst", "BENIGN", "MALICIOUS"]

    #return confusion_matrix(labels, predicted_labels, labels=list(uniqLabels))
    return confusion_matrix(sublabels, predicted_labels, labels=big_families)


def selectFeatures(features, selection):
    featureSelect=[idx-1 for idx in selection]
    selectedfeatures=list()
    for featureRow in features:
        selectedfeatures.append ( featureRow[ featureSelect ] )
    return selectedfeatures

if __name__=="__main__":

    (features, labels, Testfeatures, Testlabels) = getTrainingData( False, pruneMinor=True)

    (allfeatures_malware, malwareLabels) = getMalwareTestingData( False, FTXT_MALWARE_G_NEW, FTXT_MALWARE_ICC_NEW, FTXT_MALWARE_SEC_NEW, pruneMinor=True)
    r=0
    c=None
    for app in allfeatures_malware.keys():
        r+=1
        if c==None:
            c = len (allfeatures_malware[app])
            print "feature vector length=%d" % (c)
            continue
        if c != len (allfeatures_malware[app]):
            print "inconsistent feature vector length for app: %s --- %d" % (app, len(allfeatures_malware[app]))
        assert c == len (allfeatures_malware[app])
    newtestfeatures = numpy.zeros( shape=(r,c) )
    newtestlabels = list()
    k=0
    for app in allfeatures_malware.keys():
        newtestfeatures[k] = allfeatures_malware[app]
        newtestlabels.append ( malwareLabels[app] )
        k+=1

    models = (RandomForestClassifier(n_estimators = 100), SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())
    #models = (SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())

    uniqLabels = set()
    for item in newtestlabels:
        uniqLabels.add (item)

    fh = sys.stdout
    print >> fh, '\t'.join(uniqLabels)
    big_families=["DroidKungfu", "ProxyTrojan/NotCompatible/NioServ", "GoldDream", "Plankton", "FakeInst", "BENIGN"]

    for model in models:
        #for fset in (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_Y, FSET_YY, FSET_YYY):
        for fset in (FSET_FULL, FSET_YYY):
            print >> fh, 'model ' + str(model) + "\t" + "feature set " + str(fset)

            model.fit( selectFeatures(features,fset), labels )
            predicted_labels = model.predict( selectFeatures(newtestfeatures,fset) )

            print newtestlabels
            print predicted_labels

            ret = confusion_matrix(newtestlabels, predicted_labels, labels=["ProxyTrojan/NotCompatible/NioServ", "FakeInst"] )

            for row in ret:
                for x in row:
                    print >> fh, "%d\t" % (x),
                print >> fh

    fh.flush()
    fh.close()

    sys.exit(0)

# hcai: set ts=4 tw=100 sts=4 sw=4
