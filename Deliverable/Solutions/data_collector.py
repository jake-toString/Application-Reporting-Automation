#!/usr/bin/python
import MySQLdb
import datetime
import sys
from lxml import etree
from io import StringIO
sys.path.insert(0, '/root/Solutions Scorecard/lib')

import DCRumAPI
import Helpers
import DCRumHelpers
import ConfluenceAPI

db = MySQLdb.connect(host="host name",												     # your host, usually localhost
                     user="user",												         # your username
                     passwd="pass",										                 # your password
                     db="scorecards");                                                   # name of the database

cur = db.cursor();

html=ConfluenceAPI.get('Solutions Scorecard - ' + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%m/%d/%Y'))["results"][0]["body"]["view"]["value"]

tree=etree.parse(StringIO(html), etree.HTMLParser())

#Initialize lexical vars...
app_name = 'Solutions'

#--------------Assert First Run
check = [];
cur.execute("SELECT * FROM " + app_name + "_FrontPage WHERE dataDate = '" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "';");

for row in cur.fetchall():
    check.append(row[0]);

if len(check) != 0:
    print("Data present in RDS for " + app_name + " app. Skipping data_collector.py for " + app_name + ".");
    exit(0);

#--------------Get new data
aval = str(round(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][1]), 2));
app_perf = str(round(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][2]), 2));
avg_op = str(round(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][3]), 2));
total_ops = str(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][4]));
slow_ops = str(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][5]));
uniq_usr = str(float(DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][6][0:DCRumAPI.GET_FrontPage_Sol()['formattedData'][0][6].find(' ', 0)]));

#--------------Insert this week's front page data into RDS
cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Availability','" + aval + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Application Performance','" + app_perf + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Average Operation Time','" + avg_op + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Total Operations','" + total_ops + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Slow Operations','" + slow_ops + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Unique Users','" + uniq_usr + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y%m%d') + "');");

#--------------Get last week's trailers
NumChanges0 = tree.xpath('/html/body/div[1]/table/tbody/tr[8]/td[3]//text()')[0];

CritEvents0 = tree.xpath('/html/body/div[1]/table/tbody/tr[9]/td[3]//text()')[0];

NumIss0 = tree.xpath('/html/body/div[1]/table/tbody/tr[10]/td[3]//text()')[0];

#---------------Insert last week's trailers
cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Changes','" + NumChanges0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Critical Events','" + CritEvents0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO " + app_name + "_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Issues Identified','" + NumIss0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");


#-------------Insert this week's front page graph data into RDS
query = DCRumAPI.GET_Data_to_Export_Sol()['formattedData']

for i in range(0, len(query)):
        cur.execute("INSERT INTO Solutions_FrontPageGraph(ID,begT,Avb,appPerf,CliCnt) VALUES( 0" + ",'" + datetime.datetime.strptime(query[i][0], "%m/%d/%Y %H:%M").strftime("%Y-%m-%d %H:%M") + "'," + query[i][2] + "," + query[i][3] + "," + query[i][4] + ");");

db.commit();
db.close();
