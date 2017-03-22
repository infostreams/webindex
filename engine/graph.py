import 	re
import 	pprint
#import 	random	# TODO: Remove this line
import 	zlib
import 	string

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, os.path
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-1], os.sep))
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-2], os.sep))

from	shared import XMLConfig

def __newNode(argument):
	""" convert an 'argument' to a node """

	# add some variables to this 'argument'
	if not argument.has_key('refered_by'):
		argument['refered_by']		= []
	argument['recordnr']		= 0
	argument['recordcontents']	= None
#	argument['recordcontents']	= random.randint(0,1000) # TODO: Remove this line
	argument['outofrecords']	= 0
	argument['database']		= None

	return 	argument

def __newRootNode():
	argument					= {}
	argument['label']			= 'graphroot'
	argument['type']			= 'graphroot'
	argument['refered_by']		= []
	argument['outofrecords']	= 0
	argument['combination']		= 0
	return argument

def findValueReferences(input):
	""" Find references like {<something>=*.value} in the 'input'-string,
		and retrieve all values for '*' """

	# In the input-string, search for a '=', possibly followed by some
	# whitespace, followed by a '{', possibly followed by some
	# whitespace, an argumentname and a '.value'
	regexp	= re.compile("=\s*?{\s*?(.*?)(?=\.value)", re.IGNORECASE)
	answer	= re.findall(regexp, input)
	return answer

def findNameReferences(input):
	""" Find references like {<something>=*.name} in the 'input'-string,
		and retrieve all values for '*' """

	# In the input-string, search for a '=', possibly followed by some
	# whitespace, followed by a '{', possibly followed by some
	# whitespace, an argumentname and a '.value'
	regexp	= re.compile("\s*?{\s*?(.*?)(?=\.name)\s*=", re.IGNORECASE)
	answer	= re.findall(regexp, input)
	return answer

def toString(graph):
	""" return a stringrepresentation of the graph that could be used
		to reconstruct the graph (or, to create an identifier ;)) """
	if graph!=None:
		if len(graph['refered_by'])>0:
			answer		= ""
			childcount  = 1
			parentlabel	= XMLConfig.getProperty('label', graph)
			for child in graph['refered_by']:
				label	= XMLConfig.getProperty('label', child)
				prefix	= "::child %d of %s==>" % (childcount, parentlabel)
				answer	= "%s%s%s%s" % (answer, prefix, label, toString(child))
				childcount += 1
			return answer
		else:
			return ""
	else:
		return ""

def createIdentifier(graph):
	""" Return a unique identifier for this graph. """

	# Each individual graph will have to be assigned a unique
	# id that is reproducible given the graph structure and the
	# node names. A simple, relatively straight-forward solution
	# is to create a unique string based on the graph and to
	# return the checksum value of that string as the
	# graph's id
	return string.upper(hex(zlib.adler32(toString(graph)))[2:])

def __containsCycle(graph, visited=[]):
	""" check if this graph has a 'cycle' (eg: a->b->c->a->.....) """
	if id(graph) in visited:
		return 1
	else:
		if graph.has_key("refered_by"):
			if len(graph['refered_by'])>0:
				visited.append(id(graph))
				found	 = 0
				for child in graph['refered_by']:
					if __containsCycle(child, visited):
						found = 1
				visited.remove(id(graph))

				return found

			else:
				return 0
		else:
			return 0

def __removeDependentGraphs(from_, in_):
	# Check if the 'startingpoints' of each entry in 'source' are not part of a graph
	# If this is the case, then remove these startingpoints (since their value
	# is dependent on another arguments' value afterall)

	source	= from_
	graphs	= in_

	answer	= []
	for startingpoint in source:
		remove			= 0
		selfencounter   = 0
		startlabel		= XMLConfig.getProperty('label', startingpoint)

		for graph in graphs:

			thislabel	= XMLConfig.getProperty('label', graph)

			# if we encounter ourselves, increase the selfencounter-counter :)
			if (startlabel == thislabel):
				selfencounter += 1

			# if we encounter ourselves more than once, then remove the
			# extraneous copies
			if (selfencounter > 1):
				remove = 1
			else:
				# else, check if a node with a name equal to the one
				# we're searching for can be found in this graph
				# If so, then remove this graph from the answer
				node = findNodeInGraph(startlabel, graph)
				if node != None:
					remove	= 1

			# if this graph is not labeled, then don't remove it
			if (startlabel == None):
				remove = 0

		if remove==0:
			answer.append(startingpoint)

	return answer

