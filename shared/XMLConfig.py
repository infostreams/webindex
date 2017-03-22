# XML Config parser v0.01b
# (c) Edward Akerboom, 19/9/2003

import 	string
import	re
import	pprint
import 	types

def __getFile(filename):
	""" return the contents of the textfile 'filename' """
	f		= open(filename, "r")
	line	= f.readline()
	answer	= []

	while line != "":
		answer.append(line)
		line	= f.readline()
	f.close()

	return answer

def __clean(contents):
	""" remove comments from the list 'contents', and remove
		unnecessary whitespace """
	answer	= []
	for line in contents:
		cleaned	= string.strip(line)
		if len(cleaned)>0:
			if cleaned[0] != "#":
				answer.append(cleaned)

	return answer

def __isVariableDeclaration(line):
	""" return true if this line is a variable-declaration (e.g.: var = 'Yes! Yes!')"""
	answer	= re.findall(re.compile("^.*?=.*?$"), line)
	return len(answer)>0

def __getVariable(line):
	""" create a list containing [variablename, variablevalue] from the
		variable-declaration in the provided 'line' """
	if __isVariableDeclaration(line):
		tmp		= re.findall(re.compile("^(.*?)=(.*?)$"), line)
		answer	= []
		answer.append(string.strip(tmp[0][0]))
		answer.append(string.strip(tmp[0][1]))
		return answer
	else:
		return None

def __isTag(line):
	""" return true if the line is a tag (e.g. '<dynamic>') """
	answer	= re.findall(re.compile("^</?.+>$"), line)
	return len(answer)>0

def __getTagName(line):
	""" return the tagname of the tag on the line """
	if __isTag(line):
		answer	= re.findall(re.compile("^<(.+)>$"), line)
		return string.split(answer[0])
	else:
		return None

def getNode(name, where):
	""" get a specific node from the config-structure (e.g.: entry1.argument1) """
	parents		= string.split(name, ".")

	# if the location where this reference was found
	# is a variable, the start searching at its parents' children
	# else, start searching at your own children
	if where['type']=='variable':
		branch	= where['parent']['branch']
	else:
		branch	= where['branch']

	# initialize some loop-variables
	parsetree	= where
	foundnode	= None
	done		= 0

 	# while not yet done...
	while (done==0):

		found	= 0

		# delve into the 'parents'-part of the
		# reference (eg. "arg1" in "arg1.value")
		for parent in parents:
			for entry in branch:
				if entry['type']=='branch':
					if entry.has_key('label'):
						if entry['label']==parent:
							branch	= entry['branch']
							node	= entry
							found	+= 1

		# if the correct parents were found and entered,
		# retrieve the requested variable
		if found==len(parents):
			foundnode	= node
			done		= 1

		# if nothing was found, then go up one level
		if foundnode==None:

			# stop if we are at the root of the parsetree
			if parsetree['type'] == 'root':
				done		= 1
			else:
				parsetree   = parsetree['parent']
				branch		= parsetree['branch']

	return foundnode

def getVariable(name, where):
	""" get a specific variable (e.g.: arg1.source) from the config-structure """

	# parse requested variablename
	parts		= string.split(name, ".")
	parents		= parts[:-1]
	variable	= parts[-1]

	# if the location where this reference was found
	# is a variable, the start searching at its parents' children
	# else, start searching at your own children
	if where['type']=='variable':
		branch	= where['parent']['branch']
	else:
		branch	= where['branch']

	# initialize some loop-variables
	parsetree	= where
	foundvalue	= None
	done		= 0

 	# while not yet done...
	while (done==0):

		found	= 0

		# delve into the 'parents'-part of the
		# reference (eg. "arg1" in "arg1.value")
		for parent in parents:
			for entry in branch:
				if entry['type']=='branch':
					if entry.has_key('label'):
						if entry['label']==parent:
							branch	= entry['branch']
							found	+= 1

		# if the correct parents were found and entered,
		# retrieve the requested variable
		if found==len(parents):
			for entry in branch:
				if entry['type']=='variable':
					if entry['name']==variable:
						foundvalue	= entry['value']
						done		= 1

		# if nothing was found, then go up one level
		if foundvalue==None:

			# stop if we are at the root of the parsetree
			if parsetree['type'] == 'root':
				done		= 1
			else:
				parsetree   = parsetree['parent']
				branch		= parsetree['branch']

	return foundvalue

