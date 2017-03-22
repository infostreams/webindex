import string

class mysqlDB:

    def __init__(self, dbname=None, user=None, password=None):
        self.data = fileDB("d:\\prog\\python\\testdb.ddb")
        # print "MYSQL database code"

    def openDB(self, name):
        self.data.openDB(name)

    def closeDB(self):
        self.data.closeDB()

    def getColumnNames(self):
        return self.data.getColumnNames()
        
    def getTableNames(self):
    	return self.data.getTableNames()

    def getRecordCount(self):
        return self.data.getRecordCount()

    def getCurrentRecordNumber(self):
        return self.data.getRecordNumber()

    def getFirstRecord(self):
        return self.data.getFirstRecord()

    def getNextRecord(self):
        return self.data.getNextRecord()

    def getRecord(self, recordnumber):
        return self.data.getRecord(recordnumber)

    def issueSQLstatement(self, sql):
        # print ">>>mysqlDB.issueSQLstatement"
        return self.data.issueSQLstatement(sql)

# To implement:
#
# openDB(name)
# closeDB()
# getInternalParameters()
# setInternalParameters(internal)
# getColumnNames()
# getDataSources()
# getTableNames()
# getRecordCount()
# getCurrentRecordNumber()
# getFirstRecord()
# getNextRecord()
# getRecord(recordnumber)
# issueSQLstatement(sql)

