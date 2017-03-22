import string
import pprint

def getPage(config, page):
	for x in config:
		if x['__pagenumber']==page:
			return x['config']

def makeDBSection(dbsection, fancy=0):
	answer	= []

	answer.append("<database database1>")
	if fancy==1:
		answer += ['',
			 '\t########',
			 '\t#### Specify a database connection',
			 '\t##',
			 "\t## Required attributes:\tan identifier (in this case 'database1')",
			 '\t## Available variables:\tdbclient, dbname, user, password, host, dsn, connectstring',
			 '\t##',
			 '\t####',
			 '\t##',
			 '\t## - dbclient',
			 '\t##   > Required',
			 '\t##   > Specify which database plugin to use. Allowed values: "ODBC". No default value.',
			 '\t##',
			 '\t## - dbname',
			 '\t##   > Specify the name of the database to use. No default value.',
			 '\t##',
			 '\t## - user',
			 '\t##   > Specify which username to use to connect to the database. No default value.',
			 '\t##',
			 '\t## - password',
			 '\t##   > Specify which password to use to connect to the database. No default value.',
			 '\t##',
			 '\t## - host',
			 '\t##   > Specify to which to connect to, in order to make this database connection',
			 '\t##',
			 '\t## - dsn',
			 '\t##   > Specify which DSN (data service name) to use',
			 '\t##',
			 '\t## - connectstring',
			 '\t##   > Or, provide a connectstring to feed to the database plugin you have specified.',
			 '\t##     Doing so will override all other variables except "dbclient".',
			 '\t##',
			 '\t########',
			 '']

	for key in dbsection.keys():
		if not key in ['confirm', 'connstr', 'host']:	# TODO: Remove 'host' from this list
			if dbsection[key]!=None:
				answer.append("	%s = %s" % (key, dbsection[key]))
		if key=='connstr':
			if dbsection[key]!=None:
				answer.append("	connectstring = " + dbsection[key])
	answer.append("</database>")

	return answer

def makeArgumentsSection(arguments):
	answer	= []

	for argument in arguments:
		if argument['argumentsource']=='database':
			entry	= []
			entry.append("	<argument %s>" % (argument['name'], ))
			entry.append("		name	= %s" % (argument['name'], ))
			entry.append("		source	= database1.%s" % (argument['value'], ))

			query		= ""
			condition	= ""

			# derive 'condition' statement on basis of dependencies
			dependent	= []
			for dependency in argument['dependent_on']:
				dependent.append("{%s.table}.{%s.column}={%s.value}" % (dependency, dependency, dependency))
			condition	= string.join(dependent, " and ")

			# if no dependencies are given, then check 'query'
			# if that starts with 'select', then put this in the 'query' statement, else in the 'condition' statement
			if len(condition)==0:
				if len(argument['query'])>0:
					if string.lower(string.split(string.trim(argument['query']), ' ')[0])=="select":
						query		= argument['query']
					else:
						condition	= argument['query']

			# append 'condition' and 'query' statements
			if len(condition)>0:
				entry.append("	condition= %s" % (condition, ))
			if len(query)>0:
				entry.append("	query	= %s" % (query, ))

			entry.append("	</argument>")

			if len(condition)>0 or len(query)>0:
				answer	= answer + entry
			else:
				answer	= entry + answer

	return answer

def makeTestXMLConfig(config, currentfile=None):
	answer	= []

	# create database section
	answer	+= makeDBSection(getPage(config, 3))

	# create dynamic section
	dynamic	= getPage(config, 9)['config']
	for file in dynamic.keys():

		if currentfile!=None:
			if file!=currentfile:
				continue

		answer.append("<dynamic>")
		answer.append("url=%s" % (dynamic[file]['urltemplate'], ))
		if len(dynamic[file]['posttemplate'])>0:
			answer.append("post=%s" % (dynamic[file]['posttemplate'], ))

		answer	+= makeArgumentsSection(dynamic[file]['arguments'])

		answer.append("</dynamic>")


# 	print("Constructed test XML config:")
# 	pprint.pprint(answer)
	return answer

