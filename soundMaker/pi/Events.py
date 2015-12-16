import threading
import time
import datetime
import os
import utils as u

DELAY = 2 # seconds
THRESHOLD = 20 # seconds
TIMEFILE = "times.txt"

class Events:
    def __init__(self, delay=2, threshold=20, timefile="times.txt"):
        self.DELAY=delay # how often to check
        self.THRESHOLD=threshold # how many seconds within a trigger time to act
        self.TIMEFILE=timefile # output/input file
        self.events = []
        self.doLoop = False

        if not os.path.isfile(TIMEFILE): os.system("touch %s" % TIMEFILE)

        self.thread = threading.Thread(target=self.loop)
        self.thread.setDaemon(True)

    def readTimes(self):
        print "[times] reading events"
        with open(self.TIMEFILE,"r") as infile:
        # with open("timesbck.txt","r") as infile:
            lines = infile.readlines()
            lines = [line.strip() for line in lines if len(lines)>2]
            for line in lines:
                ta, tb, action = line.split(" ",2)
                ta, tb = u.fromTimestamp(ta), u.fromTimestamp(tb)
                self.events.append( [ta,tb, action] )
            # events = [map(fromTimestamp,line.split()) for line in lines if len(line) > 2]
        # return events

    def checkTimes(self):
        print "[times] checking events"
        leftoverEvents = []
        for event in self.events:
            ta,tb,action = event
            # print pair[1] - pair[0]
            # secsLeft = (tb-ta).seconds # FIXME change to secsLeft = (time.now()-tb).seconds
            # secsLeft = (datetime.datetime.now()-tb).seconds
            tb = u.toTimestamp(tb)
            now = u.toTimestamp(datetime.datetime.now())
            print now-tb
            secsLeft = int(now-tb)
            # print tb-datetime.datetime.now()
            # print "SECSLEFT", secsLeft
            if secsLeft > -self.THRESHOLD:
                self.handleTime(event)
                continue

            leftoverEvents.append(event)

        self.events = leftoverEvents[:]
        # return leftoverEvents

    def handleTime(self,event):
        print "[times] handling time"
        ta, tb, action = event
        # print ta, tb
        # print ta, tb
        # print u.humanReadableTime( tb - ta )

        # secsLeft = (datetime.datetime.now()-tb).seconds
        dt = (datetime.datetime.now() - ta)

        if action == "ALARM":
            print "Nick, %s ago you asked me to alarm you" % (u.humanReadableTime(dt=dt))
        else:
            print "Nick, %s ago you asked me to remind you to %s" % (u.humanReadableTime(dt=dt), action)



    def writeTimes(self):
        print "[times] writing times"
        with open(TIMEFILE,"w") as outfile:
            for ta, tb, action in self.events:
                outfile.write("%i %i %s\n" % (u.toTimestamp(ta), u.toTimestamp(tb),action))
                # print "%i %i" % (toTimestamp(ta), toTimestamp(tb))

    def addEvent(self,ta,tb,action):
        self.events.append([ta, tb, action])

    def startLoop(self):
        self.doLoop = True
        self.thread.start()

    def stopLoop(self):
        self.doLoop = False
        # doesn't actually kill the thread

    def loop(self):
        while self.doLoop:
            self.readTimes()
            self.checkTimes()
            self.writeTimes()
            time.sleep(self.DELAY)



if __name__ == '__main__':
    events = Events()
    events.startLoop()
    while True:
        test = raw_input("test")
        print test
        if test == "e":
            events.stopLoop()
        if test == "a":
            ta = u.fromTimestamp(1450306547)
            tb = u.fromTimestamp(1450306647)
            events.addEvent(ta,tb, "another thing")

