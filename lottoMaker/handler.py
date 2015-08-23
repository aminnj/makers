#!/usr/bin/python
import cgi, cgitb 
import os, sys, commands
import json


datafile = "data.txt"
data = {}
data["bets"] = []

def inputToDict(form):
    d = {}
    for k in form.keys():
        d[k] = form[k].value
    return d

def loadBets():
    global data
    fh = open(datafile, "r")
    data = json.loads(fh.read().strip())
    fh.close()

def writeBets():
    global data
    fh = open(datafile, "w")
    fh.write( json.dumps(data,indent=2) )
    fh.close()

def getBets():
    global data
    return json.dumps(data,indent=2)

def createBet(input):
    optionKeys = []
    # do it this way so that order of options is always preserved
    for i in range(10):
        if("option"+str(i) in input.keys()):
            optionKeys.append("option"+str(i))
    
    if "shortTitle" not in input:
        return "Name your bet."
    if(len(optionKeys) < 2):
        return "You must provide at least 2 options."

    bet = {}
    bet["shortTitle"] = input["shortTitle"]
    bet["description"] = input["description"] if "description" in input else ""
    bet["options"] = []
    for opt in optionKeys:
        option = {}
        option["name"] = input[opt]
        option["betters"] = []
        bet["options"].append(option)

    data["bets"].append(bet)


    return "good to go bro"



form = cgi.FieldStorage()

print "Content-type:text/html\r\n"
input = inputToDict(form)

# input = {"action": "createBet", "shortTitle": "my bet", "description": "this is my bet description", "option1": "less than 5/pb", "option2": "between 5/pb and 10/pb", "option3": "above 10/pb"}
# input = {"action": "getBets"}

loadBets()
if(input['action'] == "createBet"):
    print createBet(input)
    writeBets()
if(input['action'] == "getBets"):
    print getBets()

