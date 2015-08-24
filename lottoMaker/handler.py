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
    # bet["description"] = input["description"] if "description" in input else ""
    bet["options"] = []
    for opt in optionKeys:
        option = {}
        option["name"] = input[opt]
        option["betters"] = []
        option["amounts"] = []
        bet["options"].append(option)

    data["bets"].append(bet)


    return "Successfully created your bet"

def addBet(input):
    global data

    if("amount" not in input):
        return "How much do you want to bet?"
    if("name" not in input):
        return "What is your name?"

    name = input["name"].replace(" ","").strip().title()
    amount = int(input["amount"])
    ibet = int(input["ibet"])
    iopt = int(input["iopt"])

    # names and amounts for ibet,iopt
    try:
        names = data["bets"][ibet]["options"][iopt]["betters"]
        amounts = data["bets"][ibet]["options"][iopt]["amounts"]
    except:
        return "Invalid bet number and/or bet option. You gave me ibet=%i,iopt=%i." % (ibet, iopt)

    # already has made bet previously
    if(name in names):
        idx = names.index(name)
        data["bets"][ibet]["options"][iopt]["amounts"][idx] += amount
        return "Successfully modified your bet"
    else:
        data["bets"][ibet]["options"][iopt]["betters"].append(name)
        data["bets"][ibet]["options"][iopt]["amounts"].append(amount)
        return "Successfully added your bet"

    return "Shouldn't get here"

def getUsers():
    global data
    users = { }
    for bet in data["bets"]:
      for opt in bet["options"]:
        for i in range(len(opt["betters"])):
          user, amount = opt["betters"][i], opt["amounts"][i]
          if user in users:
            users[user] += amount
          else:
            users[user] = amount

    # convert to list ordered in descending bet amounts
    userList = users.items()
    userList.sort(key=lambda x: x[1], reverse=True)

    return json.dumps( { "users": userList } , indent=2)





form = cgi.FieldStorage()

print "Content-type:text/html\r\n"
input = inputToDict(form)

# test POST dictionaries
# input = {"action": "createBet", "shortTitle": "my bet", "description": "this is my bet description", "option1": "less than 5/pb", "option2": "between 5/pb and 10/pb", "option3": "above 10/pb"}
# input = {"action": "getBets"}
# input = {"action": "addBet", "name":"test", "ibet":0,"iopt":0, "amount":5}
# input = {"action": "getUsers"}

loadBets()
if(input['action'] == "createBet"):
    print createBet(input)
    writeBets()
if(input['action'] == "addBet"):
    print addBet(input)
    writeBets()
if(input['action'] == "getBets"):
    print getBets()
if(input['action'] == "getUsers"):
    print getUsers()

# print getBets()
