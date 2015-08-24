make sure you do
```
chmod 755 makers
chmod 755 lottomaker
chmod 755 handler.py
```
and that the .htaccess file in ~/public_html/ contains
```
AddHandler cgi-script .cgi .py
Options +ExecCGI
```
