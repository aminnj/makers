import json, urllib, os

def playSound(filename):
    # There might be flags for aplay we want to use later
    os.system("aplay %s" % filename)

storage = "status.txt"
url = "http://uaf-6.t2.ucsd.edu/~namin/monitoring/monitor.json"

# Get previous status
fh = open(storage,"r")
info = fh.read().lower().strip()
prevStatus = info.split()[0]
wasTakingData = sum(map(int, info.split()[1:])) == 3
fh.close()

# Get new status
info = json.loads(urllib.urlopen(url).read())
newStatus = info["status"].lower().strip().replace(" ","")
beams = info["isgood"]["beams"] 
bfield = info["isgood"]["bfield"] 
systems = info["isgood"]["systems"]
isTakingData = beams and bfield and systems
fh = open(storage,"w")
fh.write(newStatus + " " + str(int(beams)) + " " + str(int(bfield)) + " " + str(int(systems)))
fh.close()

# Play some sounds
if(isTakingData and not wasTakingData):
    print ">>> Starting collecting data!"
    playSound("takingdata.wav")
elif("dump" in newStatus and "dump" not in prevStatus):
    print ">>> Beam dump!"
    playSound("beamdump.wav")
else: pass

