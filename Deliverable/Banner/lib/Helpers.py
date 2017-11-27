import ConfluenceAPI
import pytz
from pprint import pprint
from math import log, floor
import datetime

app_name = 'Banner'

def handle(response):
        try:
                status = response["id"]
                return str(status);
        except:
                return str(response)

def valid(id):
        try:
                int(id);
                return 1;
        except:
                return 0

def constructPayload(value):
        f = open('/root/' + app_name + ' Scorecard/update.txt', 'a')
        try:
                f.write(value)
        finally:
                f.close()

def imageTag(id, file):
        #Get info about attachment
        try: 
                modDate = ConfluenceAPI.geta(id, file)['results'][0]['_links']['download']
        except IndexError:
    		print('Attachment ' + file + ' not found on ' + ConfluenceAPI.getURL() + ' page with ID: ' + id + '. Are you sure it was attached?');
		exit(2);

        try:
                modDate = str(modDate)
                index_start = modDate.find("version=")
                index_start = index_start + 27
                index_end = modDate.find("'", index_start)
                index_end = index_end - 7
                modDate = modDate[index_start:index_end]
        except:
                print ('Error fetching modificationDate from ' + modDate)
                exit(2)
        
        return "<p style=\\\"text-align:center;\\\"><span class=\\\"confluence-embedded-file-wrapper\\\"><img class=\\\"confluence-embedded-image\\\" src=\\\"/download/attachments/" + id + "/" + file + "?version=1&amp;modificationDate=" + modDate + "&amp;api=v2\\\" data-image-src=\\\"/download/attachments/" + id + "/" + file + "?version=1&amp;modificationDate=" + modDate + "&amp;api=v2\\\" data-unresolved-comment-count=\\\"0\\\" data-linked-resource-id=\\\"" + id + "\\\" data-linked-resource-version=\\\"1\\\" data-linked-resource-type=\\\"attachment\\\" data-linked-resource-default-alias=\\\"" + file + "\\\" data-base-url=\\\"" + ConfluenceAPI.getURL() + "\\\" data-linked-resource-content-type=\\\"image/png\\\" data-linked-resource-container-id=\\\"" + id + "\\\" data-linked-resource-container-version=\\\"1\\\"></img></span></p>"

def getDates():
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(-26 - today.weekday(), today.weekday())]
        collector = list(range(4))

        for x in (range(4)):
                collector[x] = dates[7*x].strftime('%m/%d')
        
        return collector

def unwrap(source_, target_): #parse json response (New Relic API - Helpers.unwrap(NewRelicAPI.Average_Operation_Time(), 'average')
        try:
                return source_['results'][0][target_];
	except:
                print('target_ (' + target_ + ') not found in source_: ' + str(source_));
                exit(2);

def buildStack_3(jsonPack, lim): #NewRelicAPI.buildStack(NewRelicAPI.Slow_URLs(), 10)
        stack = ['BOT__']
        for iteration in range(0, int(lim)):
                stack.append(jsonPack['facets'][iteration]['name'])
                stack.append(str(jsonPack['facets'][iteration]['results'][0]['average']))
                stack.append(str(jsonPack['facets'][iteration]['results'][1]['count']))
        
        return stack

def buildIndefiniteStack(jsonPack): #Helpers.buildIndefiniteStack(NewRelicAPI.Transaction_Perf_Plus())
        stack = ['BOT__']
        iteration = 0;

        while True:
            
             try:
                stack.append(jsonPack['facets'][iteration]['name'])
                stack.append(str(jsonPack['facets'][iteration]['results'][0]['average']))
                stack.append(str(jsonPack['facets'][iteration]['results'][1]['count']))
                stack.append(str(jsonPack['facets'][iteration]['results'][2]['result']))
                
                iteration += 1;

             except IndexError:
                return stack;

             if iteration > 5000:
                print('Infinite loop detected in Banner Helpers buidling the stack for Transaction Perf.');
                exit(2)

