#display oai verb=listrecords caller=http://www.14hoog.net/~edward/afstuderen/index.php?output= metadataprefix=oai_dc resumptionToken=lr;oai_dc;300;1067520078
#from=2003-10-28T16:00:00Z to=2003-10-28T16:01:00Z

# Produced XML is validated with XMLSpy
# According to XMLSpy, all my XML is well-formed and valid :D

import output
import common
import time
import string
import urllib2
import XMLConfig
import pprint
import graphStorage # to convert the 'expires' variable from the configfile to seconds
from HTMLParser import HTMLParser

# offtopic note: urllib (#1) has some huge memoryleak when multiple (say, a hundred)
# URLs are opened and read in succession. It caused this outputmodule to use up to
# 22 megs of memory quite rapidly and consequently produce a MemoryError. urllib2
# does not seem to have this problem.

class oai(output.output):

	def __init__(self, config):
		# call superclass
		output.output.__init__(self, config)

		self.errors	= ['badVerb', 'badArgument', 'badResumptionToken',
			'cannotDisseminateFormat', 'idDoesNotExist', 'noRecordsMatch',
			'noMetadataFormats', 'noSetHierarchy']
		self.verbs = ['GetRecord', 'Identify', 'ListIdentifiers',
			'ListMetadataFormats', 'ListRecords', 'ListSets']
		self.metadataprefixes 	= ['oai_dc', 'minimal']
		self.nometadataprefixes	= ['minimal']
		self.postSeparationMark = "&&&&"
		self.metadataprefix		= "noprefix"

		expires					= XMLConfig.getUnnamedEntryVariable('cache', 0, 'expires', config)
		self.expiretime			= graphStorage.convertExpireTime(expires)
		self.admin				= XMLConfig.getUnnamedEntryVariable('oai', 0, 'adminemail', config)
		if self.admin == None:
			self.admin			= "unspecified@unspecified.com"
		self.repositoryname		= XMLConfig.getUnnamedEntryVariable('oai', 0, 'repositoryname', config)
		if self.repositoryname == None:
			self.repositoryname	= "A DRUID webpage OAI-PMH implementation. See http://druid.sourceforge.net/ for details."
		self.chunksize			= 25
		self.output				= ""
		self.records			= None
		self.recordnr			= 0

		# create self.<errorname> variables and set them to a zero-value
		for error in self.errors:
			code	= "self." + error + "= 0"
			exec code

		self.badVerbText			= "Value of the verb argument is not a legal OAI-PMH verb, the verb argument is missing, or the verb argument is repeated."
		self.badArgumentText		= "The request includes illegal arguments, is missing required arguments, includes a repeated argument, or values for arguments have an illegal syntax."
		self.badResumptionTokenText	= "The value of the resumptionToken argument is invalid or expired."
		self.cannotDisseminateFormatText = "The metadata format identified by the value given for the metadataPrefix argument is not supported by the item or by the repository."
		self.idDoesNotExistText		= "The value of the identifier argument is unknown or illegal in this repository."
		self.noRecordsMatchText		= "The combination of the values of the from, until, set and metadataPrefix arguments results in an empty list."
		self.noMetadataFormatsText	= "There are no metadata formats available for the specified item."
		self.noSetHierarchyText		= "This repository does not support sets."

	def __tag(self, tagname, value, attributes=None, level=0):

		attrstring	= ""
		if attributes!=None:
			for name in attributes.keys():
				if attributes[name]!=None:
					attrstring += " %s=\"%s\"" % (name, attributes[name])

		tabs	= ""
		for i in range(level):
			tabs	+= "	" # tab-character

		if value!=None:
			value	= string.replace(value, "&", "&amp;")

		return "%s<%s%s>%s</%s>" % (tabs, tagname, attrstring, value, tagname)

	def __UTC(self, timestamp):
		# reinventing the wheel, tralala
		return time.strftime("%Y-%m-%d", timestamp) + "T" + time.strftime("%H:%M:%S", timestamp) + "Z"

	def __UTCtoSeconds(self, UTC):
		# reinventing the wheel, tralala
		if UTC!=None:
			index	= string.find(UTC, "T")
			if index !=-1:
				# convert a YYYY-MM-DDTHH:MM:SSZ instance
				_date	= map(string.atoi, string.split(UTC[:index], "-"))
				_time	= map(string.atoi, string.split(UTC[index+1:-1], ":"))
			else:
				# convert a YYYY-MM-DD instance
				_date	= map(string.atoi, string.split(UTC, "-"))
				_time	= map(string.atoi, string.split("00:00:00", ":"))

			struct			= time.struct_time(\
								(_date[0], _date[1], _date[2], \
								 _time[0], _time[1], _time[2], 0, -1, -1))
			return 	int(time.mktime(struct))
		else:
			return	0

	def __createResumptionTokenTag(self):
		# create a resumption token
		if string.lower(self.verb) == "listrecords":
			prefix	= "lr"
		if string.lower(self.verb) == "listidentifiers":
			prefix	= "li"

		now				= int(time.time())
		resumptiontoken	= "%s--%s--%d--%d" % (prefix, self.metadataprefix, self.recordnr, now)
		# example resumptiontoken: lr;oai_dc;100;1067346243

		attribs	= {'cursor': self.recordnr, 'expirationDate':self.__UTC(time.localtime(now + self.expiretime))}

		return self.__tag('resumptionToken', resumptiontoken, attribs, 0) + "\n"

	def __parseResumptionToken(self, resumptiontoken):
		token			= string.split(resumptiontoken, "--")
		if len(token)==4:
			prefix			= token[0]
			metadataprefix	= token[1]
			recordnr		= int(token[2])
			timestamp		= int(token[3])

			if prefix=="li":
				self.verb	= "listidentifiers"
