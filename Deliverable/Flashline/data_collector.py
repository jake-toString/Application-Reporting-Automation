#!/usr/bin/python
import MySQLdb
import datetime
import sys
from lxml import etree
from io import StringIO
sys.path.insert(0, '/root/Flashline Scorecard/lib')

import NewRelicAPI
import Helpers
import ConfluenceAPI

db = MySQLdb.connect(host="emon-scorecard-shared.c7deyjrbraxq.us-east-1.rds.amazonaws.com",     # your host, usually localhost
                     user="scorecarduser",                                               # your username
                     passwd="cheeseburger",                                              # your password
                     db="scorecards");                                                   # name of the database

cur = db.cursor();

html=ConfluenceAPI.get('Flashline Scorecard - ' + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%m/%d/%Y'))["results"][0]["body"]["view"]["value"]

tree=etree.parse(StringIO(html), etree.HTMLParser())

#--------------Assert First Run
check = [];
cur.execute("SELECT * FROM Flashline_FrontPage WHERE dataDate = '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "';");

for row in cur.fetchall():
    check.append(row[0]);

if len(check) != 0:
    print("Data present in RDS for Flashline app. Skipping data_collector.py for Flashline.");
    exit(0);

#--------------Get new data
app_perf = str(round(NewRelicAPI.Application_Performance()['results'][0]['result'], 2));

avg_op = str(round(NewRelicAPI.Average_Operation_Time()['results'][0]['average'], 2))

total_ops = str(NewRelicAPI.Total_Page_Views()['results'][0]['count']);

slow_ops = str(NewRelicAPI.SlowOps()['results'][0]['count']);

uniq_usr = str(NewRelicAPI.Unique_Users()['results'][0]['uniqueCount'])

#--------------Insert this week's front page data into RDS
cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Application Performance','" + app_perf + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Average Operation Time','" + avg_op + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Total Operations','" + total_ops + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Slow Operations','" + slow_ops + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Unique Users','" + uniq_usr + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=7)).strftime('%Y-%m-%d') + "');");

#--------------Get last week's trailers
NumChanges0 = tree.xpath('/html/body/div[1]/table/tbody/tr[7]/td[3]//text()')[0];

CritEvents0 = tree.xpath('/html/body/div[1]/table/tbody/tr[8]/td[3]//text()')[0];

NumIss0 = tree.xpath('/html/body/div[1]/table/tbody/tr[9]/td[3]//text()')[0];

#---------------Insert last week's trilers
cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Changes','" + NumChanges0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Critical Events','" + CritEvents0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");

cur.execute("INSERT INTO Flashline_FrontPage(ID,dataDescription,dataValue,dataDate) VALUES(0,'Number of Issues Identified','" + NumIss0 + "','" + (Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(days=14)).strftime('%Y%m%d') + "');");

db.commit();
db.close();
