from 	logfileAnalysis import analyzer
from 	database import database
from	Tkinter import *
import 	string
import	math
import	configfile
import	copy
import	sys
import	re
import 	pprint
import	XMLConfig
import	urllib
import 	pprint	# TODO: Remove this

class logfilePredictor:

	def __init__(self):
		self.db	= None

	def getGroupedLogfileEntries(self, logfiles=None, hostname=None):
		""" retrieve a relatively complex datastructure containing
			some interesting data extracted from the logfiles

			structure:
			[ entry1, entry2, ....]

			an entry has the following structure:
			entry['entries']	= grouped logfile-entries,
					see __group() in analyzer.py for an explanation
			entry['log']		= logfile name these entries are based on
			entry['server']		= server-name these entries apply to
		"""

		# Initialize answer
		answer		= []

		# create a logfileAnalyzer instance
		f			= analyzer.logfileAnalyzer()

		if logfiles==None:
			# get possible logfile names
			logfiles	= f.getLogfileNames()

		# retrieve which logfiles are available and process each
		for logfile in logfiles:

			# fetch the logfile-entries for the current logfile
			entries			= f.getLogfileEntries(logfile)

			# remove the non-script entries
			filtered		= f.filterNonScriptEntries(entries)

			# group the remaining entries in a dazzingly complex datastructure
			grouped			= f.groupEntries(filtered)

			# close the logfile
			f.closeLogfile()

			# create a dictionary which will hold the information
			# for this specific logfile
			entry			= {}

			# fill the dictionary with information
			if logfile['server']==None:
				logfile['server']=hostname

			entry['server']	= logfile['server']
			entry['log']	= logfile['log']
			entry['entries']= grouped

			# append the retrieved information to the answer
			answer.append(entry)

		# done
		return answer

	def printGroupedLogfileEntries(self, entries):
		for entry in entries:
 			print "Logfile %s provided the following information:" % (entry['log'], )
 			theseEntries	= entry['entries']
 			for requestverb in theseEntries.keys():
 				for file in theseEntries[requestverb].keys():
 					print string.upper(requestverb) + " " + file + ":", theseEntries[requestverb][file]

	def getDatabaseStructures(self):		# TODO: Delete this whole function?
		""" return table descriptions from accessible tables for databases specified in the configurationfile """

		dbnumber		= 1
		configname		= "database1" # TODO: Fix this! No default names, but walk through all 'entries' of type 'database'
		webindexini		= XMLConfig.parse("druid.ini")
		config			= configfile.getDBConfig(configname, 1, webindexini)
		answer			= []

		while len(config) != 0:
			# walk through all 'database'-sections in the config-file

			# Open a database
			db				= database.database(config['dbclient'], config['user'], \
								config['password'], config['dsn'], config['dbname'], \
								config['connectstring'])

			tablenames		= db.getTableNames()
			structure		= {}
			if tablenames!=None:
				for name in tablenames:
					db.issueSQLstatement("SELECT * FROM %s" % (name, ), 1)
					structure[name]	= db.getColumnNames()

			part				= {}
			part['handle']		= configname
			part['config']		= config
			part['structure'] 	= structure
			answer.append(part)

			dbnumber		+= 1
			configname		= "database%d" % (dbnumber, )
			config			= configfile.getDBConfig(configname, 1, webindexini)
			db.closeDB()

		return	answer

	def getDatabaseStructure(self, dbclient, user, password, dsn, dbname, connstr):
		""" return table descriptions from accessible tables in the specified database """

		config				= {}
		config['dbclient']	= dbclient
		config['user']		= user
		config['password']	= password
		config['dsn']		= dsn
		config['dbname']	= dbname
		config['connectstring']=connstr

