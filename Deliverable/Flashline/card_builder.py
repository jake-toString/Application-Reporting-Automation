import sys
import getopt
import os
import datetime
import time
from pprint import pprint
import boto3
import boto.ec2
import botocore
import MySQLdb
sys.path.insert(0, '/root/Flashline Scorecard/lib')

import ConfluenceAPI
import NewRelicAPI
import Helpers
import OpsGenieAPI

def main(argv):

    print('Declaring Lexical Variables...'); # -----------------------------------------------------------------------------------------
    app_name = 'Flashline';                                         # name of the application
    name = app_name + ' build fail.';                               # initial page title in Confluence
    weeks = Helpers.getDates();                                     # assign dates to array for front page table
    today = datetime.datetime.today();                              # today as a date time obj
    BUCKET_NAME = "bucket_name_here";                               # location of the screen shots (S3 Bucket)
    screenshot_path = "/root/Flashline Scorecard/Screenshots/";     # location of the screen shots (local machine)

    # MySQL Vars
    frontPage_Table_Name = 'Flashline_FrontPage';
    dataDescription = '';                                           # name of current front page row item
    MySQL_Time_Vars = [                                             # array of the last 5 wendesdays
        Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'),  # weds of last week
        Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=14)).strftime('%Y-%m-%d'), # wed 2 weeks ago
        Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=21)).strftime('%Y-%m-%d'), # wed 3 weeks ago
        Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=28)).strftime('%Y-%m-%d'), # wed 4 weeks ago
        Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=35)).strftime('%Y-%m-%d')  # wed 5 weeks ago
    ];

    print('Initializing External Modules...'); # ---------------------------------------------------------------------------------------
    s3 = boto3.resource("s3");                                      # init S3 

    db = MySQLdb.connect(                                           # init MySQL
        host="host_url",
        user="user",                                               
        passwd="pass",                                              
        db="scorecards"
    );
    cur = db.cursor();
    print('Done.');

    print("Downloading images from S3..."); # ------------------------------------------------------------------------------------------
    for obj in s3.Bucket(BUCKET_NAME).objects.all():
        filename = obj.key.rsplit('/')[-1];
        s3.Bucket(BUCKET_NAME).download_file(filename, screenshot_path + filename);
    print("Done.");	

    print("Creating Confluence page " + name + "..."); # -------------------------------------------------------------------------------
    id_ = ConfluenceAPI.post(name);
    id_ = Helpers.handle(id_);  
 
    #Assert page has been created
    if not Helpers.valid(id_):
        print(id_);
        exit(2);
    print("Done. Page ID: " + id_);     

    print("Uploading image attachments..."); # -----------------------------------------------------------------------------------------
    for currentFile in os.listdir(screenshot_path):
        ConfluenceAPI.dpost(id_, screenshot_path + currentFile);       
    print("Done."); 

    #--------------------------------------------------------Begin Assembly of Card-----------------------------------------------------
    print("Adding header to Flashline Scorecard..."); # --------------------------------------------------------------------------------
    Helpers.constructPayload(
        "<h1 style=\\\"text-align:center;text-decoration:underline;\\\">" +
            "Flashline 4 Week KPI Review" +
        "</h1>"
    );
    Helpers.constructPayload(
        "<h2 style=\\\"text-align:right;text-decoration:underline;\\\">" +
            MySQL_Time_Vars[0] + " - " + (Helpers.timeDelta_Resolution(today) - datetime.timedelta(days=1)).strftime('%m/%d/%Y') + 
        "</h2>"
    );
    print("Done.");

    print("Adding front page data to Flashline Scorecard..."); # -----------------------------------------------------------------------
    Helpers.constructPayload(
        Helpers.imageTag(
            id_, 
            "FlashLine-PerformancePercentageVsUsers-" + Helpers.timeDelta_Resolution(today).strftime("%m-%d-%Y") + ".png"
        )
    );
    Helpers.constructPayload(
        "<table style=\\\"margin-left: auto;margin-right: auto;\\\" width=\\\"967px\\\" border=\\\"0\\\">"
    );
        
    #Week of # -------------------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td width=\\\"36%\\\">" +
                    "<b>Week starting on</b>" + 
                "</td>"
    );
    Helpers.constructPayload(   
                "<td width=\\\"5%\\\">" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    "<b>" + weeks[3] + "</b>" + 
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\" width=\\\"5%\\\">" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                "<b>" + weeks[2] + "</b>" +
                                "</td>"
    );
    Helpers.constructPayload(
                "<td width=\\\"5%\\\">" + 
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                    "<b>" + weeks[1] + "</b>" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td width=\\\"5%\\\">" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                    "<b>" + weeks[0] + "</b>" +
                "</td>"
    );
    Helpers.constructPayload(
            "</tr>"
    );

    #App Performance Queries -----------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1','-1', '-1'] # reset query result array
    dataDescription = '\'Application Performance\'';

    for it in range(0, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it], MySQL_Time_Vars[it]);

    #App Performance Row --------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Application Performance" +
                    "<p style=\\\"font-size:9px\\\">% of ops completed below 8s</p>" +
                "</td>"
    );

    for it in range(0,4):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Good'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    dataSet[it] + " %" +
                "</td>"
        );
        
    Helpers.constructPayload(
            "</tr>"
    );
    
    #Avg Op Time Queries ---------------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1','-1', '-1'];
    dataDescription = '\'Average Operation Time\'';

    for it in range(0, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it], MySQL_Time_Vars[it]);

    #Avg Op Time Row -------------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Average Operation Time" +
                    "<p style=\\\"font-size:9px\\\">" +
                        "Avg. time for an op to complete = server + network + redirect time" +
                    "</p>" +
                "</td>"
    );
    
    for it in range(0,4):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Bad'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    dataSet[it] + " s" +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Total Ops Queries -----------------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1','-1', '-1'];
    dataDescription = '\'Total Operations\'';

    for it in range(0, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it], MySQL_Time_Vars[it]);

    #Total Ops Row ---------------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Total Operations" +
                    "<p style=\\\"font-size:9px\\\">" +
                        "# of operations (page loads, db queries, Oracle Forms submissions)" +
                    "</p>" +
                "</td>"
    );

    for it in range(0,4):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Indifferent'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    Helpers.hrln(dataSet[it]) +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Slow Ops Queries ------------------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1','-1', '-1'];
    dataDescription = '\'Slow Operations\'';
    
    for it in range(0, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it], MySQL_Time_Vars[it]);

    #Slow Ops Row ----------------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Slow Operations" +
                    "<p style=\\\"font-size:9px\\\"># of operations above the threshold value of 8s</p>" +
                "</td>"
    );

    for it in range(0,4):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Bad'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    Helpers.hrln(dataSet[it]) +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Unique Users Queries --------------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1','-1', '-1'];
    dataDescription = '\'Unique Users\'';

    for it in range(0, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it], MySQL_Time_Vars[it]);

    #Unique Users Row ------------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>Unique Users<p style=\\\"font-size:9px\\\">" +
                    "# of unique users</p>" +
                "</td>"
    );

    for it in range(0,4):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Indifferent'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    Helpers.hrln(dataSet[it]) +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Number of Changes Queries ---------------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1', '-1'];
    dataDescription = '\'Number of Changes\'';

    for it in range(1, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it - 1] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it - 1], MySQL_Time_Vars[it]);

    #Number of Changes Rows ------------------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Number of Changes" +
                    "<p style=\\\"font-size:9px\\\"># of maintenance entries for the service</p>" +
                "</td>"
    );
    
    Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(1, 1, 'Bad'));
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                    "-1" +
                "</td>"
    );

    for it in range(0,3):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Bad'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    dataSet[it] +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Number of Critical Events Queries -------------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1', '-1'];
    dataDescription = '\'Number of Critical Events\'';

    for it in range(1, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it - 1] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it - 1], MySQL_Time_Vars[it]);

    #Number of Critical Events Rows ----------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" +
                    "Number of Critical Events" +
                    "<p style=\\\"font-size:9px\\\"># of critical vents from BPPM, New relic, EE, and OGC</p>" +
                "</td>"
    );
    Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(1, 1, 'Bad'))
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                    "-1" + 
                "</td>"
    );
    
    for it in range(0,3):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Bad'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    dataSet[it] +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );
    
    #Number of Issues Idententified Queries --------------------------------------------------------------------------------------------
    dataSet = ['-1','-1','-1', '-1'];
    dataDescription = '\'Number of Issues Identified\'';

    for it in range(1, 5):
        cur.execute(
            "SELECT " + 
                "dataValue FROM " + frontPage_Table_Name +
            " WHERE " + 
                "dataDate LIKE '" + MySQL_Time_Vars[it] + "'" +
            " AND " + 
                "dataDescription LIKE " + dataDescription + ";"
        );
        dataSet[it - 1] = cur.fetchall()[0][0];
        Helpers.checkSQL_Resp(dataSet[it - 1], MySQL_Time_Vars[it]);
    
    #Number of Issues Identified Rows --------------------------------------------------------------------------------------------------
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td>" + 
                    "Number of Issues Identified<p style=\\\"font-size:9px\\\"># of investigated anomalies outside baseline</p>" +
                "</td>"
    );

    Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(1, 1, 'Bad'))
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" +
                    "-1" + 
                "</td>"
    );
    for it in range(0,3):
        Helpers.constructPayload(Helpers.resolve_Statistical_Inequality(dataSet[it], dataSet[it + 1], 'Bad'));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    dataSet[it] +
                "</td>"
        );

    Helpers.constructPayload(
            "</tr>"
    );

    Helpers.constructPayload(
        "</table>"
    );
    print("Done.");

    print("Adding log page to Flashline Scorecard..."); # ------------------------------------------------------------------------------
    Helpers.constructPayload(
        "<h2 style=\\\"text-align:left;font-weight:bold;\\\">" +
            "FlashLine Application Weekly Review" +
        "</h2>"
    );
    Helpers.constructPayload(
        "<h2 style=\\\"text-align:left;text-decoration:underline;\\\">" +
            "Logs" +
        "</h2>"
    );
    Helpers.constructPayload(
        "<h2 style=\\\"text-align:left;text-decoration:underline;\\\">" +
            "<br/><br/><br/><br/><br/><br/><br/>" +
        "</h2>"
    );
    print("Done.");       
 
    print ("Adding Benchmark App Health to Flashline Scorecard..."); # -----------------------------------------------------------------
    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;font-weight:bold;\\\">" +
            "Benchmark Application Health" +
        "</h3>"
    );
    Helpers.constructPayload(
        Helpers.imageTag(
            id_, 
            "FlashLine-ApplicationHealth-" + Helpers.timeDelta_Resolution(datetime.datetime.now()).strftime("%m-%d-%Y") + ".png"
        )
    );
    print("Done.")

    print('Adding Benchmark Op Time to Flashline Scorecard...'); # ---------------------------------------------------------------------
    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;font-weight:bold;\\\">" +
            "Benchmark Operation Time" +
        "</h3>"
    );
    Helpers.constructPayload(
        Helpers.imageTag(
            id_, 
            "FlashLine-BenchmarkOpTime-" + Helpers.timeDelta_Resolution(datetime.datetime.now()).strftime("%m-%d-%Y") + ".png"
        )
    );
    print("Done.");

    print ("Adding Benchmark Usage to Flashline Scorecard..."); # ----------------------------------------------------------------------
    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;font-weight:bold;\\\">" +
            "Benchmark Usage" +
        "</h3>"
    );
    Helpers.constructPayload(
        Helpers.imageTag(
            id_, 
            "FlashLine-BenchmarkUsage-" + Helpers.timeDelta_Resolution(datetime.datetime.now()).strftime("%m-%d-%Y") + ".png"
        )
    );
    print("Done.");

    print ("Adding top ten slow URLs to Flashline Scorecard..."); # --------------------------------------------------------------------
    dataContainer = Helpers.buildStack_3(NewRelicAPI.Slow_URLs(), 10);
    dataContainer.pop(0); #Remove sentenial

    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;text-decoration:underline;\\\">" +
            "Top 10 Slow Performing URLs" +
        "</h3>"
    );
        
    Helpers.constructPayload(
        "<table style=\\\"margin-left: auto;margin-right: auto;\\\" width=\\\"967px\\\" border=\\\"0\\\">"
    );
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Operation" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" +
                    "Time" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" +
                    "Count" +
                "</td>"
    );
    Helpers.constructPayload(
            "</tr>"
    );

    for y in range(0,10):    
        Helpers.constructPayload(
            "<tr>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:left;vertical-align:middle;\\\">" + 
                    dataContainer.pop(0) + 
                "</td>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" + 
                    str(round(float(dataContainer.pop(0)), 2)) + " s" +
                "</td>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" + 
                    dataContainer.pop(0) + 
                "</td>"
        );
        Helpers.constructPayload(
            "</tr>"
        );

    Helpers.constructPayload(
        "</table>"
    );
    print("Done.");

    print("Adding Transaction Performance to Flashline Scorecard..."); # ---------------------------------------------------------------
    dataContainer = Helpers.buildIndefiniteStack(NewRelicAPI.Transaction_Perf());
    current = dataContainer.append(dataContainer.pop(0));
    current = dataContainer.pop(0);

    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;text-decoration:underline;\\\">" +
            "Transaction Performance" +
        "</h3>"
    );
    Helpers.constructPayload(
        "<table style=\\\"margin-left: auto;margin-right: auto;\\\" width=\\\"967px\\\" border=\\\"0\\\">"
    );
    Helpers.constructPayload(
            "<tr>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Page URL" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" +
                    "Average Duration" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" +
                    "Page Views" +
                "</td>"
    );
    Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;font-weight:bold;\\\">" +
                    "Percentage" +
                "</td>"
    );
    Helpers.constructPayload(
            "</tr>"
    );
        
    while current != 'BOT__':
        Helpers.constructPayload(
            "<tr>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:left;vertical-align:middle;\\\">" + 
                    current + 
                "</td>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    str(round(float(dataContainer.pop(0)), 2))  + " S" +
                "</td>"
        );
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    Helpers.hrln(str(round(float(dataContainer.pop(0)), 2))) + 
                "</td>"
        );
        
        current = str(round(float(dataContainer.pop(0)), 2));
        Helpers.constructPayload(
                "<td style=\\\"text-align:center;vertical-align:middle;\\\">" + 
                    current + " %" +
                "</td>"
        );
        Helpers.constructPayload(
            "</tr>"
        );
        
        current = dataContainer.pop(0);

    Helpers.constructPayload(
        "</table>"
    );
    print("Done.");     

    print('Adding Events to Flashline Scorecard...'); # --------------------------------------------------------------------------------
    Helpers.constructPayload(
        "<h3 style=\\\"text-align:center;text-decoration:underline;\\\">" +
            "All OpsGenie Events (P3 or Higher)" +
        "</h3>"
    );

    dataContainer = Helpers.sort(Helpers.buildEventList(OpsGenieAPI.getAlertList()));
    Helpers.constructPayload(
        "<table style=\\\"margin-left: auto;margin-right: auto;\\\" width=\\\"967px\\\" border=\\\"0\\\">"
    );

    Helpers.constructPayload(
            "<tr>" +
                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Date and Time" +
                "</td>" +

                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Duration (h:m:s)" +
                "</td>" +
                
                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Server" +
                "</td>" +

                "<td style=\\\"text-align:left;vertical-align:middle;font-weight:bold;\\\">" +
                    "Message" +
                "</td>" +
            "</tr>"
    );

    while len(dataContainer) != 0:
        Helpers.constructPayload(
            "<tr>" +
                "<td style=\\\"background-color: " + dataContainer.pop(0) + "; vertical-align: left;\\\">" +
                    Helpers.escape(dataContainer.pop(0)) +
                "</td>" +
                "<td>" +
                    Helpers.escape(dataContainer.pop(0)) +
                "</td>" +
                "<td>" +
                    Helpers.escape(dataContainer.pop(0)) +
                "</td>" +
                "<td>" +
                    Helpers.escape(dataContainer.pop(0)) +
                "</td>" +
            "</tr>" 
        );

    Helpers.constructPayload(
        "</table>"
    );
    print('Done.');

    print("Pushing updates to Confluence..."); # ---------------------------------------------------------------------------------------
    statCode = ConfluenceAPI.put(
        id_, 
        "/root/Flashline Scorecard/update.txt", 
        "Flashline Scorecard - " + Helpers.timeDelta_Resolution(today - datetime.timedelta(days=7)).strftime('%m/%d/%Y'), 1);
   
    if statCode != '200':
        print('PUT Status Code: ' + statCode);
        exit(4);
    else:
        print('Done.');
        print ('https://opswiki.kent.edu/pages/viewpage.action?pageId=' + id_);
        print('Cleaning up...'); # -----------------------------------------------------------------------------------------------------
        os.remove("/root/Flashline Scorecard/update.txt");
        print('Done.');

#Capture args
if __name__ == "__main__":
   main(sys.argv[1:])
