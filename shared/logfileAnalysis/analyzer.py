import sys
import string
import types

if sys.platform[:3]=="win":
	import windows
else:
	import linux

class logfileAnalyzer:

	def __init__(self):
		if sys.platform[:3]=="win":
			self.data		= windows.logfileParser()
		else:
			self.data		= linux.logfileParser()

	def __getitem__(self, index):
		item	= self.getNext()
		if item!=None:
			return item
		else:
			raise IndexError

	def getNext(self):
		pass

	def getLogfileNames(self, configfilename=None):
		# Return the names of potential logfiles
		return self.data.getLogfileNames(configfilename)

	def openLogfile(self, log):
		if type(log) is types.DictionaryType:
			self.data.openLogfile(log['log'])
		else:
			self.data.openLogfile(log)

	def closeLogfile(self):
		self.data.closeLogfile()

	def getLogfileEntries(self, logfile=None):
    	# If necessary, open the logfile
		if logfile!=None:
			self.openLogfile(logfile)

		# Retrieve all HTTP-request entries from the logfile
		# examples: GET /, GET /index.asp?arg1=25&arg2=Yes
		entries	= []
		stop	= "false"
		while stop == "false":
			entry	= self.data.getNextEntry()
			if entry != None:
				request	= self.data.extractHTTPRequest(entry)
				if request != None:
					if string.upper(request)[:3]=="GET" or \
					   string.upper(request)[:4]=="POST":
						entries.append(request)
			else:
				stop	= "true"

		# Sort these entries
		entries.sort()

		# Remove duplicates
		unique	= []
		for index in range(0, len(entries)-1):
			if entries[index]!=entries[index+1]:
				unique.append(entries[index])

		# Last item is always unique: either it is the end of a
		# list of identical entries [of which none have been added], or
		# it is a unique entry itself. Either way, it needs to be appended.
		if len(entries)>0:
			unique.append(entries[len(entries)-1])

		# Return the entries
		return 	unique

	def filterNonScriptEntries(self, entries):
		# Filter entries that are supposedly static
		# That is, keep entries with a '?' in its request
		# in the list
		filtered	= []
		for entry in entries:
			if string.find(entry, "?")>-1:
				filtered.append(entry)

		return filtered

	def __group(self, entries, prefix):
		# Group only entries starting with 'prefix' by filename, arguments

		# To clarify this somewhat cryptic description, please take a look
		# at the example provided below
		#
		# ----------------------------------------------------------------
		# Example input:
		# ==============
		# 	entries	=
		#	["GET /index.php?page=1&contentid=12",
		#	 "GET /index.php?page=2&contentid=12",
		#	 "POST /post.php?method=...",
		#	 "GET /contents.php?variable=value&variable2=value2..."]
		#	prefix = "GET"
		#
		# Example output:
		# ===============
		# { "/index.php": params_1,
		# 	"/content.php": params_2 }
		#
		# with params_1 =
		# { "page": (1, 2),
		#	"contentid": (12, ) }
		#
		# and params_2 =
		# { "variable": ("value", ),
		#   "variable2": ("value2", ) }
		# ----------------------------------------------------------------
		#
		# The syntax "(x, )" is Python's way of listing a single-element tuple
		#
		# Note that the POST-entry is not listed in the output.
		# This is intentional.


		# Initialize output-variable
		output	= {}

		# loop through all entries
		for entry in entries:

			# split the current entry in two parts: a HTTP-request-verb and
			# the rest of the request (e.g.: "GET" and "/index.php?page=1&contentid=12")
			part	= string.split(string.strip(entry))

			# if the prefix is correct, then proceed parsing
			if part[0]==prefix:

				# split the request in two parts
				# (e.g.: "/index.php" and "page=1&contentid=12")
				urlparts	= string.split(part[1], "?")

				# the file is the first part
				file		= urlparts[0]

				# if this file not yet has an entry in the output,
				# then create one
				if not output.has_key(file):
					output[file]	= {}

				# the parameters are the second part in the splitted request
				paramstring	= urlparts[1]

				# split the parameterstring in multiple parts
				# (e.g.: "page=1" and "contentid=12")
				params		= string.split(paramstring, "&")

				# loop through all these parameters
				for param in params:

					# split each parameter in two parts
					# (e.g.: "page" and "1")
					# store these values in 'variable' and 'value' respectively
					equationpart	= string.split(param, "=")
					variable		= equationpart[0]
					value			= equationpart[1]

					# if 'variable' is not yet listed in the output for this file,
					# then make sure it does
					if not output[file].has_key(variable):
						output[file][variable]	= ()

					# if 'value' is not yet listed as a valid value for this variable,
					# then make sure it is and add it to the output
					if not value in output[file][variable]:
						output[file][variable]	+= (value, )

		# done!
		return 	output

	def groupEntries(self, entries):
		# Group entries by HTTP-method, filename and arguments for simplified processing
		# Entries should be sorted, and preferably filtered

		get		= self.__group(entries, "GET")
		post 	= self.__group(entries, "POST")

		answer = {}
		answer['get']	= get
		answer['post']	= post

		return answer


if __name__=="__main__":
	f	= logfileAnalyzer()
	for logfile in f.getLogfileNames():
		entries		= f.getLogfileEntries(logfile)
		filtered	= f.filterNonScriptEntries(entries)
		grouped		= f.groupEntries(filtered)

		print "Logfile %s provided following information:" % (logfile, )
		for group in grouped.keys():
			for file in grouped[group].keys():
				print string.upper(group) + " " + file + ":", grouped[group][file]
