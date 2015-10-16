#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb 
from datetime import date
import random
import os, sys, commands, json, urllib2


form = cgi.FieldStorage()

jsonName = form.getvalue("json")

jsonDir = 'jsons/'

if jsonName:
    print "Content-type:text/xml\r\n"
    shortName = jsonName.split("/")[-1]
    filename = jsonDir+shortName

    # download and save json if it doesn't exist
    if("/afs/" in jsonName):
        if not os.path.isfile(filename):

            # download from lxplus
            url = "http://namin.web.cern.ch/namin/getJSON.php?json=%s" % (jsonName)
            output = urllib2.urlopen(url).read()
            if(len(output) > 10):
                fh = open(filename, "w")
                fh.write(output)
                fh.close()
    else:
        # copy from uaf
        os.system("cp %s %s/%s" % (jsonName, jsonDir, shortName))
        pass
        # /home/users/namin/sandbox/missingLumis/json.txt
            

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

else:

    print "Content-type:text/html\r\n"
    print "<html>"
    print "<body>"
    print "Hey, try putting something like"
    print "<pre>    ?json=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-257599_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt</pre>"
    print "at the end of the url to fetch from lxplus, or you can even look at the UAF"
    print "<pre>    ?json=/home/users/namin/sandbox/missingLumis/json.txt</pre>"
    print "</body>"
    print "</html>"
