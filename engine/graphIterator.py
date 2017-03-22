# graphIterator v0.01
# (c) 2003 by Edward Akerboom

import string
import graph
import types
import random # TODO: Remove these two
import pprint

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, os.path
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-1], os.sep))
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-2], os.sep))

from	shared 		import XMLConfig
from 	graphCommon import *
from	common 		import *

def __createSQLfromCondition(condition, node):
#	print "create SQL from condition '%s' @ %s" % (condition, getProperty('label', node))
	references	= graph.findValueReferences(condition)

	thislabel	= XMLConfig.getProperty('label', node)
	thiscolumn	= getVariable("%s.column" % (thislabel, ), node)
	thistable 	= getVariable("%s.table" % (thislabel, ), node)

	tables		= [thistable]
	for reference in references:
		tablevariable	= "%s.table" % (reference, )
		table			= getVariable(tablevariable, node)
		if (table!=None):
			if not table in tables:
				tables.append(table)
		else:
			raise "Error in processing the variables from the configuration: : "\
				"No database 'source'-table is defined for argument '%s'" \
				% (reference, )

#	print "Gevonden tables:", tables

	# TODO: Check if databases are the same?
	# TODO: Add quotes for 'string'-type variables? Or should these be included in the configuration?
	SQL	= "SELECT DISTINCT %s.%s FROM" % (thistable, thiscolumn)
	SQL = "%s %s WHERE" % (SQL, string.join(tables, ", "), )

	SQL = "%s %s" % (SQL, replaceVariables(condition, node))

	return SQL

def __createSQLfromQuery(query, node):
	return replaceVariables(query, node)

def createSQL(node):
	""" create an SQL-statement for this node, based on both 'condition'
		or 'query' variables and the values of the references in
		these variables """

	SQL	= None
	for entry in node['branch']:
		if entry['type']=='variable':
			if entry['name']=='condition':
				SQL = __createSQLfromCondition(entry['value'], node)
			if entry['name']=='query':
				SQL	= __createSQLfromQuery(entry['value'], node)

	if SQL == None:
		column	= getVariable('column', node)
		table	= getVariable('table', node)

		SQL 	= "SELECT DISTINCT %s FROM %s" % (column, table)

#	print "Created SQL: ", SQL

	return SQL

def nodeHasNextCombination(node):
	""" Can this node fetch another record? """

	answer	= 0
	if node.has_key('type'):
		if node['type']!='graphroot':
#			print "recordnr, recordcount: %d, %d" % (node['recordnr'], node['recordcount'])
			if node.has_key('recordnr') and node.has_key('recordcount'):
				if node['recordnr']+1>=node['recordcount']:
					node['outofrecords']=1
				answer = not node['outofrecords']

	return answer

def giveNextFreeNode(graph):
	""" Return the next node in this graph that can still fetch
		another record from the database. """

	winner	= None

	if nodeHasNextCombination(graph):
		winner	= graph

	if len(graph['refered_by'])>0:
		for node in graph['refered_by']:
			localwinner	= giveNextFreeNode(node)
			if localwinner != None:
				winner	= localwinner

	return winner

def fetchNextRecord(node):
	""" Fetch the next record for a specific node in the graph.
		This increases the node's recordnr and causes a cascading
		update in its child-nodes """

	answer	= node['database'].getNextRecord()
#	answer	= random.randint(0, 1000)

	node['recordnr'] 		+= 1
	node['recordcontents']	= answer
	thislabel=XMLConfig.getProperty('label', node)
# 	print "Fetched record %d for %s from SQL: %s ====> " \
# 		% (node['recordnr'], thislabel, createSQL(node)) , node['recordcontents']
# 	print "Fetched record %d for %s: ====> " \
# 		% (node['recordnr'], thislabel) , node['recordcontents']

	if len(node['refered_by'])>0:
		for entry in node['refered_by']:
			entry = cascadingUpdate(entry)

	return node

def cascadingUpdate(node):
	""" update values in this node and its child-nodes """

	node['recordnr'] = 0
	node['outofrecords'] = 0

#	print "cascading update for %s" % (XMLConfig.getProperty('label', graph), )
	sql	= createSQL(node)
	try:
		node['database'].issueSQLstatement(sql, reusehandle=1)
	except:
		raise "Something went wrong issuing this SQL-statement: " + sql + "\nFunction: graphIterator.cascadingUpdate()"
	else:
		node['recordnr']		= 0
		node['outofrecords']	= 0
