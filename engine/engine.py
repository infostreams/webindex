import 	string
import 	pprint
import 	types
import 	sys
import 	os


# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, os.path
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-1], os.sep))

from 	shared	import XMLConfig
from	shared	import fileIndexer

# Not good. Fix.
from 	graph			import *
from 	graphIterator 	import *
from	graphStorage	import *
from	graphCommon		import *



# def printSummary(_graph):
# 	if _graph!=None:
# 		nodes	= graph.getNodeList(_graph, [])
# 		print "Available nodes:", nodes
# 		processed =[]
# 		for nodename in nodes:
# 			if not nodename in processed:
# 				node	= XMLConfig.getNode(nodename, _graph['refered_by'][0]['parent'])
# 	#			graph.printGraph(_graph['refered_by'][0]['parent'])
# 				if node!=None:
# 					print "%s, combi %d, heeft waarde %s" % (nodename, node['recordnr'], node['recordcontents'])
# 					processed.append(nodename)

def __getItemsFromInput(start, end, input):
	""" get <item></item>-pairs number
		start...end from the input-list """

# 	print "getting items", start
# 	print "to", end
# 	print "from", input

	if start==-1 and end==-1:
		all		= 1
		start 	= 0
	else:
		all = 0
		if start<0 or start>end:
			return None

	answer			= []
	maxitemcount 	= end - start + 1
	itemcount		= 0
	regexp			= re.compile("^\s*(.+?)\s*=\s*(.+?)\s*$")

	for linenr in range(len(input)):

		strippedlowercaseline	= string.strip(string.lower(input[linenr]))
		if strippedlowercaseline == "<item>":

			itemcount += 1

			if itemcount>start:

				local	= {}

				for index in range(linenr+1, len(input)):
					parts	= re.findall(regexp, input[index])
					if len(parts)>0:
						local[parts[0][0]]=parts[0][1]
					strippedlowercaseline	= string.strip(string.lower(input[index]))
					if strippedlowercaseline=="</item>":
						break

				answer.append(local)

			if itemcount==start + maxitemcount and all==0:
				break

	if answer==[]:
		answer	= itemcount

	return answer

def __getOutputFromScript(scriptConfigEntry):
	""" run the script specified in the 'script'-section
		from the configfile and return its output """

	vars	= XMLConfig.getVariables(scriptConfigEntry)

	# execute the script
	if vars.has_key('script'):
		pipe	= os.popen3(vars['script'], "t")

		# output written to stderr causes an error to be raised
		stderr	= pipe[2]
		line	= stderr.readline()[:-1]
		error	= line

		while len(line)>0:
			line= stderr.readline()[:-1]
			error = "%s\n%s" % (error, line)

		if len(error)>0:
			raise "While trying to execute <<<%s>>> the following error occurred:\n%s\n\n\n----" \
				"\nTip (free!): If applicable, in Windows, the script is executed using 'cmd.exe /c'.\n" \
				"If you can't get the 'script'-tags to work, then enter 'cmd.exe /?' in a command-shell\n" \
				"for more info on how to fix your problem. " % (vars['script'], error)

		# output written to stdout is processed by separate code
		stdout	= pipe[1]
		line	= string.rstrip(stdout.readline())
		output	= [line]

		while len(line)>0:
			line= string.rstrip(stdout.readline())
			output.append(line)

		return output

	else:

		return None

def __getDirItems(start, end, fileindex):

	if start==-1 and end==-1:
		all	= 1
	else:
		all = 0

	counter	= 0
	answer	= []
	for file in fileindex:
		if (counter>=start and counter<end) or (all==1):
			answer.append(file['public'])
		counter	+= 1

	if answer == []:
		return counter
	else:
		return answer

def __getRange(start, index, totalitems, printeditems):

	if start - index > 0:
		a	= start - index
	else:
		a	= 0

	if printeditems < totalitems:
		b	= a + totalitems - printeditems - 1
	else:
		b	= a - 1

	answer			= {}
	answer['from']	= a
	answer['to']	= b

	return answer

def getCombinations(start, end, config, nostorage=0):
	""" Get a specific range of combinations from combination
		number 'start' up to and including number 'end'

		Combinations are counted from 0 (which means that
		'60' is the 61st combination) """

	# check to see if we must return _all_ combinations
	if end==-1 and start==-1:
		start 	= 0
		all		= 1
	else:
		all	= 0

	if end <= start and all==0:
		return None

	totalitems		= end - start + 1
	printeditems	= 0
	index			= 0 # how much combinations are 'behind us'?

	# extract the database-connection parameters from the configuration
	dbparameters	= XMLConfig.getVariables(XMLConfig.getEntries("database", config)[0])
	for requireditem in ['dbclient', 'dbname', 'dsn', 'host', 'password', 'user', 'connectstring']:
		if not dbparameters.has_key(requireditem):
			dbparameters[requireditem]	= None

	items		= []

	# First, list the dynamic webpages
	dynamic		= XMLConfig.getEntries('dynamic', config)
	for dynentry in dynamic:
		depgraphs	= graph.createDependencyGraphs(dynentry)

		for depgraph in depgraphs:

			if start - index > 0:
				startAt	= start - index
			else:
				startAt = 0

			# TODO: REMOVE THIS
			# TODO: Fout zit in openGraph
