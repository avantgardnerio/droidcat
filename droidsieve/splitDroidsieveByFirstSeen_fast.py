import random
import os
import sys
import string

import inspect, re
import pickle

from droidsieve_holdout import loadFeatures
from tab_holdout_droidsieve_all import get_families

rootdir="/home/hcai/Downloads/droidsieve/"
tagprefix="static.pickle."
g_binary=False

def split(fnFSmapping, fnDstprefix, defaultYear):
    fhmapping = file (fnFSmapping, 'r')
    if not (fhmapping):
        raise Exception ("unable to open the feature-vector-key-to-dates mapping file...")
    lines_key2dates = fhmapping.readlines()
    fhmapping.close()

    key2dates=dict()
    for line in lines_key2dates:
        line = line.lstrip().rstrip()
        items = string.split(line)
        if len(items)==3:
            date = items[1]
            year = string.split(date,'-')[0]
            key2dates[items[0]] = [year, date]

    datatag = "%s%s" % (fnDstprefix,defaultYear)
    mf,_ = loadFeatures(rootdir+tagprefix+datatag)

    ml={}
    if g_binary:
        for a in mf.keys():
            ml[a] = "BENIGN"
    else:
        mfam = get_families ("../ML/md5families/"+datatag+".txt")
        for a in mf.keys():
            if a in mfam.keys():
                ml[a] = mfam[a]
            else:
                ml[a] = "UNKNOWN"

    md5list=[]
    for line in file ('../ML/samplelists/md5.apks.'+datatag).readlines():
        md5list.append (line.lstrip('\r\n').rstrip('\r\n'))

    apklist=[]
    for line in file ('../ML/samplelists/apks.'+datatag).readlines():
        apklist.append (line.lstrip('\r\n').rstrip('\r\n'))

    apk2md5={}
    md52apk={}
    assert len(md5list)==len(apklist)
    for i in range(0, len(md5list)):
        apk2md5[ apklist[i] ] = md5list[i]
        md52apk[ md5list[i] ] = apklist[i]

    defaultDate = "%s-01-01" % (defaultYear)
    fn2data={}
    for md5 in mf.keys():
        print md5
        #assert md5 in md52apk.keys()
        if md5 not in md52apk.keys():
            print >> sys.stderr, "md5 %s not found in samplelist..." % (md5)
            continue
        apk = md52apk[md5]

        year = defaultYear
        date = defaultDate
        if apk in key2dates:
            year, date = key2dates[ apk ]

        print "redistributing a feature vector from year %s to year %s ..." % (defaultYear, year)
        fnDst = rootdir+"features_droidsieve_byfirstseen/"+tagprefix+fnDstprefix+str(year)
        fhDst = None
        new_features = {}
        if fnDst not in fn2data.keys():
            if os.path.isfile(fnDst):
                fhDst = file (fnDst, 'rb')

                try:
                    cur_features = pickle.load (fhDst)
                    fn2data[fnDst] = cur_features
                    new_features.update( cur_features )
                    fhDst.close()
                except (EOFError, pickle.UnpicklingError):
                    print >> sys.stderr, "error in loading current dated features"
                    sys.exit(2)
        else:
            new_features = fn2data[fnDst]

        new_features[ (md5, date) ] = (ml[md5], mf[ md5 ])
        fn2data[fnDst] = new_features

    for fnDst in fn2data.keys():
        fhDst = file(fnDst, 'wb')
        if not (fhDst):
            raise Exception ("unable to create result file: %s" % (fnDstprefix+str(year)))

        #print fn2data[fnDst]
        pickle.dump(fn2data[fnDst], fhDst)

        fhDst.flush()
        fhDst.close()

if __name__=="__main__":
    if len(sys.argv)<4:
        print >> sys.stderr, "too few arguments."
        print >> sys.stdout, "%s [file of feature-vector-key-to-first-seen-date-mapping] [pickle file of resulting feature vectors] [default year] [IsBenign]" % (sys.argv[0])
        sys.exit (-1)

    fnFSmapping = sys.argv[1]
    fnDstprefix = sys.argv[2]
    defaultYear = int(sys.argv[3])

    if len(sys.argv)>=5:
        g_binary = sys.argv[4].lower()=='true'

    print "now processing %s and %s" % (fnFSmapping, fnDstprefix+str(defaultYear))
    split(fnFSmapping, fnDstprefix, defaultYear)
    sys.exit(0)

