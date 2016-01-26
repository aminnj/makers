#!/usr/bin/python
import cgi, cgitb 
import os, sys, commands
import json


datafile = "data.txt"
data = {}
data["meters"] = []

PI_URL = 'http://128.111.19.91:8080/say'

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
    return data

def writeMeters():
    global data
    fh = open(datafile, "w")
    fh.write( json.dumps(data,indent=2) )
    fh.close()

def getMeters():
    global data
    return json.dumps(data,indent=2)

def forSoundMaker(input):

    meterIdx = int(input["meterIdx"])
    pointerFraction = float(input["pointerFraction"])
    oldPointerFraction = oldInput["meters"][meterIdx]["pointer"]
    shortTitle = oldInput["meters"][meterIdx]["title"]
    sayMeter, sayThe = "meter", "the"
    if shortTitle.strip().lower().endswith("meter"): sayMeter = "" # don't say meter twice
    if shortTitle.strip().lower().startswith("the"): sayThe = ""
    toSay = "%s %s %s was changed from %i to %i percent" % (sayThe, shortTitle, sayMeter, round(100.0*oldPointerFraction), round(100.0*pointerFraction))

    import urllib
    import urllib2
    payload = urllib.urlencode({'words' : toSay, 'type' : "meterMaker" })
    req = urllib2.Request(PI_URL, payload)
    response = urllib2.urlopen(req)
    the_page = response.read()

def updateMeter(input):
    # print input
    meterIdx = int(input["meterIdx"])
    pointerFraction = float(input["pointerFraction"])
    if(meterIdx >= len(data["meters"])):
        print "Woah there dude! Invalid canvas index!"
        return
    if( not ( 0.0 < pointerFraction < 1.0) ):
        print "Woah there dude! Invalid pointer fraction!"
        return

    try:
        forSoundMaker(input)
    except:
        pass

    data["meters"][meterIdx]["pointer"] = pointerFraction
    print "Updated meter %i to %i%%" % (meterIdx, round(100.0*pointerFraction))

def createMeter(input):
    # make things empty if they don't exist
    ls = ["pointerFraction","shortTitle"]
    ls.extend( ["label"+str(i) for i in range(1,7)] )
    ls.extend( ["rgb"+str(i) for i in range(1,7)] )
    ls.extend( ["fraction"+str(i) for i in range(1,7)] )
    for e in ls:
        if(e not in input): input[e] = ""

    pointerFraction = 0.5
    if( not (0.0 < pointerFraction < 1.0 and len(input["pointerFraction"]) < 1) ):
        pointerFraction = float(input["pointerFraction"])


    slices = []
    for i in range(1,7):
        label = input["label"+str(i)]
        rgb = input["rgb"+str(i)]
        fraction = -1
        if(len(input["fraction"+str(i)]) > 0):
            fraction = float(input["fraction"+str(i)])
        if(len(rgb) < 1): continue

        if( not (0.0 < fraction < 1.0) ): fraction = -1.0
        slices.append( [label, rgb, fraction] )


    if(len(slices) < 1):
        print "You don't have any valid slices. Make sure RGB is provided."
        return


    autoDivide = False
    totalFraction = 0.0
    for label, rgb, fraction in slices:
        if fraction < 0:
            autoDivide = True
        else:
            totalFraction += fraction

    # if fractions don't add up to 1, make last slice pick up the slack
    if(not autoDivide):
        if(totalFraction < 1.0):
            slices[-1][2] += 1.0 - totalFraction
    else:
        for i in range(len(slices)):
            slices[i][2] = 1.0/len(slices)

    newMeter = { }
    newMeter["pointer"] = pointerFraction
    newMeter["title"] = input["shortTitle"]
    newMeter["slices"] = []
    totalFraction = 0.0
    for label, rgb, fraction in slices:
        slice = { }

        slice["color"] = rgb
        slice["label"] = label
        slice["fraction"] = fraction

        newMeter["slices"].append(slice)

    data["meters"].append(newMeter)
    print "Successfully added a new meter!"

form = cgi.FieldStorage()

print "Content-type:text/html\r\n"
input = inputToDict(form)


# test POST dictionaries

# input = {"action": "getMeters"}
# input = {"action": "updateMeter", "meterIdx": 2, "pointerFraction": 0.5}

# input = {"action": "createMeter", "shortTitle": "", "pointerFraction": "", 
# "label1":"test","label2":"test","label3":"test","label4":"","label5":"","label6":"","rgb1":"#f1f1f1","rgb2":"#fff1ff","rgb3":"#0f00ff","rgb4":"","rgb5":"","rgb6":"",
# "fraction1":"","fraction2":"","fraction3":"","fraction4":"","fraction5":"","fraction6":""}

oldInput = loadMeters()
if(input['action'] == "updateMeter"):
    updateMeter(input)
    writeMeters()
if(input['action'] == "getMeters"):
    print getMeters()
if(input['action'] == "createMeter"):
    createMeter(input)
    writeMeters()

