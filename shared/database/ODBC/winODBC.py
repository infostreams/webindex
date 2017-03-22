#
# Parts of this code were copied from Sam Rushing's odbc-implementation
# in the DynWin package
#
# Other parts are based on my own linuxODBCbasedAPI-module, which is based
# on code by OpenLink Software in their iODBC-software for Linux.
#
# The following code is considered pre-beta quality. It is only tested on my
# own computer, and even that doesn't work all the time. It is hardly debugged.
# This code is known to be quite sensitive to order of execution of the various
# functions. If your code gives strange errors, then swap the statements
# and see what happens :)
#
# Nevertheless, (c) 2003 by Edward Akerboom
#

from winODBCdeclarations import *
from ctypes import *
import types
import sys
import random

def clean(byte):
	byte = byte & 0xff
	if byte > 127:
		return - (256 - byte)
	else:
		return byte

class winODBC:

	def __init__(self, user=None, password=None, dsn=None, database=None, connectstring=None):
		random.seed()
		self.magicnumber	= int(random.randint(0,1000))
		self.printstatements= 0
		if self.printstatements==1: print "#%d: winODBC.init" % (self.magicnumber, )

		# TODO: Fix hard-coded odbc-version
		if sys.platform[:3]=="win":
			self.odbc		= windll.odbc32
		else:
			self.odbc		= cdll.LoadLibrary("/usr/lib/libiodbc.so.2")	# TODO: Make this more independent
		self.odbcversion	= 3.51
		self.connected		= 0
		self.recordnum		= 0
		self.errorvalue		= None
		self.sql			= None

		# odbc-handles
		self.environment	= c_int(0)
		self.connection		= c_int(0)
		self.statement		= c_int(0)

		if (user!=None) or (password!=None) or (dsn!=None) or (database!=None) or (connectstring!=None):
			self.openDB(user, password, dsn, database, connectstring)

	def printinfo(self, name=None):
		if (name!=None):
			print "INFORMATION ON INSTANCE '%s'" % (name, )
		else:
			print "INFORMATION ON THIS INSTANCE"
		print "****************************"
		print "connected			      %d" % (self.connected, )
		print "recordnum		         %d" % (self.recordnum, )
		print "environment %d" % (self.environment.value, )
		print "connection  %d" % (self.connection.value, )
		print "statement   %d" % (self.statement.value, )
		print "sql: '%s'" % (self.sql, )

	def error(self, odbcfunction, pythonfunction):
		if self.printstatements==1: print "#%d: winODBC.error" % (self.magicnumber, )

		sqlstate	= c_buffer(16)
		buffersize	= 1024
		buffer		= c_buffer(buffersize)
		errorstring	= ""

		while (clean(self.odbc.SQLError(self.environment, self.connection, self.statement, \
				byref(sqlstate), None, byref(buffer), buffersize, None)) \
				== SQL_SUCCESS):
				errorstring	= "%s\n%s, SQLSTATE=%s\n" % (errorstring, buffer.value, sqlstate.value)

		while (clean(self.odbc.SQLError(self.environment, self.connection, SQL_NULL_HSTMT, \
				byref(sqlstate), None, byref(buffer), buffersize, None)) \
				== SQL_SUCCESS):
				errorstring	= "%s\n%s, SQLSTATE=%s\n" % (errorstring, buffer.value, sqlstate.value)

		while (clean(self.odbc.SQLError(self.environment, SQL_NULL_HDBC, SQL_NULL_HSTMT, \
				byref(sqlstate), None, byref(buffer), buffersize, None)) \
				== SQL_SUCCESS):
				errorstring	= "%s\n%s, SQLSTATE=%s\n" % (errorstring, buffer.value, sqlstate.value)

		raise "\n%s: %s failed\nDetails: %s" % (pythonfunction, odbcfunction, errorstring)


	def openDB(self, user=None, password=None, dsn=None, database=None, connectstring=None):
		if self.printstatements==1: print "#%d: winODBC.openDB" % (self.magicnumber, )

