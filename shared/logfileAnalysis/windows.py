import _winreg
import os
import string
import IISLog, NCSALog

class logfileParser:

	def __init__(self, logfilename=None):
		if logfilename!=None:
			openLogfile(logfilename)

	def __getLogdirs(self):
		key		= _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\W3SVC\\Parameters\\")
		mainlog	= _winreg.QueryValueEx(key, "LogFileDirectory")[0]
		subdirs	= os.listdir(mainlog)
		dirs	= []
		for dir in subdirs:
			dirs.append(mainlog + "\\" + dir)
		return dirs

	def __getLogfiles(self, dir):
		files	= os.listdir(dir)
		logs	= []
		invalidLogEncountered	= 0

		for file in files:

			if string.lower(file[-3:])=="log" and \
			   string.lower(file[:2])!="ex":
				logs.append(dir + "\\" + file)

			if string.lower(file[:2])=="ex":
				invalidLogEncountered	= 1

# 		if invalidLogEncountered == 1:
# 			print "Warning: Invalid logfiles (of the 'W3C Extended Log File Format'-type) were encountered and ignored"

		return logs

	def getLogfileNames(self, configfilename=None):
		logfiles = []
		for dir in self.__getLogdirs():
			for log in self.__getLogfiles(dir):
				entry			= {}
				entry['server']	= None
				entry['log']	= log
				logfiles.append(entry)

		return logfiles

	def openLogfile(self, logfilename):
		# TODO: ODBC-logging toevoegen
		parts		= string.split(logfilename, "\\")
		filename	= string.lower(parts[len(parts) - 1])
		if filename[:2]=="in":
			self.data	= IISLog.IISLog(logfilename)
		if filename[:2]=="nc":
			self.data	= NCSALog.NCSALog(logfilename)
		if filename[:2]=="ex":
			raise TypeError, "The 'W3C Extended Log File Format', the format of the logfile you are trying to open, is unsuitable for this application"
#			print "The 'W3C Extended Log File Format', the format of the logfile you are trying to open, is unsuitable for this application"

	def closeLogfile(self):
		self.data.closeLogfile()

	def extractHTTPRequest(self, entry):
		return	self.data.extractHTTPRequest(entry)

	def getNextEntry(self):
		return	self.data.getNextEntry()


if __name__=="__main__":
	l	 = logfileParser()
	for dir in l.getLogdirs():
		for log in l.getLogfiles(dir):
			l.openLogfile(log)
			print "e sorted=", e
