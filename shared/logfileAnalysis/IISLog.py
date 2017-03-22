import string

class IISLog:

	def __init__(self, filename):
#		print "IISLog"
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
				parts		= string.split(entry, ",")
				answer		= string.strip(parts[12]) + " " + string.strip(parts[13]) \
							   + "?" + string.strip(parts[14])
				return answer
		# else statement for both if's
		return None