# 		print "winODBC.openDB",
# 		print "connectstring = ", connectstring

		# create connect-string
		connect	= ""
		if (dsn!=None) and (len(dsn)>0):
			connect	+= "DSN=" + dsn + ";"
		if (user!=None) and (len(user)>0):
			connect	+= "UID=" + user + ";"
		if (password!=None) and (len(password)>0):
			connect	+= "PWD=" + password + ";"
		if (database!=None) and (len(database)>0):
			connect	+= "DATABASE=" + database
		if (connectstring!=None) and (len(connectstring)>0):
			connect	= connectstring

		if connect[-1]==";":
			connect	= connect[:-1]

		if self.odbcversion<3:
			# Allocate environment-handle
			if (clean(self.odbc.SQLAllocEnv(byref(self.environment)))!=SQL_SUCCESS):
				self.error("SQLAllocEnv", "openDB")

	    	# Allocate connection-handle
			if (clean(self.odbc.SQLAllocConnect(self.environment, byref(self.connection)))!=SQL_SUCCESS):
				self.error("SQLAllocConnect", "openDB")
		else:
			# Allocate environment-handle
			if (clean(self.odbc.SQLAllocHandle(SQL_HANDLE_ENV, None, byref(self.environment)))!=SQL_SUCCESS):
				self.error("SQLAllocHandle #1", "openDB")

	    	# Set some environment-options
			self.odbc.SQLSetEnvAttr(self.environment, SQL_ATTR_ODBC_VERSION, c_long(3), 0)

	    	# Allocate connection-handle
			if (clean(self.odbc.SQLAllocHandle(SQL_HANDLE_DBC, self.environment, byref(self.connection)))!=SQL_SUCCESS):
				self.error("SQLAllocHandle #2", "openDB")

		# initialize parameters for SQLDriverConnect-request
		buffersize			= 1024
		outbuffer			= c_buffer(buffersize)
		reportedbuffersize	= c_short(0)

		# Connect to driver
		status	= clean(self.odbc.SQLDriverConnect(self.connection, 0, connect, SQL_NTS, \
						byref(outbuffer), buffersize, byref(reportedbuffersize), SQL_DRIVER_COMPLETE))

		# Check how that worked out
		if ((status!=SQL_SUCCESS) and (status!=SQL_SUCCESS_WITH_INFO)):
#			print SQL_SUCCESS, SQL_SUCCESS_WITH_INFO, SQL_NO_DATA, SQL_ERROR, SQL_INVALID_HANDLE
#			print status
			self.error("SQLDriverConnect", "openDB")

		if self.odbcversion<3:
			if (clean(self.odbc.SQLAllocStmt(self.connection, byref(self.statement)) != SQL_SUCCESS)):
				self.error("SQLAllocStmt", "openDB")
		else:
			if (clean(self.odbc.SQLAllocHandle(SQL_HANDLE_STMT, self.connection, byref(self.statement))) != SQL_SUCCESS):
				self.error("SQLAllocHandle #3", "openDB")

		self.connected 	= 1
		self.recordnum	= 0

		return	 None

	def closeDB(self):
		if self.printstatements==1: print "#%d: winODBC.closeDB" % (self.magicnumber, )

		if self.connected == 1:
#			print "winODBC: closeDB, freeing handles"

			if self.odbcversion<3:
				if (self.statement!=c_int(0)):
					self.odbc.SQLFreeStmt(self.statement, SQL_DROP)

				if (self.connected!=0):
					self.odbc.SQLDisconnect(self.connection)

				if (self.connection!=c_int(0)):
					self.odbc.SQLFreeConnect(self.connection)

				if (self.environment!=c_int(0)):
					self.odbc.SQLFreeEnv(self.environment)
			else:

				if (self.statement!=c_int(0)):
					self.odbc.SQLCloseCursor(self.statement)
					self.odbc.SQLFreeHandle(SQL_HANDLE_STMT, self.statement)

				if (self.connected!=0):
					self.odbc.SQLDisconnect(self.connection)

				if (self.connection!=c_int(0)):
					self.odbc.SQLFreeHandle(SQL_HANDLE_DBC, self.connection)

				if (self.environment!=c_int(0)):
					self.odbc.SQLFreeHandle(SQL_HANDLE_ENV, self.environment)

			self.recordnum = 0

		return	None

	def getInternalParameters(self):
		if self.printstatements==1: print "#%d: winODBC.getInternalParameters" % (self.magicnumber, )
		answer	= {}
		answer['statement']		= self.statement
		answer['environment']   = self.environment
		answer['connection']	= self.connection
		answer['sql']			= self.sql
		answer['connected']		= self.connected
		answer['recordnum']		= self.recordnum
		# Meer?

		# pack the answer in a string-format,
		# so the actual de-packing always occurs in
		# setInternalParameters. This procedure handles
		# the c_int type of self.statement etc. correctly.
		return "%s" % (answer, )

	def setInternalParameters(self, internalparameters):
		if self.printstatements==1: print "#%d: winODBC.setInternalParameters" % (self.magicnumber, )
		if internalparameters!=None:
			values		= eval(internalparameters)
			if type(values)==types.DictType:
				self.statement		= values['statement']
				self.environment	= values['environment']
				self.connection		= values['connection']
				self.sql			= values['sql']
				self.connected		= values['connected']
				self.recordnum		= values['recordnum']

	def getTableNames(self):
		if self.printstatements==1: print "#%d: winODBC.getTableNames" % (self.magicnumber, )
		status	= clean(self.odbc.SQLTables(self.statement, None, 0, None, 0, None, 0, None, 0))

		if (status != SQL_SUCCESS):
			self.error("SQLTables", "getTableNames status=%d" % (status, ))

		answer	= []

		record	= self.getFirstRecord()

		while (record != self.errorvalue):
			record	= self.getNextRecord()