def resolve_Statistical_Inequality(new_, old_, domination_Implication_):
        if domination_Implication_ == 'Good':
            if float(new_) > float(old_):
                return "<td style=\\\"color:green;text-align:center;vertical-align:middle;\\\">&#9650;</td>"; #Green /\
            elif float(new_) < float(old_):
                return "<td style=\\\"color:red;text-align:center;vertical-align:middle;\\\">&#9660;</td>"; #Red \/
            else:
                return "<td style=\\\"text-align:center;vertical-align:middle;\\\"></td>";

        elif domination_Implication_ == 'Bad':
            if float(new_) > float(old_):
                return "<td style=\\\"color:red;text-align:center;vertical-align:middle;\\\">&#9650;</td>"; #Red /\
            elif float(new_) < float(old_): 
                return "<td style=\\\"color:green;text-align:center;vertical-align:middle;\\\">&#9660;</td>"; #Green \/ 
            else:
                return "<td style=\\\"text-align:center;vertical-align:middle;\\\"></td>";

        elif domination_Implication_ == 'Indifferent':
            if float(new_) > float(old_): 
                return "<td style=\\\"color:black;text-align:center;vertical-align:middle;\\\">&#9650;</td>"; #Black /\
            elif float(new_) < float(old_):
                return "<td style=\\\"color:black;text-align:center;vertical-align:middle;\\\">&#9660;</td>"; #Black \/
            else:
                return "<td style=\\\"text-align:center;vertical-align:middle;\\\"></td>";

def timeDelta_Resolution(today_):
		return today_ + datetime.timedelta(days=(2 - today_.weekday()));

def hrln(number):
		units = ['', 'K', 'M', 'G', 'T', 'P']
		k = 1000.0
		magnitude = int(floor(log(float(number), k)))
		
		if str(number).find('.0') == -1 and str(number).find('.') != -1: #has decimals
			percision = len(str(number)) - (str(number).find('.') + 1);
			
			try:
				return int((("{0:." + str(percision) + "f}").format(float(number) / k**magnitude))) + units[magnitude];
			except ValueError:
				return (("{0:." + str(percision) + "f}").format(float(number) / k**magnitude)) + units[magnitude];
		else:
			return '%g%s' % (round(float(number) / k**magnitude, 1), units[magnitude])
			
def timeRound(ms_):
		if len(ms_) > 6:
			return str(round(float(ms_) / 1000, 2)) + ' S'
		else: #assume length is in ms
			return ms_ + ' ms';

def checkSQL_Resp(item_, date_):
	if item_ == '':
		print('App Performance MySQL Query caused critical failure for date ' + date_ + '. Missing or corrupted data.');
        # send to OpsGenie
		exit(2);
	else:
		return;

def buildEventList(alerts_):
    alert_list = [];

    for a in alerts_:
        alert_list.append(resolvePriority(a.data.priority));
        alert_list.append(a.data.created_at.strftime('%Y-%m-%d %H:%M:%S'));
        alert_list.append(getDuration(a.data.created_at, a.data.updated_at));
        alert_list.append('Wht is this in OpsGenie?');
        alert_list.append(a.data.message);

    return alert_list;

def getDuration(created, updated):
    duration = updated - created;
    return str(datetime.timedelta(seconds=duration.seconds));

def resolvePriority(priority):
    if priority == 'P1':
        return 'red';
    elif priority == 'P2':
        return 'orange';
    elif priority == 'P3':
        return 'yellow';
    else:
        return 'white';

def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    html=html.replace('&', 'and');
    html=html.replace('<', '&lt;');
    html=html.replace('>', '&gt;');
    html=html.replace('!', '');
    html=html.replace('"', '');
    html=html.replace('\'', '');
    html=html.replace('\\', '/');
    return html;

	
def sort(list_):
	list_out = [];
	for i in range(0, len(list_)):
		if list_[i] == 'red':
			for j in range(0, 5):
				list_out.append(list_[i + j]);
	for i in range(0, len(list_)):
		if list_[i] == 'orange':
			for j in range(0, 5):
				list_out.append(list_[i + j]);
	for i in range(0, len(list_)):
		if list_[i] == 'yellow':
			for j in range(0, 5):
				list_out.append(list_[i + j]);	
	return list_out;