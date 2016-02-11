import numpy as np
import commands
import datetime

stat,out = commands.getstatusoutput("for i in {3..10}; do time -p (ssh -o ConnectTimeout=15 -o BatchMode=yes -o StrictHostKeyChecking=no namin@uaf-${i}.t2.ucsd.edu hostname); done >& tempuptime.txt")
stat,out = commands.getstatusoutput("awk 'BEGIN {ORS=\" \"}; /^uaf-/{print; getline; print; print \"\\n\"}' tempuptime.txt")
times = {int(line.split(".")[0].split("-")[1]):float(line.split("real")[1]) for line in out.split("\n") if len(line)>1}
c1 = np.array([0,212,0]) # green
c2 = np.array([236,13,13]) # red
buff="(as of %s): &nbsp;" % str(datetime.datetime.now().strftime("%I:%M %p"))
for uaf in range(3,11):
    f = 1.0 # fraction of the way from c1 to c2
    if uaf in times: f = times[uaf]/15.0
    buff += "<span style='border: 2px solid #%02x%02x%02x;'> uaf-%i </span> &nbsp; " % tuple(list(c1+f*(c2-c1))+[uaf])

with open("overview.html.replace","r") as fhin: data = fhin.read().replace("UAFPLACEHOLDER",buff)
with open("overview.html","w") as fhout: fhout.write(data)