#			continue

			depgraph 	= openGraph(depgraph, startAt, nostorage, dbparameters)


			if type(depgraph) != types.IntType:

				# increase index with starting combination of graph
				index += startAt

				while 1==1:
					if printeditems<totalitems or all==1:
						try:
							combi	= giveNextCombination(depgraph)
						except:
							break
						if combi!=None:
							items.append(getCombinationItem(combi))
							printeditems += 1
							index		 += 1
						else:
							break
					else:
						break

				if nostorage == 0:
					recordState(depgraph)

			else:

				# if the answer returned by 'openGraph' is
				# an integer, then this means the provided
				# graph is out of combinations. The integer
				# returned is equal to the number of combinations
				# that has been provided by the graph.
				#
				# Here we increase the number of combinations
				# that are behind us with this number.
				index	+= depgraph

			closeDatabaseConnections(depgraph)

#	print "#1 Printing range (%d, %d), index=%d, printed %d of %d items" % (start, end, index, printeditems, totalitems)

	if printeditems<totalitems or all==1:

		# Second, process the 'script'-entries
		scripts		= XMLConfig.getEntries('script', config)
		for script in scripts:

			output	= __getOutputFromScript(script)

			# which items do we need to get?
			_range	= __getRange(start, index, totalitems, printeditems)

			if all==0:
				answer	= __getItemsFromInput(_range['from'], _range['to'], output)
			else:
				answer	= __getItemsFromInput(-1, -1, output)

			if type(answer) == types.IntType:

	        	# If the returned answer is not a list but an integer,
	        	# then this integer represents the number of combinations
	        	# in the output of this script
				index	+= answer

			else:

				if type(answer) == types.ListType:
					# if the answer is a list, then append the contents of this list
					# to the already obtained partial answer
					items.extend(answer)
					printeditems += len(answer)

#		print "#2 Printing range (%d, %d), index=%d, printed %d of %d items" % (start, end, index, printeditems, totalitems)

	if printeditems<totalitems or all==1:

		# Third, process the 'textfile'-entries
		textfiles	= XMLConfig.getEntries('textfile', config)
		for textfile in textfiles:
			vars	= XMLConfig.getVariables(textfile)
			handle	= open(vars['file'])

			line	= string.rstrip(handle.readline())
			output	= [line]
			while len(line)>0:
				line	= string.rstrip(handle.readline())
				output.append(line)

			# which items do we need to get?
			_range	= __getRange(start, index, totalitems, printeditems)

			if all==0:
				answer	= __getItemsFromInput(_range['from'], _range['to'], output)
			else:
				answer	= __getItemsFromInput(-1, -1, output)

			if type(answer) == types.IntType:

	        	# If the returned answer is not a list but an integer,
	        	# then this integer represents the number of combinations
	        	# in the output of this script
				index	+= answer

			else:

				if type(answer) == types.ListType:
					# if the answer is a list, then append the contents of this list
					# to the already obtained partial answer
					items.extend(answer)
					printeditems += len(answer)

#		print "#3 Printing range (%d, %d), index=%d, printed %d of %d items" % (start, end, index, printeditems, totalitems)

	if printeditems<totalitems or all==1:

		# Fourth, process the 'directory'-entries
		fileindex	= fileIndexer.fileIndexer()

		directories	= XMLConfig.getEntries('directory', config)
		for directory in directories:
			vars	= XMLConfig.getVariables(directory)
			if vars.has_key('local') and vars.has_key('public'):
				local	= replaceVariables(vars['local'], directory)
				public	= replaceVariables(vars['public'], directory)

	            # remove trailing slashes
				while public[-1]=="/":
					public	= public[:-1]
				fileindex.addDir(local, public)

		# which items do we need to get?
		_range	= __getRange(start, index, totalitems, printeditems)

		# get content from directories and rewrite as URLs
		if all==0:
			diritems	= __getDirItems(_range['from'], _range['to'], fileindex)
		else:
			diritems	= __getDirItems(-1, -1, fileindex)

		if type(diritems) == types.IntType:

			index	+= diritems

		else:

			if diritems != None:
				for item in diritems:
					items.append(newItem(url=item))
					printeditems += 1
					index		 += 1

#		print "#4 Done - Tried to print range (%d, %d), index=%d, printed %d of %d items" % (start, end, index, printeditems, totalitems)

	return items

if __name__=="__main__":
	if len(sys.argv)>1:
		start	= string.atoi(sys.argv[1])
		end		= string.atoi(sys.argv[2])
	else:
		start	= 0
		end		= 300

	config	= XMLConfig.parse('webindex.ini')
#	XMLConfig.printConfigtree(config)
	items	= getCombinations(start, end, config)
	pprint.pprint(items)

#	print "Done"
