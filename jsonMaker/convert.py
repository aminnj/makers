import json, urllib2, sys, os

jsonDir = 'jsons/'
# jsonPrefix = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/"


jsonName = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-257599_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt"
shortName = jsonName.split("/")[-1]
# jsonName = "Cert_246908-257599_13TeV_PromptReco_Collisions15_25ns_JSON_MuonPhys.txt"

filename = jsonDir+shortName

# download and save json if it doesn't exist
if not os.path.isfile(filename):
    url = "http://namin.web.cern.ch/namin/getJSON.php?json=%s" % (jsonName)
    fh = open(filename, "w")
    fh.write(urllib2.urlopen(url).read())
    fh.close()



fh = open(filename, "r")
data = fh.read()
fh.close()
js = json.loads(data)

print "<?xml version='1.0'?>"
print "<?xml-stylesheet type='text/xsl' href='grl.xsl' title='grlview' ?>"
print "<LumiRangeCollection>"
print "  <NamedLumiRange>"
print "    <Name>%s</Name>" % shortName
print "    <Link>%s</Link>" % filename
for run in sorted(js.keys()):
    print "    <LumiBlockCollection>"
    print "      <Run>%s</Run>" % run
    for lumis in js[run]:
        print "      <LBRange Start='%i' End='%i' />" % (lumis[0], lumis[1])
    print "    </LumiBlockCollection>"
print "  </NamedLumiRange>"
print "</LumiRangeCollection>"
