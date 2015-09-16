import os, sys, random, json

import numpy as np
import getStocks as gs
import utils as u
import indicators as ind
import tradeReport as tr
import backtestBenchmark as btbm

# fh = open("btbenchmark_crossover.txt","r")
fh = open("test.txt","r")
res = json.loads(fh.read())
fh.close()


users = []
rands = []
bahs = []
days = []
for sym in res.keys():
    if res[sym]["user"][2] < 0.001: continue # ntrades
    if res[sym]["rand"][2] < 0.001: continue # ntrades
    if res[sym]["bah"][2] < 0.001: continue # ntrades
    if res[sym]["ndays"] < 10: continue

    users.append( res[sym]["user"] )
    rands.append( res[sym]["rand"] )
    bahs.append( res[sym]["bah"] )
    days.append( res[sym]["ndays"] )

users = np.array(users)
rands = np.array(rands)
bahs = np.array(bahs)
days = np.array(days)

print "Found %i stocks!\n" % len(days)

# rand
print "RAND:"
print "rand strat yields $(%.2f +- %.2f)/day" % (np.mean(rands[:,0]/days), np.mean(rands[:,1]/days)/np.sqrt(100))
print "rand strat yields $(%.2f +- %.2f)/trade" % (np.mean(rands[:,0]/rands[:,2]), np.mean(rands[:,1]/rands[:,2])/np.sqrt(100))
print "rand strat has %.1f trades/yr" % (365.0*np.mean(rands[:,2]/days))
print "rand strat win percentage: %i" % (np.sum(rands[:,2]*rands[:,3])/np.sum(rands[:,2]))
print "rand strat profit per winning trade %.1f%%" % (np.mean(rands[:,4]))
print "rand strat profit per losing trade %.1f%%" % (np.mean(rands[:,5]))
print "-"*30,"\n"

# bah
print "BAH:"
print "bah strat yields $%.2f/day" % np.mean(bahs[:,0]/days)
print "bah strat yields $%.2f/trade" % np.mean(bahs[:,0]/bahs[:,2])
print "bah strat has %.1f trades/yr" % (365.0*np.mean(bahs[:,2]/days))
print "bah strat win percentage: %i" % (np.sum(bahs[:,2]*bahs[:,3])/np.sum(bahs[:,2]))
print "bah strat profit per winning trade %.1f%%" % (np.mean(bahs[:,4]))
print "bah strat profit per losing trade %.1f%%" % (np.mean(bahs[:,5]))
print "-"*30,"\n"

# user
print "USER:"
print "user strat yields $%.2f/day" % np.mean(users[:,0]/days)
print "user strat yields $%.2f/trade" % np.mean(users[:,0]/users[:,2])
print "user strat has %.1f trades/yr" % (365.0*np.mean(users[:,2]/days))
print "user strat win percentage: %i" % (np.sum(users[:,2]*users[:,3])/np.sum(users[:,2]))
print "user strat profit per winning trade %.1f%%" % (np.mean(users[:,4]))
print "user strat profit per losing trade %.1f%%" % (np.mean(users[:,5]))
print "-"*30,"\n"

sigmas = (users[:,0]-rands[:,0])/rands[:,1] # how many sigma away is user from rand
print "on average, user strat is %.1f sigma above random" % np.mean(sigmas)
