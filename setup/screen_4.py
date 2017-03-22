from wizard import *
from screen_3 import *
import sys

class screen_4(screen_3):
	# inherit all functionality from screen_3
	# only change the text that is displayed
	def displaySetupText(self):
		master	= self.contentcanvas
		self.defaultHeader(master, "Database setup page 2").grid(row=0, columnspan=20)

# 		text	= 	"WebIndex requires access to the database that is used for your web site. For security reasons, "
# 		text	+=	"two different database accounts are needed.\n\n"

#		text	+=	"The first account is only used by this setup program. The second account is used in day-to-day operations."

		text	= 	"The database account you have just specified will only be used by this setup program. " + \
			"The database account you can specify below will used in day-to-day operations."

		self.defaultText(master, text, pady=0).grid(row=1, columnspan=20)

		text	=	"Please specify a database account with read access to the relevant parts of the database, for use in day-to-day operations:"
		self.defaultText(master, text, pady=0, font=defaultFont + bold).grid(row=2, columnspan=20, sticky=W)
# 		Label(master, text=text, padx=self.padding, pady=0, wraplength=master.winfo_reqwidth() - 2*self.padding,
# 				justify=LEFT, anchor=NW, font=defaultFont + bold, fg="black").grid(row=2, columnspan=20, sticky=W)

	def nextButtonPressed(self):
		if sys.platform[:3]=="win":
			screen_3.nextButtonPressed(self, 2)
		else:
			screen_3.nextButtonPressed(self, 1)
