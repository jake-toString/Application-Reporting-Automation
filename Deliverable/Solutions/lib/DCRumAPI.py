#!/usr/bin/python

import requests

user_ = 'user'
pass_ = 'pass'

#----------------------Solutions----------------------------
def GET_Data_to_Export_Sol():
        url = 'https://emoncasprod01.uis.kent.edu/rest/dmiquery/getDMIData3?appId=CVENT&viewId=ClientView&dimensionIds=[\'begT\',\'appl\']&metricIds=[\'Avb\',\'appPerf\',\'CliCnt\']&resolution=1&dimFilters=[[\'appl\',\'Solutions Web Servers\',false]]&metricFilters=[]&sort=[[\'begT\',DESC]]&topFilter=1000&timePeriod=7D&numberOfPeriods=1&dataSourceId=ALL_AGGR';
        
        r = requests.get(
                url,
                auth=(user_, pass_)
        );
        
        return r.json();

def GET_FrontPage_Sol():
        url = 'https://emoncasprod01.uis.kent.edu/rest/dmiquery/getDMIData3?appId=CVENT&viewId=ClientView&dimensionIds=[\'appl\']&metricIds=[\'Avb\',\'appPerf\',\'transTime\',\'trans\',\'slowTrans\',\'trAffUsrAppLdBR\']&resolution=1&dimFilters=[[\'appl\',\'Solutions Web Servers\',false]]&metricFilters=[]&sort=[]&topFilter=1000&timePeriod=7D&numberOfPeriods=1&dataSourceId=ALL_AGGR';

        r = requests.get(
                url,
                auth=(user_, pass_)
        );

        return r.json();

def GET_Top_Ten_Slow_Sol():
        url = 'https://emoncasprod01.uis.kent.edu/rest/dmiquery/getDMIData3?appId=CVENT&viewId=ClientView&dimensionIds=[\'pUrl\',\'anal\',\'appl\']&metricIds=[\'trans\',\'transTime\']&resolution=d&dimFilters=[[\'appl\',\'Solutions Web Servers\',false]]&metricFilters=[[\'trans\',\'>\',100,1]]&sort=[[\'transTime\',DESC]]&topFilter=1000&timePeriod=7D&numberOfPeriods=1&dataSourceId=ALL_AGGR';

        r = requests.get(
                url, 
                auth=(user_, pass_)
        );

        return r.json();
