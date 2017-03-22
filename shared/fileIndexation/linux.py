import os
import string
import re

class fileIndexer:

	def __init__(self):
		pass

	def getHttpdConfLocations(self):
		# Find the httpd.conf file on this computer
		# code replicated in logfileAnalysis/linux.py
		pipe	= os.popen('locate httpd.conf | grep "httpd\.conf$" | grep -v "examples"')
		data	= pipe.read()
		pipe.close()
		if len(data)==0:
			data= "/etc/apache/httpd.conf"
		return data

	def getHttpdConfEntries(self, httpdconf, entry):
		# code replicated in logfileAnalysis/linux.py
		regexp	= "^[ \t]*(<"+entry+".*?>\n(?:.*\n)*?</"+entry+">)"
		pattern	= re.compile(regexp, re.MULTILINE | re.IGNORECASE)
 		entries	= re.findall(pattern, httpdconf)	# Regular expressions b'vo!
		return	entries

	def getPublicDirs(self, configfilename=None):

		# Todo: add support for httpd.conf-locations other than /etc/apache/
		if configfilename==None:
			logfilelocations	= string.split(self.getHttpdConfLocations(), "\n")
			configfilename		= locations[0]

		file		= open(configfilename)
		configfile	= file.read()
		file.close()

		# Create an answer-list which will contain all public dirs
		answer		= []


		#### STEP 1


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

		# fetch documentroot
		regexp			= "^[ \t]*documentroot (.*/.*)$"
		pattern			= re.compile(regexp, re.MULTILINE | re.IGNORECASE)
		entries			= re.findall(pattern, configfile)
		documentroot	= entries[0]

		# add the gathered information to the answer
		dir				= {}
		dir['public']	= servername
		dir['local']	= documentroot
		answer.append(dir)


		#### STEP 2


		# fetch all 'virtualhost' xml-like entries from the configfile
		dirs		= self.getHttpdConfEntries(configfile, "virtualhost")

		# parse those entries
		for entry in dirs:

			# fetch the servername from the <virtualhost> header
			lines			= string.split(string.strip(entry), "\n")
			lastpart		= string.split(string.strip(lines[0]))[1]
			public			= string.split(lastpart, ">")[0]

			pattern			= re.compile("(?<=documentroot ).*", re.MULTILINE | re.IGNORECASE)
			local			= re.search(pattern, entry).group(0)

			# check to see if the obtained local directory is already present in the answer.
			# If this is not the case, then append the found directory to the answer
			alreadypresent	= "false"
			for item in answer:
				if item['local']==local:
					alreadypresent="true"

			if alreadypresent=="false":
				dir				= {}
				dir['public']	= public
				dir['local']	= local
				answer.append(dir)


		#### STEP 3


		# check if users can setup a personal webpage
		modules	= self.getHttpdConfEntries(configfile, "IfModule")
		for module in modules:
			pattern		= re.compile("(?<=userdir ).*", re.MULTILINE | re.IGNORECASE)
			result		= re.findall(pattern, module)

			if result!=None and len(result)>0:
				userdir	= result[0]

 		# Yes, they can, so check the users' homedirs for personal webpages
 		if len(userdir)>0:
			homedir			= os.listdir("/home")
			for dir in homedir:
				fullpath		= "/home/"+dir+"/"+userdir
				if os.path.isdir(fullpath):
					result				= {}
					result['public']	= servername+"/~"+dir
					result['local']		= fullpath
					answer.append(result)


		#### STEP 4


		return answer

	def getNext(self):
		return None
