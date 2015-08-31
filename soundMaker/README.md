0) Make sure audio works on raspberry pi by doing `speaker-test`
1) Change BASEDIRECTORY and put the following line in your crontab via `crontab -e`:
```*/5 * * * * cd BASEDIRECTORY/makers/soundMaker ; python sounds.py```
