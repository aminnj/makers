#!/bin/bash

# do
#    which sysctl
#    which tesseract
# and modify the below path
export PATH=$PATH:/usr/sbin:/usr/local/bin

python get_cms_data.py
python plot_cms_status.py

picture="cms_status.png"
json="monitor.json"
overview="overview.html"
outdir="~/public_html/monitoring/"

if [[ ${HOST} == *uaf-* ]]; then 
    # cp to public_html
    cp $picture $outdir/
    cp $json $outdir/
    cp $overview $outdir/
else
    # scp to public_html
    scp $picture ${USER}@uaf-6.t2.ucsd.edu:$outdir
    scp $json ${USER}@uaf-6.t2.ucsd.edu:$outdir
    scp $overview ${USER}@uaf-6.t2.ucsd.edu:$outdir
fi