def parse(filename=None, text=None):
	""" create a config-structure from either the file 'filename' or the text 'text', if possible """

	# Open file
	if text==None:
		file		= __getFile(filename)
		file		= __clean(file)
	else:
		file		= __clean(text)
	root			= {}
	root['parent']	= None
	root['type']	= 'root'
	root['branch']	= []
	parentnodes		= []

	# Read lines
	finger			= root
	for line in file:

    	# If this is a variable-declaration (e.g.: var='bla'), then
    	# append a 'variable'-type to the current branch
		if __isVariableDeclaration(line):
			variable		= __getVariable(line)
			entry			= {}
			entry['type']	= 'variable'
			entry['name']	= variable[0]
			entry['value']	= variable[1]
			entry['parent']	= finger
			finger['branch'].append(entry)

		# If this is a tag, then either create or close a branch
		# of the tree
		if __isTag(line):
			tag				= __getTagName(line)
			tagname			= tag[0]

			if tagname[0]=='/':

				# close this branch: branch back
				if tagname[1:]==finger['tag']:
					finger		= finger['parent']
					branch		= finger['branch']
				else:

					# is this really necessary?
					raise TypeError, "Invalid closing-tag ( <%s> )" % (tag[0])
			else:

            	# open a branch
				entry				= {}
				entry['tag']		= tag[0]
				entry['type']		= 'branch'
				entry['branch']		= []
				entry['parent']		= finger
				if len(tag)>1:
					entry['label']	= tag[1]
				finger['branch'].append(entry)

				finger				= entry
				branch				= finger['branch']

	# Done
	return root

def getEntries(tag, config):
	""" return a list of config-structures containing the configuration enclosed
		within the '<tag>' and '</tag>'-elements in the highest branch of the
		provided config-structure """
	answer	= []
#	pprint.pprint(config)
	for entry in config['branch']:

		if entry['type']=='branch':
			if string.lower(entry['tag'])==string.lower(tag):
				answer.append(entry)

	return answer

def getVariables(config):
	""" get all the variables in the highest branch of the provided config-structure """

#  	print "GetVariables, config="
#  	pp	= pprint.PrettyPrinter(depth=2)
#  	pp.pprint(config)

	answer	= {}
	for entry in config['branch']: # TODO: Check if it has a 'branch' (in case of wrong argument)
		if entry['type']=='variable':
			answer[string.lower(entry['name'])]	= entry['value']

	return answer

def getUnnamedEntryVariable(entryname, nr, variablename, config):
	""" get a variable from an unnamed <tag></tag> entry
		provide its number (in case of multiple <tag></tag>-entries)
		and the required variablename """

	variablename= string.lower(variablename)
	entryname	= string.lower(entryname)

	entries		= getEntries(entryname, config)
	if len(entries)>nr:
		entry	= entries[nr]
		vars	= getVariables(entry)
		if vars.has_key(variablename):
			return vars[variablename]

def getRoot(node):
	""" return the rootnode of this node """
	while node['type'] != 'root':
		node	= node['parent']
	
	return node

def getProperty(property, config):
	""" return a property (if present) of the top-level entity in the
		provided config-structure """

	if type(config) is types.DictType:
		if config.has_key(property):
			return config[property]
		else:
			return None
	else:
		return None

def __copyConfig(config, copyparentlink=0, maxdepth=10):
	# Make a copy of the configtree and leave out the 'parent' statements
	# This makes a printed version of the configtree considerably more readable
	#
	# if 'copyparentlink' == 1, then copy the 'parent' entry as well
	copy	= {}
	for key in config.keys():
		if key == 'parent':
#		if key in ['parent', 'branch', 'tag', 'type']:
			if copyparentlink==1:
				copy[key] = config[key]
			continue
		if key != 'branch' and key != 'refered_by':
			try:
				copy[key]	= config[key][:]
			except:
				copy[key]	= config[key]
		else:
			copy[key]	= []
			for child in config[key]:
				if maxdepth>0:
					copyOfChild	= __copyConfig(child, copyparentlink, maxdepth-1)
					copy[key].append(copyOfChild)

	return	copy

def printConfigtree(config):
	""" print a surprisingly readable copy of the configstructure """
	if config==None:
		print None
	else:
		copy	= __copyConfig(config, 0)
		pp		= pprint.PrettyPrinter()
		pp.pprint(copy)

if __name__=="__main__":
	root	= parse("d:\prog\Release\webindex.ini")
	printConfigtree(root)

	print getVariable("arg1.source", root['branch'][4]['branch'][1])
	print getVariable("x.arg1.source", root)
	print getVariable("server", root['branch'][4]['branch'][1])
	print getVariable("d.arg3.source", root['branch'][4]['branch'][1])
	printConfigtree(getRoot(root['branch'][4]['branch'][1]))
