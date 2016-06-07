#!/bin/bash

# do
#    which sysctl
#    which tesseract
# and modify the below path
export PATH=$PATH:/usr/sbin:/usr/local/bin

echo ">>> Getting monitoring data"
python get_cms_data.py

echo ">>> Plotting"
python plot_cms_status.py

echo ">>> Adding uaf health"
python add_uaf_health.py # this makes overview.html from overview.html.replace

picture="cms_status.svg"
json="monitor.json"
overview="overview.html"
outdir="monitoring"
style="style.css"
image="monitorlogo.png"
user=$USER

if [[ ${HOST} == *uaf-* ]]; then 
    # cp to public_html
    cp $picture $outdir/
    cp $json $outdir/
    cp $overview $outdir/
    cp $image $outdir/
    cp $style $outdir/
else
    # scp to public_html
    scp -o COnnectTimeout=10 -o StrictHostKeyChecking=no $picture $json $overview $image $style $user@uaf-6.t2.ucsd.edu:~/public_html/$outdir/ || scp -o COnnectTimeout=10 -o StrictHostKeyChecking=no $picture $json $overview $image $style $user@uaf-7.t2.ucsd.edu:~/public_html/$outdir/ || scp -o COnnectTimeout=10 -o StrictHostKeyChecking=no $picture $json $overview $image $style $user@uaf-8.t2.ucsd.edu:~/public_html/$outdir/
fi

echo ">>> Output in uaf-6.t2.ucsd.edu/~$user/$outdir/$overview"
