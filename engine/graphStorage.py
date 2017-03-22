# graphStorage v0.01
# (c) 2003 by Edward Akerboom

import graph
import re
import string
import time
import zlib
import base64
import types
import os

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, os.path
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-1], os.sep))
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-2], os.sep))

from graphCommon 		import *
from graphIterator 		import *
from shared.database 	import database
from shared 			import XMLConfig
from shared				import configfile # TODO: Remove this rather useless module

def test(db):
	return None

	print "Testing databaseconnection:"
	print "=====>0<====="
	print "database:", db
	print "=====>1<====="
	print "connection parameters:"
	pprint.pprint( db.getConnectionParameters())
	print "=====>2<====="
	print "getting next record:"
	print db.getNextRecord()
	print "=====>3<====="
	print "C'est tout"

def restoreDatabaseConnections(graph, restorepoint):
#	print "-="*50
#	print "restoreconnection for %s" % ( XMLConfig.getProperty('label', graph), )
#	pprint.pprint(restorepoint)

	if type(graph) is types.DictType:
		if graph['type']!='graphroot':
			if graph['database']==None:
				restoredata			= restorepoint['nodes'].pop(0)
				dbinternaldata		= eval(restoredata['db'])

				# first, create a new database-instance
				graph['database']	= database.database()
				# then, redefine it
				graph['database']	= graph['database'].restoreConnection(dbinternaldata)

				test(graph['database'])

				graph['recordnr']	= dbinternaldata['recordnr'] - 1 # see recordState
				graph['recordcount']= restoredata['recordcount']

#				print "internaldata:"
#				pprint.pprint(dbinternaldata)
#				graph['recordcount']=

		for node in graph['refered_by']:
			node		= restoreDatabaseConnections(node, restorepoint)

			if len(restorepoint['nodes'])>0:
				restorepoint['nodes'].pop(0)

	return graph

def restoreState(root, state):
	if state!=None:
		graphroot	= graph.getRoot(root)
		graphroot['combination']	= state['combination']
		root		= restoreDatabaseConnections(root, state)
		return root

def openDatabaseConnections(graph, dbparameters=None):
	""" Open a connection to the database for each node in this graph """
	# this was edited months after I initially wrote it; I think I screwed something up :)
	# (with the introduction of the dbparameters parameter?)

	if type(graph) is types.DictType:

		if graph['type']!='graphroot':
			if graph['database']==None:
				label	= XMLConfig.getProperty('label', graph)
				db		= getVariable("%s.database" % (label, ), graph)
#				print "Opening database: ", db

				if db!=None:
					config	= XMLConfig.getNode(db, XMLConfig.getRoot(graph))

				if db==None or config==None:
					raise "Error in configuration: The database that is " \
						"specified for %s (namely, '%s') is not defined in the " \
						"configurationfile" % (label, db)

				if dbparameters==None:
					dbparameters	= configfile.getDBConfig(db, 1)

				graph['database']	= database.database(dbparameters['dbclient'], \
									dbparameters['user'], dbparameters['password'], \
									dbparameters['dsn'], dbparameters['dbname'], \
									dbparameters['connectstring'])

		for node in graph['refered_by']:
			node	= openDatabaseConnections(node, dbparameters)

	return graph

def closeDatabaseConnections(graph): # relatively untested
	""" Close a connection to the database for each node in this graph """

	if type(graph) is types.DictType:

		if graph['type']!='graphroot':
			if graph['database']!=None:
				graph['database'].closeDB()

		for node in graph['refered_by']:
			node	= closeDatabaseConnections(node)

def __getState(graph):

	if graph!=None:
		if len(graph['refered_by'])>0:
			answer		= ""
			parentlabel	= XMLConfig.getProperty('label', graph)
			for child in graph['refered_by']:
#				nr		= XMLConfig.getProperty('recordnr', child)+1
				total	= XMLConfig.getProperty('recordcount', child)
				if child.has_key('database'):
					db	= "%s" % (child['database'].getRestoreData(), )
				else:
					# the root-node has no 'database'-key
					db	= ""

				db	= string.replace(base64.encodestring(zlib.compress(db)), "\n", "")
#				decompress = zlib.decompress(base64.decodestring(db))

				if total==None and XMLConfig.getProperty('sql', child)==None:
					# If you define two exactly similar 'dynamic'-entries in the configfile,
					# with the same dependencies and the same variable-names, then
					# these two entries have the same ID. In at least one occasion, one of
					# these graphs was left untouched, and it ended up in this procedure.
					#
					# Since the graph contained no information (no 'recordcount' and 'sql'
					# properties, for example) the 'answer = ....' statement caused an error.
					#
					# To prohibit the state of such graphs to be recorded in the cache-file,
					# which causes problems the next time this program is run, graphs that
					# are 'empty' are not allowed in the cache-file. Therefore, set the
					# answer to None and break from the loop.
					answer	= None
					break
				answer	= "%s::%d:%s%s" % (answer, total, db, __getState(child))
			return answer
		else:
			return ""
	else:
		return ""

def recordState(root):

	if root!=None:

		# create an id for this graph
		id		= graph.createIdentifier(root)

		# recall how many combinations were made with this graph
		counter	= root['combination']
		state	= __getState(root)

		if state!=None:
			state	= "%s::%d::%d%s" % (id, int(time.time()), counter, state)

			# Here, we know a cachefilename is defined
			cache	= open(__getSectionVariable(root, "cache", "file", "cache.web"), "a")
			cache.write(state)
			cache.write("\n")
			cache.close()
	# 		print vars
	# 		print state