### Following two procedures are for testing purposes only

def __copyGraph(graph, copyparentlink=0, maxdepth=5, simple=0):
	# Make a copy of the graph and leave out the 'parent' statements
	# This makes a printed version of the graph considerably more readable
	#
	# if 'copyparentlink' == 1, then copy the 'parent' entry as well
	
	copy	= {}
	for key in graph.keys():
		if simple==1:
			dontcopy	= ['parent', 'branch', 'tag', 'type', 'graph_parent']
		else:
			dontcopy	= ['parent']
		if key in dontcopy:
			if copyparentlink==1:
				copy[key] = graph[key]
			continue
		if key != 'branch' and key != 'refered_by':
			try:
				if key!='database':		# not including this 'if' would cause erroneous 'database'-values in the printed graph
					copy[key]	= graph[key][:]
				else:
					copy[key]	= graph[key]
			except:
				copy[key]	= graph[key]
		else:
			copy[key]	= []
			for child in graph[key]:
				if maxdepth>0:
					copyOfChild	= __copyGraph(child, copyparentlink, maxdepth-1, simple)
					copy[key].append(copyOfChild)

	return	copy

def printGraph(graph, simple=0):
	if graph==None:
		print None
	else:
		copy	= __copyGraph(graph, copyparentlink=0, simple=simple)
		pp		= pprint.PrettyPrinter(depth=7)
		pp.pprint(copy)

### The previous two procedures are for testing purposes only

def findNodeInGraph(label, graph):
	""" find a node labeled 'label' in the provided graph """

	if XMLConfig.getProperty('label', graph) == label:
		return graph
	else:
		if graph.has_key('refered_by'):
			if graph['refered_by']!=[]:
				# if this node has a branch, then search these
				# nodes too
				found	= None
				for node in graph['refered_by']:
					tmp	= findNodeInGraph(label, node)
					if tmp != None:
						found	= tmp
				return found

def __tieInterdependentGraphs(graphs):
	""" Tie graphs together that share a node. Graphs not sharing
		nodes with other graphs are given the special 'rootnode'
		anyway. """

	tielist	= []

	# check each element in the graph
	for source in graphs:

		# create a list of nodes in this element
		sourcelist		= getNodeList(source, [])

		# and check it against each other element in the graph
		for target in graphs:

			# create a list of nodes in this other element
			targetlist 	= getNodeList(target, [])

            # if these node-lists are different, then do a full-scale search
			if sourcelist!=targetlist:

            	# check each entry in the sourcelist
				for entry in sourcelist:

					# if it also occurs in the targetlist,
					# then put it on the list of nodes to be tied
					# (if that hasn't been done already)
					if entry in targetlist:
						if (len(tielist)==0):
							tielist.append([source, target])
						else:
							# Check if this entry is already enlisted
							# in the 'tie-list'
							nothingfound	= 1
							for tie in tielist:
								sourcefound = 0
								targetfound = 0
								for tie_entry in tie:
									if id(tie_entry)==id(source):
										sourcefound		= 1
										nothingfound 	= 0
									if id(tie_entry)==id(target):
										targetfound		= 1
										nothingfound 	= 0

								if (sourcefound) and (not targetfound):
									tie.append(target)
								if (targetfound) and (not sourcefound):
									tie.append(source)

                            # please do not indent this
							if (nothingfound):
								tielist.append([source, target])

	answer	= []

# 	# First, give the graphs that are not listed in the
# 	# 'tielist' a special 'rootnode'
	# This used to be the default behaviour. Now (some time later), I think
	# it is better to include 'unconnected' nodes under the 'main' rootnode
	for graph in graphs:

		listed	= 0
		for node in tielist:
			for entry in node:
				if id(entry) == id(graph):
					listed = 1

		if not listed:
# 			root				= __newRootNode()
# 			root['refered_by']	= [graph]
# 			answer.append(root)
			tielist.append([graph])

# 	# then, tie together the entries listed in
# 	# each node of the tielist
# 	for node in tielist:
# 		root			= __newRootNode()
# 		for entry in node:
# 			root['refered_by'].append(entry)
# 		answer.append(root)

	# as said, that was the previous behaviour. It might
	# be better to generate only 1 root-node:
	root		= __newRootNode()
	for node in tielist:
		for entry in node:
			root['refered_by'].append(entry)

	answer.append(root)

	return answer

