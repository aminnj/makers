import os, sys
import pycurl 
import StringIO 
import ast
import urllib2
import json
import traceback
import sys
import commands


def get(cmd, returnStatus=False):
    status, out = commands.getstatusoutput(cmd)
    if returnStatus: return status, out
    else: return out

def cmd(cmd, returnStatus=False):
    status, out = commands.getstatusoutput(cmd)
    if returnStatus: return status, out
    else: return out

def proxy_hours_left():
    try:
        info = get("voms-proxy-info")
        hours = int(info.split("timeleft")[-1].strip().split(":")[1])
    except: hours = 0
    return hours

def proxy_renew():
    # http://www.t2.ucsd.edu/tastwiki/bin/view/CMS/LongLivedProxy
    cert_file = "/home/users/{0}/.globus/proxy_for_{0}.file".format(os.getenv("USER"))
    if os.path.exists(cert_file): cmd("voms-proxy-init -q -voms cms -hours 120 -valid=120:0 -cert=%s" % cert_file)
    else: cmd("voms-proxy-init -hours 9876543:0 -out=%s" % cert_file)

def get_proxy_file():
    cert_file = '/tmp/x509up_u%s' % str(os.getuid()) # TODO: check that this is the same as `voms-proxy-info -path`
    return cert_file

def get_dbs_url(url):
    # get json from a dbs url (API ref is at https://cmsweb.cern.ch/dbs/prod/global/DBSReader/)
    b = StringIO.StringIO() 
    c = pycurl.Curl() 
    cert = get_proxy_file()
    c.setopt(pycurl.WRITEFUNCTION, b.write) 
    c.setopt(pycurl.CAPATH, '/etc/grid-security/certificates') 
    c.unsetopt(pycurl.CAINFO)
    c.setopt(pycurl.SSLCERT, cert)
    c.setopt(pycurl.URL, url) 
    c.perform() 
    s = b.getvalue().replace("null","None")
    ret = ast.literal_eval(s)
    return ret

def get_dbs_instance(dataset):
    if dataset.endswith("/USER"): return "phys03"
    else: return "global"

def dataset_event_count(dataset):
    # get event count and other information from dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/filesummaries?dataset=%s&validFileOnly=1" % (get_dbs_instance(dataset),dataset)
    ret = get_dbs_url(url)
    if len(ret) > 0:
        if ret[0]:
            return { "nevents": ret[0]['num_event'], "filesizeGB": round(ret[0]['file_size']/1.9e9,2), "nfiles": ret[0]['num_file'], "nlumis": ret[0]['num_lumi'] }
    return None

def list_of_datasets(wildcardeddataset, short=False):
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasets?dataset=%s&detail=0" % (get_dbs_instance(wildcardeddataset),wildcardeddataset)
    ret = get_dbs_url(url)
    if len(ret) > 0:
            vals = []
            for d in ret:
                dataset = d["dataset"]
                if short:
                    vals.append(dataset)
                else:
                    info = dataset_event_count(dataset)
                    info["dataset"] = dataset
                    vals.append(info)
            return vals
    return []

def get_dataset_files(dataset):
    # return list of 3-tuples (LFN, nevents, size_in_GB) of files in a given dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/files?dataset=%s&validFileOnly=1&detail=1" % (get_dbs_instance(dataset),dataset)
    ret = get_dbs_url(url)
    files = []
    for f in ret:
        files.append( [f['logical_file_name'], f['event_count'], f['file_size']/1.0e9] )
    return files

def get_dataset_parent(dataset):
    # get parent of a given dataset
    ret = get_dbs_url("https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasetparents?dataset=%s" % (get_dbs_instance(dataset),dataset))
    if len(ret) < 1: return None
    return ret[0].get('parent_dataset', None)

def get_gen_sim(dataset):
    # recurses up the tree of parent datasets until it finds the gen_sim dataset
    while "GEN-SIM" not in dataset:
        dataset = get_dataset_parent(dataset)
        if not dataset: break
    return dataset if "GEN-SIM" in dataset else None

def get_mcm_json(dataset):
    # get McM json for given dataset
    url = "https://cms-pdmv.cern.ch/mcm/public/restapi/requests/produces/"+dataset
    mcm_json = json.load(urllib2.urlopen(url))
    return mcm_json

def get_slim_mcm_json(dataset):
    out = {}
    mcm_json = get_mcm_json(dataset)
    
    try: out['cross_section'] = mcm_json['results']['generator_parameters'][-1]['cross_section']
    except: pass

    try: out['filter_efficiency'] = mcm_json['results']['generator_parameters'][-1]['filter_efficiency']
    except: pass

    try: out['match_efficiency'] = mcm_json['results']['generator_parameters'][-1]['match_efficiency']
    except: pass

    try: out['cmssw_release'] = mcm_json['results']['cmssw_release']
    except: pass

    try: out['mcdb_id'] = mcm_json['results']['mcdb_id']
    except: pass

    try: out['fragment'] = mcm_json['results']['fragment']
    except: pass

    return out

def filelist_to_dict(files, short=False):
    newfiles = []
    for f in files:
        newfiles.append({"name": f[0], "nevents": f[1], "sizeGB": round(f[2],2)})
    if short: newfiles = newfiles[:5]
    return newfiles

def make_response(query, payload, failed, fail_reason):
    status = "success"
    if failed: status = "failed"

    return json.dumps( { "query": query, "response": { "status": status, "fail_reason": fail_reason, "payload": payload } } )
    # return { "query": query, "response": { "status": status, "fail_reason": fail_reason, "payload": payload } }

if __name__=='__main__':

    arg_dict = {}
    # arg_dict = {"dataset": "/TChiChi_mChi-150_mLSP-1_step1/namin-TChiChi_mChi-150_mLSP-1_step1-695fadc5ae5b65c0e37b75e981d30125/USER", "type":"files"}
    # arg_dict = {"dataset": "/TChiNeu*/namin-TChiNeu*/USER", "type":"files"}

    if not arg_dict:
        arg_dict_str = sys.argv[1]
        arg_dict = ast.literal_eval(arg_dict_str)

    query_type = arg_dict.get("type","basic")
    dataset = arg_dict.get("dataset", None)
    short = arg_dict.get("short", False)

    failed = False
    fail_reason = ""
    payload = {}

    if "*" in dataset:
        query_type = "listdatasets"

    if proxy_hours_left() < 5: proxy_renew()

    if not dataset:
        failed = True
        fail_reason = "Dataset not specified"


    try:
        if query_type == "basic":
            info = dataset_event_count(dataset)
            if not info:
                failed = True
                fail_reason = "Dataset not found"
            payload = info

        if query_type == "listdatasets":
            datasets = list_of_datasets(dataset, short)
            if not datasets:
                failed = True
                fail_reason = "No datasets found"
            payload = datasets

        elif query_type == "files":
            files = get_dataset_files(dataset)
            payload["files"] = filelist_to_dict(files, short)

        elif query_type == "mcm":
            gen_sim = get_gen_sim(dataset)
            if short:
                info = get_slim_mcm_json(gen_sim)
            else:
                info = get_mcm_json(gen_sim)["results"]
            info["gensim"] = gen_sim
            payload = info

        elif query_type == "lhe":
            gen_sim = get_gen_sim(dataset)
            lhe = get_dataset_parent(gen_sim)
            files = get_dataset_files(lhe)
            payload["files"] = filelist_to_dict(files, short)

        else:
            failed = True
            fail_reason = "Query type not found"
    except:
        failed = True
        fail_reason = traceback.format_exc()

    print make_response(arg_dict, payload, failed, fail_reason)




