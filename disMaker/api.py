import os
import sys
import pycurl 
import StringIO 
import ast
import urllib2
import json
import traceback
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
    cert_file = "/home/users/{0}/.globus/proxy_for_{0}.file".format(get("whoami").strip())
    if os.path.exists(cert_file): cmd("voms-proxy-init -q -voms cms -hours 120 -valid=120:0 -cert=%s" % cert_file)
    else: cmd("voms-proxy-init -hours 9876543:0 -out=%s" % cert_file)

def get_proxy_file():
    cert_file = '/tmp/x509up_u%s' % str(os.getuid()) # TODO: check that this is the same as `voms-proxy-info -path`
    return cert_file

def get_url_with_cert(url, return_raw=False):
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
    s = b.getvalue()
    if return_raw: return s
    s = s.replace("null","None")
    ret = ast.literal_eval(s)
    return ret

def get_dbs_instance(dataset):
    if dataset.endswith("/USER"): return "phys03"
    elif "Nick" in dataset: return "phys03"
    else: return "global"

def dataset_event_count(dataset):
    # get event count and other information from dataset
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/filesummaries?dataset=%s&validFileOnly=1" % (get_dbs_instance(dataset),dataset)
    ret = get_url_with_cert(url)
    if len(ret) > 0:
        if ret[0]:
            return { "nevents": ret[0]['num_event'], "filesizeGB": round(ret[0]['file_size']/1.9e9,2), "nfiles": ret[0]['num_file'], "nlumis": ret[0]['num_lumi'] }
    return None

def list_of_datasets(wildcardeddataset, short=False):
    url = "https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasets?dataset=%s&detail=0" % (get_dbs_instance(wildcardeddataset),wildcardeddataset)
    ret = get_url_with_cert(url)
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
    ret = get_url_with_cert(url)
    files = []
    for f in ret:
        files.append( [f['logical_file_name'], f['event_count'], f['file_size']/1.0e9] )
    return files

def get_dataset_parent(dataset):
    # get parent of a given dataset
    ret = get_url_with_cert("https://cmsweb.cern.ch/dbs/prod/%s/DBSReader/datasetparents?dataset=%s" % (get_dbs_instance(dataset),dataset))
    if len(ret) < 1: return None
    return ret[0].get('parent_dataset', None)

def get_specified_parent(dataset, typ="LHE", fallback=None):
    # recurses up the tree of parent datasets until it finds the gen_sim dataset
    found = False
    for i in range(4):
        dataset = get_dataset_parent(dataset)
        if not dataset: break
        if typ in dataset or fallback and fallback in dataset: 
            found = True
            break

    if found:
        return dataset
    else:
        raise LookupError("Could not find parent dataset")

def get_mcm_json(dataset):
    # get McM json for given dataset
    url = "https://cms-pdmv.cern.ch/mcm/public/restapi/requests/produces/"+dataset
    mcm_json = json.load(urllib2.urlopen(url))
    return mcm_json

def get_mcm_setup(campaign):
    # get McM json for given dataset
    url = "https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_setup/"+campaign
    ret_data = urllib2.urlopen(url).read()
    if "#!/bin/bash" in ret_data: ret_data = "\n" + ret_data
    return ret_data

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


