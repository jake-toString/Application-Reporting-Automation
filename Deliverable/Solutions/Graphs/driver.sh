#!/bin/sh

#Declare lexical variables...
APP_NAME=Solutions

echo "Generating $APP_NAME Front Page Graph..." 
python /root/"$APP_NAME"\ Scorecard/Graphs/FrontPage.py
echo "Done." 

echo "Uploading image to S3..."
/root/"$APP_NAME"\ Scorecard/Graphs/bucketUpload.sh
echo "Done."