# 		print "logfilePredictor.getDatabaseStructure"
# 		pprint.pprint(config)

		# Open a database
		db				= database.database(config['dbclient'], config['user'], \
							config['password'], config['dsn'], config['dbname'], \
							config['connectstring'])

		answer			= []
		tablenames		= db.getTableNames()
		structure		= {}
		if tablenames!=None:
			for name in tablenames:
				db.issueSQLstatement("SELECT * FROM %s" % (name, ), 1)
				structure[name]	= db.getColumnNames()

		part				= {}
		part['handle']		= "database1"	# TODO: Fix?
		part['config']		= config
		part['structure'] 	= structure
		answer.append(part)

		db.closeDB()

		return	answer

 	def __findColumnMapping(self, logfileentry, databasestructure):
 		""" return mapping for best matching table and the accompanying score,
		    calculated on basis of columnnames """

		# TODO: Support multiple matching columns (!)
		# TODO: Make datastructure match __findContentMapping

		# Create an empty answer
		answer	= {}

		# Walk through all databases in the databasestructure
		for database in databasestructure:

			# Parse entries in 'GET' and 'POST' categories
			for method in ['get', 'post']:

				# For each database, check for matches in all 'GET' and 'POST'-entries
				for file in logfileentry['entries'][method].keys():

					# Extract the arguments for this 'GET' or 'POST'-entry
					arguments	= logfileentry['entries'][method][file]

					# Create an empty mapping for this file
					mapping		= {}

					# For each argument, check if there are columns with the same name
					for argname in arguments.keys():
						argvalue	= arguments[argname]

						# Check each table in this database
						for table in database['structure'].keys():
							columnnames	= database['structure'][table]

							# Check each column in this table
							for column in columnnames:

								# If this column has the same name as the argument,
								# then consider it a candidate
								if column == argname:
									entry				= {}
									entry['database']	= database['handle']
									entry['table']		= table
									entry['column']		= column
									entry['method']		= method
									mapping[argname]	= entry

					# A mapping is stored in the eventual answer
					if not answer.has_key(file):
						answer[file]= []

					if len(mapping)>0:
						answer[file].append(mapping)

		# TODO: Check if obtained mappings are consistent with argument-values in the database
		# In other words: check the validity of the mappings

		#print 'ColumnMapping:', answer

		# Done!
		return answer

	def __quote(self, inputstring):
		# 'escape' and "quote" a string if it is not a number

        # check if inputstring is a number
		x	= re.findall(re.compile("^[0-9]+$"), string.strip(inputstring))
		if len(x)==0:

			# inputstring is not a number:
			# place quotes around inputstring and replace " by \"
			outputstring= urllib.unquote_plus(inputstring)	# translate %2A, %7E and '+' markers
# 			outputstring= string.replace(outputstring, '"', '\"')
# 			outputstring= "\"%s\"" % (outputstring, )
			outputstring= string.replace(outputstring, "'", "\\'")
			outputstring= "'%s'" % (outputstring, )

		else:
			# outputstring is a number: no changes
			outputstring= inputstring

		# Done
		return outputstring

	def __contentFinder(self, arguments, database, tablename):
		# Voor ieder argument: stel sql-statement samen dat kijkt of die data ergens
		# in een kolom voorkomt. Zo niet, dan stop met zoeken voor dat argument.
		# Indien wel wat gevonden wordt: kijk of de (evt.) tweede waarde van het argument
		# ook in die kolom staat, en de derde, etc. Als niet meer klopt, dan helaas geen match.
		#

		# TODO: Split functionality in multiple functions (too long now)
		#
		# TODO: Replace "SELECT * FROM <table> WHERE <arg1>=value OR <arg2>=value OR ..."
		# TODO: with a series of "SELECT * FROM <table> WHERE <arg1>=value",
		# TODO: "SELECT * FROM <table> WHERE <arg2>=value" etc. (should trigger
		# TODO: less 'Data type mismatch' errors with winODBC and is more portable)
		# TODO: (also fixes and simplifies 'find matching column'-code)
		#
		# TODO2: Perhaps restore original functionality? The current code is truly _very_ slow!
		#
		# TODO: Do as much closeDB-calls as there are openDB-calls

		# Create an answer
		answer		= {}
