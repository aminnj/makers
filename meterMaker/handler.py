#!/usr/bin/python
import cgi, cgitb 
import os, sys, commands
import json


datafile = "data.txt"
data = {}
data["meters"] = []

def inputToDict(form):
    d = {}
    for k in form.keys():
        d[k] = form[k].value
    return d

def loadMeters():
    global data
    fh = open(datafile, "r")
    data = json.loads(fh.read().strip())
    fh.close()

def writeMeters():
    global data
    fh = open(datafile, "w")
    fh.write( json.dumps(data,indent=2) )
    fh.close()

def getMeters():
    global data
    return json.dumps(data,indent=2)

def updateMeter(input):
    print input
    meterIdx = int(input["meterIdx"])
    pointerFraction = float(input["pointerFraction"])
    if(meterIdx >= len(data["meters"])):
      print "Woah there dude! Invalid canvas index!"
      return
    if( not ( 0.0 < pointerFraction < 1.0) ):
      print "Woah there dude! Invalid pointer fraction!"
      return

    data["meters"][meterIdx]["pointer"] = pointerFraction
    print "Updated meter %i to %i%%" % (meterIdx, round(100.0*pointerFraction))

form = cgi.FieldStorage()

print "Content-type:text/html\r\n"
input = inputToDict(form)

# test POST dictionaries

# input = {"action": "getMeters"}
# input = {"action": "updateMeter", "meterIdx": 2, "pointerFraction": 0.5}

loadMeters()
if(input['action'] == "updateMeter"):
    print updateMeter(input)
    writeMeters()
if(input['action'] == "getMeters"):
    print getMeters()

