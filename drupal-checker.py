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

timeout = 3
f = Figlet(font='slant')
print colored(f.renderText('Drupal Checker'),"red", attrs=['bold'])
print "==========================="
print "Drupal Checker v0.1\nAuthor: 0ways\nGitHub: https://github.com/oways\nTip: increase timeout if you have slow internet connection"
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
		with eventlet.Timeout(timeout):
			content = requests.get('http://%s/' % y.replace("\n",""))
	except:
		pass
	# check if the website contain drupal
	if content:
		if "/sites/default/files/js/" in content.text:
			drupals.append(y.replace("\n",""))
		bar.update(i)
	content = ""
	i = i+1
bar.finish()
print "\n\nResult:\n-------------------\n"
for x in drupals:
	b=0
	a={0}
	o=2
	version=""
	# get drupal version
	a = os.popen('curl --connect-timeout 1 --max-time 1 http://%s/CHANGELOG.txt 2>/dev/null | grep -m2 .' % x).readlines()
	try:
		with eventlet.Timeout(timeout):
			b = requests.get('http://%s/admin/views/ajax/autocomplete/user/w' % x, allow_redirects=False)
	except:
		pass
	if a[0]!=0 and "DOCTYPE" not in a[0]:
		if "Drupal" in a[0]:
			o=0
		elif "Drupal" in a[1]:
			o=1
		if o!=2:	
			print colored('{0} [Drupal] ==> {1}'.format(x, a[o].replace("\n","").replace("Drupal","")), 'green')
			version = re.search('[0-9.]+', a[o]).group()
			print "Exploits: https://www.cvedetails.com/google-search-results.php?q=drupal+%s&sa=Search" % version
	else:
		print colored('{0} [Drupal] ==> Version Not Found'.format(x), 'yellow')
	if b!=0:
		if 200 == b.status_code:
			print colored("vuln to autocomplete exploit ==> http://%s/admin/views/ajax/autocomplete/user/w" % x, 'magenta')