#				print "#2 self.verb=", self.verb
			elif prefix=="lr":
				self.verb	= "listrecords"
#				print "#2 self.verb=", self.verb
			else:
				self.badResumptionToken	= 1

			if (timestamp + self.expiretime < int(time.time())):
				self.badResumptionToken = 1

			if (metadataprefix not in self.metadataprefixes) and (metadataprefix!='noprefix'):
				self.badResumptionToken = 1

			if self.hasErrors():
				return

			self.metadataprefix	= metadataprefix
			answer	= {'from': recordnr, 'to': recordnr + self.chunksize}

			return answer
		else:
			self.badResumptionToken = 1
			answer	= {'from': -1, 'to': -1}

	def __createIdentifier(self, record):
		# TODO: Adjust __isValidIdentifier to support this new type
		id	= record['url']

		if record.has_key('post'):
			id	+=  self.postSeparationMark + record['post']

		return id

	def __parseIdentifier(self, id):
		parts	= string.split(id, self.postSeparationMark)
		answer	= {'url': parts[0]}
		if len(parts)>1:
			answer['post']	= parts[1]
		else:
			answer['post']	= None

		return answer

	def __isValidIdentifier(self, identifier):
		# if the identifier cannot be opened, it does not exist
		# note: it is very possible that the identifier points to a
		# webpage that is not hosted on this server, but _does_ exist
		# in that case, no error is raised (which _would_ be the correct behaviour)
		parts		= self.__parseIdentifier(identifier)

		answer		= 1
		try:
			test	= urllib2.urlopen(parts['url'], parts['post'])
		except:
			answer	= 0

		return	answer

	def __getMetadata(self, id):
		parts	= self.__parseIdentifier(id)

		try:
			file	= urllib2.urlopen(parts['url'], parts['post'])
