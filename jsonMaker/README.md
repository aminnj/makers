put files in lxplus/ on lxplus (in ~/www/lumis) such that it is accessible via
```
    url = "http://namin.web.cern.ch/namin/lumis/getJSON.php?json=%s" % (jsonName)
```
crontab on lxplus should have something like
```
* */5 * * * /usr/bin/python /afs/cern.ch/user/n/namin/www/lumis/lumis.py
```

Right now, the cronjob is running on lxplus0048.


Actually, this cronjob does not work because lxplus sucks. I have now done this:
```
acrontab -e
```
paste in
```
0 0 * * * lxplus.cern.ch /usr/bin/python /afs/cern.ch/user/n/namin/www/lumis/lumis.py > /afs/cern.ch/user/n/namin/www/lumis/acron.log 2>&1
0 12 * * * lxplus.cern.ch /usr/bin/python /afs/cern.ch/user/n/namin/www/lumis/lumis.py > /afs/cern.ch/user/n/namin/www/lumis/acron.log 2>&1
```
