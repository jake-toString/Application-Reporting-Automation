#!/bin/sh
#Author : Jake Adkins
#File : Install.sh
#Application : Learn
#Project: Scorecard Automation

#--------------------------------------------------- Variable Declaration ------------------------------------------------------
home_DIR='/root'
deployment_DIR='/root/Scorecard-Automation-Project/Deliverable'
now=$(date)
id_=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
ip_=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
application="Learn"

#------------------------------------------------------- Local Functions -------------------------------------------------------
post_init_data()
{
        cat << STOP
        {
                "message":"EC2 instance started for $application Scorecard creation at $now",
                "description":"Instance ID: $id_ <br/> Public IPv4: $ip_",
                "priority":"P5"
        }
STOP
}

post_gitFailure_data()
{
        cat << STOP
        {
                "message":"EC2 unable to connect to code.kent.edu",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ cannot connect to code.kent.edu",
                "priority":"P3"
        }
STOP
}

post_gitDownloadFailure_data()
{
        cat << STOP
        {
                "message":"EC2 for $application failed to download Git repo...",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ failed to download the code from code.kent.edu",
                "priority":"P3"
        }
STOP
}

post_RDSFailure_data()
{
        cat << STOP
        {
                "message":"RDS Script failure within EC2 for $application...",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ failed to execute data_collector.py",
                "priority":"P3"
        }
STOP
}

post_buildStart_data()
{
        cat << STOP
        {
                "message":"$application Scorecard build start...",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ has launched card_builder.py",
                "priority":"P5"
        }
STOP
}

post_buildFailure_data()
{
        cat << STOP
        {
                "message":"$application Scorecard build failure at $now...",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ has encountered a critical error while executing card_builder.py",
                "priority":"P3"
        }
STOP
}

post_buildSuccess_data()
{
        cat << STOP
        {
                "message":"$application Scorecard build finished",
                "description":"$application Scorecard has been posted to Confluence.",
                "priority":"P5"
        }
STOP
}

post_graphFail_data()
{
        cat << STOP
        {
                "message":"$application Scorecard Front Page Graph failed to build...",
                "description":"$application Scorecard builder EC2 instance with ip $ip_ has encountered a critical error while executing FrontPage.py",
                "priority":"P3"
        }
STOP
}

check_ops_post()
{
        # check status of POST request
        if [ "$1" != '{"result":"Request will be processed"' ]; then
                echo 'POST successfully sent to OpsGenie...'
        else
                echo 'Unable to send POST request to OpsGenie. Non-critical failure.'
        fi
}

graphBuildFail()
{
		echo 'Encountered an error building the Front Page Graph. Likely PoF is corrupt RDS instance. Critical failure. Failure imminent...'
		echo 'Notifying OpsGenie...'
		curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
             -H "Content-Type: application/json"\
             -H "Authorization: GenieKey GENIE_KEY_HERE"\
             -d "$(post_graphFail_data)")

		check_ops_post $curl_out
}

dlFail()		
{		
	echo 'Failed to download code repository. Aborting...'		
	echo "Log: $1"		
	# send code.kent.edu failure notification to OpsGenie		
	curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\		
		-H "Content-Type: application/json"\		
		-H "Authorization: GenieKey GENIE_KEY_HERE"\		
		-d "$(post_gitDownloadFailure_data)")		
	check_ops_post $curl_out		
	gracefulExit		
}


gracefulExit()
{
	#attach log
	alert_id=$(curl -XGET -H "Authorization: GenieKey GENIE_KEY_HERE" 'https://api.opsgenie.com/v2/alerts?limit=1&sort=createdAt&order=desc&query=message:*Learn*' | jq '.data|.[0]|.id')
	temp="${alert_id%\"}"
	temp="${temp#\"}"

	curl -X POST "https://api.opsgenie.com/v2/alerts/$temp/attachments/?alertIdentifierType=id" -H 'authorization: GenieKey GENIE_KEY_HERE' -H content-type="multipart/form-data" -F file=@/var/log/cloud-init-output.log

	aws ec2 stop-instances --instance-ids $id_ --region us-east2
}

#-------------------------------------------------------- Begin Preliminary Checks ---------------------------------------------
echo 'Sending instance start notification to OpsGenie...' # --------------------------------------------------------------------
curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
             -H "Content-Type: application/json"\
             -H "Authorization: GenieKey GENIE_KEY_HERE"\
             -d "$(post_init_data)")
