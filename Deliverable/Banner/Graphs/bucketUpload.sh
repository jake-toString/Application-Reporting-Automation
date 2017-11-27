#!/bin/sh
echo "Uploading Front Page Graph to S3..."
aws s3 cp /root/Banner\ Scorecard/Graphs/Banner-FrontPageGraph-*.png s3://bucket_name_here --region us-east-2 