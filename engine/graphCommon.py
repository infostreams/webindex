import 	string
import 	types
import	pprint	# TODO: Remove

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os, os.path
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-1], os.sep))
sys.path.append(string.join(string.split(os.path.dirname(sys.argv[0]), os.sep)[:-2], os.sep))

from	shared import XMLConfig

def getVariable(variable, where):
	""" Get the value of a specific variable (eg: arg1.source)
		This function is slightly different from the one in
		XMLConfig: the values 'table', 'database' and 'column'
		are extracted from the 'source'-variable, the
		'value'-value is extracted from the 'recordcontents' """

	# Why is this? I don't know :)

#	print "Fetching variable", variable
	parts	= string.split(variable, ".")
	var		= parts[-1]
	if var == 'value':
		destination	= string.join(parts[:-1], ".")
		node		= XMLConfig.getNode(destination, where)
		if node != None:
			if node.has_key('recordcontents'):
				result	= node['recordcontents']
			else:
				result	= None
		else:
			result	= None
	elif var in ['database', 'table', 'column']:
		parts[-1]	= 'source'
		destination	= string.join(parts, '.')
		getvar		= XMLConfig.getVariable(destination, where)
		if getvar!=None:
			answer	= string.split(getvar, ".")
			if var == 'database':
				result	= answer[0]
			if var == 'table':
				result	= answer[1]
			if var == 'column':
				result	= answer[2]
		else:
			result	= None
	else:
		result		= XMLConfig.getVariable(variable, where)

# 	print "Variable %s @ %s = %s" % (variable, getProperty('label', where), result)
# 	print "where ="
# 	printGraph(where)

	return result

def replaceVariables(input, node):
	""" replace {arg1.var}-style variables with their actual values """

	skip 	= 0
	i		= 0
	answer	= ""

	if (input!=None):

		while (skip+i)<len(input):

			char	= input[skip + i]

			if char!="{":
				answer += char
				i+=1
			else:
				variable	= ""
				for val in input[i+1:]:
					if val!="}":
						variable += val
					else:
						break

				i += len(variable)+2

				value	= getVariable(variable, node)

				# Answers obtained from an SQL-query are lists
				# Fetch only the first
				# TODO: Check if this behaviour is correct
				if type(value) is types.ListType:
					value	= value[0]

				if type(value) is types.IntType:
					answer	= "%s%d" % (answer, value, )
				elif type(value) is types.StringType:
					answer	= "%s%s" % (answer, value, )
				else:
					if value==None:
						raise "Error in processing the variables from the configuration: " \
							"The value of the variable '%s' could not be determined, " \
							"possibly due to a program-, a configuration- or a " \
							"database-error" % (variable, )
					else:
						raise "Error in processing the variables from the configuration: "\
							"type of variable '%s' in argument '%s' is neither " \
							"string nor integer" % (variable, XMLConfig.getProperty('label', node))

		return answer