#			file	= open("f:\\viewtt.html", "r")
		except:
			return None
		else:
			parser	= MyMetaTagParser()
			try:
				parser.feed(file.read())
				file.close()
				parser.close()
			except:
				pass
			return parser.getMetaTags()

	def __metadataTag(self, metadata, sourcetag, targettag, level):
		if metadata==None:
			return ""

		for meta in metadata:
			if meta['metatag'] == sourcetag:
				if meta['value']!=None:
					return self.__tag(targettag, meta['value'], level=level) + "\n"

		return "" # nothing found

	def __getMetadataTag(self, metadata, format):
		metadatatag	= ""
		if format=="oai_dc":
			metadatablock	= ""
			metadatablock	+= self.__metadataTag(metadata, 'title', 'dc:title', 2)
			metadatablock	+= self.__metadataTag(metadata, 'author', 'dc:creator', 2)
			metadatablock	+= self.__metadataTag(metadata, 'keywords', 'dc:subject', 2)
			metadatablock	+= self.__metadataTag(metadata, 'description', 'dc:description', 2)
			metadatablock	+= self.__metadataTag(metadata, 'publisher', 'dc:publisher', 2)
			metadatablock	+= self.__metadataTag(metadata, 'copyright', 'dc:rights', 2)
			metadatablock	+= self.__metadataTag(metadata, 'content-language', 'dc:language', 2)

			if len(metadatablock)>0:
				metadatatag = "	<metadata>\n"
				metadatatag	+= "		<oai_dc:dc\n" \
				"		 xmlns:oai_dc=\"http://www.openarchives.org/OAI/2.0/oai_dc/\"\n" \
				"		 xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n" \
				"		 xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" \
				"		 xsi:schemaLocation=\"http://www.openarchives.org/OAI/2.0/oai_dc/ \n" \
				"		 http://www.openarchives.org/OAI/2.0/oai_dc.xsd\">\n"
				metadatatag	+= metadatablock
				metadatatag	+= "		</oai_dc:dc>\n"
				metadatatag += "	</metadata>\n"

		if format=="minimal":
			metadatablock	= ""
			metadatablock	+= self.__metadataTag(metadata, 'get', 'min:get', 2)
			metadatablock	+= self.__metadataTag(metadata, 'post', 'min:post', 2)
			if len(metadatablock)>0:
				metadatatag = "	<metadata>\n"
				metadatatag	+= "		<minimal:min\n" \
				"		 xmlns:minimal=\"http://druid.sourceforge.net/\"\n" \
				"		 xmlns:min=\"http://14hoog.dyndns.org/~edward/afstuderen/min.xsd\"\n" \
				"		 xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n" \
				"		 xsi:schemaLocation=\"http://www.openarchives.org/OAI/2.0/oai_dc/ \n" \
				"		 http://www.openarchives.org/OAI/2.0/oai_dc.xsd\">\n"
				metadatatag	+= metadatablock
				metadatatag	+= "		</minimal:min>\n"
				metadatatag += "	</metadata>\n"

		return metadatatag

	def __getRecordTag(self, id=None, record=None, includemetadatatags=0, metadatatagsrequired=0):
		# print a <record></record>-tag
		# id and record are mutually exclusive

		if (id==None and record==None) or (id!=None and record!=None):
			return

		if record!=None:
			id	= self.__createIdentifier(record)

		recordtag	= "	<header>\n"
		recordtag	+= self.__tag("identifier", id, level=2) + "\n"
		recordtag	+= self.__tag("datestamp", self.__UTC(time.localtime()), level=2) + "\n"
		recordtag	+= "	</header>\n"
		if includemetadatatags == 1:
			if not self.metadataprefix in self.nometadataprefixes:
				metadata	= self.__getMetadata(id)
			else:
				data		= self.__parseIdentifier(id)
				metadata	= [{'metatag':'get', 'value':data['url']}, \
							   {'metatag':'post', 'value':data['post']}]

			metadatatag	= self.__getMetadataTag(metadata, self.metadataprefix)
			if len(metadatatag)>0:
				recordtag	= "<record>\n" + recordtag + metadatatag + "</record>\n"
			else:
				# Do not include records if no metadata can be obtained. Only do this
				# if the caller specified that inclusion of metadata is required
				if metadatatagsrequired == 1:
					return ""

		return recordtag

	def do_GetRecord(self):
		# follows protocol: yes
		identifier			= common.getHTTPValue("identifier", self.parameters)

		if not self.__isValidIdentifier(identifier):
			self.idDoesNotExist = 1

		self.metadataprefix	= common.getHTTPValue("metadataPrefix", self.parameters)

		if not self.metadataprefix in self.metadataprefixes:
			self.cannotDisseminateFormat = 1

		if self.metadataprefix == None or identifier == None:
			self.badArgument = 1

		recordtag	= self.__getRecordTag(id=identifier, includemetadatatags=1, metadatatagsrequired=1)

		if len(recordtag)>0:
			self.output	+= "<GetRecord>\n" + recordtag + "</GetRecord>\n"
		else:
			self.cannotDisseminateFormat = 1

	def do_Identify(self):
		# follows protocol: mostly
		# Default emailaddress [when none provided] is fake => this is done to ensure well-formed & valid XML
		self.output += "<Identify>\n"
		self.output += self.__tag('repositoryName', self.repositoryname, level=1) + "\n"
		self.output += self.__tag('baseURL', common.getHTTPValue('caller', self.parameters), level=1) + "\n"
		self.output += self.__tag('protocolVersion', "2.0", level=1) + "\n"
		self.output += self.__tag('adminEmail', self.admin, level=1) + "\n"
		self.output += self.__tag('earliestDatestamp', self.__UTC(time.localtime()), level=1) + "\n"
		self.output += self.__tag('deletedRecord', 'no', level=1) + "\n"
		self.output += self.__tag('granularity', 'YYYY-MM-DD', level=1) + "\n"
		self.output += "</Identify>\n"

	def __commonListRoutine(self, includemetadatatags, metadatatagsrequired):
		# this function does all the work for ListRecords and ListIdentifiers
		#
		# since their functionality is roughly similar one central function seemed logical :)
		if self.resumptiontoken == None:

			set		= common.getHTTPValue('set', self.parameters)
			if set!=None:
				self.noSetHierarchy	= 1

			if includemetadatatags==1:
				self.metadataprefix	= common.getHTTPValue('metadataPrefix', self.parameters)
				if self.metadataprefix == None:
					self.badArgument	= 1

				if self.metadataprefix not in self.metadataprefixes:
					self.cannotDisseminateFormat = 1

			_from	= self.__UTCtoSeconds(common.getHTTPValue("from", self.parameters))
			_to		= self.__UTCtoSeconds(common.getHTTPValue("to", self.parameters))

			if _from>_to or _from>int(time.time()):
				self.noRecordsMatch	= 1

			if self.hasErrors():
				return ""

		# At this point, we have a valid request
		output	= ""
		for record in self.records:
			x	= self.__getRecordTag(record=record, includemetadatatags=includemetadatatags, metadatatagsrequired=metadatatagsrequired)
			if len(x)>0:
				output	 		+= x
			self.recordnr	+= 1

		if len(self.records)>0:
			output	+= self.__createResumptionTokenTag()

		return output

	def do_ListIdentifiers(self):
		# follows protocol: mostly
		# resumptionToken argument should be exclusive; this is not enforced
		identifiertags	= self.__commonListRoutine(includemetadatatags=0, metadatatagsrequired=0)
		if len(identifiertags)==0:
			self.noRecordsMatch = 1
		else:
			self.output	+= "<ListIdentifiers>\n" + identifiertags + "</ListIdentifiers>\n"

	def do_ListMetadataFormats(self):
		# follows protocol: sort of
		# does nothing with the identifier, so figuring out which metadataformats
		# are supported for a specific element is impossible :)
		#
		# IF YOU ADD A METADATAPREFIX HERE, then be sure to also add an entry
		# to the self.metadataPrefixes-list defined in __init__ as well
		# and add some code to __getMetadataTag
		identifier 	= common.getHTTPValue('identifier', self.parameters)

		# check if the identifier is valid
		if identifier!=None:
			if not self.__isValidIdentifier(identifier):
	 			self.idDoesNotExist = 1
	 			return

		# this one is obligatory (darn! :))
		self.output	+= "<ListMetadataFormats>\n"
		self.output	+= "	<metadataFormat>\n"
		self.output	+= self.__tag('metadataPrefix', 'oai_dc', level=2) + "\n"
		self.output	+= self.__tag('schema', 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd', level=2) + "\n"
		self.output	+= self.__tag('metadataNamespace', 'http://www.openarchives.org/OAI/2.0/oai_dc/', level=2) + "\n"
		self.output	+= "	</metadataFormat>\n"
#		self.output	+= "</ListMetadataFormats>"

		self.output	+= "	<metadataFormat>\n"
		self.output	+= self.__tag('metadataPrefix', 'minimal', level=2) + "\n"
		self.output	+= self.__tag('schema', 'http://www.inventingsomethinghere.nl/merules.php', level=2) + "\n"
		self.output	+= self.__tag('metadataNamespace', 'http://www.inventingsomethinghere.nl/merules.php', level=2) + "\n"
		self.output	+= "	</metadataFormat>\n"
		self.output	+= "</ListMetadataFormats>"

	def do_ListRecords(self):
		# follows protocol: mostly
		# resumptionToken argument should be exclusive; this is not enforced
		records	= self.__commonListRoutine(includemetadatatags=1, metadatatagsrequired=1)
		if len(records)==0:
			self.noRecordsMatch = 1
		else:
			self.output	+= "<ListRecords>\n" + records + "</ListRecords>\n"

	def do_ListSets(self):
		# follows protocol: yes
		self.noSetHierarchy	= 1

	def parseRequest(self, parameters):

		# save parameters
		self.parameters		= parameters

		try:
			self.verb		= string.lower(string.strip(common.getHTTPValue("verb", parameters)))
		except:
			self.verb		= 'Nonexistent'

		# check of the provided verb is a legal one, and
		# execute the accompanying procedure
		try:
			index	= map(string.lower, self.verbs).index(self.verb) # generates a ValueError if self.verb not found
		except:
			self.badVerb	= 1

		self.resumptiontoken	= common.getHTTPValue("resumptionToken", parameters)
# 		print "self.resumptiontoken:"
# 		print self.resumptiontoken

		if self.resumptiontoken != None:
			self.badVerb		= 0
			self._range			= self.__parseResumptionToken(self.resumptiontoken)

			if not self.hasErrors():
				self.recordnr	= self._range['from']
			# the 'resumptiontoken' argument is exclusive, which means
			# no other arguments should be passed when the 'resumptiontoken'
			# argument is passed
			#
			# this is the right place to enforce that rule :)
		else:
			# select all records by using 'magic numbers'
			self._range			= {'from':0, 'to':self.chunksize, 'configfile':'druid.ini'}

#		print "Range:", _range
		return	self._range

	def displayErrors(self):
		for error in self.errors:
			if eval('self.' + error) == 1:
				print '<error code="%s">%s</error>' % (error, eval('self.' + error + 'Text'))

	def hasErrors(self):
		founderror	= 0
		for error in self.errors:
			if eval('self.' + error) == 1:
				founderror += 1

		return (founderror > 0)

	def displayHeader(self):
		# print XML tag
		print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

		# print OAI-PMH tag
		print "<OAI-PMH xmlns=\"http://www.openarchives.org/OAI/2.0/\""
		print " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""
		print " xsi:schemaLocation=\"http://www.openarchives.org/OAI/2.0/"
		print " http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd\">"

		# print responseDate
		print "<responseDate>" + self.__UTC(time.localtime()) + "</responseDate>"

	def displayRequestTag(self):
		# print request-summary
		baseurl 	= common.getHTTPValue("caller", self.parameters)
		verb		= common.getHTTPValue("verb", self.parameters)
		id			= common.getHTTPValue("identifier", self.parameters)
		prefix		= common.getHTTPValue("metadataPrefix", self.parameters)

		# if badVerb or badArgument: no attributes
		if not self.badVerb and not self.badArgument:
			# set 'verb' in correct case (e.g.: 'identify' -> 'Identify')
#			print "self.verb:",self.verb
			verb			= self.verbs[map(string.lower, self.verbs).index(self.verb)]
			attributes		= {'verb': verb, 'identifier': id, 'metadataPrefix': prefix}
			print self.__tag('request', baseurl, attributes)
		else:
			print self.__tag('request', baseurl)

	def displayFooter(self):
		print "</OAI-PMH>"

	def displayHTTPHeader(self):
		print "Content-Type: text/xml"

	def display(self, list):
		self.records	= list

		self.displayHeader()

		# execute the procedure belonging to this verb (eg.: do_Identify())
		if not self.hasErrors():
			if not self.badVerb:
				index		= map(string.lower, self.verbs).index(self.verb)
				exec "self.do_%s()" % (self.verbs[index], )

		self.displayRequestTag()

		# only display procedure-output if no errors occurred
		if self.hasErrors():
			self.displayErrors()
		else:
			print string.strip(self.output)

		# display footer
		self.displayFooter()


class MyMetaTagParser(HTMLParser):
	""" this class extracts metadata from a HTML file """

	def __init__(self):
		HTMLParser.__init__(self)
		self.titletag	= 0
		self.metatags	= []

	def handle_starttag(self, tag, attrs):
		if tag=='meta':
			entry	= {}
			for attr in attrs:
				if attr[0] == 'name':
					entry['metatag']	= string.lower(attr[1])
				if attr[0] == 'content':
					entry['value']		= attr[1]

			if entry.has_key('metatag') and entry.has_key('value'):
				self.metatags.append(entry)

		if tag=='title':
			self.titletag	= 1

	def handle_endtag(self, tag):
		self.titletag	= 0

	def handle_data(self, data):
		if self.titletag == 1:
			self.metatags.append({'metatag':'title', 'value': string.strip(data)})

	def getMetaTags(self):
		return self.metatags
