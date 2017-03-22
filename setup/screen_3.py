import 	os
import 	tkMessageBox
from	wizard import *
from	shared.database import database

class screen_3(wizard):

	def displaySetupText(self):
		# display main setup text for this page
		# provided so screen_4 can inherit all functionality but only override this one function
		master	= self.contentcanvas
		self.defaultHeader(master, "Database setup").grid(row=0, columnspan=20)

		text	= 	"WebIndex requires access to the database that is used for your web site. For security reasons, "
		text	+=	"two different database accounts are needed.\n\n"

		text	+=	"The first account is only used by this setup program. The second account is used in day-to-day operations."
		self.defaultText(master, text, pady=0).grid(row=1, columnspan=20, sticky=W)

		text	=	"Please specify an account with read access to the complete database, for use during this setup program:"
		self.defaultText(master, text, pady=0, font=defaultFont + bold).grid(row=2, columnspan=20, sticky=W)
#   		Label(master, text=text, padx=self.padding, pady=0, wraplength=master.winfo_reqwidth() - 2*self.padding,
# 		  		justify=LEFT, anchor=NW, font=defaultFont + bold, fg="black").grid(row=2, columnspan=20, sticky=W)

#		self.defaultText(master, text, pady=0, color='red').grid(row=2, columnspan=20, sticky=W)

	def setContents(self):
		master		= self.contentcanvas
		fieldwidth  = 40
		pady		= 1
		self.shownconfirmation = 0

		self.displaySetupText()

		###
		### dbclient-field (AAARGH! UGLY!!!)
		###
		self.defaultText(master, "Database type:", pady=pady).grid(row=3, column=0, sticky=W)

		# get possible databases from ../shared/database/DBClients/*.*
		parentpath		= string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep)
		files			= os.listdir(parentpath + os.sep + "shared" + os.sep + "database" + os.sep + "DBClients")
		DBs				= []
		for file in files:
			if string.lower(file[-2:])=='py' and file[:2]!="__":
				DBs.append(file[:-5]) # supported database is named filename minus "DB.py"

		DBs.append("odbc")
		self.dbclient 	= StringVar()
		self.dbclient.set(DBs[1]) # default value	# TODO: Change back to DBs[0]
		self.dbclientwidget	= apply(OptionMenu, (master, self.dbclient) + tuple(DBs))
		self.dbclientwidget.grid(row=3, column=1, sticky=W)
		self.dbclientwidget.configure(font=defaultFont)
		self.dbclientwidget.bind("<Configure>", self.dbclientevent)	# 'onChange' event
		self.dbclientwidget.bind("<Button-1>", self.dbclientevent)	# 'onChange' event

		###
		### other fields
		###
		self.defaultText(master, "Database name:", pady=pady).grid(row=4, column=0, sticky=W)
		self.dbname		= Entry(master, width=fieldwidth, font=defaultFont)
		self.dbname.grid(row=4, column=1, sticky=W)

		self.defaultText(master, "User name:", pady=pady).grid(row=5, column=0, sticky=W)
		self.user		= Entry(master, width=fieldwidth, font=defaultFont)
		self.user.grid(row=5, column=1, sticky=W)

		self.defaultText(master, "Password:", pady=pady).grid(row=6, column=0, sticky=W)
		self.password	= Entry(master, show='*', width=fieldwidth, font=defaultFont)
		self.password.grid(row=6, column=1, sticky=W)

		self.defaultText(master, "Host:", pady=pady).grid(row=7, column=0, sticky=W)
		self.host		= Entry(master, width=fieldwidth, font=defaultFont)
		self.host.insert(0, "localhost")
		self.host.grid(row=7, column=1, sticky=W)

		###
		### DSN-field
		###

		self.defaultText(master, "DSN:", pady=pady).grid(row=8, column=0, sticky=W)

		# try to retrieve the DSN - names on this computer by using an ordinary
		# hack (the dsn 'dBASE files' is mostly present on windows computers)

		# This stinks. Implement using the SQLBrowseConnect-function from ODBC instead. TODO: <- That :)
		if sys.platform[:3]=="win":
			try:
				tmpdb	= database.database('odbc', dsn='dBASE files')
			except:
				DSN		= [""]
			else:
				DSN		= tmpdb.getDataSources()
		else:
			DSN	= [""]

		self.dsn 		= StringVar()
		if len(DSN)>0:
			self.dsn.set(DSN[0]) # default value
		self.dsnwidget	= apply(OptionMenu, (master, self.dsn) + tuple(DSN))
		self.dsnwidget.configure(font=defaultFont)
		self.dsnwidget.grid(row=8, column=1, sticky=W)

		self.defaultText(master, "Connectstring:", pady=pady).grid(row=9, column=0, sticky=W)
		self.connstr	= Entry(master, width=fieldwidth, font=defaultFont, state=DISABLED)
		self.connstr.grid(row=9, column=1, sticky=W)
		self.defaultText(master, "*", pady=pady, padx=0, color="red").grid(row=9, column=2, sticky=W)

 		self.defaultText(master, "Optional (if available). Example of a valid connectstring: dsn=myDSN;database=sales;uid=webmaster;pwd=secret", pady=pady, padx=30).grid(row=10, column=0, columnspan=3, sticky=W)
 		self.defaultText(master, "*", pady=pady, color="red").grid(row=10, column=0, sticky=NW)

		self.dbclientevent(None)

	def setConfigData(self, configdata):
		self.dbclient.set(configdata['dbclient'])
		self.setField(self.dbname, configdata['dbname'])
		self.setField(self.user, configdata['user'])
		self.setField(self.password, configdata['password'])
		self.setField(self.host, configdata['host'])
		self.connstr.config(state=NORMAL, bg="#ffffff")		# these two fields must be enabled
		self.dsnwidget.config(state=NORMAL, bg="#ffffff")	# if you want to 'set' them
		self.dsn.set(configdata['dsn'])
		self.setField(self.connstr, configdata['connstr'])
		self.shownconfirmation=configdata['confirm']

		self.dbclientevent(None)

	def getConfigData(self):
		config={'dbclient': self.dbclient.get(),
				'dbname': 	self.dbname.get(),
				'user':		self.user.get(),
				'password':	self.password.get(),
				'host':		self.host.get(),
				'dsn':		self.dsn.get(),
				'connstr':	self.connstr.get()}
		for key in config.keys():
			if len(config[key])==0:
				config[key]=None

		config['confirm']= self.shownconfirmation;
		return config

	def dbclientevent(self, event):
		grey	= "#E0E0E0"
		if self.dbclient.get()=="odbc":
			self.connstr.config(state=NORMAL, bg="white")
			self.dsnwidget.config(state=NORMAL, bg=self.dbclientwidget.config()['background'][4])
		else:
			self.connstr.config(state=DISABLED, bg=grey)
			self.dsnwidget.config(state=DISABLED, bg=grey)

	def nextButtonPressed(self, step=1):
		config		= self.getConfigData()
		text		= self.defaultText(self.contentcanvas, "Trying to connect to database...", pady=0)
		text.grid(row=10, columnspan=4, sticky=W)

		try:
			self.db	= database.database(config['dbclient'], config['user'], \
					config['password'], config['dsn'], config['dbname'], \
					config['connstr'])
		except:
			text.grid_forget()
			tkMessageBox.showerror("Testing database connection", "Connecting to this database was unsuccessful.\nPlease review the parameters you provided and check your database-setup.")
		else:
			text.grid_forget()
			if self.shownconfirmation==0 and self.shownconfirmation==1: # effectively disabled
				tkMessageBox.showinfo("Testing database connection", "Successfully connected to the database!\nProceeding...")
			self.shownconfirmation = 1
			self.db.closeDB()
			wizard.nextButtonPressed(self, step)