#		columns		= self.db.getColumnNames()

		# Walk through all arguments
		for argname in arguments.keys():

			##
			### STEP 1: Create SQL-statement for first (argument-)value
			##

			# extract first value of this argument
			argvalue	= arguments[argname][0];

			# walk through all columns
			for column in database['structure'][tablename]:

				# create SQL
				sql	= "SELECT * FROM %s WHERE %s=%s" % (tablename, column, self.__quote(argvalue))

#				print "0. issue SQL statement:", sql

				##
				### STEP 2: Try to execute SQL-statement
				##

				try:
					# execute sql-statement
					resultset	= self.db.issueSQLstatement(sql, 1)
#					print "... Done"
				except:

					# if an exception occured, then fetch info about that exception
					cla, exception, traceback = sys.exc_info()

					# Now, check if this error is raised because of an illegal assignment of values in
					# the SQL-statement (e.g. we have done a: SELECT * FROM table WHERE number='bla';
					# such statements make the winODBC module choke). If this is the case, then ignore
					# this exception.

					# This code works for the winODBC module
					if string.find(cla, "Data type mismatch") > 0:
#						print "Data type mismatch"
						pass
					else:
						raise cla
				else:
					# the sql-statement succeeded, check if we have an answer
					if resultset!=None:
						# yes! therefore:

						##
						### STEP 3: Try other argument values
						##

						# So far this column contains 1 of the values for this argument
						# that were found in the logfiles
						matchcount		= 1

						# Try all other argument-values
						for argvalue in arguments[argname][1:]:

							# create an SQL-statement that searches this argument-value
							# in the 'matching' column
							sql	= "SELECT * FROM %s WHERE %s=%s" % (tablename, column, self.__quote(argvalue))

							# issue this query to the database
#							print "1. issue SQL statement:", sql
							try:
								resultset	= self.db.issueSQLstatement(sql, 1)
							except:
								continue
	#						print "... Done"


							# If the number of results from this query is larger than 0, then
							# this argumentvalue is present in the same column. Therefore,
							# increase the matchcount
#							print "2. Fetch first record... ",
							firstrecord	= resultset.getFirstRecord();
#							print "Done"
#							print "firstrecord:", firstrecord
							if firstrecord!=None:
								if len(firstrecord)>0:
									matchcount	+= 1

						# The 'score' is calculated as the percentage of argument-values that
						# are found in this specific matching column
						#
						# The highest scoring matching columns are used in the final mapping
						score	= (100*matchcount)/len(arguments[argname])

						# Append obtained parameters to answer
						if not answer.has_key(argname):
							answer[argname]		= []

						entry					= {}
						entry['score']			= score
						entry['matchcount']		= matchcount
						entry['column']			= column
						entry['table']			= tablename
						entry['database']		= database['handle']

	#					print "appending ", entry
						answer[argname].append(entry)

		# Done
		return answer

	def __findContentMapping(self, logfileentry, databasestructure, progressvar, descriptionvar, filevar, master):
		""" return mapping for best matching table and the accompanying score,
			calculated on basis of content """
		# voor iedere file: geef arguments mee, en tabel namen
		# klus daar een sql-statement van

		answer	= {}
		count	= 0
		total	= 0

		for database in databasestructure:
			for method in ['get', 'post']:
				for file in logfileentry['entries'][method].keys():
					for table in database['structure'].keys():
						total	+= 1

		# Walk through all databases in the databasestructure
		for database in databasestructure:

			try:
				config	= database['config']
				self.openDB(config['dbclient'], config['user'], config['password'], config['dsn'], \
							config['dbname'], config['connectstring'], database['handle'])
			except:
				continue

			# Parse entries in 'GET' and 'POST' categories
			for method in ['get', 'post']:

				# For each database, check for matches in all 'GET' and 'POST'-entries
				for file in logfileentry['entries'][method].keys():

					filevar.set(file)

					# Extract the arguments for this 'GET' or 'POST'-entry
					arguments	= logfileentry['entries'][method][file]

					answer[file]= {}

					# Check each table in this database
					for table in database['structure'].keys():

						# Find mappings
						contentMapping		= self.__contentFinder(arguments, database, table)
						count += 1
						progressvar.set("%d%%" % (100*count/total, ))
						descriptionvar.set("Checking table '%s'" % (table, ))
						master.update_idletasks()
						master.update()