#			print record
			if (record!= self.errorvalue):
				if (record[3]=="TABLE"):
					answer.append(record[2])

		return answer

	def getDataSources(self):
		if self.printstatements==1: print "#%d: winODBC.getDataSources" % (self.magicnumber, )
		answer			= []

		buffersize		= 256
		datasourcename	= c_buffer(buffersize)
		description		= c_buffer(buffersize)
		totalbytes		= c_short(0)
		totalbytes2		= c_short(0)

		status	= clean(self.odbc.SQLDataSources(self.environment, SQL_FETCH_FIRST, byref(datasourcename), \
					buffersize, byref(totalbytes), byref(description), buffersize, byref(totalbytes2)))

		if (status!=SQL_SUCCESS):
			self.error("SQLDataSources", "getDataSources")
		else:
			answer.append(datasourcename.value)
			while (clean(self.odbc.SQLDataSources(self.environment, SQL_FETCH_NEXT, byref(datasourcename), \
					buffersize, byref(totalbytes), byref(description), buffersize, byref(totalbytes2))) \
					!=SQL_NO_DATA):
				answer.append(datasourcename.value)
# 				print datasourcename.value
# 				print description.value

		return	answer

	def getColumnCount(self):
		if self.printstatements==1: print "#%d: winODBC.getColumnCount" % (self.magicnumber, )
		numcols	= c_short(0)
# 		print self.odbc
# 		print self.statement
# 		print byref(numcols)
# 		print self.odbc.SQLNumResultCols(self.statement, byref(numcols))
		status	= clean(self.odbc.SQLNumResultCols(self.statement, byref(numcols)))
#		print status
		if (status != SQL_SUCCESS):
			self.error("SQLNumResultCols", "getColumnCount")
		return numcols.value

	def issueSQLstatement(self, sqlquery):
		if self.printstatements==1: print "#%d: winODBC.issueSQLstatement" % (self.magicnumber, )
		self.odbc.SQLFreeStmt(self.statement, SQL_CLOSE)

		if (clean(self.odbc.SQLPrepare (self.statement, sqlquery, SQL_NTS)) != SQL_SUCCESS):
			self.error("SQLPrepare", "issueSQLstatement")

		status	 =	clean(self.odbc.SQLExecute(self.statement))
#		print "%d, %d, %d, %d, %d, %d, %d" % (SQL_SUCCESS, SQL_SUCCESS_WITH_INFO, SQL_NEED_DATA, SQL_STILL_EXECUTING, SQL_ERROR, SQL_NO_DATA, SQL_INVALID_HANDLE)
#		status	= clean(self.odbc.SQLExecDirect(self.statement, sqlquery, len(sqlquery)))
		if (status != SQL_SUCCESS):
			self.error("SQLExecute", "issueSQLstatement, status=%d" % (status, ))

		self.sql		= sqlquery
		self.recordnum	= 0

	def getRecordCount(self):
		if self.printstatements==1: print "#%d: winODBC.getRecordCount" % (self.magicnumber, )
#		thisRecordnum	= self.recordnum
		recordCount		= 0
		record			= 0

		if (self.getFirstRecord()!=self.errorvalue):
			while (record!=self.errorvalue):
				record		= self.getNextRecord()
				recordCount	+= 1

		self.getFirstRecord()

		return	recordCount

	def getColumnNames(self):
		if self.printstatements==1: print "#%d: winODBC.getColumnNames" % (self.magicnumber, )

		numcols		= self.getColumnCount()
		answer		= []

		buffersize	= 50
		colname		= c_buffer(buffersize)
		coltype		= c_short(0)
		colprecision= c_ulong(0)
		colscale	= c_short(0)
		colnullable	= c_short(0)

		for colnum in range(1, numcols+1):
			status	= clean(self.odbc.SQLDescribeCol ( \
								self.statement, colnum, byref(colname), \
								buffersize, None, byref(coltype), byref(colprecision), \
								byref(colscale), byref(colnullable)))
			if (status != SQL_SUCCESS):
				self.error("SQLDescribeCol", "getColumNames %d" % (status, ))
			else:
				answer.append(colname.value)

		return	answer

	def getNextRecord(self):
		if self.printstatements==1: print "#%d: winODBC.getNextRecord" % (self.magicnumber, )
