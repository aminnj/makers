import os, sys, random, json

import numpy as np
import getStocks as gs
import utils as u
import indicators as ind
import tradeReport as tr
import backtestBenchmark as btbm

fh = open("test.txt","r")
res = json.loads(fh.read())
fh.close()


users = []
rands = []
bahs = []
days = []
for sym in res.keys():
    users.append( res[sym]["user"] )
    rands.append( res[sym]["rand"] )
    bahs.append( res[sym]["bah"] )
    days.append( res[sym]["ndays"] )

users = np.array(users)
rands = np.array(rands)
bahs = np.array(bahs)
days = np.array(days)

print "Found %i stocks!\n" % len(res.keys())

# rand
print "RAND:"
print "rand strat yields $(%.2f +- %.2f)/day" % (np.mean(rands[:,0]/days), np.mean(rands[:,1]/days))
print "rand strat yields $(%.2f +- %.2f)/trade" % (np.mean(rands[:,0]/rands[:,2]), np.mean(rands[:,1]/rands[:,2]))
print "rand strat has %.1f trades/yr" % (365.0*np.mean(rands[:,2]/days))
print "-"*30,"\n"

# bah
print "BAH:"
print "bah strat yields $%.2f/day" % np.mean(bahs[:,0]/days)
print "bah strat yields $%.2f/trade" % np.mean(bahs[:,0]/bahs[:,2])
print "bah strat has %.1f trades/yr" % (365.0*np.mean(bahs[:,2]/days))
print "-"*30,"\n"

# user
print "USER:"
print "user strat yields $%.2f/day" % np.mean(users[:,0]/days)
print "user strat yields $%.2f/trade" % np.mean(users[:,0]/users[:,2])
print "user strat has %.1f trades/yr" % (365.0*np.mean(users[:,2]/days))
print "-"*30,"\n"

sigmas = (users[:,0]-rands[:,0])/rands[:,1] # how many sigma away is user from rand
print "on average, user strat is %.1f sigma above random" % np.mean(sigmas)
