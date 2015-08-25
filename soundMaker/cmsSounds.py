import json, urllib, os


def playSound(filename):
    # There might be flags for aplay we want to use later
    os.system("aplay %s" % filename)

sounds = True
storage = "status.txt"
url = "http://uaf-6.t2.ucsd.edu/~namin/monitoring/monitor.json"
#url = "../cmsMonitorMaker/monitor.json"


# Get previous status
fh = open(storage,"r")
info = fh.read().lower().strip()
prevStatus = info.split()[0]
prevLastDump = info.split()[1]
wasTakingData = sum(map(int, info.split()[2:])) == 3
fh.close()

# Get new status
info = json.loads(urllib.urlopen(url).read())
#info = json.loads(open(url).read())
newStatus = info["status"].lower().strip().replace(" ","")
beams = info["isgood"]["beams"] 
bfield = info["isgood"]["bfield"] 
systems = info["isgood"]["systems"]
newLastDump = info["lastbeamdump"]
isTakingData = beams and bfield and systems
fh = open(storage,"w")
fh.write(newStatus + " " + newLastDump + " " + str(int(beams)) + " " + str(int(bfield)) + " " + str(int(systems)))
fh.close()

# Play some sounds
if(isTakingData and not wasTakingData):
    print ">>> Starting collecting data!"
    if(sounds): playSound("datacollection.wav")
elif prevLastDump != newLastDump:
    print ">>> Beam dump!"
    if(sounds): playSound("beamdump_withvoice.wav")
else: pass

