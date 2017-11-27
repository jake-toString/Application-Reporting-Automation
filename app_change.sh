#!/bin/sh
#Author :: Jake Adkins
#Date :: 8/28/17
#Instructions :: Call script with app name

if [ "$1" != "" ]; then
	find ./ -type f -exec sed -i -e 's/YOUR_APP_HERE/'"$1"'/g' {} \;
	cd /root/Scorecard-Automation-Project/Deliverable/$1/
	rename -v APPLICATION $1 *.sh
	cd /root/Scorecard-Automation-Project/Deliverable/$1/Bucketlist/
	rename -v APPLICATION $1 *.py
        cd /root/Scorecard-Automation-Project/Deliverable/$1/Bucketlist/Drive/
        rename -v APPLICATION $1 *.py
else
	echo 'Not enough parameters. ./app_change.sh $APP_NAME'
fi
