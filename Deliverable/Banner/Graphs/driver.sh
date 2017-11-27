#!/bin/sh
echo "Generating Banner Front Page Graph..." 
python /root/Banner\ Scorecard/Graphs/FrontPage.py
echo "Done." 

echo "Uploading image to S3..."
/root/Banner\ Scorecard/Graphs/bucketUpload.sh
echo "Done."