#						print "%s: Processing %s.%s: %d%%" % (file, database['handle'], table, 100*count/total)

						if len(contentMapping)>0:

							# If a contentmapping is found, then
							# reorganize the answer to be identical to the
							# datastructure returned by '__findColumnMapping'
							for argument in contentMapping.keys():

								if not answer[file].has_key(argument):
									answer[file][argument]	= []

								for entry in contentMapping[argument]:
									answer[file][argument].append(entry)

            # close this database
			self.closeDB()

		# Done
		return answer

	def compareMappings(self, x, y):
		# compare two "mappings" (see 'findMapping') on basis of score
		# used to sort a list of mappings in an descending matter
		if (x['score']==y['score']):
			return 0
		else:
			if (x['score']>y['score']):
				return -1
			else:
				return 1

	def __sortAndCombineMappings(self, columnmapping, contentmapping):
		""" sort and combine the provided mappings  """

		if len(contentmapping)==0:
			answer	= {}
			for file in columnmapping.keys():
				answer[file]	= {}
				for mappingset in columnmapping[file]:
					for argument in mappingset.keys():
						entry				= mappingset[argument]
						entry['score']		= 100
						entry['matchcount']	= 0
						if not answer[file].has_key(argument):
							answer[file][argument]=[]
						answer[file][argument].append(entry)


# 			print"nieuw ding gemaakt"
# 			pprint.pprint(answer)
			return answer

		if len(columnmapping)==0:
			return contentmapping

		# create a copy of the 'content'-mapping
		winners	= copy.deepcopy(contentmapping)

		# walk through all files
		for file in winners.keys():

			# ...and through all columnmappings for this file
			# (if those are available, that is)
			if columnmapping.has_key(file):

				listofmappings	= columnmapping[file]

				for columnmapping in listofmappings:

					for arg in columnmapping.keys():
						thiscol	= columnmapping[arg]

						# if the columnmapping we are processing is also present
						# in the (copy of) the content-mappings, then it is
						# more likely that this is the column we're looking for
						# therefore, increase its score
						if winners[file].has_key(arg):
							for x in winners[file][arg]:
								if ((x['database'] == thiscol['database']) and \
									(x['table'] == thiscol['table']) and \
									(x['column'] == thiscol['column'])):

									x['score']	+= 50

							winners[file][arg].sort(self.compareMappings)

		return winners


	def findMapping(self, logfileentry, databasestructure, progressvar, descriptionvar, filevar, master):
		""" return possible mappings for a specific file """

		# An example of a mapping for the parameter 'pagina' of
		# the '/viewtt.php' script is as follows:
		#
		#  {'/viewtt.php': {'pagina': [{'column': 'pagina',
		# 							 'database': 'database',
		# 							 'matchcount': 4,
		# 							 'score': 40,
		# 							 'table': 'nieuws'},
		# 							{'column': 'id',
		# 							 'database': 'database',
		# 							 'matchcount': 10,
		# 							 'score': 100,
		# 							 'table': 'huislijst'}]}}
		#
		# In this case, two possible mappings are provided. The
		# datastructure indicates that for the parameter 'pagina', it is
		# both possible that this parameter is related to the column 'pagina'
		# from the table 'nieuws' (in the database 'database'), or to the
		# column 'id' from the table 'huislijst'. It is more likely that
		# the latter is the case, since its 'score' is higher.

