# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, string
sys.path.append(string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep))

import engine
import types
import pprint
import common
#import cachedoutput

from shared import XMLConfig

version 	= "0.1"
releasedate	= "17-12-2003"

# An outputclass for (e.g.) xml-output, aptly named 'xml',
# should reside in the directory 'output', in a file called
# 'xml.py'. The class should be named 'xml'.

def __getValueOrDefault(dict, key, default):
	if type(dict) is types.DictType:
		if dict.has_key(key):
			return	dict[key]

	return	default

def getOutputClass(parameters, config):
	if len(parameters)>0:
		if string.find(parameters[0], "=")>0:
			parameters = ["html"] + parameters
	else:
		parameters	= ["html"]

	outputmodule	= parameters[0]

# 	if outputmodule == None:
# 		outputmodule = "html"

	try:
		code	= "from output import " + outputmodule
		exec code
		code	= "outputclass = " + outputmodule + "." + outputmodule + "(config)"
		exec code
 	except NameError:
 		raise "The outputmodule you specified ('%s') does not exist" % (outputmodule, )

	return outputclass

def header(parameters, config):
	outputclass	= getOutputClass(parameters, config)
	outputclass.displayHTTPHeader()

def help(parameters, config):
	outputclass	= getOutputClass(parameters, config)
	outputclass.help()

def display(parameters, config):
	outputclass	= getOutputClass(parameters, config)

	info	= outputclass.parseRequest(parameters)
	a		= __getValueOrDefault(info, 'from', -1)
	b		= __getValueOrDefault(info, 'to', -1) # set default to 'all'

	# Ze big red ztartbutton
	items	= engine.getCombinations(a, b, config)

# 	if a==b==-1:
# 		items 	= cachedoutput.combilist
# 	else:
# 		items	= cachedoutput.combilist[a:b]

	outputclass.display(items)

def printUsageInstructions():
	width	= 75

	format	= string.center

	print ""
	print format("WebIndex - a rather universal web indexing device", width)
	print format("-" * (width / 4), width)
	print ""
	print format("version " + version + ", released " + releasedate, width)
	print format("check http://webindex.sourceforge.net/ for the latest release", width)
	print ""
	print "Syntax:"
	print "	webindex	display|header|help"
	print "			<outputmodule>"
	print "			(parameters)"
	print ""
	print ""
	print "Available outputmodules:",

	curdir	= os.path.dirname(sys.argv[0])
	if len(curdir)>0:
		curdir += os.sep
	dirs	= os.listdir(curdir + "output" + os.sep)
	modules	= []
	for dir in dirs:
		parts	= string.split(dir, ".")
		if len(parts)>1:
			if parts[1] == "py" and parts[0][:2]!="__" and parts[0]!='output':
				modules.append("'" + parts[0] + "'")
				print parts[0],

	print ""
	print ""

	print common.justify("WebIndex is a tool to help you maintain a complete index of webpages on your " \
		"webserver. To use it, you need a webserver and (usually) a database. Maintaining a " \
		"complete index of webpages can help you increase your website's visibility in search " \
		"engines. WebIndex provides the functionality to automatically build and maintain such an " \
		"index.", width) + "\n"

	print common.justify("The program you have just run is the main component of WebIndex. It reads your " \
		"configurationfile, which defines which things are in the index, and consequently " \
		"creates and outputs (a part of) the index. Most of the time, it is unneccesary to " \
		"run this program yourself. It is usually run by another program that communicates " \
		"with the search engine.", width) + "\n"

	print common.justify("You can influence how WebIndex creates the index, which part it creates and " \
		"what it output looks like. To do that, you need to provide some extra information.", width) + "\n"

	print common.justify("WebIndex can return information on three subjects. It can 'display' the index " \
		"it has created, it can provide 'help' on the outputmodule you have chosen and it can " \
		"provide HTTP 'header' information for the outputmodule you have chosen. You can specify " \
		"which information you want WebIndex to return by providing one of the three quoted words " \
		"from the previous sentence as WebIndex's first parameter. For example, if you want WebIndex to " \
		"display help for the 'text'-outputmodule, then you can run WebIndex as follows: ", width) + "\n"

	print "	WebIndex help text" + "\n"

	print common.justify("This example introduces another obligated piece of information you have to " \
		"provide, the outputmodule. In this case, the outputmodule WebIndex will use is the 'text' " \
		"outputmodule. On this system, the available outputmodules are " + \
		string.join(modules[:-1], ", ") + " and " + modules[-1] + ". " + \
		"It is not unlikely that additional outputmodules can be found at " \
		"http://webindex.sourceforge.net/", width) + "\n"

	print common.justify("If you run WebIndex in the 'help' mode, as is the case in the example above, " \
		"then the outputmodule displays some information on how that specific outputmodule is " \
		"best used. Usually you have to provide which records from the index you want to show. " \
		"Most outputmodules can be tweaked substantially, so be sure to check which information " \
		"you have to provide to get the best result.", width) + "\n"

	print common.justify("Since WebIndex is most often indirectly accessed through the web, it must include " \
		"some functionality to make communication with the web as smooth as possible. The 'header' " \
		"mode is one of the elements designed to do just that. It displays the HTTP Content-Type " \
		"header of the specified outputmodule.", width) + "\n"

	print common.justify("When using the 'display' mode, WebIndex returns some parts or all of the index " \
		"using the outputmodule you have specified. Which parameters have to be passed to obtain " \
		"the correct results depends on which outputmodule you have chosen to use. Use the 'help' " \
		"mode to figure this out.", width) + "\n"

	print common.justify("Please remember that this is still beta-software and that it is only " \
		"tested on my home computer and a couple of other machines. It is very possible that " \
		"this software contains bugs and flaws. If you happen to find one (or multiple), then " \
		"please send a bug-report to akerboom@ch.tudelft.nl.", width) + "\n"

	print "This software is released under the GNU Public Licence." + "\n"

	print "(c) 2003 Edward Akerboom"

if __name__=="__main__":
	parameters	= sys.argv[1:]

	if len(parameters)>0:
		mode		= string.lower(string.strip(parameters[0]))
		parameters	= parameters[1:]
		defaultconfig	= string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep) + os.sep + "webindex.ini"
		config		= XMLConfig.parse(defaultconfig)	# not the world's best solution

		if string.lower(mode) in ["header", "display", "help"]:
			exec string.lower(mode) + "(parameters, config)"
		else:
			printUsageInstructions()
	else:
		printUsageInstructions()