check_ops_post $curl_out

echo 'Checking connection to Kent Network VPN...' # ----------------------------------------------------------------------------
ping_out=$(ping -qc 4 code.kent.edu)

if [ "$ping_out" != "*4 received*" ]; then
        echo 'code.kent.edu is up...'
else
        echo 'Cannot connect to code.kent.edu. Connection or server is down. Critical failure. Failure imminent...'

        #Attempt to notify OpsGenie
        echo 'Attempting to notify OpsGenie...'
        if [ "$(ping -qc 4 4.2.2.2)" != "*4 received*" ]; then
                # send code.kent.edu failure notification to OpsGenie
                curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
                        -H "Content-Type: application/json"\
                        -H "Authorization: GenieKey GENIE_KEY_HERE"\
                        -d "$(post_gitFailure_data)")
                check_ops_post $curl_out
        else
                echo 'Internet connection not established. Aborting...'
                aws ec2 stop-instances --instance-ids $id_ --region us-east2
        fi
fi

#-------------------------------------------------------- Begin Playbook -------------------------------------------------------
echo "Deploying $application Scorecard Automation Module..." # -----------------------------------------------------------------
#Assume dependencies have been resolved...
#Assume screenshots have been taken...

echo 'Fetching Deployment Package from code.kent.edu...' # ---------------------------------------------------------------------
git_out=$(git clone -b prod git@code.kent.edu:IO/Scorecard-Automation-Project.git $home_DIR/Scorecard-Automation-Project 2>&1)

[ -f /root/Scorecard-Automation-Project/app_change.sh ] && echo 'Done.' || dlFail $git_out

echo "Deploying $application Scorecard Build Scripts..." # ------------------------------------------------------------------------
mv "$deployment_DIR/$application" "$home_DIR/$application Scorecard"
chmod 777 "$home_DIR/$application Scorecard"
mkdir "$home_DIR/$application Scorecard/Screenshots/"
echo 'Done.'

echo 'Deploying matplotlib init...' # ------------------------------------------------------------------------------------------
sudo mv -f "$deployment_DIR/matplotlibrc" "/usr/local/lib64/python2.7/site-packages/matplotlib/mpl-data/matplotlibrc"
echo 'Done.'

echo "Running $application RDS Data Script..." # -------------------------------------------------------------------------------
python "$home_DIR/Learn Scorecard/data_collector.py"

if [[ $? = 0 ]]; then
    echo 'Done.'
else
    echo 'RDS script execution failed. Aborting...'
    # send failure notification to OpsGenie
    curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
         -H "Content-Type: application/json"\
         -H "Authorization: GenieKey GENIE_KEY_HERE"\
         -d "$(post_RDSFailure_data)")
    check_ops_post $curl_out
    gracefulExit
fi

echo "Generating $application Front Page Graph..." # ---------------------------------------------------------------------------
chmod 777 $home_DIR/Learn\ Scorecard/Graphs/driver.sh
chmod 777 $home_DIR/Learn\ Scorecard/Graphs/bucketUpload.sh
$home_DIR/Learn\ Scorecard/Graphs/driver.sh

[ -f $home_DIR/Learn\ Scorecard/Graphs/Learn-FrontPageGraph-*.png ] && echo 'Done.' || graphBuildFail

echo 'Building Scorecard...' # -------------------------------------------------------------------------------------------------

curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
    -H "Content-Type: application/json"\
    -H "Authorization: GenieKey GENIE_KEY_HERE"\
	-d "$(post_buildStart_data)")
check_ops_post $curl_out

python "$home_DIR/Learn Scorecard/card_builder.py"

if [[ $? = 0 ]]; then
    echo 'Done.'
	curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
		-H "Content-Type: application/json"\
        -H "Authorization: GenieKey GENIE_KEY_HERE"\
        -d "$(post_buildSuccess_data)")
	check_ops_post $curl_out
	sleep 5
	gracefulExit
else
    echo 'Build script execution failed. Aborting...'
	# send failure notification to OpsGenie
    curl_out=$(curl -s -X POST https://api.opsgenie.com/v2/alerts\
         -H "Content-Type: application/json"\
         -H "Authorization: GenieKey GENIE_KEY_HERE"\
         -d "$(post_buildFailure_data)")
    check_ops_post $curl_out
	sleep 5
    gracefulExit
fi