#		global cols, content

		cols	= self.__findColumnMapping(logfileentry, databasestructure)
		content	= self.__findContentMapping(logfileentry, databasestructure, progressvar, descriptionvar, filevar, master)
		combined= self.__sortAndCombineMappings(cols, content)

		return	combined

	def convertBaseN(self, x, base):
		# convert a specific decimal number x to a number in base-N form
		sum			= x % base
		iteration	= 1
		divider		= 1
		answer		= "%d" % (sum, )
		while sum!=x:
			divider	= divider * base
			this	= math.floor(x/divider) % base
			sum		+= this * divider
			answer	= "%d%s" % (this, answer)

		return answer

	def isValidDependencyRelation(self, number):
		# check if the provided number is a valid dependency-relationship between two or more arguments.
		# (see below for a slightly more detailed explanation about dependency-relationships on basis of numbers)
		# It is valid if:
		# rule 1: the number is longer than 1 digit
		# rule 2: a digit does not occur twice (or even more)
		# rule 3: it does not contain a zero
		if len(number)==1:
			return 0
		for digit in number:
			if string.count(number, digit)>1:
				return 0
			if digit=='0':
				return 0
		return 1

	def createAllPossibleDependencies(self, mapping, server, dbstructure, n):
		# write at most 'n' URL-like rules per parameter per file, based on the provided mapping
		# it is (was?) assumed that the provided mapping is sorted descendingly

		# Process all files
		config					= {}
		config['__database']	= {'config': dbstructure[0]['config'], 'handle': dbstructure[0]['handle']}
		for file in mapping.keys():

			# first, extract the top 'n' mappings per parameter per file
			# and store them in a more accessible datastructure :)
			arguments			= mapping[file]

			config[file]		= {}

			# create target-url
			if server!=None:
				url				= "http://" + server + file + "?"
			else:
				url				= "http://localhost/" + file + "?"	# TODO: replace 'localhost'
			basetemplate		= url[:]
			x					= []
			for arg in arguments.keys():
				x.append("{%s.name}={%s.value}" % (arg, arg))

			# save this information
			config[file]['urltemplate']	= url + string.join(x, "&")
			config[file]['basetemplate']= basetemplate
			config[file]['posttemplate']= ''

			answer			= []
			combinations	= 1

			# The datastructure we are about to create is a matrix that looks like this:
			# 			answer[argument][argumentvalue]
			#
			# Each argument is referenced by its number (e.g.: first argument, second argument)
			# Each argumentvalue is referenced by its position in the provided mapping that is sorted
			# descendingly (e.g.: the first argumentvalue is the one with the highest associated 'score')
			# Each element in this matrix contains a mapping (to see what that is, look at findMapping)
			#
			# example:
			# ========
			# answer[0][0]	= 'mapping1a'	# this concerns the first argument for this file,
			#					and the highest scoring mapping associated with it. Its value is a mapping
			# answer[0][1]	= 'mapping1b'   # still the first argument, but now the second highest
			# 					scoring mapping is referenced
			# etc.
			#
			# Since each argument is referenced by its number, it is necessary to store its original name
			# (e.g. "pagenumber") somewhere. These argument names are stored in the last row of the matrix,
			# more specific: answer[n][len(answer[n])-1]

			# Do it :)
			for arg in arguments.keys():
				index			= len(answer)
				answer.append([])
				arguments[arg].sort(self.compareMappings)
				for i in range(n):
					if i<len(arguments[arg]):
						element	= arguments[arg][i]
						answer[index].append(arguments[arg][i])


				combinations	*= len(answer[index])

				# save argument name
				answer[index].append(arg)


			# Second, this matrix is used to create all possible combinations of the top-n argumentvalues
			# of all arguments.
			#
			# The algorithm being used is the following:
			# - count from 0 to number_of_possible_combinations-1
			# - first_argument	= answer[0][count % number_of_argumentvalues_for_first_argument]
			# - second_argument = answer[1][(count / number_of_argumentvalues_for_first_argument) %
			#								number_of_argumentvalues_for_first_argument]
			# - third_argument	= answer[2][(count /
			#			(number_of_argumentvalues_for_first_argument * ...._second_argument)) %
			#			(..._first_argument * ..._second_argument)]
			# - fourth_argument	= answer[3][(count /
			#			(..._first_argument * ..._second_argument * ..._third_argument)) %
			#			(..._first_argument * ..._second_argument * ..._third_argument)]
			# and so on
			#
			# TODO: FIX ALGORITHM
			# (Did I do this already?? don't remember :))
			# should be: 	first_arg	= answer[0][count % numargs0]
			#               second_arg	= answer[1][(count % (numargs0 * numargs1))/numargs0]
			#				third_arg	= answer[2][(count % (numargs0 * numargs1 * numargs2))/  (numargs0 * numargs1)]


            # Note: These 6 lines of code were added a few months later. I have no intention of re-grasping what I
            # hacked together a few months ago. Perhaps these 6 lines approximately do the same as the complicated story
            # above. I really wouldn't know :)
            # Anyway, what this part does is setting up a 'dependencies' list for the current arguments. This list contains
            # numbers (in string-form), that can be interpreted as follows:
            # "123"	=> argument 1 is dependent on argument 2 and 3
            # "321" => argument 3 is dependent on argument 2 and 1
            # etc.
            # This list can be constructed by converting a range of numbers to base-(n+1) and filtering these results.
			n			= len(arguments)
			dependencies= ['0']
			for dependencycounter in range((n+1)**n):
				dependency	= self.convertBaseN(dependencycounter, n+1)
				if self.isValidDependencyRelation(dependency):
					dependencies.append(dependency)

			config[file]['argumentsets']	= []

			for combination in range(combinations):

				for dependency in dependencies:
					divider	= 1
					score	= 0
					dependencyconfig= []

					for argnr in range(len(arguments)):

					 	if argnr==0:
					 		divider = len(answer[0]) - 1
					 		arrayindex	= combination % divider
					 	else:
					 		if argnr>1:
							 	divider	= (len(answer[argnr-1]) - 1) * divider
					 		arrayindex	= (combination / divider) % divider

						element	= answer[argnr][arrayindex]
						argname	= answer[argnr][len(answer[argnr])-1]

						score += element['score']

						# More conversion between datastructures to make it work (sigh, again :(....)
						# Should have thought of this before ... :(
						thisconfig					= {}
						thisconfig['dependent_on']	= []
						thisconfig['database']		= element['database']
						thisconfig['table']			= element['table']
						thisconfig['column']		= element['column']
						thisconfig['name']			= argname

						# dependency can be, for example, "124", which means that argument 1 is dependent on argument 2 and 4.
						if argnr==int(dependency[0])-1:

							condition		= []
							for digit in dependency[1:]:
								digit		= int(digit)-1
								thatargname	= answer[digit][len(answer[digit])-1]
								thisconfig['dependent_on'].append(thatargname)

						# make sure that configs with a dependency are listed last
						if len(thisconfig['dependent_on'])>0:
							dependencyconfig.append(thisconfig)
						else:
							dependencyconfig.insert(0, thisconfig)

					config[file]['argumentsets'].append(dependencyconfig)

