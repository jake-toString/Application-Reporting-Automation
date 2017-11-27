#!/usr/bin/python
#OpsGenie API
#Jake Adkins
#10/31/17
#Happy Halloween :)

#import statements
import datetime
import time as mod_time
import requests
import sys
import urllib2
from opsgenie.swagger_client import AlertApi
from opsgenie.swagger_client.models import *
from opsgenie.swagger_client.rest import ApiException
from opsgenie.swagger_client import configuration

sys.path.insert(0, '/root/Banner Scorecard/lib');
import Helpers

#Declare global vars
integration_key = 'int key here';
default_key = 'default key here';

#Initialize OpsGenie Object
configuration.api_key['Authorization'] = integration_key;
configuration.api_key_prefix['Authorization'] = 'GenieKey';

def sendRequest(body_):
    try:
        response = AlertApi().create_alert(body=body_)

        print('request id: {}'.format(response.request_id))
        print('took: {}'.format(response.took))
        print('result: {}'.format(response.result))
    except ApiException as err:
        print("Exception when calling AlertApi->create_alert: %s\n" % err)

def getAlertList():
    configuration.api_key['Authorization'] = default_key;
    try:
        id_list = [];
        alert_list = [];
        toTimestamp = Helpers.timeDelta_Resolution(datetime.datetime.today());

        response = AlertApi().list_alerts(
            query = 'createdAt<=' + 
                        str(int(mod_time.mktime(toTimestamp.timetuple()) + toTimestamp.microsecond / 1e6)) + 
                        ' AND priority: (P3 OR P2 OR P1)' + 
                        ' AND teams!= 6dee2e36-413e-4fa2-8e08-ab3c60b4a6a9' +
                        ' AND status: (closed OR open)' +
						' AND message: (*solut* OR *apph* OR *ssweb* OR *arr*)',
            order='asce', 
            sort='createdAt', 
            limit=100
        );

        for alert_response in response.data:
            id_list.append(alert_response.id);

        for entry in id_list:
            get_alert_response = AlertApi().get_alert(identifier=entry, identifier_type='id')
            alert_list.append(get_alert_response);

        configuration.api_key['Authorization'] = integration_key;
        return alert_list;

    except ApiException as err:
        configuration.api_key['Authorization'] = integration_key;
        print("Exception when calling AlertApi->list_alerts: %s\n" % err);

def buildGeneralAlert(message_, priority_):
    
    body = CreateAlertRequest(
        message=message_,
        description=datetime.datetime.today().strftime('%m-%d-%Y %H:%M:%S'),
        priority=priority_
    );

    sendRequest(body);