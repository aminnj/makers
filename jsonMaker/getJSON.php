<?php
/* $json = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-257599_13TeV_PromptReco_Collisions15_25ns_JSON.txt'; */
$json=$_GET['json'];
echo shell_exec('cat '.$json);
?>
