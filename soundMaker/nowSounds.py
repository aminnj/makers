import json, urllib, os, re

def sayText(text):
    os.system('espeak "%s" -s 150 -a 100' % text)

storage = "googlenow.txt"
url = "http://uaf-6.t2.ucsd.edu/~namin/navsa/data.txt"

fh = open(storage,"r")
try:
    oldtime = int(fh.readlines()[-1].strip())
except: oldtime = -1
print oldtime
fh.close()

j = urllib.urlopen(url).readlines()[-1].strip()
j = j.replace("'", '"') # replace single quotes with double or json not happy
newinfo = json.loads(j)
newtime = newinfo["time"]

if newtime > oldtime:

    stuffAfterSay = " ".join(newinfo["words"].split("say")[1:])
    sayText(stuffAfterSay)

    fh = open(storage,"a")
    fh.write(str(newtime) + "\n")
    fh.close()

