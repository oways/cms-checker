#!/usr/bin/python

import subprocess
from termcolor import colored
import requests
import eventlet
import time
import progressbar
from pyfiglet import Figlet
import argparse
import sys
import re

class MyParser(argparse.ArgumentParser):
    def error(self, message):
       	sys.stderr.write(colored('\n\nExample: cms-checker.py -l /root/list.txt\n\n' ,"yellow" ))
        self.print_help()
        sys.exit(2)

timeout = 10#1.5
f = Figlet(font='slant')
print colored(f.renderText('CMS Checker'),"red", attrs=['bold'])
print "==========================="
print "CMS Checker v2\nAuthor: 0ways\nGitHub: https://github.com/oways\nCMSs Included: Wordpress,Joomla,Drupal,Sharepoint\nTip: increase timeout if you have slow internet connection"
print "==========================="
eventlet.monkey_patch()

parser=MyParser()
parser.add_argument('-l', type=argparse.FileType('r'))
args=parser.parse_args()

try:
	urls = args.l.readlines()
except:
	parser.error("")

#bar = progressbar.ProgressBar(maxval=len(urls), \
    #widgets=[progressbar.Bar('x', '+[', ']+'), ' ', progressbar.Percentage()])

print "\n\n------- Quick Check ---------\n"
#bar.start()

drupal = []
sharepoint = []
wordpress = []
joomla = []
content = ""
i = 0
for y in urls:
	try:
		# connection timeout 3 sec
		with eventlet.Timeout(timeout):
			content = requests.get('http://%s/' % y.replace("\n",""))
	except:
		pass
	# check if the website contain drupal
	if content!="":
		#Drupal
		if "/sites/default/files/" in content.text:
			drupal.append(y.replace("\n",""))
			print colored("%s => Drupal" % y.replace("\n",""), 'green')

		#sharepoint
		elif "MicrosoftSharePointTeamServices" in content.headers:
			sharepoint.append(y.replace("\n",""))
			sharepoint.append(content.headers['MicrosoftSharePointTeamServices'])
			print colored("%s => Sharepoint" % y.replace("\n",""), 'green')

		#wordpress
		elif "wp-content" in content.text:
			wordpress.append(y.replace("\n",""))
			print colored("%s => Wordpress" % y.replace("\n",""), 'green')
		
		#joomla
		elif "com_content" in content.text:
			joomla.append(y.replace("\n",""))
			print colored("%s => Joomla" % y.replace("\n",""), 'green')

		#unkown
		else:
			print colored("%s => Unkown" % y.replace("\n",""), 'red')
			content = ""
		#bar.update(i)
	
	i = i+1
#bar.finish()
print "\n\n------- Drupal Check --------\n"
if drupal:
	for x in drupal:
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
			print "Exploits: https://www.cvedetails.com/google-search-results.php?q=drupal+%s&sa=Search" % version
		else:
			print colored('{0} [Drupal] ==> Version Not Found'.format(x), 'yellow')
		if b!=0:
			if 200 == b.status_code:
				print colored("vuln to autocomplete exploit ==> http://%s/admin/views/ajax/autocomplete/user/w" % x, 'magenta')
else:
	print colored("Nothing here ..\n\n", 'red')

print "\n\n------- Sharepoint Check ---------\n"
if sharepoint:
	i = 0
	for i in range(len(sharepoint)):
 		if i<sharepoint[i]:
			ch = sharepoint[i]
			if ".0." not in ch:
				continue
			if ch == '15.0.0.4763' or ch == '15.0.0.4797' or ch == '15.0.0.4687' :
				ver = "2013 Build %s" % ch 
			elif ch == '15.0.0.4599':
				ver = "2010 Build %s" % ch
			else:
				ver = ch
			print colored('{0} [SharePoint] ==> {1}'.format(sharepoint[i-1],ver), 'green')
else:
	print colored("Nothing here ..\n\n", 'red')

print "\n\n------- Wordpress Check --------\n"
if wordpress:
	for x in wordpress:
		a=0
		version=""
		v=""
		# get wordpress version
		a = requests.get('http://%s/feed/' % x)

		if a: 
			v = re.search('\?v=[0-9.]+<\/', a.text).group()
			version = re.search('[0-9.]+', v).group()
			print colored('{0} [Wordpress] ==> {1}'.format(x, version), 'green')
			print "Exploits: https://wpvulndb.com/wordpresses/%s" % version.replace('.','')
		else:
			print colored('{0} [Wordpress] ==> Version Not Found'.format(x), 'yellow')
else:
	print colored("Nothing here ..\n\n", 'red')

print "\n\n------- Wordpress Check --------\n"
if joomla:
	for x in joomla:
		a=0
		version=""
		v=""
		# get joomla version
		a = requests.get('http://%s/language/en-GB/en-GB.xml' % x)

		if a: 
			v = re.search('<version>[0-9.]+<\/', a.text).group()
			version = re.search('[0-9.]+', v).group()
			print colored('{0} [Joomla] ==> {1}'.format(x, version), 'green')
		else:
			print colored('{0} [Joomla] ==> Version Not Found'.format(x), 'yellow')
else:
	print colored("Nothing here ..\n\n", 'red')
