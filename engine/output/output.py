# This is the superclass for all the outputclasses in this module
# (c) 2003 Edward Akerboom

import string

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os
sys.path.append(string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep))
sys.path.append(string.join(string.split(os.getcwd(), os.sep)[:-2], os.sep))

import common

class output:
	def __init__(self, config):
		self.config			= config

	def parseRequest(self, parameters):
		answer		= {}

		try:
			answer['from']	= string.atoi(common.getHTTPValue('from', parameters))
			answer['to']	= string.atoi(common.getHTTPValue('to', parameters))
		except:
			pass

		return answer

	def displayHTTPHeader(self):
		print "Content-Type: text/html"

 	def help(self):
 		print "Unfortunately, this outputmodule does not provide any help."

	def default_help(self, name):
		width	= 75
		print common.justify("This outputmodule only supports two parameters, 'from' and 'to'. " \
			"You can specify these parameters by appending a 'parametername=value' pair " \
			"to the commandline for each parameter you want to provide. For example, the " \
			"following commandline should display index entries numbers 10 to 20.", width)

		print ""

		name	= string.split(name, ".")[-1]
		print "	druid display " + name + " from=10 to=20"

		print ""
		print common.justify("Beware not to include any whitespace ('spaces') between the " \
			"parameter, its value and the equals-sign", width)

	def displayItem(self, item):
		pass

	def displayHeader(self):
		pass

	def displayFooter(self):
		pass

	def display(self, items):
		self.displayHeader()
		for item in items:
			self.displayItem(item)
		self.displayFooter()
