#! /usr/bin/env python

###########################################################
# takes data from files produced by get_cms_status.py and
# get_lumi.py to produce a nice plot.
###########################################################

import time
import os
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from scipy import integrate

# moving average to smooth out curve. n is the number of datapoints on each
# side of a given point to average over. fixvals tells it to not perform
# average for all array values equal to something in fixvals. Use it to
# pin things at 5 points
def moving_avg(arr, n=2, fixvals=[]):
    arr_new = np.copy(arr)
    m = arr.size
    for i in range(n, m-n):
        if round(arr[i],2) not in fixvals:
            arr_new[i] = np.sum(arr[i-n:i+n+1])/(2.0*n+1)
    for i in range(1,n):
        if round(arr[i],2) not in fixvals:
            arr_new[i] = np.sum(arr[0:2*i+1])/(2.0*i+1)        
        if round(arr[m-i-1],2) not in fixvals:
            arr_new[m-i-1] = np.sum(arr[m-2*i-1:m])/(2.0*i+1)        

    return arr_new

PLOT_LUMI = True

datafile = "cms_status.txt"
datafile_lum = 'monitor_lumi.txt'

datefmt = mdates.DateFormatter("%H:%M")

curtime = time.time()
fid = open(datafile)
lines = [line.strip().split('\t') for line in fid.readlines()]
fid.close()

time_vals = []
B_vals = []
E_vals = []
beam_vals = []
c1_vals = []
c2_vals = []

for i in range(len(lines)-1,-1,-1):
    line = lines[i]
    t = round(float(line[0]))

    # only use past 24 hours
    if t < curtime - 24*60*60:
        break

    B = float(line[1])
    E = float(line[2])
    beam_stat = line[3]
    c1 = [int(i) for i in line[4:18]]
    c2 = [int(i) for i in line[18:]]

    # bad values
    if B==-1 or c1.count(-1)!=0 or c2.count(-1)!=0:
        continue
    time_vals.append(datetime.fromtimestamp(t))
    B_vals.append(B)
    E_vals.append(E)
    if beam_stat=="STABLE":
        beam_vals.append(1)
    else:
        beam_vals.append(0)
    c1_vals.append(float(sum(c1))/(len(c1)-1))
    c2_vals.append(float(sum(c2))/(len(c2)-1))

time_vals = np.array(time_vals[::-1])
B_vals = np.array(B_vals[::-1])
E_vals = np.array(E_vals[::-1])
beam_vals = np.array(beam_vals[::-1])
c1_vals = np.array(c1_vals[::-1])
c2_vals = np.array(c2_vals[::-1])

scoreB = 5.*B_vals/3.801
scoreE = 2.0*beam_vals + 3.0*E_vals/6500
scoreS = 5.*(c1_vals*13+c2_vals*8)/21

scoreB = moving_avg(scoreB, 4, fixvals=[5])
scoreE = moving_avg(scoreE, 4, fixvals=[5])
scoreS = moving_avg(scoreS, 4, fixvals=[5])

score = scoreB+scoreE+scoreS

atlas_int_lumi_vec = []
cms_int_lumi_vec = []

if PLOT_LUMI:
    fid = open(datafile_lum)
    lines = [line.strip().split('\t') for line in fid.readlines()]
    fid.close()

    time_vals_lumi = []
    cms_lumi = []
    atlas_lumi = []

    for line in lines:
        t = float(line[0])
        if t < curtime - 24*60*60:
            continue
        time_vals_lumi.append(t)
        cms_lumi.append(float(line[1]))

        # BUG: sometimes atlas lumi isn't read and tesseract gives blank string.
        # temp workaround until I figure out why
        if len(line)>=3:
            atlas_lumi.append(float(line[2]))
        elif len(atlas_lumi)>0:
            atlas_lumi.append(atlas_lumi[-1])
        else:
            atlas_lumi.append(0)
        
    cms_int_lumi_vec = integrate.cumtrapz(cms_lumi, x=time_vals_lumi) / 1000000 # in picobarns
    atlas_int_lumi_vec = integrate.cumtrapz(atlas_lumi, x=time_vals_lumi) / 1000000 # in picobarns


    cms_int_lumi = cms_int_lumi_vec[-1]

    time_vals_lumi = np.array([datetime.fromtimestamp(t) for t in time_vals_lumi])
    time_vals_lumi = np.array(time_vals_lumi)
    cms_lumi = moving_avg(np.array(cms_lumi),1)
    atlas_lumi = moving_avg(np.array(atlas_lumi),1)

