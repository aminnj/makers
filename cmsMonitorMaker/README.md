0) Install matplotlib and tesseract. On a Mac, this can be done via
```
sudo brew install tesseract
sudo brew link tesseract
sudo pip install matplotlib
sudo pip install --upgrade matplotlib
```

1) Edit the paths at the top of do.sh as indicated in the file

2) Change BASEDIRECTORY and put the following line in your crontab via `crontab -e`:
```*/5 * * * * cd BASEDIRECTORY/makers/cmsMonitorMaker ; source do.sh```

3) Every 5 minutes, http://uaf-6.t2.ucsd.edu/~USER/monitoring/overview.html will be updated
