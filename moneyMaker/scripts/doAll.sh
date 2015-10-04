# filename="forBDT_100115.txt"
filename="data_2015.txt"
folder=bdtplots6

# produce the file for the machine learner
python soverbForBDT.py $filename

# use the file to learn, test, and print out predicted "good" events
# algos: BDT BDT2 BDTG SVC NuSVC SVR LinearSVC LDA
alg=SVC
mkdir -p ../$folder
rm ../$folder/*
python learnTest.py $filename $alg "../$folder/"
cd ..
. ~/syncfiles/miscfiles/niceplots.sh $folder
cd -

# take predicted events and format them into csv for Quantopian
python tradesToQuantopian.py "trades_$filename" > test_trades.csv

# upload to website for usage with Quantopian
scp -rp test_trades.csv namin@uaf-6.t2.ucsd.edu:~/public_html/dump/
echo "uaf-6.t2.ucsd.edu/~$USER/dump/test_trades.csv"