def __recursiveSetParents(node, parent):
	if node.has_key('graph_parent'):
		node['graph_parent'].append(parent)
	else:
		node['graph_parent']	= [parent]

	if len(node['refered_by'])>0:
		for child in node['refered_by']:
			child = __recursiveSetParents(child, node)

	return node

def __determineParents(graphs):

	for graph in graphs:
		graph	= __recursiveSetParents(graph, None)

	return graphs

def getNodeList(graph, answer):
	""" return a list of the names of all the nodes in this graph """

	answer.extend([XMLConfig.getProperty('label', graph)])

	for child in graph['refered_by']:
		getNodeList(child, answer)

	return answer

def getNodeLists(graphs):
	""" return a list of node-lists """
	answer	= []
	for graph in graphs:
		answer.append(getNodeList(graph, []))
	return answer

def __createGraphStructure(argument, references, graphs, arguments):
	""" Using the 'references' of this 'argument', create a graph-like
		structure and make it part of the graphs in 'graphs'. The other
		'arguments' from the config-subtree of the "dynamic"-tag are provided
		to locate the referenced arguments.  """

	# If we have found that this argument's value depends on other
	# arguments, then make these arguments point to this one
	if len(references)>0:

		label	= XMLConfig.getProperty('label', argument)

		# Do each of these arguments (from now on: references) individually
		for reference in references:

			# Self-referencing is strictly prohibited
			# [Sadly, it is common-practice for some of the professors at
			# my university, but I certainly won't allow it here! :)]
			if reference == label:
				raise "Error in configuration: Argument %s "\
						"references itself" % (label, )

			referencednode	= None
			newnode			= 0

			# It is possible that this reference is already
			# part of a graph, so we'll look there first
			for graph in graphs:
				referencednode = findNodeInGraph(reference, graph)
				if referencednode != None:
					# This node is already in a graph,
					# do not add another copy
# 						print "Found a node (%s) in one of the graphs that is referenced by %s" \
# 							% (XMLConfig.getProperty('label', referencednode), label)
					newnode		= 0
					break

			# If this reference is not found in one of the graphs,
			# then search the arguments that were provided by the caller
			# of this function
			if referencednode==None:
				for arg in arguments: # 'argument' is already used in the main loop
					if XMLConfig.getProperty('label', arg)==reference:
						referencednode	= __newNode(arg)
						# This node is not yet in a graph, so
						# include a copy
# 							print "Found a node (%s) in the argument-list that is referenced by %s" \
# 								% (XMLConfig.getProperty('label', referencednode), label)
						newnode			= 1
						break

			# If this reference is not in one of the graphs and not provided
			# by the caller, then it does not exist. Throw an error.
			if referencednode == None:
				raise "Error in configuration: Argument " \
					"%s, which is referenced in the definition of " \
					"argument %s, does not exist." % (reference, label)

			# At this point, we are sure we have found the reference which
			# is used in the definition of 'argument'. We will notify this
			# reference that its value is used in determining another
			# argument's value

			# To do that, we create a link from this reference's 'node' in
			# the graph to the 'node' belonging to this argument.
			referencednode['refered_by'].append(__newNode(argument))

			# If this node is not yet found in the list of graphs,
			# then it is safe to store a copy
			if newnode == 1:
				graphs.append(referencednode)

#				print "Resultaat tot nu toe:"
#				printjetsers(graphs, unconnected)
#				print "-="*50

	return graphs

def createDependencyGraphs(dynamicconfigentry, argumentlist=[]):
	""" Create a list of dependency-graphs based on the 'condition'
		and 'query' statements provided in the arguments of the
		config-subtree of the 'dynamic' tag contained within the
		parameter. """

	# TODO: Check input??

	arguments	= XMLConfig.getEntries('argument', dynamicconfigentry)
	graphs		= []
	unconnected	= []

	# find out which variables are referenced in the 'url'-variable of this
	# 'dynamic'-entry
	# At the very least, we have to iterate through all the values for the
	# variables mentioned in that url.
	url			= XMLConfig.getVariable('url', dynamicconfigentry)
	varlist 	= findValueReferences(url)
	varlist.extend(findNameReferences(url))

	for argument in arguments:

		# if this argument has no label, then it cannot be referenced
		# therefore, it is not part of a graph
		if XMLConfig.getProperty('label', argument)==None:
			unconnected.append(newNode(argument))
			continue					# continue with next argument

