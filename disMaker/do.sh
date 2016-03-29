#!/bin/bash

CMSSW_VER=CMSSW_7_4_4

source /code/osgcode/cmssoft/cms/cmsset_default.sh
if [ ! -d $CMSSW_VER ]; then
    scramv1 p -n ${CMSSW_VER} CMSSW $CMSSW_VER
    cd ${CMSSW_VER}
else
    cd ${CMSSW_VER}
fi
eval `scramv1 runtime -sh`

cd ..

python api.py "$*" | tee -a log.txt

