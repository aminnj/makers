# DIS (DAS Is Slow)
## Installation
Do `git clone https://github.com/cmstas/DataTuple-backup/` inside the directory in order to use the pick_cms3 option. Make sure all python files have `chmod 755` including the directories they reside in.

## Instructions and examples
A query has 3 parts: the query string, the query type, and the boolean "short" option (which governs the level of detail that is returned by the API).


### General notes

* Wildcards are accepted (`*`) for most queries. Just try it.
* `dis_client.py` syntax will be used here, but of course they have obvious mappings to use them on the website 
* `dis_client.py` is available from <https://raw.githubusercontent.com/cmstas/NtupleTools/master/AutoTwopler/scripts/dis_client.py>. I recommend putting this in your PATH (and PYTHONPATH) somewhere.


### Query types

#### _basic_

`
dis_client.py -t basic /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* Here, you will see an output of the number of events in the dataset, the number of files, number of lumi blocks, and dataset file size.
* Also note that the `-t basic` is default, so you don't need to do it for this basic query type.

`
dis_client.py "/GJets_HT-*_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"
`

* The wildcard now will cause the output to be a list of matching dataset names.

`
dis_client.py --detail "/GJets_HT-*_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"
`

* Specifying `--detail` (equivalently, unchecking `short` in the web interface) will show the number of events, number of files, etc. for each dataset matching the wildcard.

#### _files_

`
dis_client.py -t files /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* This will show a list of a handful of the files from this dataset, along with filesize and number of events. To show all the files, provide the `--detail` option (note that sometimes, you can get thousands of files since datasets can be large, which is why the default is only a handful, which suits my main use case which is to check one file in a dataset for something specific).

#### _config_

`
dis_client.py -t files /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* Shows information about the CMSSW version and global tag used for processing this dataset

#### _mcm_

`
dis_client.py -t mcm /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* This shows basic MCM information (for ALL information, throw it the detail option) for the OLDEST PARENT of the dataset (presumably GENSIM)
* This includes the fragment, cross-section, matching/filter efficiency, CMSSW release, MCDB ID, and dataset status (done, running, etc.)

`
dis_client.py -t mcm "/GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM,this"
`

* To get MCM information for the actual dataset you feed in, tack on the `,this` modifier

#### _driver_

`
dis_client.py -t driver /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* Same story as above (finds the cmsDriver commands for the highest parent, unless you give it the `,this` modifier)


#### _parents_

`
dis_client.py -t parents /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* Returns a list of datasets found as we recurse up the tree of parenthood


#### _lhe_

`
dis_client.py -t lhe /GJets_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM
`

* Returns a list of LHE files for this dataset (only a few are returned unless `--detail` is asked for, in the same way as the files query type)


#### _snt_

`
dis_client.py -t snt "/GJets_HT-*_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM"
`

* Much like the other database queries, this just uses the SNT datasets (returns information about ntupled nevents, cross-section, kfactor, hadoop location, etc.)
* The `--detail` option just provides more details like the filter type, twiki name, who the sample was assigned to, etc.


#### _dbs_

`
dis_client.py -t dbs "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/files?dataset=/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/MINIAODSIM&detail=1&lumi_list=[134007]&run_num=1"
`

* For development use, or other cases not covered here, you can feed in a direct URL for a DBS query.


#### _runs_

`
dis_client.py -t runs "/SinglePhoton/Run2016E-PromptReco-v2/MINIAOD"
`

* Returns a list of runs contained within the dataset


#### _pick_

`
dis_client.py -t pick "/MET/Run2016D-PromptReco-v2/MINIAOD,276524:9999:2340928340,276525:2892:550862893,276525:2893:823485588,276318:300:234982340,276318:200:234982340"
`

* This is a parallelized edmPickEvents which returns the files containing the specified events


#### _pick\_cms3_

`
dis_client.py -t pick_cms3 "/MET/Run2016D-PromptReco-v2/MINIAOD,276524:9999:2340928340,276525:2892:550862893,276525:2893:823485588,276318:300:234982340,276318:200:234982340"
`

* This is a pickEvents implementation for CMS3 data which returns the merged files containing the specified events


### Selectors/modifiers, greppers, and all that

`
dis_client.py -t snt "/gjet*,cms3tag=*V08*,gtag=*v3 | grep location,cms3tag,gtag,xsec"
`

* This uses a selector and grepper to show all Gjet SNT samples that have a cms3tag containing V08 and global tag ending with v3. The "cms3tag" name comes from the return value when doing a normal query, so you can find all the values that are selectable by making an inclusive query. Same goes for the grep fields which limit what is shown to you in the return information.
* But Nick, this looks ugly and I can't copy and paste the output easily into other scripts. It would be nice if we could put the same information for each sample on the same line. Fear not. There is a `--table` option which puts the results into a pretty table with nice columns.

`
dis_client.py -t snt "/gjet*,cms3tag=*V08*,gtag=*v3 | grep location,cms3tag,gtag,xsec" --table
`

For a more practical application, what if we want to get the total number of events for all HT binned GJet samples in CMS3?

`
dis_client.py -t snt "/gjet*ht-*/*/*,cms3tag=*V08* | grep nevents_out"
`

* This is a start. We see one column of numbers with the "nevents_out" field. What if we could add them together and display some statistics?

`
dis_client.py -t snt "/gjet*ht-*/*/*,cms3tag=*V08* | grep nevents_out | stats"
`

* Piping it into `stats`, we get the number of entries, the total, the minimum, and maximum for a list of numbers. More generally, any list of numbers can be piped into `stats`. Same with the run query type above (if we wanted to find the first or last run in a dataset, for example).

### API Usage
The primary purpose of this was to provide programmatic access to DBS, MCM, DAS, etc, so the `--json` option can be passed to any `dis_client.py` query to output a json. Even better, if it's on your path, you can import it directly from python and get a dictionary back as the response

```python
import dis_client
response =  dis_client.query(q="..." [, typ="basic"] [, detail=False])
data = response["response"]["payload"]
print response
print data
```
