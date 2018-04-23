#!/usr/bin/python

import sys, os, re, json, requests, threading, bs4, argparse, time, subprocess
from Queue import Queue
from pyfiglet import Figlet
from termcolor import colored

listData =[]
timeout = 3#1.5
f = Figlet(font='slant')
print colored(f.renderText('CMS Checker'),"red", attrs=['bold'])
print "==========================="
print "CMS Checker v3.1\nAuthor: 0ways\nGitHub: https://github.com/oways\nCMSs Included: Wordpress,Joomla,Drupal,Sharepoint\nNote: increase timeout if you have a slow internet connection"
print "==========================="

path = "result-%s" % time.strftime("%s-%m-%H_%d-%m-%Y")
outputPath="%s" % path

def getServerIP(x):
	c = 'nslookup %s |grep -m2 Address | tail -1 | cut -d":" -f2' % x
	push = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	a, errors = push.communicate()
	return a
class ThreadedFetch(object):

	class FetchUrl(threading.Thread):
		def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue
		def run(self):
			while self.queue.empty() == False:
				try:
					url = self.queue.get()
					title=""
					content = ""
					ip_port =""
					Status = ""
					srv =""
					content = requests.get('http://%s/' % url,timeout=timeout, stream=True)
					html = bs4.BeautifulSoup(content.text,"html.parser")
					ip_ = getServerIP(url)

					if content!=0:
						if not os.path.exists(outputPath):
							os.mkdir(outputPath,0755)
						htmlpath = "%s/%s.html" %(outputPath,url)
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
						#Drupal 
						if "/sites/default/files/" in content.text:
							listData.append({"Url":url,"Title":title,"IP":ip_,"Status":content.status_code,"Server":srv,"CMS":"Drupal","Version":"","Reference":""})
							print colored("%s => [Drupal] Server: %s" % (url,srv), 'green')

						#sharepoint
						elif "MicrosoftSharePointTeamServices" in content.headers:
							listData.append({"Url":url,"Title":title,"IP":ip_,"Status":content.status_code,"Server":srv,"CMS":"SharePoint","Version":content.headers['MicrosoftSharePointTeamServices'],"Reference":""})
							print colored("%s => [Sharepoint] Server: %s" % (url,srv), 'green')

						#wordpress
						elif "wp-content" in content.text:
							listData.append({"Url":url,"Title":title,"IP":ip_,"Status":content.status_code,"Server":srv,"CMS":"Wordpress","Version":"","Reference":""})
							print colored("%s => [Wordpress] Server: %s" % (url,srv), 'green')
						
						#joomla
						elif "com_content" in content.text:
							listData.append({"Url":url,"Title":title,"IP":ip_,"Status":content.status_code,"Server":srv,"CMS":"Joomla","Version":"","Reference":""})
							print colored("%s => [Joomla] Server: %s" % (url,srv), 'green')

						#unkown app / adding server type
						else:
							listData.append({"Url":url,"Title":title,"IP":ip_,"Status":content.status_code,"Server":srv,"CMS":"Unknown","Version":"","Reference":""})
							print colored("%s => Server: %s" % (url,srv), 'red')
				except:
					pass
				self.queue.task_done()

	def __init__(self, urls=[], directory_structure=False, thread_count=5):
		self.queue = Queue(0) # Infinite sized queue
		self.threads = []
		self.thread_count = thread_count
		self.directory_structure = directory_structure
		
		# Prepopulate queue with any values we were given
		for url in urls:
			self.queue.put(url)


	def run(self):
		#for url in array:
		for i in range(self.thread_count):
			thread = ThreadedFetch.FetchUrl(self.queue)
			thread.start()
			self.threads.append(thread)
#		if self.queue.qsize() > 0:
			self.queue.join()


class ThreadedFetch2(object):

	class FetchUrl2(threading.Thread):
		def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue

		def run(self):
			while self.queue.empty() == False:
				try:
					data = self.queue.get()
					x = data["Url"]
					if data["CMS"]=="Drupal":
						b=0
						a=""
						version=""
						# get drupal version
						s = 'curl --connect-timeout 1 --max-time 1 http://%s/CHANGELOG.txt 2>/dev/null | grep -m2 .' % x
						push = subprocess.Popen(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
						a, errors = push.communicate()
						b = requests.get('http://%s/admin/views/ajax/autocomplete/user/w' % x, allow_redirects=False,timeout=timeout)
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
					except:
						pass
				self.queue.task_done()

	def __init__(self, urls=[], directory_structure=False, thread_count=5):
		self.queue = Queue(0) # Infinite sized queue
		self.threads = []
		self.thread_count = thread_count
		self.directory_structure = directory_structure
		
		# Prepopulate queue with any values we were given
		for url in urls:
			self.queue.put(url)


	def run(self):
		#for url in array:
		for i in range(self.thread_count):
			thread = ThreadedFetch2.FetchUrl2(self.queue)
			thread.start()
			self.threads.append(thread)
		#if self.queue.qsize() > 0:
			self.queue.join()

def main():
	if len(sys.argv) == 1:
		print 'No URLs given.'
		sys.exit()
	# Number of threads
	if len(sys.argv) >= 3:
		threads = int(sys.argv[2])
	else:
		threads = 20

	with open(sys.argv[1], "r") as ins:
		urls = []
		for line in ins:
			urls.append(line.rstrip())
	print "\n\n------- Quick Check ---------\n"
	Fetcher = ThreadedFetch(urls, True, threads)
	Fetcher.run()

	print "\n------- Version Check ---------\n"
	Fetcher2 = ThreadedFetch2(listData, True, threads)
	Fetcher2.run()
	print "\nGenerating the Output ..."
	html='<html><head><title>CMS Checker</title><script src="https://raw.githubusercontent.com/oways/cms-checker/master/js/jquery-1.12.4.js"></script></script><script src="https://raw.githubusercontent.com/oways/cms-checker/master/js/dataTables.bootstrap.min.js"></script><script src="https://raw.githubusercontent.com/oways/cms-checker/master/js/jquery.dataTables.min.js"></script><link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"><link rel="stylesheet" type="text/css" href="https://raw.githubusercontent.com/oways/cms-checker/master/css/dataTables.bootstrap.min.css"></head><script>$(document).ready(function() {$("#example").DataTable();} );</script><div id="example_wrapper" class="dataTables_wrapper form-inline dt-bootstrap"><table id="example" class="table table-striped table-bordered" cellspacing="0" width="100%"><thead><th>#</th><th>Title</th><th>Url</th><th>IP</th><th>Status</th><th>CMS</th><th>Server</th><th>HTML Snapshot</th><th>Reference</th></thead><tbody>'
	ID=0
	for dat in listData:
		html += "<tr><td>%s</td><td>%s</td><td><a href='http://%s' target='_blank'>%s</a></td><td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td><a href='./%s.html' target='_blank'>View</a></td><td>%s</td></tr>" % (ID,dat["Title"],dat["Url"],dat["Url"],dat["IP"],dat["Status"],dat["CMS"],dat["Version"],dat["Server"],dat["Url"],dat["Reference"])
		ID = ID+1
	html += "</tbody></table></div></html>"
	outputHtml = "%s/index.html" % outputPath
	with open(outputHtml , "w+") as f:
	    f.write(html)
	print colored("Output path: %s\n" % outputHtml, 'green')
	
if __name__ == "__main__":
	main()
