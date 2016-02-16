import numpy as np
import commands
import datetime

stat,_ = commands.getstatusoutput("for i in {3..10}; do time -p (ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no namin@uaf-${i}.t2.ucsd.edu hostname); done >& tempuptime.txt")
stat,uaf_out = commands.getstatusoutput("awk 'BEGIN {ORS=\" \"}; /^uaf-/{print; getline; print; print \"\\n\"}' tempuptime.txt")
stat,das_out = commands.getstatusoutput("time (curl -m 30 -k https://cmsweb.cern.ch/das/ >& /dev/null)")
times = {int(line.split(".")[0].split("-")[1]):float(line.split("real")[1]) for line in uaf_out.split("\n") if len(line)>1}
print times
c1 = np.array([0,212,0]) # green
c2 = np.array([236,13,13]) # red
buff="(as of %s): &nbsp;" % str(datetime.datetime.now().strftime("%I:%M %p"))
for uaf in range(3,11):
    f = 1.0 # fraction of the way from c1 to c2
    if uaf in times: f = min(times[uaf]/10, 1.0)
    buff += "<span style='border: 2px solid #%02x%02x%02x;'> uaf-%i </span> &nbsp; " % tuple(list(c1+f*(c2-c1))+[uaf])


das_time = [float(line.split("real")[1].split("m")[1].replace("s","")) for line in das_out.split("\n") if len(line)>1 and "real" in line][0]
f = das_time/30.0
buff += "<span style='border: 2px solid #%02x%02x%02x;'> DAS </span> &nbsp; " % tuple(list(c1+f*(c2-c1)))

with open("overview.html.replace","r") as fhin: data = fhin.read().replace("HEALTHPLACEHOLDER",buff)
with open("overview.html","w") as fhout: fhout.write(data)