def convertExpireTime(expire):
	""" convert a string containing items such as '1 day, 2 hours and
		3 minutes' to seconds. Years, months, weeks, days, hours, minutes
		and seconds are supported. A month is four weeks, a year 365 days. """

	# clean and simple :)
	totaltime	= 24 * 60 * 60 # default expiretime is one day
	if expire!=None:
		if type(expire) is types.StringType:
			if len(expire)>0:
				totaltime	= 0
				timeitems	= re.findall(re.compile("([0-9]+)\s+([a-zA-Z]+)"), expire)
				for item in timeitems:
					qty		= string.atoi(item[0])
					unit	= item[1]
					if unit[-1]=='s':
						unit= unit[:-1]
					unit	= string.lower(unit)
					if 		unit=="second":
						totaltime	+= qty
					elif 	unit=="minute":
						totaltime	+= qty * 60
					elif	unit=="hour":
						totaltime	+= qty * 60 * 60
					elif	unit=="day":
						totaltime	+= qty * 60 * 60 * 24
					elif 	unit=="week":
						totaltime	+= qty * 60 * 60 * 24 * 7
					elif	unit=="month":
						totaltime	+= qty * 60 * 60 * 24 * 7 * 4
					elif	unit=="year":
						totaltime	+= qty * 60 * 60 * 24 * 365

	return totaltime

def findRestorePoint(root, combinationnr=None):
	""" retrieve a valid restore-point for this graph
		from the cache-file, if present, and put it
		in a nice and accessible datastructure.

		If multiple restorepoints are present, then the
		restorepoint with a combinationcounter close to,
		but not above, the combinationnr is returned.

		Added bonus: Removes outdated items from the cache """

	thisid		= graph.createIdentifier(root)

	cachename	= __getSectionVariable(root, "cache", "file", "cache.web")
	try:
		cache   	= open(cachename, "r")
	except:
		try:
			cache		= open(cachename, "a")
		except:
			return None


	newcachename= "%s.new.tmp" % (cachename, )
	try:
		newcache	= open(newcachename, "w")
	except IOError:
		raise "Could not create cache file. You can specify where the cache file should be stored in the webindex.ini configurationfile"

	expiretime	= __getSectionVariable(root, "cache", "expires", 24*60*60)

	if type(expiretime) is types.StringType:
		expiretime	= convertExpireTime(expiretime)
	now			= round(time.time())
	answer		= {}
	answer['combination']	= 0
	found		= 0

#	print "expiretime, cache:", expiretime, cache

	state		= ""
	try:
		state		= cache.readline()
	except IOError:
		pass

#	for state in cache:
	while len(state)>0:

		outdated	= 1

		if len(state)>2:
			parts		= string.split(state, "::")
#			print "parts:", parts
			id			= parts[0]
			timestamp  	= string.atoi(parts[1])

			if (id==thisid) and (timestamp+expiretime>now):
				newentry				= {}
				newentry['id'] 			= id
				newentry['combination']	= string.atoi(parts[2])
				newentry['nodes']		= []
				outdated				= 0

				for i in range(3, len(parts)):
					node				= string.split(parts[i], ":")

					newnode					= {}
					newnode['recordcount'] 	= string.atoi(node[0])
					newnode['db']			= zlib.decompress(base64.decodestring(node[1]))

					newentry['nodes'].append(newnode)

				if combinationnr != None:
					if newentry['combination']<=combinationnr:
						if newentry['combination']>=answer['combination']:
#							print "found combi with combination #%d" % (newentry['combination'], )
							answer 	= newentry
							found   = 1

		if outdated == 0:
			newcache.write(state)
		state	= cache.readline()

	cache.close()
	newcache.close()

	# replace old cache with new cache
	os.remove(cachename)
	os.rename(newcachename, cachename)

	if found == 1:
# 		print "Returning:"
#		pprint.pprint(answer)
		return answer
	else:
		return None

def openGraph(graph, combinationnr, nostorage=0, dbparameters=None):
	""" Open database connections for this graph and
		proceed up to the specified combinationnumber. """

	if nostorage==0:
		restorepoint	= findRestorePoint(graph, combinationnr)
	else:
		restorepoint	= None

	if restorepoint != None:
		graph	= restoreState(graph, restorepoint)
	else:
		graph	= openDatabaseConnections(graph, dbparameters)

	fetchcount	= combinationnr - graph['combination']

	for i in range(fetchcount):
		next = giveNextCombination(graph)

		if next==None:
			# this graph has no more combinations,
			# save the state to the cache and break
			# from the loop
			# BEWARE: Instead of returning the graph,
			# return the number of combinations this
			# graph has produced
			recordState(graph)
			graph = graph['combination'] + i
			break
		else:
			graph = next

	if combinationnr!=0 and type(graph)!=types.IntType and nostorage==0:
		recordState(graph)

	return graph

def __getSectionVariable(graph, section, variable, default):
	""" retrieve a variable from a section
		defined in webindex.ini or resort to the default """

	answer	= default

	# Retrieve the section from the configfile. To do this, we need to fetch
	# the rootnode of the _tree_ this graph is part of. This is done by fetching
	# one of the children of the rootnode of this _graph_, and consequently finding
	# its root in the _tree_
	if graph!=None:

		if len(graph['refered_by'])>0:
			cache	= XMLConfig.getEntries(section, XMLConfig.getRoot(graph['refered_by'][0]))
		else:
			if graph['type']!='graphroot':
				cache	= XMLConfig.getEntries(section, XMLConfig.getRoot(graph))
			else:
				cache	= None

		# If no such entry exist, resort to defaults
		if not (cache==None or len(cache)==0):

			# get the variables defined within this section
			vars	= XMLConfig.getVariables(cache[0])

			# if this variable has not been defined, resort to default
			if vars.has_key(variable):
				answer	= vars[variable]

	return answer
