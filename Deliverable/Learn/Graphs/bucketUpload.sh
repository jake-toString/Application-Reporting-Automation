#!/bin/sh
echo "Uploading Front Page Graph to S3..."
App_Name=Learn
BUCKET_NAME=bucket_name_here s3 cp "/root/Learn Scorecard/Graphs/"*.png s3://$BUCKET_NAME --region us-east-2