# 		pprint.pprint(config)
		return config

	def findMappings(self, logfileentries, databasestructure, depth=2):
#		f	= file("outputfilefromlogfilepredictor.py", "a")
#		p	= pprint.PrettyPrinter(stream=f)
		for entry in logfileentries:
			mapping	= self.findMapping(entry, databasestructure)
#			self.createConfigEntries(mapping, entry['server'], databasestructure, depth)
#			p.pprint("\n\n------------------------------------------------------------------------------------\n\n")
#			p.pprint(mapping)
#		f.close()
#		mapping	= self.findMapping(logfileentries[0], databasestructure)
#		self.__writeRules(mapping, logfileentries[0]['server'], 2)

	def findCandidate(self, candidate, mapping, file, argument):
		arguments	= mapping[file][argument]
		for x in arguments:
			if 	x['column']==candidate['column'] and \
				x['database']==candidate['database'] and \
				x['table']==candidate['table']:
				return x

	def getTopN(self, argumentmapping, n):
		# get the top 'n' highest scoring arguments from the argumentmapping
		# answer may contain up to 2*n elements, if equally scoring arguments are present
		# if more than 2*n arguments qualify, then return the top 2*n
		answer	= []
		argumentmapping.sort(self.compareMappings)
		for arg in argumentmapping:
			if len(answer)<n:
				answer.append(arg)
			else:
				if answer[n-1]['score']==arg['score'] and len(answer)<2*n:
					answer.append(arg)

		return answer

	def getLikelyURLTemplates(self, mapping, servername, databasestructure, n):
		for file in mapping.keys():

			# (richly) reward candidates with the same name as this argument
			for argument in mapping[file].keys():
				for candidate in mapping[file][argument]:
					if candidate['column']==argument:
						candidate['score']+=100

			# for each of the different arguments in this file, reward candidates
			# in the top 'n+1' which originate from the same database and table
			#
			# if arguments have sources in the same table then these mappings (guesses) are
			# expected to have more chance to be correct
			for argument in mapping[file].keys():
				for other in mapping[file].keys():
					if id(argument)==id(other):
						continue
					argumentTop	= self.getTopN(mapping[file][argument], n+1)
					otherTop	= self.getTopN(mapping[file][other], n+1)
					for candidate in argumentTop:
						for othercandidate in otherTop:
							if candidate['database']==othercandidate['database'] and \
								candidate['table']==othercandidate['table'] and \
								candidate['column']!=othercandidate['column']:
									_candidate	= self.findCandidate(othercandidate, mapping, file, argument)
									if _candidate!=None:
										_candidate['score']	+= 25

