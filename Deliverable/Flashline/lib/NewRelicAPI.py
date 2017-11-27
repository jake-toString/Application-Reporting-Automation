#!/usr/bin/python

import requests
import json
import sys, getopt
import os
import Helpers
import datetime

#Declare local vars
queryKey = '**query key**'
begT = Helpers.timeDelta_Resolution(datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d');
endT = (Helpers.timeDelta_Resolution(datetime.datetime.today())).strftime('%Y-%m-%d');

def Application_Performance():
		
	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20percentage%28%20count%28%2A%29%2C%20where%20duration%20-%20%28pageRenderingDuration%20%2B%20domProcessingDuration%29%20%20%3C%3D%205.0%29%20%20from%20PageView%20where%20appName%20%3D%27kentstateportal.prod%27%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27';
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
					
	r = requests.get(
		url,
		headers=headers
	)

	return r.json()
	
#Application Performance (Backend + Network) is the same as the above query

def Average_Operation_Time():
		
	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20average%28duration%29%20from%20PageView%20where%20appName%20%3D%27kentstateportal.prod%27%20%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27';
	
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
					
	r = requests.get(
		url,
		headers=headers
	)

	return r.json()
	
def Total_Page_Views():

	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20count%28%2A%29%20from%20PageView%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27%20where%20appName%20%3D%20%27kentstateportal.prod%27'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
					
	r = requests.get(
		url,
		headers=headers
	)

	return r.json()
	
		
def SlowOps():

	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20%20count%28duration%29%20from%20PageView%20where%20duration%20%3E%205%20and%20appName%20%3D%27kentstateportal.prod%27%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
					
	r = requests.get(
		url,
		headers=headers
	)

	return r.json()

def Unique_Users():
        url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20uniquecount%28%20username%20%20%29%20from%20PageView%20where%20appName%20%3D%20%27kentstateportal.prod%27%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27'

        headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}

        r = requests.get(
                url,
                headers=headers
        )

        return r.json()

def Slow_URLs():
	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=select%20%20%20%20average%28%20duration%29%2C%20count%28%2A%29%20%20from%20PageView%20facet%20pageUrl%20limit%2010%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27%20where%20appName%20%3D%20%27kentstateportal.prod%27%20%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Fjsp%2F%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Fsearch%2F%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Frender%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25render.user%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcp%2F%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcontent%2F%25%27and%20pageUrl%20NOT%20LIKE%27%25sctwf%25%27and%20pageUrl%20NOT%20LIKE%20%27%25file%3A%2F%2F%2F%25%27'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
					
	r = requests.get(
		url,
		headers=headers
	)

	return r.json()
	
def Transaction_Perf(): #Helpers.buildIndefiniteStack(NewRelicAPI.Transaction_Perf())
    url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20average%28duration%29%2C%20count%28%2A%29%2C%20percentage%28count%28%2A%29%2C%20where%20duration%20%3E%3D%205%29%20from%20PageView%20where%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2FStudentDashboard%27or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2FEmployeeDashboard%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2FFacultyDashboard%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2FKSUView%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2Fcampusresources%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline.kent.edu%2Fwelcome%27%20FACET%20pageUrl%20since%20%27' + begT + '%2004%3A00%3A00%27%20until%20%27' + endT + '%2003%3A59%3A00%27%20limit%20100%20where%20appName%20%3D%20%27kentstateportal.prod%27'	

    headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey};
	
    r = requests.get(url,headers=headers);
	
    return r.json()
	
def Transaction_Perf_Plus():

	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20average%28duration%20-%20%28pageRenderingDuration%20%2B%20domProcessingDuration%29%20%29%2C%20count%28%2a%29%2C%20percentage%28count%28%2a%29%2C%20where%20duration%20-%20%28pageRenderingDuration%20%2B%20domProcessingDuration%29%20%3E%3D%205%29%20from%20PageView%20where%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2FStudentDashboard%27or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2FEmployeeDashboard%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2FFacultyDashboard%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2FKSUView%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2Fcampusresources%27%20or%20pageUrl%20%3D%20%27https%3A%2F%2Fflashline%2ekent%2eedu%2Fwelcome%27%20FACET%20pageUrl%20since%201%20week%20ago%20limit%20100%20where%20appName%20%3D%20%27kentstateportal%2eprod%27'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
	
	r = requests.get(
		url,
		headers=headers
	)

	return r.text
	
def Top_Slow(): #Helpers.buildStack_8(NewRelicAPI.Top_Slow(), 25)
	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20percentage%28count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3E%208%29%20as%20%27Delete%27%2C%20count%28%2A%29%2C%20%20percentage%28count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3C%3D%202%29%20as%20%27%3C%202s%27%2C%20percentage%28count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3E%3D%202%20and%20%28duration%20-%20pageRenderingDuration%29%20%3C%203%29%20as%20%272s%20-%203s%27%2C%20percentage%28%20count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3E%3D3%20and%20%28duration%20-%20pageRenderingDuration%29%20%3C5%29%20as%20%273s%20-%205s%27%2C%20percentage%28count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3E%3D%205%20and%20%28duration%20-%20pageRenderingDuration%29%20%3C8%29%20as%20%275s%20-%208s%27%2C%20percentage%28count%28%2A%29%2C%20where%20%28duration%20-%20pageRenderingDuration%29%20%3E%208%29%20as%20%27%3E%208s%27%20from%20PageView%20since%201%20week%20ago%20facet%20pageUrl%20where%20appName%20%3D%20%27kentstateportal.prod%27%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Frender%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Fjsp%2F%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Fsearch%2F%25%27%20and%20pageUrl%20NOT%20LIKE%20%27%25render.userLayoutRootNode%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcp%2F%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcontent%2F%25%27and%20pageUrl%20NOT%20LIKE%27%25file%3A%25%27%20limit%20100'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
	
	r = requests.get(
		url,
		headers=headers
	)
	
	return r.text[1:int(len(r.text))]

def Top_Slow_Plus(): 

	url = 'https://insights-api.newrelic.com/v1/accounts/1030087/query?nrql=SELECT%20count%28%2a%29%2C%20%20percentage%28count%28%2a%29%2C%20where%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3E%208%29%20as%20%27%3E%208s%27%2C%20percentage%28count%28%2a%29%2C%20where%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3E%3D%205%20and%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3C8%29%20as%20%275s%20-%208s%27%2C%20percentage%28%20count%28%2a%29%2C%20where%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3E%3D3%20and%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3C5%29%20as%20%273s%20-%205s%27%2C%20percentage%28%20count%28%2a%29%2C%20where%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3E%3D%202%20and%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3C%203%29%20as%20%272s%20-%203s%27%2C%20percentage%28%20count%28%2a%29%2C%20where%20duration%20-%20pageRenderingDuration%20-%20domProcessingDuration%20%3C%3D%202%29%20as%20%27%3C%202s%27%20from%20PageView%20since%201%20week%20ago%20facet%20pageUrl%20where%20appName%20%3D%20%27kentstateportal%2eprod%27%20%20and%20pageUrl%20NOT%20LIKE%20%27%25%2Frender%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcp%2F%25%27%20and%20pageUrl%20NOT%20LIKE%27%25%2Fcontent%2F%25%27%20limit%2025'
	headers = {'Content-Type' : 'application/json', 'X-Query-Key' : queryKey}
	
	r = requests.get(
		url,
		headers=headers
	)
	
	return str(r.json())