#!/usr/bin/python

import requests
import json
import sys, getopt
import os

#Declare local vars
url = '**host name**'
user = 'user'
pass_ = 'pass'
SPACE_ID = 'EM'

def post(title):
		
	payload = '{"type":"page","title":"' + title + '","ancestors":[{"id":14058846}],"space":{"key":"EM"},"body":{"storage":{"value":"<p>This is a new page</p>","representation":"storage"}}}'

	headers = {'Content-Type' : 'application/json'}
					
	r = requests.post(
		url + '/rest/api/content/',
		data = payload,
		auth=(user, pass_),
		headers=headers
	)

	return r.json()
	
def geta(id, file):
	
	payload = {'filename' : file}
		
	r = requests.get(
		url + '/rest/api/content/' + id + '/child/attachment',
		params = payload,
		auth=(user, pass_)
	)
	
	return r.json()
	
def put(id, path, title, version): #return current version number
	
	version = int(version) + 1
	update = '"'
	
	f = open(path, 'r')
	try:
		update += f.read()
	finally:
		f.close()
		
	update += '"'

	payload = '{"version":{"number": "' + str(version) + '"},"title": "' + title + '","type":"page","body":{"storage": {"value": ' + update + ',"representation": "storage"}}}'

	headers = {'Content-Type' : 'application/json'}
	
	r = requests.put(
		url + '/rest/api/content/' + id,
		data = payload,
		auth=(user, pass_),
		headers=headers
	)
		
	return str(r.status_code);
	
def dpost(id, path):

	files = {'file': open(path, 'rb')}
	
	headers = {'X-Atlassian-Token' : 'nocheck'}
	
	r = requests.post(
		url + '/rest/api/content/' + id + '/child/attachment',
		files=files,
		auth=(user, pass_),
		headers=headers
	)
		
	print('DPOST Status Code: ' + str(r.status_code))
	
def get(title):
		
	payload = {'spaceKey' : 'EM', 'title' : title}
		
	r = requests.get(
		url + '/rest/api/content/?expand=version,body.view',
		params = payload,
		auth=(user, pass_)
	)
		
	return r.json()
	
def delete(id):
			
	r = requests.delete(
		url + '/rest/api/content/' + id,
		auth=(user, pass_)
	)
		
	if r.status_code == 204 or r.status_code == 200:
		print('Page with ' + id + ' successfully deleted.')
	else: 
		print ('Couldn\'t find page ID or failed to delete page.')
		
def getURL():
	return url
