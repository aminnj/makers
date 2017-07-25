import sys
# sys.path.insert(0, "../dashboard/")
sys.path.insert(0, "/home/users/namin/junk/old/forFrank/NtupleTools/AutoTwopler/dashboard/")
import twiki
import time
import pickle
from db import DBInterface

import urllib2 
from multiprocessing.dummy import Pool as ThreadPool 

def remove_unicode(x):
    return x.decode('unicode_escape').encode('ascii','ignore')

def get_samples(site):
    print "Getting %s" % site
    return twiki.get_samples(assigned_to="all", username="namin", get_unmade=False, page=site)

sites = [
# "Run2_Data",
"Run2_Data2016",
"Run2Samples25ns80X",
"Run2Samples25ns80XminiAODv2",
"Run2Samples25ns80XPrivate",
# "Run2SamplesPrivateSMSFastSim25ns",
# "Run2Samples25ns76XminiAODv2",
# "Run2SamplesSMSFastSim_25ns",
# "Run2SamplesReMINIAOD_25ns",
# "Run2Samples_25ns",
"Run2Samples25ns80XFS",
"Run2Samples25nsMoriond17",
"testTwiki", # used for testing various things
]

db = DBInterface(fname="allsamples.db")
db.drop_table()
db.make_table()

pool = ThreadPool(4)
site_samples = pool.map(get_samples, sites)
pool.close()
pool.join()

isample = 0
for site,samples in zip(sites,site_samples):
    for sample in samples:
        s = {}

        if "dataset" not in sample: continue

        s["sample_type"] = "CMS3"
        s["twiki_name"] = site
        s["dataset_name"] = sample["dataset"]
        s["location"] = sample.get("location","")
        s["filter_type"] = sample.get("filter_type","")
        s["nevents_in"] = sample.get("nevents_in",-1)
        s["nevents_out"] = sample.get("nevents_out",-1)
        s["filter_eff"] = sample.get("efact",-1)
        s["xsec"] = sample.get("xsec",-1)
        s["kfactor"] = sample.get("kfact",-1)
        s["gtag"] = sample.get("gtag","")
        s["cms3tag"] = sample.get("cms3tag","")
        s["assigned_to"] = sample.get("assigned","")
        s["comments"] = remove_unicode(sample.get("comments",""))
        s["timestamp"] = int(time.time())

        db.update_sample(s)
        isample += 1

db.close()

print "saved %i samples in total" % isample