# 		x	= random.randint(0, 1000)
# 		print "cu: Assigning %d to %s" % (x, XMLConfig.getProperty('label', graph))
# 		graph['recordcontents']	= x
# 		graph['recordcount']	= 2
		node['recordcontents'] 	= node['database'].getFirstRecord()
		node['recordcount']		= node['database'].getRecordCount()

	if len(node['refered_by'])>0:
		for childnode in node['refered_by']:
			childnode = cascadingUpdate(childnode)

	return node

def __resetLowerRankedSiblings(node):
	""" reset lower ranked siblings. This procedure is called
		when increasing a higher ranked sibling (compare to
		binary counting) """
	siblings	= graph.getSiblings(node, includeself=1)

	for siblingset in siblings:

		startreset	= 0
		for sibling in siblingset:

			# if necessary, reset this sibling to its first
			# combination ('zero')
			if startreset==1 and id(sibling)!=id(node):
				sibling	= cascadingUpdate(sibling)

			if id(sibling)==id(node):
				# We have found the provided node in the list
				# of siblings. From this point on, reset all
				# siblings to its first combination.
				startreset	= 1

	return graph.getRoot(node)

def __increaseCombinationCounter(root):
	""" increase the combination-counter,
		which is located in the provided root-node """
	if root['type']=='graphroot':
		root['combination']	+= 1

	return root

def __resetCombinationCounter(root):
	""" reset the combination-counter,
		which is located in the provided root-node """
	if root['type']=='graphroot':
		root['combination']	= 0

	return root

def giveNextCombination(graph):
	""" return the next combination of this graph or node """

	if graph!= None:
		if graph['label']=='graphroot':
			if graph['combination'] == 0:
				return giveFirstCombination(graph)

	node = giveNextFreeNode(graph)
	if node != None and node['label']!='graphroot':
		node	= fetchNextRecord(node)
		graph	= __resetLowerRankedSiblings(node)
		graph	= __increaseCombinationCounter(graph)
		return graph
	else:
		return None

def giveFirstCombination(graph):
	""" Initialize the provided graph with the contents of the
		first record. """

	if graph['type']=='graphroot':

		graph	= __resetCombinationCounter(graph)

		# Each childnode directly positioned under the root is
		# assigned a value first
		for node in graph['refered_by']:
			sql	= createSQL(node)
			try:
				node['database'].issueSQLstatement(sql, reusehandle=1)
			except:
				raise "Something went wrong issuing this SQL-statement:" + sql + "\nFunction: graphIterator.giveFirstCombination()"
			else:
				node['recordnr']		= 0
				node['outofrecords']	= 0
				node['recordcontents'] 	= node['database'].getFirstRecord()
				node['recordcount']		= node['database'].getRecordCount()
				graph					= __increaseCombinationCounter(graph)

# 				print "Obtained data:"
# 				pprint.pprint(node)

# 				x	= random.randint(0, 1000)
# 				print "Assigning %d to %s" % (x, XMLConfig.getProperty('label', node))
# 				node['recordcontents']	= x
# 				node['recordcount']		= 2

		# then, these obtained values are propagated throughout the
		# graph
		for node in graph['refered_by']:
			for grandchild in node['refered_by']:
				grandchild	= cascadingUpdate(grandchild)

	return graph

def __printURL(graph):
	""" given a specific combination or 'state' in the graph,
		print an URL - based on a 'template' variable provided
		in the configfile, reflecting this state. """

	if graph!=None:
		if graph['type']=='graphroot':
			where	= graph['refered_by'][0]
		else:
			where	= graph
		template	= getVariable('template', where)
		url			= replaceVariables(template, where)
		print url
		
		
def jets(grap):
	if not grap.has_key('refered_by'):
		print "graphiterator.getcombiitem: Fout hier???"
		graph.printGraph(grap, simple=1)
		print "----"*50

def getCombinationItem(graph):
	""" given a specific combination or 'state' in the graph,
		return a datastructure containing the URL of this item """

	if graph!=None:
		if graph['type']=='graphroot':
			jets(graph)
			if len(graph['refered_by'])>0:
				where	= graph['refered_by'][0]
			else:
				return newItem(url="ERROR", post="ERROR")
		else:
			where	= graph

		urltemplate	= getVariable('url', where)
		url			= replaceVariables(urltemplate, where)

		posttemplate= getVariable('post', where)
		if posttemplate!=None:
			post	= replaceVariables(posttemplate, where)
		else:
			post	= None

		return newItem(url=url, post=post)
