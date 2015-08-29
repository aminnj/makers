import json, urllib, os

def sayText(text):
    print 'espeak "%s"' % text
    # os.system('espeak "%s"' % text)

storage = "meter.txt"
url = "http://uaf-6.t2.ucsd.edu/~namin/makers/meterMaker/data.txt"

fh = open(storage,"r")
oldinfo = json.loads(fh.read().strip())
newinfo = json.loads(urllib.urlopen(url).read())
fh = open(storage,"w")
fh.write(json.dumps(newinfo))
fh.close()

for i,meter in enumerate(oldinfo["meters"]):
    oldfrac = float(oldinfo["meters"][i]["pointer"]) 
    newfrac = float(newinfo["meters"][i]["pointer"])
    metertitle = oldinfo["meters"][i]["title"]
    metertitle = metertitle.replace("Meter","").replace("meter","")
    if(abs(oldfrac-newfrac) > 0.05):
        sayText("%s meter was changed from %i percent to %i percent" % (metertitle, 100*oldfrac, 100*newfrac))
        break

