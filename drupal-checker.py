#!/usr/bin/python


import os
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
       	sys.stderr.write(colored('\n\nExample: drupal-checker.py -l /root/list.txt\n\n' ,"yellow" ))
        self.print_help()
        sys.exit(2)


f = Figlet(font='slant')
print colored(f.renderText('Drupal Checker'),"red", attrs=['bold'])
print "==========================="
print "Drupal Checker v0.1\nAuthor: 0ways\nGitHub: https://github.com/oways"
print "==========================="
eventlet.monkey_patch()

parser=MyParser()
parser.add_argument('-l', type=argparse.FileType('r'))
args=parser.parse_args()

try:
	urls = args.l.readlines()
except:
	parser.error("")

bar = progressbar.ProgressBar(maxval=len(urls), \
    widgets=[progressbar.Bar('x', '+[', ']+'), ' ', progressbar.Percentage()])

print "\n\nPlease wait .."
bar.start()

drupals = []
content = ""
i = 0
for y in urls:

	try:
		# connection timeout 3 sec
		with eventlet.Timeout(3):
			content = requests.get('http://%s/' % y.replace("\n",""))
	except:
		pass
	# check if the website contain drupal
	if content:
		if "drupal.org" in content.text:
			drupals.append(y.replace("\n",""))
		bar.update(i)
	content = ""
	i = i+1
bar.finish()
print "\n\nResult:\n-------------------\n"
for x in drupals:
	# get drupal version
	a = os.popen('curl --connect-timeout 1 --max-time 1 http://%s/CHANGELOG.txt 2>/dev/null | grep -m2 .' % x).readlines()
	try:
		with eventlet.Timeout(3):
			b = requests.get('http://%s/admin/views/ajax/autocomplete/user/w' % x,allow_redirects=False)
	except:
		pass
	
	if a:
		if "Drupal" in a[0]:
			print colored('{0} [Drupal] ==> {1}'.format(x, a[0].replace("\n","").replace("Drupal","")), 'green')
			version = re.search('[0-9.]+', a[0]).group()
			print "Exploits: https://www.cvedetails.com/google-search-results.php?q=drupal+%s&sa=Search" % version
		if "Drupal" in a[1]:
			print colored('{0} [Drupal] ==> {1}'.format(x, a[1].replace("\n","").replace("Drupal","")), 'green')
			version = re.search('[0-9.]+', a[1]).group()
			print "Exploits: https://www.cvedetails.com/google-search-results.php?q=drupal+%s&sa=Search" % version
	else:
		print colored('{0} [Drupal] ==> Version Not Found'.format(x), 'yellow')
	if 403 != b.status_code and b.status_code != 302:
		print "vuln to autocomplete exploit ==> http://%s/admin/views/ajax/autocomplete/user/w" % x


