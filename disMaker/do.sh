#!/bin/bash

CMSSW_VER=CMSSW_7_4_4


# source /code/osgcode/cmssoft/cms/cmsset_default.sh
# if [ ! -d $CMSSW_VER ]; then
#     scramv1 p -n ${CMSSW_VER} CMSSW $CMSSW_VER
#     cd ${CMSSW_VER}
# else
#     cd ${CMSSW_VER}
# fi
# eval `scramv1 runtime -sh`
# cd ..

# OK, evidently the following 3 lines take 0.1 seconds to execute (presumably because the strings are long?)
export PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/bin:$PATH
export PYTHONPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/py2-pycurl/7.19.0-cms/lib/python2.7/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/${CMSSW_VER}/external/slc6_amd64_gcc491/lib:$LD_LIBRARY_PATH

python api.py "$*"
# python api.py "$*" | tee -a log.txt
echo `date +%s` >> timestamps.txt
# python api.py "$*"

