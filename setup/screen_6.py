# Web server logs
import 	tkFileDialog
from 	wizard 					import *
from 	shared.logfileAnalysis	import analyzer

class screen_6(wizard):
	def setContents(self):
		master			= self.contentcanvas
		self.myconfig	= []
		self.defaultHeader(master, "Web server logs").grid(row=0, columnspan=3)

		text			=	"Next, it is necessary to specify where your web server logs are. The following "
		text			+=	"web server logs have been identified:\n"
		self.defaultText(master, text, pady=0).grid(row=1, sticky=W, columnspan=3)

		# create a listbox and two scrollbars
		frame			= Frame(master, borderwidth=0, relief=RAISED)

		vscroll			= Scrollbar(frame, orient=VERTICAL)
		hscroll			= Scrollbar(frame, orient=HORIZONTAL)
		self.listbox	= Listbox(frame, selectmode=BROWSE, yscrollcommand=vscroll.set, xscrollcommand=hscroll.set, height=10, width=50, borderwidth=2, font=defaultFont)
		vscroll.config(command=self.listbox.yview)
		hscroll.config(command=self.listbox.xview)

		# insert default logfiles in listbox
		self.defaults()

		# draw listbox + scrollbars
		self.listbox.grid(row=0, sticky=EW)
 		vscroll.grid(row=0, column=1, sticky=NS, padx=0)
 		hscroll.grid(row=1, column=0, columnspan=2, sticky=EW, pady=0)

		frame.grid(row=2, column=0, columnspan=10, sticky=EW, padx=self.padding)

		# place buttons
		frame	= Frame(master)
		buttonwidth = 12
		remove	= Button(frame, text="Delete", command=self.delete, width=buttonwidth, font=defaultFont)
		remove.grid(row=0, column=0, sticky=W)

		add		= Button(frame, text="Add", command=self.add, width=buttonwidth, font=defaultFont)
		add.grid(row=0, column=1, sticky=W, padx=self.padding)

		default	= Button(frame, text="Defaults", command=self.defaults, width=buttonwidth, font=defaultFont)
		default.grid(row=0, column=2, sticky=W)

		frame.grid(row=4, column=0, padx=self.padding, pady=self.padding)

	def add(self):
		# TODO: Insert sanity-check
		self.listbox.insert(0, tkFileDialog.askopenfilename())

	def defaults(self):
		# insert the default logfile-names in the listbox

		configfilename	= None
		thisconfig		= self.getConfigForPage(5)
		if thisconfig!=None:
			if len(thisconfig)>0:
				configfilename	= thisconfig['filename']

		# retrieve the logfile names
		f		= analyzer.logfileAnalyzer()	# brrrrrr :(
		logfiles= f.getLogfileNames(configfilename)
		self.myconfig = []

		# delete everything from the listbox
		self.listbox.delete(0, END)

		# process each logfile and set 'text' variable accordingly
		for log in logfiles:
			logfile	= log['log']
			if log['server'] == None:
				log['server'] = self.getConfigForPage(2)['hostname']

			text	= "%s (for server '%s')" % (logfile, log['server'])
			self.myconfig.append({'log':logfile, 'server':log['server']})

			# insert logfile-entry in listbox
			self.listbox.insert(END, text)

		# select first item in listbox
		self.listbox.select_set(0, 0)

	def delete(self):
		# remove the currently selected logfile from the listbox
		self.listbox.delete(ACTIVE)
		self.listbox.select_clear(0, END)
		self.listbox.select_set(0, 0)

	def setConfigData(self, configdata):
		if configdata!=None:
			self.listbox.delete(0, END)
			for item in configdata:
				text	= "%s (for server '%s')" % (item['log'], item['server'])
				self.listbox.insert(END, text)
			self.listbox.select_set(0, 0)

	def getConfigData(self):
		return self.myconfig

	def previousButtonPressed(self):
		if sys.platform[:3]=="win":
			wizard.previousButtonPressed(self, 2)
		else:
			wizard.previousButtonPressed(self, 1)
