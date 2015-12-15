from bottle import post, route, run, request
import os, sys


# Test with:
#   import urllib
#   import urllib2
#   data = urllib.urlencode({'words' : 'this is a test', 'accel' : 0.012 })
#   req = urllib2.Request('http://169.231.9.192:8080/say', data)
#   response = urllib2.urlopen(req)
#   the_page = response.read()

def getCommand(words,reqType=None):
    if reqType == "meterMaker":
        return 'espeak "%s" &' % words

    elif reqType == "voice":

      if("Search, or say" in words or "Ok Google" in words or "Okay Google" in words): return

      if (   "his name is" in words
          or "is name his" in words
          or "what's his name" in words
          or "what is his" in words
          or "what is name" in words
          or "his name his" in words
          or "whats the name" in words  ):
          return 'aplay johncena_nointro.wav'

      if("john cena" in words):
          return 'aplay johncena.wav'

      if("say" in words): words = " ".join(words.split("say", 1)[1:])

      return 'espeak "%s"' % words

    return 'espeak "%s"' % words
    # return 'say -v Vicki "%s" &' % words # MAC

@post('/say')
def getWords():
    d = dict(request.forms)
    print d
    words = d["words"]
    reqType = d["type"] if "type" in d else None
    print words, reqType
    cmd = getCommand(words,reqType)
    os.system(cmd)

run(host="0.0.0.0", port=8080)