#		self.printinfo()
#		print "winodbc.getNextRecord"
		numcols	= self.getColumnCount()
#		numcols = 2 # TODO: Remove this line

		status	= clean(self.odbc.SQLFetch(self.statement))

		if (status == SQL_NO_DATA_FOUND):
			return self.errorvalue

		if (status != SQL_SUCCESS):
# 			print "status:",status
# 			print "errorcodes:", SQL_SUCCESS, SQL_SUCCESS_WITH_INFO, SQL_NO_DATA, SQL_STILL_EXECUTING, SQL_ERROR, SQL_INVALID_HANDLE
			self.error("SQLFetch", "getNextRecord")

		answer		= []
		buffersize  = 1024
		fetchbuffer	= c_buffer(buffersize)
		colindicator= c_long(0)

		for colnum in range(1, numcols+1):
			fetchbuffer	= c_buffer(buffersize)
			if (clean(self.odbc.SQLGetData(self.statement, colnum, SQL_CHAR, \
					byref(fetchbuffer), buffersize, byref(colindicator))) \
					!= SQL_SUCCESS):
				self.odbc.SQLFreeStmt(self.statement, SQL_CLOSE)
				self.error("SQLGetData", "getNextRecord")

			if (colindicator==SQL_NULL_DATA):
				fetchbuffer	= c_buffer("NULL", buffersize)

			answer.append(fetchbuffer.value)

		self.recordnum	+= 1

		return	answer

	def getFirstRecord(self):
		if self.printstatements==1: print "#%d: winODBC.getFirstRecord" % (self.magicnumber, )
		if (self.recordnum==0):
			return self.getNextRecord()
		else:
			if ((self.sql!=None) and (len(self.sql)>0)):
				status	= self.issueSQLstatement(self.sql)

			return self.getNextRecord()

	def getRecord(self, n):
		if self.printstatements==1: print "#%d: winODBC.getRecord" % (self.magicnumber, )
		result	= self.getFirstRecord()

		if (result==self.errorvalue):
			return self.errorvalue

		for i in range(n):
			result	= self.getNextRecord()
			if (result==self.errorvalue):
				return self.errorvalue

		return	result

	def getCurrentRecordNumber(self):
		if self.printstatements==1: print "#%d: winODBC.getCurrentRecordNumber" % (self.magicnumber, )
		return	self.recordnum

if __name__=="__main__":
	x = winODBC()
	y = winODBC()
	z = winODBC()
	a = winODBC()
	b = winODBC()
	c = winODBC()
	d = winODBC()
	e = winODBC()

	x.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	x.issueSQLstatement("select * from nieuws")
	x.issueSQLstatement("select * from nieuws")
	x
	y.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	y.issueSQLstatement("select * from nieuws")
	a.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	a.issueSQLstatement("select * from nieuws")
	b.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	b.issueSQLstatement("select * from nieuws")
	c.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	c.issueSQLstatement("select * from nieuws")
	d.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	d.issueSQLstatement("select * from nieuws")
	e.openDB(connectstring="dsn=Mysql;uid=edward;pwd=INSERT_PASSWORD_HERE;database=website")
	e.issueSQLstatement("select * from nieuws")

	print x.getDataSources()

	y = winODBC()
	y.openDB(None, None, None, None, "DSN=Mysql4;UID=edward;PWD=INSERT_PASSWORD_HERE;DATABASE=website")
	print y.getTableNames()

	print x.getTableNames()

	x.issueSQLstatement("Select * from nieuws")
#	x.issueSQLstatement("SELECT * FROM inetlog WHERE ClientHost='ja'")


	print x.getColumnNames()

	record	= x.getFirstRecord()

	while (record!=x.errorvalue):
		print record
		record	= x.getNextRecord()

	details	= x.getInternalParameters()
	print details
#	x.restoreConnection(details)
	print "getNext enzo:"
	print x.getFirstRecord()

	x.closeDB()
	y.closeDB()