def handle_query(arg_dict):

    query_type = arg_dict.get("type","basic")
    query = arg_dict.get("query", None).strip()
    short = arg_dict.get("short", False)


    # parse extra information in query if it's not just the dataset
    # /Gjet*/*/*, cms3tag=*07*06* | grep location,dataset_name
    # ^^dataset^^ ^^^selectors^^^   ^^^^^^^^^^^pipes^^^^^^^^^^
    selectors = None
    pipes = None
    if "|" in query:
        first = query.split("|")[0].strip()
        pipes = query.split("|")[1:]

        if "," in first:
            entity = first.split(",")[0].strip()
            selectors = first.split(",")[1:]
        else:
            entity = first
    elif "," in query:
        entity = query.split(",")[0].strip()
        selectors = query.split(",")[1:]
    else:
        entity = query.strip()

    failed = False
    fail_reason = ""
    payload = {}

    if "*" in entity and query_type in ["basic","files"]:
        query_type = "listdatasets"

    if query_type in ["basic", "files", "listdatasets", "mcm", "driver", "lhe"]:
        if proxy_hours_left() < 5: proxy_renew()

    if not entity:
        failed = True
        fail_reason = "Dataset not specified"


    try:
        if query_type == "basic":
            info = dataset_event_count(entity)
            if not info:
                failed = True
                fail_reason = "Dataset not found"
            payload = info

        elif query_type == "listdatasets":
            datasets = list_of_datasets(entity, short)
            if not datasets:
                failed = True
                fail_reason = "No datasets found"
            payload = datasets

        elif query_type == "files":
            files = get_dataset_files(entity)
            payload["files"] = filelist_to_dict(files, short)

        elif query_type == "mcm":
            gen_sim = get_specified_parent(entity, typ="GEN-SIM", fallback="AODSIM")
            if short:
                info = get_slim_mcm_json(gen_sim)
            else:
                info = get_mcm_json(gen_sim)["results"]
            info["gensim"] = gen_sim
            payload = info

        elif query_type == "driver":
            gen_sim = get_specified_parent(entity, typ="GEN-SIM", fallback="AODSIM")
            info = get_mcm_json(gen_sim)["results"]
            dataset_base = info["dataset_name"]
            campaign = info["prepid"]
            driver = get_mcm_setup(campaign)
            payload = { "dataset": dataset_base, "cmsDriver": driver }

        elif query_type == "lhe":
            lhe = get_specified_parent(entity, typ="LHE")
            # lhe = get_dataset_parent(gen_sim)
            files = get_dataset_files(lhe)
            payload["files"] = filelist_to_dict(files, short)

        elif query_type == "snt":
            from db import DBInterface
            db = DBInterface(fname="allsamples.db")

            match_dict = {"dataset_name": entity}

            if selectors:
                for more in selectors:
                    key = more.split("=")[0].strip()
                    val = more.split("=")[1].strip()
                    match_dict[key] = val

            samples = db.fetch_samples_matching(match_dict)

            if short:
                new_samples = []
                for sample in samples:
                    for key in ["kfactor","nevents_in","sample_id","filter_eff","filter_type","assigned_to", \
                                "comments","gtag","twiki_name","xsec","sample_type"]:
                        del sample[key]
                    new_samples.append(sample)
                samples = new_samples

            payload = samples

        else:
            failed = True
            fail_reason = "Query type not found"
    except:
        failed = True
        fail_reason = traceback.format_exc()

    if pipes:
        for pipe in pipes:
            pipe = pipe.strip()
            parts = pipe.split(" ",1)
            if len(parts) == 2:
                verb, keys = parts
                keys = map(lambda x: x.strip(), keys.split(","))
            else:
                verb = parts[0]

            if verb == "grep":
                for ipay in range(len(payload)):
                    if type(payload[ipay]) is not dict: continue

                    if len(keys) > 1:
                        d = {}
                        for key in keys: d[key] = payload[ipay].get(key,None)
                        payload[ipay] = d
                    else:
                        payload[ipay] = payload[ipay].get(keys[0],None)

    return make_response(arg_dict, payload, failed, fail_reason)


if __name__=='__main__':

    arg_dict = {}
    # arg_dict = {"query": "/TChiChi_mChi-150_mLSP-1_step1/namin-TChiChi_mChi-150_mLSP-1_step1-695fadc5ae5b65c0e37b75e981d30125/USER", "type":"files"}
    # arg_dict = {"query": "/TChiNeu*/namin-TChiNeu*/USER", "type":"files"}
    # arg_dict = {"type": "snt", "query": "/TChiChi_mChi-150_mLSP-1_step1/namin-TChiChi_mChi-150_mLSP-1_step2_miniAOD-eb69b0448a13fda070ca35fd76ab4e24/USER"}
    # arg_dict = {"type": "snt", "query": "/TChiChi*/*/USER", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/TChiChi*/*/USER, gtag=*74X*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*, gtag=*74X*, cms3tag=*07*", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/GJet*HT-400*/*/*, gtag=*74X*, cms3tag=*07* | grep nevents_out,dataset_name", "short":"short"}
    # arg_dict = {"type": "snt", "query": "/G* | grep cms3tag"}
    # arg_dict = {"type": "driver", "query": "/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/MINIAODSIM"}
    # arg_dict = {"type": "lhe", "query": "/SMS-T5qqqqWW_mGl-600to800_mLSP-0to725_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15MiniAODv2-FastAsympt25ns_74X_mcRun2_asymptotic_v2-v1/MINIAODSIM"}
    # arg_dict = {"type": "driver", "query": "/SMS-T5qqqqWW_mGl-600to800_mLSP-0to725_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15MiniAODv2-FastAsympt25ns_74X_mcRun2_asymptotic_v2-v1/MINIAODSIM"}


    if not arg_dict:
        arg_dict_str = sys.argv[1]
        arg_dict = ast.literal_eval(arg_dict_str)

    print handle_query(arg_dict)

