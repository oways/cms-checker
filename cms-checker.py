#!/usr/bin/python

import subprocess
from termcolor import colored
import eventlet
import time
import progressbar
from pyfiglet import Figlet
import argparse
import sys
import re
import bs4
import os
import Queue
import threading


import httplib

def getresponse(self,*args,**kwargs):
    response = self._old_getresponse(*args,**kwargs)
    if self.sock:
        response.peer = self.sock.getpeername()
    else:
        response.peer = None
    return response


httplib.HTTPConnection._old_getresponse = httplib.HTTPConnection.getresponse
httplib.HTTPConnection.getresponse = getresponse

import requests

def check_peer(resp):
    orig_resp = resp.raw._original_response
    if hasattr(orig_resp,'peer'):
        return getattr(orig_resp,'peer')

class MyParser(argparse.ArgumentParser):
    def error(self, message):
       	sys.stderr.write(colored('\n\nExample: cms-checker.py -l /root/list.txt\n\n' ,"yellow" ))
        self.print_help()
        sys.exit(2)

timeout = 50#1.5
f = Figlet(font='slant')
print colored(f.renderText('CMS Checker'),"red", attrs=['bold'])
print "==========================="
print "CMS Checker v3.0\nAuthor: 0ways\nGitHub: https://github.com/oways\nCMSs Included: Wordpress,Joomla,Drupal,Sharepoint\nTip: increase timeout if you have a slow internet connection"
print "==========================="
eventlet.monkey_patch()
parser=MyParser()
parser.add_argument('-l', type=argparse.FileType('r'))
args=parser.parse_args()

path = "result-%s" % time.strftime("%s-%m-%H_%d-%m-%Y")
outputPath="%s" % path

try:
	urls = args.l.readlines()
except:
	parser.error("")

listData =[]

q = Queue.Queue()

def quick(q,url):
	title=""
	content = ""
	ip_port =""
	Status = ""
	srv =""
	try:
		# connection timeout
		with eventlet.Timeout(timeout):
			content = requests.get('http://%s/' % url.replace("\n",""))
			html = bs4.BeautifulSoup(content.text,"html.parser")
			ip_port = check_peer(content)
	except:
		content=0

	if content!=0:
		if not os.path.exists(outputPath):
			os.mkdir(outputPath,0755)
		htmlpath = "%s/%s.html" %(outputPath,url.replace("\n",""))
		with open(htmlpath , "w+") as f:
			f.write(content.text.encode('utf-8'))
		if html.title:
			title = html.title.text.replace("<title>","").replace("</title>","").encode('utf-8')
		else:
			title =""
		if content.headers!="":
			if "Server" in content.headers:
				srv=content.headers['Server']
			else:
				srv=""
		else:
			srv=""
		#Drupal content.status_code
		if "/sites/default/files/" in content.text:
			listData.append({"Url":url.replace("\n",""),"Title":title,"(IP, Port)":ip_port,"Status":content.status_code,"Server":srv,"CMS":"Drupal","Version":"","Reference":""})
			print colored("%s => [Drupal] Server: %s" % (url.replace("\n",""),srv), 'green')

		#sharepoint
		elif "MicrosoftSharePointTeamServices" in content.headers:
			listData.append({"Url":url.replace("\n",""),"Title":title,"(IP, Port)":ip_port,"Status":content.status_code,"Server":srv,"CMS":"SharePoint","Version":content.headers['MicrosoftSharePointTeamServices'],"Reference":""})
			print colored("%s => [Sharepoint] Server: %s" % (url.replace("\n",""),srv), 'green')

		#wordpress
		elif "wp-content" in content.text:
			listData.append({"Url":url.replace("\n",""),"Title":title,"(IP, Port)":ip_port,"Status":content.status_code,"Server":srv,"CMS":"Wordpress","Version":"","Reference":""})
			print colored("%s => [Wordpress] Server: %s" % (url.replace("\n",""),srv), 'green')
		
		#joomla
		elif "com_content" in content.text:
			listData.append({"Url":url.replace("\n",""),"Title":title,"(IP, Port)":ip_port,"Status":content.status_code,"Server":srv,"CMS":"Joomla","Version":"","Reference":""})
			print colored("%s => [Joomla] Server: %s" % (url.replace("\n",""),srv), 'green')

		#unkown app / adding server type
		else:
			listData.append({"Url":url.replace("\n",""),"Title":title,"(IP, Port)":ip_port,"Status":content.status_code,"Server":srv,"CMS":"Unknown","Version":"","Reference":""})
			print colored("%s => Server: %s" % (url.replace("\n",""),srv), 'red')


