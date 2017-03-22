import 	string
import 	os
import 	types
import 	time
import 	pprint
import 	sys
from 	ODBC 	import winODBC

class database:
	"""
		Superclass skeleton for a higher level (non-textfile)
		implementation of database-like functionality.

		v0.1 (1/8/2003)   Edward Akerboom """

	def __init__(self, dbclient=None, user=None, password=None, dsn=None, dbname=None, connectstring=None):
		self.data		= self.__openDatabase(dbclient, user, password, dsn, dbname, connectstring)

	def __reconnect(self, dbclient=None, user=None, password=None, dsn=None, dbname=None, connectstring=None):
		self.closeDB()
		self.data		= self.__openDatabase(dbclient, user, password, dsn, dbname, connectstring)

	def __del__(self):
		self.closeDB()

	def __getitem__(self, index):
		if self.getCurrentRecordNumber()==0:
			item	= self.getFirstRecord()
		else:
			item	= self.getNextRecord()

		if item!=None and item!=-1:
			return item
		else:
			raise IndexError

	def __openDatabase(self, dbclient=None, user=None, password=None, dsn=None, dbname=None, connectstring=None):
		self.dbclient 	= dbclient
		self.user 		= user
		self.password 	= password
		self.dsn 		= dsn
		self.dbname 	= dbname
		self.connectstring = connectstring
		self.sql 		= None
		self.connected	= 0
		if dbclient == "odbc":
			return winODBC.winODBC(user, password, dsn, dbname, connectstring)
# 			platform	= sys.platform[:3]
# 			if platform == "win":
# 				return winODBC.winODBC(user, password, dsn, dbname, connectstring)
# 			else:
# 				return linODBC.linODBC(user, password, dsn, dbname, connectstring)
		else:
			if dbclient!=None:
				pythoncode  = "return " + dbclient + "DB(user, password, dsn, dbname, connectstring)"
				exec pythoncode

	def openDB(self, name):
		self.data.openDB(name)

	def closeDB(self):
		try:
			self.data.closeDB()
		except:
			pass

	def getConnectionParameters(self):
		answer					= {}
		answer['dbclient']		= self.dbclient
		answer['user']			= self.user
		answer['password']		= self.password
		answer['dsn']			= self.dsn
		answer['dbname']		= self.dbname
		answer['connectstring']	= self.connectstring
		return answer

	def setConnectionParameters(self, connparameters):
		# why? asymmetry is _bad_.
		if (type(connparameters) is types.DictType):
			self.__reconnect(connparameters['dbclient'], connparameters['user'], \
				connparameters['password'], connparameters['dsn'], \
				connparameters['dbname'], connparameters['connectstring'])

	def getRestoreData(self):
		""" retrieve the data needed to restore
			this connection at a later time """

		answer					= {}

		# store the connectionparameters (database-type, username, password....)
		answer['connection']	= self.getConnectionParameters()

		# get the connection's internal parameters
#		answer['internal']		= self.data.getInternalParameters()

		# store the connection's issued SQL-statement
		answer['sql']			= self.sql

		# store the recordnumber
		answer['recordnr']		= self.getCurrentRecordNumber()

		# set time-out for a connection to 120 seconds, unless specified otherwise
		if not answer['connection'].has_key('timeout'):
			answer['connection']['timeout']	= 120

		# store the current time
		answer['created']		= int(time.time())

		# Done
		return answer

	def restoreConnection(self, restoredata):
		""" restore a connection; provide the
			information obtained with getRestoreData. """

		# Per default, a connection times out in 120 seconds.
		# A functionally equivalent new connection is created
		# after that. The default timeout can be changed by
		# providing a 'timeout' entry in the dictionary-object
		# returned by the getInternalParameters()-call.

		# IMPORTANT NOTE:
		# Support for the time-out parameter is planned. At the
		# moment, however, the parameter is ignored. Due to
		# time-constraints and some unsuspected troubles I ran
		# into, this feature has been suspended - for now.

		try:
			internal	= restoredata['internal']
		except:
			internal	= None
		connection	= restoredata['connection']