# colorB = '#e74c3c'
# colorS = '#3498db'
# colorE = '#2ecc71'

# colorB = '#0c2c84'
# colorS = '#225ea8'
# colorE = '#1d91c0'

colorB = '#2171b5'
colorS = '#6baed6'
colorE = '#bdd7e7'

fig = plt.figure(num=2, figsize=(10,10))
plt.subplots_adjust(hspace=0.1)
# ax1 = fig.add_subplot(111)
# ax1 = fig.add_subplot(211)
ax1 = plt.subplot2grid((5,1), (0,0), rowspan=4)
ax1.stackplot(time_vals,scoreB,scoreS,scoreE, colors=[colorB,colorS,colorE])
ax1.set_ylim(0,20)
ax1.set_yticks([0,5,10,15])
ax1.set_yticks([2.5,7.5,12.5], minor=True)
ax1.yaxis.grid(which='both')
ax1.set_ylabel('Score')
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
ax1.xaxis.set_major_formatter(datefmt)
ax1.set_xlabel("Last updated "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(curtime)))


if PLOT_LUMI:
    ax3 = plt.subplot2grid((5,1), (4,0), rowspan=1)
    ax3.plot(time_vals_lumi[1:],cms_int_lumi_vec,color='#F5AB35', label='ATLAS Lumi', linewidth=1.5)
    ax3.plot(time_vals_lumi[1:],atlas_int_lumi_vec,color='#F62459', label='CMS Lumi', linewidth=1.5)
    ax3.yaxis.tick_right()
    ax3.yaxis.set_label_position("right")
    ax3.set_ylabel(r'Int. Lumi. ($pb^{-1}$)')
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax3.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    ax3.xaxis.set_major_formatter(datefmt)
    ax3.set_xlabel("Last updated "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(curtime)))
    plt.figtext(0.161, 0.295,r"$\int\/ \mathcal{L}\/ dt$ past day = "+str(round(cms_int_lumi,1))+' pb$^{-1}$')

curBscore = scoreB[-1]
curEscore = scoreE[-1]
curSscore = scoreS[-1]

red_patch = mpatches.Patch(facecolor=colorB, label='Magnet ('+str(round(curBscore,2))+')', edgecolor='k')
blue_patch = mpatches.Patch(facecolor=colorS, label='Subsystems ('+str(round(curSscore,2))+')', edgecolor='k')
green_patch = mpatches.Patch(facecolor=colorE, label='Beam ('+str(round(curEscore,2))+')', edgecolor='k')

if PLOT_LUMI:
    ax2 = ax1.twinx()
    atl_lumi_plot, = ax2.plot(time_vals_lumi,atlas_lumi,color='#F5AB35', label='ATLAS Lumi', linewidth=1.5)
    cms_lumi_plot, = ax2.plot(time_vals_lumi,cms_lumi,color='#F62459', label='CMS Lumi', linewidth=1.5)
    ax2.set_ylabel(r'Luminosity ($\mu b^{-1}/s$)')
    ax2.set_ylim(0,1200)
    ax2.set_yticks([300,600,900])
    ax2.set_yticks([150,450,750,1050], minor=True)
    leg = plt.legend(handles=[red_patch, blue_patch, green_patch, cms_lumi_plot, atl_lumi_plot], fontsize='small')
else:
    leg = plt.legend(handles=[red_patch, blue_patch, green_patch], fontsize='small')
    
ax1.set_xlim(time_vals[0], time_vals[-1])
fig.autofmt_xdate()

badColor = '#96281B'
goodColor = 'g'
if curBscore >= 5:
    leg.get_texts()[0].set_color(goodColor)
else:
    leg.get_texts()[0].set_color(badColor)

if curSscore >= 5:
    leg.get_texts()[1].set_color(goodColor)
else:
    leg.get_texts()[1].set_color(badColor)

if round(curEscore,2) >= 5:
    leg.get_texts()[2].set_color(goodColor)
else:
    leg.get_texts()[2].set_color(badColor)

plt.title('24 hour CMS Functionality Score')
plt.figtext(0.20,0.85,"current score = "+str(round(score[-1],2)))


plt.savefig("cms_status.svg", format='svg', dpi=1200)
plt.clf()

