filename="forBDT_092915.txt"

# produce the file for the machine learner
python soverbForBDT.py $filename

# use the file to learn, test, and print out predicted "good" events
python learnTest.py $filename

# take predicted events and format them into csv for Quantopian
python tradesToQuantopian.py "trades_$filename" > test_trades.csv

# upload to website for usage with Quantopian
scp -rp test_trades.csv namin@uaf-6.t2.ucsd.edu:~/public_html/dump/
echo "uaf-6.t2.ucsd.edu/~$USER/dump/test_trades.csv"
