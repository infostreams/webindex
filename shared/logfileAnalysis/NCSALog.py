import string

class NCSALog:

	def __init__(self, filename):
#		print "NCSALog"
		self.openLogfile(filename)

	def openLogfile(self, filename):
		self.file	= open(filename, "r")

	def closeLogfile(self):
		self.file.close()

	def getNextEntry(self):
		entry	= self.file.readline()
		if len(entry) == 0:
			return None
		else:
			return entry

	def extractHTTPRequest(self, entry):
		if	entry != None:
			if len(entry)>0:
				parts		= string.split(string.strip(entry), "\"")
				if len(parts)>1:
					request		= parts[1]
					requestparts= string.split(request, " ")
					return string.strip(requestparts[0]) + " " + string.strip(requestparts[1])

		return None
