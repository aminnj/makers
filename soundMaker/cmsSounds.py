import json, urllib, os

def playSound(filename):
    # there might be flags for aplay we want to use later
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
newStatus = info["status"].lower().strip()
beams = info["isgood"]["beams"] 
bfield = info["isgood"]["bfield"] 
systems = info["isgood"]["systems"]
isTakingData = beams and bfield and systems
fh = open(storage,"w")
fh.write(newStatus + " " + str(int(beams)) + " " + str(int(bfield)) + " " + str(int(systems)))
fh.close()

# print wasTakingData, isTakingData
# print prevStatus, newStatus

# If status changed, play some sounds
if newStatus != prevStatus:
    if(isTakingData and not wasTakingData):
        print ">>> Starting collecting data!"
        playSound("takingdata.wav")
    elif("dump" in newStatus):
        print ">>> Beam dump!"
        playSound("beamdump.wav")
    else:
        pass


