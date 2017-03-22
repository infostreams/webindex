import	os
import	re
import	string
import	types

class logfileParser:

	def __init__(self):
		regexp					= ".*((?:get|post).*? .*?) http/[0-9]\.[0-9].*"
		self.httprequestpattern	= re.compile(regexp, re.IGNORECASE)
#		print "Logfile: Linux!"

	def getHttpdConfLocations(self):
		# Find the httpd.conf file on this computer
		#
		# Not a very solid solution, since it depends on
		# 'locate' to perform correctly. Perhaps replace?
		#
		# code replicated in fileIndexation/linux.py
		pipe	= os.popen('locate httpd.conf | grep "httpd\.conf$" | grep -v "examples"')
		data	= pipe.read()
		pipe.close()
		if len(data)==0:
			data= "/etc/apache/httpd.conf"
		return data

	def getHttpdConfEntries(self, httpdconf, entry):
		# code replicated in fileIndexation/linux.py
		regexp	= "^[ \t]*(<"+entry+".*?>\n(?:.*\n)*?</"+entry+">)"
		pattern	= re.compile(regexp, re.MULTILINE | re.IGNORECASE)
		entries	= re.findall(pattern, httpdconf)	# Regular expressions b'vo!
		return	entries

	def getLogfileNames(self, configfilename=None):
		# a lot of code replicated in fileIndexation/linux.py

		### STEP 1

		# Get configfile location
		if configfilename==None:
			locations		= string.split(self.getHttpdConfLocations(), "\n")
			configfilename	= locations[0]

		# open configfile
		file		= open(configfilename)
		configfile	= file.read()
		file.close

		# Create an answer-list which will contain all locations of the logfiles
		answer		= []


    	### STEP 2


		# Retrieve this server's online ip-address
		# Do this by fetching the ip-addresses for each network-interface
		pipe		= os.popen('/sbin/ifconfig | grep inet | cut -d ":" -f 2 | cut -d " " -f 1')
		IPaddresses	= string.split(string.strip(pipe.read()), "\n")
		pipe.close()

		# filter out the 'local' ip-addresses
		for address in IPaddresses:
			parts	= string.split(address, ".")
			if (not ((parts[0]=="127") or (parts[0]=="192" and parts[1]=="168") or (parts[0]=="10"))):
				ip	 = address

		# The last non-local ip-address is considered the true online ip-address
		# do a DNS-lookup to find out which server-address belongs to this ip-address
		pipe		= os.popen("nslookup "+ip+" 2>&1 | grep name | grep -v nameserver | cut -d \"=\" -f 2")
		rawname		= string.strip(pipe.read())
		pipe.close()
		servername	= rawname[:-1]

		# fetch 'customlog'
		regexp		= "^[ \t]*CustomLog (.*?) .*?\n"
		pattern		= re.compile(regexp, re.MULTILINE | re.IGNORECASE)
		entries		= re.findall(pattern, configfile)
		logfile		= entries[0]

		# add the obtained information to the answer
		main			= {}
		main['server']	= servername
		main['log']		= logfile
		answer.append(main)


    	### STEP 3


		# fetch all 'virtualhost' xml-like entries from the configfile
		virtualhosts= self.getHttpdConfEntries(configfile, "virtualhost")

		# parse those entries
		for entry in virtualhosts:

			# fetch the servername from the <virtualhost> header
			lines			= string.split(string.strip(entry), "\n")
			lastpart		= string.split(string.strip(lines[0]))[1]
			server			= string.split(lastpart, ">")[0]

			# check if this <virtualhost> has a log file
			pattern			= re.compile("(?<=customlog ).*", re.MULTILINE | re.IGNORECASE)
			result			= re.search(pattern, entry)

            # at this point, code differs relatively significantly from
            # the code in fileIndexation/linux.py
			if result!=None:
				log			= result.group(0)

				# check to see if the obtained local directory is already present in the answer.
				# If this is not the case, then append the found directory to the answer
				alreadypresent	= "false"

				for item in answer:
					if item['log']==log:
						alreadypresent="true"

				if alreadypresent=="false":
					dir				= {}
					dir['server']	= server
					dir['log']		= log
					answer.append(dir)

    	### STEP 4

		return answer


	def openLogfile(self, logfilename):
		self.file	= open(logfilename)

	def closeLogfile(self):
		self.file.close()

	def extractHTTPRequest(self, entry):
		if entry != None:
			result	= re.match(self.httprequestpattern, entry)
			if result!=None:
				return	result.group(1)
			else:
				return	None
		else:
			return None

	def getNextEntry(self):
		entry	= self.file.readline()
		if len(entry) == 0:
			return None
		else:
			return entry

if __name__=="__main__":
	l		= logfileParser()
	logs	= l.getLogfileNames()
	for log in logs:
		l.openLogfile(log)
		entry	= l.getNextEntry()
		while entry!=None:
			print extractHTTPRequest(entry)
			entry	= l.getNextEntry()
		l.closeLogfile()