# 				print "file %s, argument %s:" % (file, argument)
# 				pprint.pprint(self.getTopN(mapping[file][argument], n))
# 				print "-="*50

#		pprint.pprint(mapping)
		return self.createAllPossibleDependencies(mapping, servername, databasestructure, 2)

	def openDB(self, client=None, user=None, passwd=None, dsn=None, dbname=None, connstr=None, handle="database"):
		""" open database connection """
		if client==None and user==None and passwd==None and dsn==None and dbname==None and connstr==None:
			config	= configfile.getDBConfig(handle)
# 			print config
			self.db	= database.database(config['dbclient'], config['user'], \
						config['password'], config['dsn'], config['dbname'], \
						config['connectstring'])
		else:
			self.db	= database.database(client, user, passwd, dsn, dbname, connstr)

	def closeDB(self):
		""" close database connection """
		if (self.db!=None):
			self.db.closeDB()

if __name__=="__main__":
	cached	= 0

	if cached==0:
		l	= logfilePredictor()
#		l.openDB()
#		logfiles	= l.getGroupedLogfileEntries()
 		dbstructure	= l.getDatabaseStructure("odbc", "edward", "INSERT_PASSWORD_HERE", "Mysql", "website", None)
 		pprint.pprint(dbstructure)
		dbstructure	= l.getDatabaseStructure("odbc", None, None, None, None, 'DSN=Mysql;UID=edward;PWD=INSERT_PASSWORD_HERE;DATABASE=website')
		pprint.pprint(dbstructure)
# 		f	= file("outputfilefromlogfilepredictor.py", "w")
# 		p	= pprint.PrettyPrinter(stream=f)
# 		p.pprint(logfiles)
# 		p.pprint("-------------------------------------------------------------------------------------------------------------------------")
# 		p.pprint(dbstructure)
# 		f.close()
# 		l.findMappings(logfiles, dbstructure)
#		l.closeDB()
	else:
		mapping		= outputfilefromlogfilepredictorunderlinux.mapping # :)
		dbstructure	= outputfilefromlogfilepredictorunderlinux.dbstructure
		logfiles	= outputfilefromlogfilepredictorunderlinux.logfiles
		l			= logfilePredictor()
		l.getLikelyURLTemplates(mapping, logfiles[0]['server'], dbstructure, 2)
