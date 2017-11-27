#!/bin/sh
echo "Uploading Front Page Graph to S3..."
App_Name=Solutions
BUCKET_NAME=bucket_here
aws s3 cp /root/"$App_Name"\ Scorecard/Graphs/"$App_Name"-FrontPageGraph-*.png s3://$BUCKET_NAME --region us-east-2 