# 		if restoredata['created'] + connection['timeout'] >= round(time.time()):
# 			print "This connection has not yet timed out... restoring"
# 			self.setConnectionParameters(connection)
# 			self.sql	= restoredata['sql']
# 			self.data.setInternalParameters(internal)
# 		else:
# 			print "This connection has timed out... creating new connection"

		# to test the time-out parameter, tab rest of function from here
		self.setConnectionParameters(connection)
		self.issueSQLstatement(restoredata['sql'])
		try:
#			print "Fetching first..."
#			print self.getFirstRecord()
			self.getFirstRecord()
		except:
			raise "Error: Connection could not be restored" # TODO: Is this necessary?
		else:
			for recordnr in range(restoredata['recordnr']-1):
#				print "fetching next (#%d)" % (recordnr, )
				x	= self.getNextRecord()

		return self

	def getColumnNames(self):
		return self.data.getColumnNames()

	def getDataSources(self):
		return self.data.getDataSources()

	def getTableNames(self):
		return self.data.getTableNames()

	def getRecordCount(self):
		return self.data.getRecordCount()

	def getCurrentRecordNumber(self):
		return self.data.getCurrentRecordNumber()

	def getFirstRecord(self):
		return self.data.getFirstRecord()

	def getNextRecord(self):
		return self.data.getNextRecord()

	def getRecord(self, recordnumber):
		return self.data.getRecord(recordnumber)

	def issueSQLstatement(self, sql, reusehandle=0):
		""" issue an SQL statement to the database.
		    A handle is returned that can be used to iterate the answers
			If reusehandle==1, then no new handles are created """

		# if this instance has not yet issued an SQL-statement to
		# the database, then the SQL-statement is bound to _this_ instance.
		# Else, a _new_ instance is made that handles the SQL-statement.
		#
		# This gives the class some desired behaviour:
		#
		# db = complexDB(dbname, user, password, "mysql")
		# result1 = db.issueSQLstatement("select * from table1")
		# result2 = db.issueSQLstatement("select * from table2")
		# etc.
		if ((self.sql == None) or (reusehandle==1)):
#			print "Issue SQL statement:", sql
			self.data.issueSQLstatement(sql)
			self.sql = sql
			return self

		else:
			handle  = database(self.dbclient, self.user, self.password, self.dsn, self.dbname)
			handle.issueSQLstatement(sql)
			return handle

if __name__=="__main__":
	db = database("odbc", "edward", "INSERT_PASSWORD_HERE", "Mysql", "website")
	print "\n\n>>>>>Issue sql-cmd 1"
#	print db.getTableNames()
#	print db.getTableNames()
	result=db.issueSQLstatement("select * from nieuws")
	print result.getFirstRecord()
	print result.getNextRecord()
	print result.getNextRecord()
	print result.getNextRecord()
	print result.getNextRecord()
	print result.getNextRecord()
	print result.getNextRecord()

	print "\n\n>>>>>Issue sql-cmd 2"
	db2 = database("odbc", "edward", "INSERT_PASSWORD_HERE", "Mysql", "website")
	result2=db2.issueSQLstatement("select * from tvgids")
	print result2.getRecord(5)
	print result.getRecord(6)
	print "Hierna gaat het stuk:"
	print result2.getRecord(6)

	print "\n\n>>>>>Issue sql-cmd 3"
	result3=db.issueSQLstatement("select * from nieuws")
	x	= result3.getRecordCount()
	print "Aantal records: ", x
	for i in range(x):
		print result3.getRecord(i)
	print result3.getRecord(5)
	print result2.getRecord(7)
	print result3.getRecord(6)
	print result.getRecord(7)
	a	= db.getConnectionParameters()
	print a
#	db.setConnectionParameters(a)
	db.closeDB()
	db2.closeDB()
	print "-"*50
	print "-"*50
	print "-"*50
	print "-"*50
	print "-"*50
	print "-"*50