def makeFinalXMLConfig(config):

	# create header and <cache> section
	answer	= ['#### Webindex configuration file',
				 '##',
				 '## Please read the information provided with the various tags in this configuration file.',
				 '##',
				 "## A note on variables: It is possible to create variables, for example a 'server' variable",
				 '## in the following manner.',
				 '##',
				 '## server\t= www.mydomain.com',
				 '##',
				 '## This definition creates a variable that can be used throughout this configuration file.',
				 '## Variables defined within tags have a limited scope. You can reference this variable by enclosing',
				 '## its name with braces, as in {server}.',
				 '##',
				 '##',
				 '',
				 '<cache>',
				 '\t########',
				 '\t#### Control how the cache operates',
				 '\t##',
				 '\t## Required attributes:\t(None)',
				 '\t## Available variables:\texpires, file',
				 '\t##',
				 '\t####',
				 '\t##',
				 '\t## - expires',
				 '\t##   > Specify how long an entry in the cache remains valid. Valid units are: "year(s)", ',
				 '\t##     "month(s)", "week(s)", "day(s)", "hour(s)", "minute(s)" and "second(s)". You may ',
				 '\t##     combine these units (e.g.: "1 day and 12 hours"). Defaults to "6 hours".',
				 '\t##',
				 '\t## - file',
				 '\t##   > Specify where the cache is located. Defaults to "cache.web".',
				 '\t##',
				 '\t########',
				 '',
				 '\texpires\t\t= 6 hours',
				 '#\tfile\t\t= cache.web',
				 '</cache>',
				 '']

	# create 'database' section
	answer	+= makeDBSection(getPage(config, 4), fancy=1)

	# insert 'static dirs' section
	dirs	= getPage(config, 7)
	counter	= 0
	for dirset in dirs:
		counter += 1
		local	= dirset[0]
		public	= dirset[1]
		answer	+= ["", "<directory>"]
		if counter==1:
			answer+=[ '',
				 '\t########',
				 "\t#### Include a directory with ordinary 'static' web pages in the index.",
				 '\t#### Each file in that directory will be included in the index.',
				 '\t##',
				 '\t## Required attributes:\t(None)',
				 '\t## Available variables:\tlocal, public',
				 '\t##',
				 '\t####',
				 '\t##',
				 '\t## - local',
				 '\t##   > Required',
				 "\t##   > Specify which directory contains the ordinary 'static' web pages",
				 '\t##',
				 '\t## - public',
				 '\t##   > Required',
				 '\t##   > Specify how this directory and its content can be accessed online.',
				 '\t##',
				 '\t########',
				 '\n']

		answer	+= ["	local = " + local, \
					"	public = " + public, \
					"</directory>"]

	# insert 'dynamic pages' section
	dynamic	= getPage(config, 9)['config']
	counter	= 0
	for file in dynamic.keys():
		counter += 1

		answer	+= ["", "<dynamic>"]
		if counter==1:
			answer += ['\t########',
				 '\t#### Use this tag to specify a dynamic webpage',
				 '\t##',
				 '\t## Required attributes:\t(None)',
				 '\t## Available variables:\turl, post',
				 '\t## Available tags:\targument',
				 '\t##',
				 '\t####',
				 '\t##',
				 '\t## - url',
				 '\t##   > Required',
				 '\t##   > Provide a template to specify how this URL generally looks. See example below.',
				 '\t##',
				 '\t## - post',
				 "\t##   > Provide a template of the 'post' variables this web pages requires. Usage similar",
				 "\t##     to the 'url' variable.",
				 '\t##',
				 '\t########',
				 '',
				 '',
				 '\t#### The <argument> - tag',
				 "\t#### Required for each argument used in the 'url' and 'post' variables",
				 '\t##',
				 '\t## Required attributes:\tan identifier (usually name of the argument)',
				 '\t## Available variables: name, source, condition, query',
				 '\t##',
				 '\t####',
				 '\t##',
				 '\t## - name',
				 '\t##   > Required',
				 '\t##   >',
				 '\t##',
				 '\t## - source',
				 '\t##   > Required',
				 '\t##   >',
				 '\t##',
				 '\t## - condition',
				 '\t##   >',
				 '\t##',
				 '\t## - query',
				 '\t##   >',
				 '\t##',
				 '\t########',
				 '',
				 '\t####',
				 '\t##',
				 '\t## Example configuration (16 lines)',
				 '\t##',
				 '\t##  1. <dynamic>',
				 '\t##  2.   server = www.mydomain.com',
				 '\t##  3.   url = http://{server}/article.php?{arg1.name}={arg1.value}&{arg2.name}={arg2.value}',
				 '\t##  4.',
				 '\t##  5.   <argument arg1>',
				 '\t##  6.       name         = article',
				 '\t##  7.       source       = database1.articles.id',
				 '\t##  8.   </argument>',
				 '\t##  9.',
				 '\t## 10.   <argument arg2>',
				 '\t## 11.        name        = page',
				 '\t## 12.        source      = database1.articles.page',
				 '\t## 13.        condition   = {arg1.column}={arg1.value}',
				 '\t## (13a.      query       = SELECT page FROM articles WHERE {arg1.table}.{arg1.column}={arg1.value}  )',
				 '\t## 14.   </argument>',
				 '\t## 15.',
				 '\t## 16. </dynamic>',
				 '\t##',
				 '\t## This configuration will generate URLs such as:',
				 '\t##',
				 '\t## \thttp://www.mydomain.com/article.php?article=1&page=1',
				 '\t## \thttp://www.mydomain.com/article.php?article=1&page=2',
				 '\t## \thttp://www.mydomain.com/article.php?article=1&page=3',
				 '\t## \thttp://www.mydomain.com/article.php?article=2&page=1',
				 '\t## \thttp://www.mydomain.com/article.php?article=2&page=2',
				 '\t## \thttp://www.mydomain.com/article.php?article=3&page=1',
				 '\t## \thttp://www.mydomain.com/article.php?article=3&page=2',
				 '\t## \thttp://www.mydomain.com/article.php?article=3&page=3',
				 '\t## \thttp://www.mydomain.com/article.php?article=3&page=4',
				 '\t## \t... etcetera',
				 '\t##',
				 '\t## Explanation:',
				 '\t##',
				 '\t##  1. Opening tag',
				 "\t##  2. You can create your own variables such as the convenient 'server' variable in the example.",
				 "\t##  3. Specify how an URL for this page generally looks. This page references the 'server' variable",
				 '\t##     defined in line 1 and introduces two arguments: arg1 and arg2.',
				 "\t##     Note how the name and value of these arguments are referenced. You can access an argument's",
				 '\t##     associated database, table and column in a similar way, by use of the keywords "database",',
				 '\t##     "table" and "column".',
				 '\t##  4.',
				 "\t##  5. Opening tag for the definition of argument 'arg1'. The identifier ('arg1' in this case) is required.",
				 "\t##  6. The 'name' variable defines the argument's name that will end up in the final URL",
				 "\t##  7. The 'source' variable defines the database source for this argument. This database source contains",
				 '\t##     values which, if assigned to this argument, help create a valid URL.',
				 "\t##     The form of this 'source' variable is <database identifier>.<table>.<column>, which in this case",
				 '\t##     translates to database1.articles.id',
				 '\t##  8. Closing tag for this argument',
				 '\t##  9.',
				 "\t## 10. Opening tag for 'arg2'",
				 "\t## 11. The 'name' variable",
				 "\t## 12. The 'source' variable",
				 "\t## 13. The 'condition' variable helps control which values are assigned to this argument. It is not uncommon",
				 '\t##     that the value of some other argument is a deciding factor in determining which values are valid for',
				 '\t##     this argument.',
				 "\t##     In the example above, the 'page' variable is dependent on 'argument': the value for 'article' determines",
				 "\t##     which values are valid for 'page' (look to see what I mean).",
				 "\t##     In the process of generating the URLs, the value for 'article' is determined first. This limits the",
				 "\t##     number of possible values for 'page'. The only valid values are those where the value in the source",
				 "\t##     column for 'article' is equal to the value that was assigned to 'article', which can be expressed as",
				 '\t##     "id={arg1.value}". Or, in more general terms, as "{arg1.column}={arg1.value}".',
				 '\t##',
				 '\t##     For those interested: Internally, this condition will be translated to the SQL-query',
				 '\t##',
				 '\t##           SELECT DISTINCT page FROM articles WHERE id={arg1.value}',
				 '\t##',
				 "\t##     The values resulting from this query are sequentially assigned to the 'page' variable. Each assignment",
				 "\t##     causes a new URL to be generated. If the query runs out of results, then the next value for 'arg1' is",
				 '\t##     fetched and the process starts over again. Eventually this causes all valid URLs to be generated.',
				 '\t##',
				 '\t##     You can also manually provide an SQL string to feed this process, as is demonstrated in line 13a. Make',
				 "\t##     sure your query returns only _one_ column. Also beware that the 'query' and 'condition' variables are",
				 "\t##     mutually exclusive (you can't use both).",
				 '\t##',
				 "\t##     This file is processed by a one-pass interpreter, so parameters that are referenced in other arguments'",
				 '\t##     "conditions" should be declared first.',
				 '\t##',
				 '\t## 14. Closing tag for this argument',
				 '\t## 15.',
				 '\t## 16. Closing tag for this dynamic web page',
				 '\t##',
				 '\t##',
				 "\t## In case your web pages cannot be described with this mechanism, then you can resort to the 'script' and",
				 "\t## 'textfile' tags described below.",
				 '\t########',
				 '\n']

		answer.append("	url=%s" % (dynamic[file]['urltemplate'], ))
		if len(dynamic[file]['posttemplate'])>0:
			answer.append("	post=%s" % (dynamic[file]['posttemplate'], ))

		answer	+= makeArgumentsSection(dynamic[file]['arguments'])

		answer.append("</dynamic>")

	# append disabled 'script' and 'textfile' tags, and 'output-section' header
	answer	+= [ '',
			 '#<script>',
			 '',
			 '\t########',
			 '\t#### Provide a script that returns a list of URLs',
			 '\t##',
			 '\t## Required attributes:\t(None)',
			 '\t## Available variables:\tscript',
			 '\t##',
			 '\t####',
			 '\t##',
			 '\t## - script',
			 '\t##   > Required',
			 '\t##   > Specify the path and filename of the script to execute',
			 '\t##',
			 '\t########',
			 '',
			 '\t####',
			 '\t##',
			 '\t## The script needs to provide a list of URLs in the following format:',
			 '\t##',
			 '\t## <item>',
			 '\t##   url  = http://www.mydomain.com/article.php?article=1&page=1',
			 '\t##   post = wantscookie=1',
			 '\t## </item>',
			 '\t##',
			 "\t## The 'post' variable is optional.",
			 '\t##',
			 '\t####',
			 '',
			 '# \tscript\t= "C:\\Program Files\\Python\\2.2.3\\python.exe" script.py',
			 '# \tscript\t= "/home/webmaster/urlscript.py"',
			 '#</script>',
			 '',
			 '#<textfile>',
			 '',
			 '\t########',
			 '\t#### Provide a textfile that contains a list of URLs',
			 '\t##',
			 '\t## Required attributes:\t(None)',
			 '\t## Available variables:\tfile',
			 '\t##',
			 '\t####',
			 '\t##',
			 '\t## - file',
			 '\t##   > Required',
			 '\t##   > Specify the path and filename of the textfile',
			 '\t##',
			 '\t########',
			 '',
			 '#\tfile\t= c:\\textfile.example.txt',
			 '#\tfile\t= /var/www/urls.txt',
			 '#</textfile>',
			 '',
			 '',
			 '########',
			 '#### Configuration for output-plugins',
			 '########',
			 '']

	# insert output-plugin configuration
	output	= getPage(config, 10)

	answer	+= ["<oai>", \
				"	adminEmail	= " + output['adminemail'],
				"	repositoryname	= " + output['repositoryname'],
				"</oai>"]

	answer	+= ["", "<html>",
				"	template	= " + output['htmltemplate'],
				"	chunksize	= " + output['chunksize'],
				"</html>"]

	return answer