#		print "inserting %s in some graph" % (XMLConfig.getProperty('label', argument), )

		if len(argumentlist)>0:
			if not XMLConfig.getProperty('label', argument) in argumentlist:
				continue

		if len(varlist)>0:
			if not XMLConfig.getProperty('label', argument) in varlist:
				continue

		condition	= XMLConfig.getProperty('condition', XMLConfig.getVariables(argument))
		query		= XMLConfig.getProperty('query', XMLConfig.getVariables(argument))

		# If this argument has no 'condition' and no 'query' variable, then
		# its value does not depend on another arguments' value. Therefore,
		# it will not be included in a graph yet. However, its value can
		# still be referenced by another argument. In that case it will
		# become part of the graph afterall.
		if condition==None and query==None:
			unconnected.append(__newNode(argument))
			continue

		if condition!=None and query!=None:
			raise "Error in configuration for argument %s: Specify " \
					"either 'condition' or 'query', not both" % (label, )

		# If we've reached this point, an argument has both a label and either
		# a 'condition' or a 'query' property. Now, we have to check if it
		# references other arguments.

		if condition!=None:
			references	= findValueReferences(condition)
		if query!=None:
			references	= findValueReferences(query)

		graphs	= __createGraphStructure(argument, references, graphs, arguments)

	# Check the graphs for cycles
	for graph in graphs:
		if __containsCycle(graph, []):
			raise "Error in configuration: Some of the provided conditions " \
				"and/or queries are mutually dependent ('circular'). Therefore, it is " \
				"impossible to determine which argument to evaluate first. Please fix."

	# Check if the 'startingpoints' of each graph are not part of another graph
	# If this is the case, then remove these startingpoints (since their value
	# is dependent on another arguments' value afterall)
	tmp1	= __removeDependentGraphs(graphs, graphs)

	# Create a new list without the items from the 'unconnected' list that
	# eventually DID end up in one of the graphs
	tmp2	= __removeDependentGraphs(unconnected, tmp1)

	answer	= []
	answer.extend(tmp1)
	answer.extend(tmp2)

    # old code (instead of answer=....)
    # tested much much better
# 	unconnected	= __removeDependent
# 	for argument in unconnected:
# 		label	= XMLConfig.getProperty('label', argument)
# 		remove	= 0
# 		if label!=None:
# 			for graph in graphs:
# 				if findNodeInGraph(label, graph)!=None:
# 					remove	= 1
#
# 		if remove==0:
# 			answer.append(argument)

	# A node may appear in only one graph. If a node references multiple
	# arguments, it can potentially be part of multiple graphs. This causes
	# erroneous behaviour. Therefore, graphs containing the same node are
	# tied together using a special 'root node'. For reasons of symmetry
	# and simplified processing, each graph in the final answer will be
	# equipped with such a special 'root node'.
	answer	= __tieInterdependentGraphs(answer)

	# Finally, each node in each graph is equipped with information
	# about its parents.
	answer	= __determineParents(answer)

	# Done!
	return answer

def getRoot(node):
	if node!=None:
		if XMLConfig.getProperty('label', node)!='graphroot':
			return getRoot(node['graph_parent'][0])
		else:
			return node

def getSiblings(node, includeself=0):
	answer	= []
	if node != None:
		parents	= node['graph_parent']
		for parent in parents:

			localanswer	= []
			for sibling in parent['refered_by']:

				include	= 1

				if includeself==0:
					if id(sibling)!=id(node):
						include	= 0

				if include==1:
					localanswer.append(sibling)

			if len(localanswer)>0:
				answer.append(localanswer)

	return answer

if __name__=="__main__":
	config	= XMLConfig.parse("webindex.ini")
	dynamic	= XMLConfig.getEntries('dynamic', config)

	for dynentry in dynamic:
		graphs	= createDependencyGraphs(dynentry)
		print "Aantal grafen:", len(graphs)
		for graph in graphs:
			test	= findNodeInGraph('arg4', graph)
			root	= getRoot(test)
			sibs	= getSiblings(test, includeself=1)
			for sib in sibs:
				print "Sibling van %s: %s" % (XMLConfig.getProperty('label', test), XMLConfig.getProperty('label', sib))
			print XMLConfig.getProperty('label', test)
			print XMLConfig.getProperty('label', root)
#			printGraph(graph, simple=1)

#	print "Done"
