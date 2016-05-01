import sys
# sys.path.insert(0, "../dashboard/")
sys.path.insert(0, "/home/users/namin/forFrank/NtupleTools/AutoTwopler/dashboard/")
import twiki
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
"Run2Samples25ns80X",
"Run2Samples25ns80XPrivate",
"Run2SamplesPrivateSMSFastSim25ns",
"Run2Samples25ns76XminiAODv2",
"Run2SamplesSMSFastSim_25ns",
"Run2SamplesReMINIAOD_25ns",
"Run2Samples_25ns",
"SMS_T5ttttDM175_74X",
"SMS_T5qqqqWW_74X",
"SMS_T5ttcc_74X",
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

        s["sample_type"] = "CMS3"
        s["twiki_name"] = site
        s["dataset_name"] = sample["dataset"]
        s["location"] = sample["location"]
        s["filter_type"] = sample["filter_type"]
        s["nevents_in"] = sample["nevents_in"]
        s["nevents_out"] = sample["nevents_out"]
        s["filter_eff"] = sample["efact"]
        s["xsec"] = sample["xsec"]
        s["kfactor"] = sample["kfact"]
        s["gtag"] = sample["gtag"]
        s["cms3tag"] = sample["cms3tag"]
        s["assigned_to"] = sample["assigned"]
        s["comments"] = remove_unicode(sample["comments"])

        db.update_sample(s)
        isample += 1

db.close()

print "saved %i samples in total" % isample
