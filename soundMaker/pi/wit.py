import urllib
import urllib2
import json
import datetime
import utils as u
import time
from dateutil import parser
import sys
import Events

# data = {'access_token' : '5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP', 'q' : "remind me to pick up items in 37 minutes" }
data = {'access_token' : '5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP', 'q' : "remind me to pick up items at 11pm tomorrow" }
# data = {'access_token' : '5WGVQPPDHU7JH2J5WDBJHMJLRXB5WDTP', 'q' : "set a timer in 2 hours" }

# response = urllib2.urlopen('https://api.wit.ai/message?'+urllib.urlencode(data)).read()
# print response
# out = json.loads(response)

# out = {
#   "msg_id" : "a6b9089d-b8a6-4ac1-8adc-52f43a821db1",
#   "_text" : "remind me to pick up items at 11pm tomorrow",
#   "outcomes" : [ {
#     "_text" : "remind me to pick up items at 11pm tomorrow",
#     "confidence" : 0.57,
#     "intent" : "reminder",
#     "entities" : {
#       "datetime" : [ {
#         "type" : "value",
#         "value" : "2015-12-16T23:00:00.000-08:00",
#         "grain" : "hour",
#         "values" : [ {
#           "type" : "value",
#           "value" : "2015-12-16T23:00:00.000-08:00",
#           "grain" : "hour"
#         } ]
#       } ],
#       "reminder" : [ {
#         "entities" : { },
#         "type" : "value",
#         "value" : "pick up items",
#         "suggested" : True
#       } ],
#       "contact" : [ {
#         "type" : "value",
#         "value" : "me",
#         "suggested" : True
#       } ]
#     }
#   } ]
# }


out = {
  "msg_id" : "3bb7c361-c932-43c1-94b8-0cf511484836",
  "_text" : "set a timer in 20 seconds",
  "outcomes" : [ {
    "_text" : "set a timer in 20 seconds",
    "confidence" : 0.556,
    "intent" : "timer",
    "entities" : {
      "duration" : [ {
        "hour" : 2,
        "value" : 2,
        "unit" : "hour",
        "normalized" : {
          "value" : 20,
          "unit" : "second"
        }
      } ]
    }
  } ]
}


events = Events.Events(delay=3,threshold=10)
events.startLoop()

intent = None
try: intent = out["outcomes"][0]["intent"]
except: pass

if intent == "reminder":
    entities = out["outcomes"][0]["entities"]
    what = entities["reminder"][0]["value"]
    when = entities["datetime"][0]["value"]
    when = parser.parse(when).replace(tzinfo=None)

    now = datetime.datetime.now()
    dt = when - now

    events.addEvent(now, when, what)

elif intent == "timer":
    seconds = out["outcomes"][0]["entities"]["duration"][0]["normalized"]["value"] # seconds

    now = datetime.datetime.now()
    when = now + datetime.timedelta(seconds=seconds)
    # print now, when
    dt = when - now

    events.addEvent(now, when, "ALARM")


time.sleep(30)
