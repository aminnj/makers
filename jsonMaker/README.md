put files in lxplus/ on lxplus (in ~/www/lumis) such that it is accessible via
```
    url = "http://namin.web.cern.ch/namin/lumis/getJSON.php?json=%s" % (jsonName)
```
crontab on lxplus should have something like
```
* */5 * * * /usr/bin/python /afs/cern.ch/user/n/namin/www/lumis/lumis.py
```

Right now, the cronjob is running on lxplus0048.

