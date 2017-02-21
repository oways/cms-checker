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

class MyParser(argparse.ArgumentParser):
    def error(self, message):
       	sys.stderr.write(colored('\n\nExample: drupalfinder.py -l /root/list.txt\n\n' ,"yellow" ))
        self.print_help()
        sys.exit(2)


f = Figlet(font='slant')
print colored(f.renderText('Drupal Finder'),"red", attrs=['bold'])
print "==========================="
print "Drupal Finder v0.1\nAuthor: 0ways\nGitHub: https://github.com/oways"
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
		# connection timeout 1 sec
		with eventlet.Timeout(1):
			content = requests.get('http://%s/' % y.replace("\n",""))
	except:
		nothing = ""
	# check if the website contain drupal
	if content:
		if "http://drupal.org" in content.text:
			drupals.append(y.replace("\n",""))
		bar.update(i)
	i = i+1
bar.finish()
print "\n\nResult:\n-------------------\n"
for x in drupals:
	# get drupal version
	a = os.popen('curl --connect-timeout 1 --max-time 1 http://%s/CHANGELOG.txt 2>/dev/null | grep -m1 .' % x).readlines()
	if a and "Drupal" in a[0]:
		print colored('{0} [Drupal] ==> {1}'.format(x, a[0].replace("\n","").replace("Drupal","")), 'green')
	else: 
		print colored('{0} [Drupal] ==> Version Not Found'.format(x), 'yellow')