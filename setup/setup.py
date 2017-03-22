# efficient? nah. useful? yah.

from wizard import *

if __name__ == "__main__":
	wizard(1)

# setup:
#
# 1.	x	introduction
#
# 2. 	x	specify target configuration-file
# 
# 3a. 	x	specify database-configuration for use in day-to-day operation
# 3b. 	x	check database-access
# 
# 4a. 	x	specify temporary user + password for config-time full database access
# 4b. 	x	check validity of answer and potentially redo or skip
# 
# 5a. 	x	specify logfile-location (present guess)
# 5b. 	x?	check validity of answer and potentially redo or skip
# 
# 6. 	x	show and accept 'static' directories
# 		no	check validity of answer
#
# 7.	x	Collect info on database + logfiles and combine these; test assumed URLs and dependencies
#
# 8. 	x	per dynamic page, show variables + presumed dependencies
#
# 9.	x	Configure output plugins
#
# 10. 	x	write configfile
#
# 11. 	x	ask preferred scriptinglanguage (for stub-file) + master to install it
# 11b. 	no	skip is possible
#
# 12.	x	display HTML to paste or URL to visit
#
# 13. 	x	done
