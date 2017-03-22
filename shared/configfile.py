#### DIT IS SLECHTS EEN KOPIE!!!!

import string
import XMLConfig

def getDBConfig(section, mustexist):

	# Initialize defaults
	_defaults = {
		"database.dbclient":		None,
		"database.dbname":			None,
		"database.user":			None,
		"database.password":		None,
		"database.host":			"127.0.0.1",
		"database.dsn":				None,
		"database.connectstring":   None
		}

	# read configurationfile
	config	= XMLConfig.parse("druid.ini")

	# initialize some variables
	found	= 0
	answer	= {}

	# try to fetch all values as defined in _defaults
	for key in _defaults.keys():

		# get the 'variable' part
		parts		= string.split(key, ".")
		variable	= parts[1]

		# retrieve the associated value
		value		= XMLConfig.getVariable(section + "." + variable, config)

		# if it is not found then assume the default-value
		if value==None:
			value	= _defaults[key]
		else:
			found	= 1

		# store in answer
		answer[variable]= value

	# if the requested section must exist, and it is not found in the ini-file,
	# then create an empty answer
	if mustexist == 1:
		if found == 0:
			answer = {}

	# Done
	return answer

if __name__=="__main__":
	print getDBConfig("database1", 1)
