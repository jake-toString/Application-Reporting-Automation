import matplotlib.pyplot as plt
import numpy as np
import datetime
import MySQLdb
import sys

sys.path.insert(0, '/root/Learn Scorecard/lib')

import Helpers

#Initialize SQL
db = MySQLdb.connect(host="**host name**",												 # your host, usually localhost
                     user="user",														 # your username
                     passwd="password",													 # your password
                     db="scorecards");                                                   # name of the database

cur = db.cursor();

app_name = 'Learn';

#Build data lists
aval_total = [];
cur.execute("SELECT avb FROM " + app_name + "_FrontPageGraph WHERE begT > '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(hours=672)).strftime("%Y-%m-%d %H:%M") + "' AND begT < '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=0)).strftime("%Y-%m-%d %H:%M") +"' ORDER BY begT;");

for row in cur.fetchall():
    aval_total.append(row[0]);

uniq_user = [];
cur.execute("SELECT CliCnt FROM " + app_name + "_FrontPageGraph WHERE begT > '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(hours=672)).strftime("%Y-%m-%d %H:%M") + "' AND begT < '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=0)).strftime("%Y-%m-%d %H:%M") +"' ORDER BY begT;");

for row in cur.fetchall():
    uniq_user.append(row[0]);

app_perf = [];
cur.execute("SELECT appPerf FROM " + app_name + "_FrontPageGraph WHERE begT > '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(hours=672)).strftime("%Y-%m-%d %H:%M") + "' AND begT < '" + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=0)).strftime("%Y-%m-%d %H:%M") +"' ORDER BY begT;");

for row in cur.fetchall():
    app_perf.append(row[0]);

db.close(); 

aval_total = list(reversed(aval_total))
app_perf = list(reversed(app_perf))
uniq_user = list(reversed(uniq_user))

size = len(aval_total)

x = np.array([Helpers.timeDelta_Resolution(datetime.datetime.today()) - datetime.timedelta(hours=x) for x in range(0, size)])

fig = plt.figure(figsize=(20,8))
ax1 = fig.add_subplot(111)

axes = plt.gca()
axes.set_ylim([0,100])

ax1.plot(x, aval_total, label='Availability (Total) (%)', linewidth=17.0)
ax1.plot(x, app_perf, label='Application Performance (%)', color='r')
ax1.set_ylabel('Availability and Application Performance Percentage')
leg = ax1.legend(loc=1, bbox_to_anchor=(0.57, -0.1), ncol=2)

for legobj in leg.legendHandles:
    legobj.set_linewidth(2.0)

ax2 = ax1.twinx()
ax2.plot(x, uniq_user, label='Unique Users', color='g')
ax2.set_ylabel('Unique Users', color='g')
ax2.tick_params('y', colors='g')
ax2.legend(loc=2, bbox_to_anchor=(0.57, -0.1))

plt.savefig('/root/' + app_name + ' Scorecard/Graphs/' + app_name + '-FrontPageGraph-' + Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=0)).strftime("%Y-%m-%d") + '.png', bbox_inches="tight")