def version(q,data):
	x = data["Url"]
	if data["CMS"]=="Drupal":
		b=0
		a=""
		version=""
		# get drupal version
		s = 'curl --connect-timeout 1 --max-time 1 http://%s/CHANGELOG.txt 2>/dev/null | grep -m2 .' % x
		push = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		a, errors = push.communicate()

		try:
			with eventlet.Timeout(timeout):
				b = requests.get('http://%s/admin/views/ajax/autocomplete/user/w' % x, allow_redirects=False)
		except:
			pass
		if "Drupal" in a: 
			fullversion = re.search('[0-9.]+, [0-9]{4}-[0-9]{2}-[0-9]{2}', a).group()
			print colored('{0} [Drupal] ==> {1}'.format(x, fullversion), 'green')
			version = re.search('[0-9.]+', a).group()
			data["Version"] = version
			data["Reference"] = "https://www.cvedetails.com/google-search-results.php?q=drupal+%s&sa=Search" % version
			print "Exploits: %s" % data["Reference"]
			data["Reference"] = "<a href='%s' target='_blank'>Link</a>" % data["Reference"]


		else:
			print colored('{0} [Drupal] ==> Version Not Found'.format(x), 'yellow')
		if b!=0:
			if 200 == b.status_code:
				print colored("vuln to autocomplete exploit ==> http://%s/admin/views/ajax/autocomplete/user/w" % x, 'magenta')

	if data["CMS"]=="SharePoint":
		i = 0
	 	if i<data["Version"]:
			ch = data["Version"]
			if ".0." not in ch:
				pass
			if ch == '15.0.0.4763' or ch == '15.0.0.4797' or ch == '15.0.0.4687' :
				ver = "2013 Build %s" % ch 
			elif ch == '15.0.0.4599':
				ver = "2010 Build %s" % ch
			else:
				ver = ch
			print colored('{0} [SharePoint] ==> {1}'.format(x,ver), 'green')
			data["Version"] = ver


	if data["CMS"]=="WordPress":
		a=0
		version=""
		v=""
		# get wordpress version
		a = requests.get('http://%s/feed/' % x)

		if a: 
			v = re.search('\?v=[0-9.]+<\/', a.text).group()
			version = re.search('[0-9.]+', v).group()
			print colored('{0} [Wordpress] ==> {1}'.format(x, version), 'green')
			data["Version"] = version.replace('.','')
			data["Reference"] = "https://wpvulndb.com/wordpresses/%s" % version.replace('.','')
			print "Exploits: %s" % data["Reference"]
			data["Reference"] = "<a href='%s' target='_blank'>Link</a>" % data["Reference"]
		else:
			print colored('{0} [Wordpress] ==> Version Not Found'.format(x), 'yellow')

	if data["CMS"]=="Joomla":
		a=0
		version=""
		v=""
		# get joomla version
		a = requests.get('http://%s/language/en-GB/en-GB.xml' % x)

		if a: 
			v = re.search('<version>[0-9.]+<\/', a.text).group()
			version = re.search('[0-9.]+', v).group()
			data["Version"] =  version
			print colored('{0} [Joomla] ==> {1}'.format(x, version), 'green')
		else:
			print colored('{0} [Joomla] ==> Version Not Found'.format(x), 'yellow')

print "\n\n------- Quick Check ---------\n"
threads = []
for url in urls:
	t = threading.Thread(target=quick, args = (q,url))
	t.daemon=True
	t.start()
	threads.append(t)
for t in threads:
	t.join()

print "\n------- Version Check ---------\n"
threads = []
for data in listData:
	t = threading.Thread(target=version, args = (q,data))
	t.daemon=True
	t.start()
	threads.append(t)
for t in threads:
	t.join()

print "\nGenerating the Output ..."
html='<html><head><title>CMS Checker</title><script src="../js/jquery-1.12.4.js"></script></script><script src="../js/dataTables.bootstrap.min.js"></script><script src="../js/jquery.dataTables.min.js"></script><link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><link rel="stylesheet" type="text/css" href="../css/dataTables.bootstrap.min.css"></head><script>$(document).ready(function() {$("#example").DataTable();} );</script><div id="example_wrapper" class="dataTables_wrapper form-inline dt-bootstrap"><table id="example" class="table table-striped table-bordered" cellspacing="0" width="100%"><thead><th>#</th><th>Title</th><th>Url</th><th>(IP, Port)</th><th>Status</th><th>CMS</th><th>Server</th><th>HTML Snapshot</th><th>Reference</th></thead><tbody>'
ID=0
for dat in listData:
	html += "<tr><td>%s</td><td>%s</td><td><a href='http://%s' target='_blank'>%s</a></td><td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td><a href='./%s.html' target='_blank'>View</a></td><td>%s</td></tr>" % (ID,dat["Title"],dat["Url"],dat["Url"],dat["(IP, Port)"],dat["Status"],dat["CMS"],dat["Version"],dat["Server"],dat["Url"],dat["Reference"])
	ID = ID+1
html += "</tbody></table></div></html>"

outputHtml = "%s/index.html" % outputPath
with open(outputHtml , "w+") as f:
    f.write(html)

print colored("Output path: %s\n" % outputHtml, 'green')


