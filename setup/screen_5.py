import 	os
import 	tkFileDialog
from 	wizard import *

class screen_5(wizard):
	# this screen is only shown non-Windows machines

	def getHttpdConfLocations(self):
		# Find the httpd.conf file on this computer
		# code replicated in logfileAnalysis/linux.py and fileIndexation/linux.py
		pipe	= os.popen('locate httpd.conf | grep "httpd\.conf$" | grep -v "examples"')
		data	= pipe.read()
		pipe.close()
		if len(data)==0:
			data= "/etc/apache/httpd.conf"
		return data

	def setContents(self):

		# display welcome text
		master	= self.contentcanvas
		self.hasApprovedOverwrite	= None
		self.defaultHeader(master, "Web server configuration").grid(row=0, columnspan=6)

		text	=	"WebIndex can use the information from your web server's configuration file.\n\n"
		text	+=	"Which Apache configuration file do you want to use?"

		self.defaultText(master, text, pady=0).grid(row=1, columnspan=6)

		text	=	"Configuration file: "
		self.defaultText(master, text).grid(row=2, column=0, sticky=W)

		self.entry	= Entry(master, width=30, font=defaultFont)
		self.setConfigData({'filename':self.getHttpdConfLocations()})
		self.entry.focus()
		self.entry.grid(row=2, column=1, sticky=W, padx=self.padding)

		self.filename	= ""

 		browse	= Button(master, text='...', command=self.chooseFile, width=1, height=1, font=defaultFont)
 		browse.grid(row=2, column=2, sticky=W)

	def chooseFile(self):
		new		= tkFileDialog.askopenfilename()
		if len(new)>0:
			self.entry.delete(0, END)
			self.entry.insert(0, new)

	def setConfigData(self, configdata):
		self.setField(self.entry, configdata['filename'])

	def getConfigData(self):
		if sys.platform[:3]!="win":
			return {'filename': self.entry.get()}
		else:
			return None

	def nextButtonPressed(self):
		validfilename	= 1

		self.filename	= self.entry.get()

		# check for existing file
		try:
			x	= file(self.filename, "r")
		except:
			x.close()
			tkMessageBox.showerror("Error", "The file you have chosen does not exist. Please try again.")
			validfilename	= 0
		else:
			x.close()
			validfilename	= 1

		# check for nothing entered:
		if len(self.filename)==0:
			tkMessageBox.showerror("No file", "You must enter a valid filename")
			validfilename	= 0

		# only proceed if we have a valid filename
		if validfilename == 1:
			wizard.nextButtonPressed(self)
