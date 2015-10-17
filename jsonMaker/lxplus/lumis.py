import os, sys, commands


jsonDir = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/"
normTag = "/afs/cern.ch/user/c/cmsbril/public/normtag_json/OfflineNormtagV1.json"

fh = open("lumis.txt", "r")
data = fh.readlines()
fh.close()

doneJsonFiles = [e.strip().split()[0] for e in data if len(e) > 3]
# print doneJsonFiles

status,output = commands.getstatusoutput("ls -1 %s" % jsonDir)
jsonFiles = [e for e in output.split("\n") if "Cert" in e and "~" not in e and "ZeroTesla" not in e]
# only calculate lumi for new files

# print jsonFiles
jsonFiles = list(set(jsonFiles)-set(doneJsonFiles))
print jsonFiles
# print doneJsonFiles
# print doneJsonFiles

# print jsonFiles
fh = open("lumis.txt", "a")

for jsonFile in jsonFiles:

# jsonFile = "Cert_246908-247381_13TeV_PromptReco_Collisions15_ZeroTesla_JSON_CaloOnly.txt"


    cmd = "~/.local/bin/brilcalc lumi --normtag %s -u /pb -i %s/%s | grep totrecorded -A 2 | tail -1" % (normTag, jsonDir, jsonFile)
    status,output = commands.getstatusoutput(cmd)
    # print [e.strip() for e in output.split("|") if len(e.strip())>0]
    # | nfill | nrun | nls  | ncms | totdelivered(/pb) | totrecorded(/pb) |
    nfill, nrun, nls, ncms, totdelivered, totrecorded = [e.strip() for e in output.split("|") if len(e.strip())>0]

    # print "%s %s %s %s %s %s %s" % (jsonDir+jsonFile, nfill, nrun, nls, ncms, totdelivered, totrecorded)
    print "%s %s %s" % (jsonFile, totdelivered, totrecorded)
    fh.write( "%s %s %s\n" % (jsonFile, totdelivered, totrecorded) )

fh.close()
