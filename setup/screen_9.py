# Dynamic pages, advanced screen

# TODO before done:
#
# - Include likelihood information in dialog (dependencies-dialog + source-table)
#
# - No longer retrieve 'logfiles' info from cached file (setup linux-machine with X for this????)
#   -- Create dialog that:
#			a) displays progress (percentage + which table it is doing now)
#			b) consequently tests best guesses
# 			c) allows guesses that did not result in 100% correct URLs to be modified
#					-> direct them to screen_8 (currently named screen_7)
#
# - Write configuration
#
# - Write stub-file (+display location of stub/link to HTML-version)
#
# - Install files? (while we're at it)
#
# - Output-plugin configuration
#
# - Textfile and script configuration
#
# - Create help-texts

import 	tkFileDialog
import 	webindex
import	makeConfig
import	pprint

from	shared	import XMLConfig
from	engine 	import engine
from 	wizard 	import *

from 	screen_9_dialogs 		import *
from	shared.logfilePredictor import *

# For cached 'logfiles', 'dbstructure' and 'mapping' variables. Remove it.
#from 	outputfilefromlogfilepredictorunderlinux import *

class screen_9(wizard):

	#################################################################################################################
	### Functions inherited from 'wizard'
	###
	###
	#################################################################################################################
	#################################################################################################################

	def setContents(self):
		master				= self.contentcanvas
		self.currentargument= ""
		self.lastargument	= self.currentargument
		self.clicktext		= "Click to change"

# 		logfiledata			= logfiles
# 		databasestructure	= dbstructure
# 		self.contentmapping	= mapping

#		self.contentmapping	= self.__sortAndLimitContentMapping(contentmapping, 5)

		###	Draw upper half of page: Header, file + URL
		###
		##########################################################

		self.drawImage()
		self.defaultHeader(master, "Dynamic web pages").grid(row=0, columnspan=3)

		self.defaultText(master, text='File:', pady=0).grid(row=1, column=0, sticky=W)
		self.currentfilevar		= StringVar()
		Label(master, textvariable=self.currentfilevar, pady=0, padx=0, font=defaultFont).grid(row=1, column=1, padx=self.padding, sticky=W)

		self.defaultText(master, text='URL:', pady=0).grid(row=2, column=0, sticky=W)
		self.urltemplateentry	= Entry(master, font=defaultFont)
		self.urltemplateentry.grid(row=2, column=1, padx=self.padding, sticky=EW)

		self.defaultText(master, text='with POST:', pady=0).grid(row=3, column=0, sticky=W)
		self.posttemplateentry	= Entry(master, font=defaultFont)
		self.posttemplateentry.grid(row=3, column=1, padx=self.padding, sticky=EW)

		###	Draw upper half of page, part II: Buttons + line
		###
		##########################################################

		frame				= Frame(master, bd=0, relief=RAISED)

		prevnextframe		= Frame(frame, bd=0, relief=RAISED)
		button				= self.freesizeButton(prevnextframe, label='+', command=self.addfile, width=30, height=24)
		button.grid(row=0, column=0, sticky=E)
		button				= self.freesizeButton(prevnextframe, label='--', command=self.delfile, width=30, height=24)
		button.grid(row=0, column=1, sticky=E)
		button				= self.freesizeButton(prevnextframe, label='<<', command=self.previousfile, width=30, height=24)
		button.grid(row=0, column=2, sticky=E)
		button				= self.freesizeButton(prevnextframe, label='>>', command=self.nextfile, width=30, height=24)
		button.grid(row=0, column=3, sticky=W)
		prevnextframe.grid(row=0, column=0, padx=self.padding, sticky=W)

		testacceptframe		= Frame(frame, bd=0, relief=RAISED)
		test				= self.freesizeButton(testacceptframe, label='Test', command=self.test, width=60, height=24)
		test.grid(row=0, column=0, sticky=W)
		test				= self.freesizeButton(testacceptframe, label='Accept', command=self.test, width=60, height=24)
		test.grid(row=0, column=1, sticky=W)
		testacceptframe.grid(row=0, column=1, padx=70)

		frame.grid(row=4, column=1, columnspan=4, sticky=NW, padx=0, pady=5)

		# line
		line				= PhotoImage(data="R0lGODlhkAECAJEAAAAAAP///4CAgAAAACwAAAAAkAECAAACJpSPqcvtD6Oct" +
								"NqLs968+68F4kiW5omm6sq27gvH8kzX9o3n+m4XADs=") # hehehehe :)
		canvas 				= Canvas(master, width=200, height=4)
		canvas.image		= line
		item				= canvas.create_image(0, 4, anchor=NW, image=line)
		canvas.grid(row=5, column=0, columnspan=9, pady=5, padx=self.padding, sticky=EW)

		###	Draw lower half of page, part I: The left-hand frame
		###
		##########################################################

		# create + draw a listbox and a scrollbar
		frame				= Frame(master, bd=0, relief=RAISED)
		self.defaultText(frame, text='Arguments', font=smallheaderFont, pady=0).grid(row=0, column=0, columnspan=2, sticky=W)

		self.vscroll		= Scrollbar(frame, orient=VERTICAL, width=5)
		self.listbox		= Listbox(frame, selectmode=BROWSE, yscrollcommand=self.vscroll.set, highlightthickness=1,
								width=9, height=8, borderwidth=1, selectborderwidth=2, font=defaultFont + bold,
								background=self.vscroll.config()['background'][4])
		self.listbox.grid(row=1, column=0, padx=self.padding, sticky=EW)

		self.vscroll.config(command=self.listbox.yview)
		self.vscroll.grid(row=1, column=1, sticky=NS)

		buttonframe			= Frame(frame, bd=0, relief=RAISED)
		self.addargbutton	= self.freesizeButton(buttonframe, label="Add", width=30, height=18, command=self.addargument)
		self.addargbutton.grid(row=0, column=0)
		self.delargbutton	= self.freesizeButton(buttonframe, label="Del", width=30, height=18, command=self.delargument)
		self.delargbutton.grid(row=0, column=1)
		buttonframe.grid(row=2, column=0, columnspan=2, padx=0, pady=0)

		frame.grid(row=6, column=0, rowspan=2, sticky=W, pady=0)

#		self.localconfig	= self.__convertLogfileOutput(logfiledata) # TODO: Fix this
# 		self.currentfile	= self.localconfig.keys()[len(self.localconfig.keys())-1]
# 		self.urltemplate	= self.localconfig[self.currentfile]['urltemplate']
# 		self.posttemplate	= self.localconfig[self.currentfile]['posttemplate']
		self.localconfig	= {}
		self.currentfile	= None
		self.urltemplate	= None
		self.posttemplate	= None
		self.dbstructure	= None

		###	Draw lower half of page, part II: The right-hand frame
		###
		##########################################################

		self.argumentframe	= Frame(master, bd=0, relief=RAISED)

		# 'Name' field
		self.defaultText(self.argumentframe, text='Name:', padx=0, pady=0).grid(row=1, column=0, sticky=W)
		self.nameentry		= Entry(self.argumentframe, font=defaultFont)
		self.nameentry.grid(row=1, column=1, sticky=EW, columnspan=2)

		# 'Value' field with radiobuttons
		self.argumentsource	= StringVar()
		self.defaultText(self.argumentframe, "Value:", padx=0, pady=0).grid(row=2, column=0, sticky=W)

		self.argumentsourcebutton1	= Radiobutton(self.argumentframe, font=defaultFont,
								text="From database", variable=self.argumentsource,
								command=self.argumentsourcebutton1command, value="database")
		self.argumentsourcebutton1.grid(row=2, column=1, sticky=W, padx=0, pady=0)

		self.argumentsourcebutton2	= Radiobutton(self.argumentframe, font=defaultFont,
								text="Constant", variable=self.argumentsource,
								command=self.argumentsourcebutton2command, value="constant")
		self.argumentsourcebutton2.grid(row=3, column=1, sticky=W, padx=0, pady=0)

		# - in 'value' field: button for dialog to set database-source
#		self.dbstructure	= databasestructure # TODO: Fix
		self.dbsource		= StringVar()
		self.dbsource.set(self.clicktext) # default value

		self.dbsourcebutton	= self.freesizeButton(self.argumentframe, textvariable=self.dbsource, width=155, height=20, command=self.askDatabaseSource)
		self.dbsourcebutton.grid(row=2, column=2, sticky=EW, padx=0, pady=0)

		# - in 'value' field: entry field for 'constant' value
		self.constvalueentry	= Entry(self.argumentframe, font=defaultFont)
		self.constvalueentry.grid(row=3, column=2, sticky=EW, padx=0, pady=0)

		# --> default to first radiobutton
		self.argumentsource.set("database")
		self.argumentsourcebutton1command()

		# - 'location' field
		self.defaultText(self.argumentframe, "Location:", padx=0, pady=0).grid(row=4, column=0, sticky=W)

		self.method		= StringVar()
		frame			= Frame(self.argumentframe, bd=0, relief=RAISED)

		self.locationbutton1	= Radiobutton(frame, text="in URL", variable=self.method, command=self.locationbutton1command, value="get", font=defaultFont)
		self.locationbutton1.grid(row=0, column=1, sticky=W, padx=0, pady=0)

		self.locationbutton2	= Radiobutton(frame, text="in POST", variable=self.method, command=self.locationbutton2command, value="post", font=defaultFont)
		self.locationbutton2.grid(row=0, column=2, sticky=W, padx=0, pady=0)

		self.defaultText(frame, text="on place: ", padx=0, pady=0).grid(row=0, column=3, sticky=E)

		self.locationentry		= Entry(frame, width=4)
		self.locationentry.grid(row=0, column=4, sticky=E)

		frame.grid(row=4, column=1, columnspan=2, sticky=W, padx=0, pady=0)

		# --> default to 'in URL'
		self.locationbutton1.select()
		self.method.set("get")

		# Create 'if this argument changes... etc' text:
		# - create label with first line of 'if this argument changes' text
		x				= self.defaultText(self.argumentframe,
								text="\nIf this argument changes value, then these arguments", padx=0, pady=0)
		x.grid(row=5, column=0, sticky=W, columnspan=4)

		# - create Text widget
		self.dependenttext	= Text(self.argumentframe, font=defaultFont, width=40, height=2, wrap=WORD, borderwidth=0,
									background=x.config()['background'][4], cursor="arrow")

		# - add a 'bold' tag
		self.dependenttext.tag_add("bold", END)
		self.dependenttext.tag_configure("bold", font=defaultFont + bold)

		# - disable editing and place widget
		self.dependenttext.config(state=DISABLED)
		self.dependenttext.grid(row=6, column=0, sticky=W, columnspan=4, pady=0)

		# - place button under this text
		self.argumentsbuttontext	= StringVar()
		self.dependenciesbutton		= self.freesizeButton(self.argumentframe, command=self.askDependencies,
										textvariable=self.argumentsbuttontext, width=50, height=24)
		self.dependenciesbutton.grid(row=6, column=2, sticky=SE, pady=0, padx=self.padding)

		# Draw right frame
		self.argumentframe.grid(row=6, column=1, sticky=NW, pady=5)

		# cause all possible causes for change in focus to redraw the listbox
		# this will make sure the 'selection' is always visible (hack #1)
		self.contentcanvas.bind_all('<Button-1>', self.redrawLowerHalf)
 		self.contentcanvas.bind_all('<B1-Motion>', self.redrawLowerHalf)
 		self.contentcanvas.bind_all('<Key>', self.redrawLowerHalf, add=1)
 		self.contentcanvas.bind_all('<FocusIn>', self.redrawLowerHalf)
 		self.contentcanvas.bind_all('<FocusOut>', self.redrawLowerHalf)

		# these actions will save the possibly edited information and redraw the page
 		self.listbox.bind("<Button-1>", self.saveArgumentInfoAndRedraw)
 		self.listbox.bind("<Double-Button-1>", self.askDependencies)
 		self.listbox.bind("<B1-Motion>", self.saveArgumentInfoAndRedraw)
  		self.listbox.bind("<Up>", self.saveArgumentInfoAndRedraw)
  		self.listbox.bind("<Down>", self.saveArgumentInfoAndRedraw)

 		self.nameentry.bind('<Tab>', self.saveArgumentInfoAndRedraw, add=1)
 		self.nameentry.bind('<Shift-Tab>', self.saveArgumentInfoAndRedraw, add=1)
 		self.constvalueentry.bind('<Tab>', self.deriveURLandPOSTtemplates, add=1)
 		self.constvalueentry.bind('<Shift-Tab>', self.deriveURLandPOSTtemplates, add=1)
  		self.locationentry.bind('<Tab>', self.deriveURLandPOSTtemplates, add=1)
  		self.locationentry.bind('<Shift-Tab>', self.deriveURLandPOSTtemplates, add=1)

 		self.constvalueentry.bind("<Button-1>", self.argumentsourcebutton2command, add=1)

#		pprint.pprint(self.localconfig)

	def getConfigData(self):
		config	= {'currentfile':self.currentfile, 'config':self.localconfig, 'dbstructure':self.dbstructure}
		return config

	def setConfigData(self, configdata):
		self.localconfig	= configdata['config']
		self.dbstructure	= configdata['dbstructure']
		keys				= self.localconfig.keys()
		if len(keys)>0:
			self.currentfile	= configdata['currentfile']
			self.basetemplate	= self.localconfig[self.currentfile]['basetemplate']
			self.urltemplate	= self.localconfig[self.currentfile]['urltemplate']
			self.posttemplate	= self.localconfig[self.currentfile]['posttemplate']
			info				= self.localconfig[self.currentfile]['arguments']
			self.redrawUpperHalf()
			if len(info)>0:
				info			= info[0]

				self.setWidgetStates(NORMAL)
				self.updateListboxContents()

				self.method.set(info['method'])
				if info['method']=='get':
					self.locationbutton1command()
				else:
					self.locationbutton2command()

				self.argumentsource.set(info['argumentsource'])

				if info['argumentsource']=='database':
					self.dbsource.set(info['value'])
					self.argumentsourcebutton1command()
				else:
					self.setField(self.constvalueentry, info['value'])
					self.argumentsourcebutton2command()

				self.listbox.selection_set(0, 0)

			self.redrawArgumentFrame()

		self.redrawAll()

		self.root.update_idletasks()
		self.root.update()

	def previousButtonPressed(self):
		self.saveArgumentInfoAndRedraw()
		wizard.previousButtonPressed(self)

	def nextButtonPressed(self):
		self.saveArgumentInfoAndRedraw()
		wizard.nextButtonPressed(self)

	def cancelButtonPressed(self):
		self.saveArgumentInfoAndRedraw()
		wizard.cancelButtonPressed(self)

	#################################################################################################################
	### Functions invoked by pressing a button or radiobutton
	###
	###
	#################################################################################################################
	#################################################################################################################

	def askDatabaseSource(self):
		# popup a dialog where the user can indicate which column from which table to use
		thisargument		= self.getLocalConfig(self.currentfile, self.currentargument)

		try:
			top				= self.contentmapping[self.currentfile][self.currentargument][:5]
		except:
			top				= None
		newdatabasesource	= databaseSourceDialog(self.root, databasestructure=self.dbstructure[0]['structure'],
								argument=self.currentargument, currentvalue=thisargument['value'], top=top).result
		if newdatabasesource!=None:
			self.dbsource.set(newdatabasesource)
			thisargument['value']=newdatabasesource

		self.updateListboxContents()

	def askDependencies(self, event=None):
		# popup a dialog where the user can indicate which dependencies this argument has

		olddependencies		= self.getDependentArgs(self.currentargument)

		newdependencies		= dependenciesDialog(self.root, argument=self.currentargument,
									arguments=self.localconfig[self.currentfile]['arguments']).result
		if newdependencies!=None:

			# get current configuration for the argument whose dependencies we're editing
			thisargument	= self.getLocalConfig(self.currentfile, self.currentargument)

			# each argument from the dialog is processed
			for argument in newdependencies:

				# only the arguments whose checkboxes are ticked are treated
				if argument['dependent']==1:

					# get current configurations for the argument whose checkbox was ticked
					thatargument				= self.getLocalConfig(self.currentfile, argument['argument']['name'])

					# try to remove it from the list of dependencies for the argument we're editing
					# when all arguments are processed, we're left with a list of dependencies that need
					# to be removed
					try:
						olddependencies.remove(argument['argument']['name'])
					except:
						pass

					# put the data the user provided in the right place
					if argument['relationshiptype']=='direct':
						thatargument['dependent_on'].append(self.currentargument)
					else:
						thatargument['query']	= argument['customrelationship']

			# olddependencies now contains a list of arguments that are no longer dependent on this argument
			# we remove these dependencies
			for dumpedargument in olddependencies:
				thatargument	= self.getLocalConfig(self.currentfile, dumpedargument)
				try:
					thatargument['dependent_on'].remove(self.currentargument)
				except:
					# if the dumped argument is not in the 'dependent_on' list, then it is in the
					# 'query' field. The following approach is correct, but quite brutal. TODO: Think of something better?
					thatargument['query']=""

			self.redrawArgumentFrame(force=1)

	def addfile(self, *dummy):
		# add a dynamic webpage to the configuration
		new		= tkFileDialog.askopenfilename()
		if len(new)>0:
			if self.localconfig.has_key(new):
				tkMessageBox.showerror("Error", "You cannot add the same file twice.")
			else:
				self.localconfig[new]	= {'urltemplate': '', 'basetemplate':'', 'posttemplate': '', 'arguments':[]}

			self.currentfile		= new
			self.urltemplate		= "http://"
			self.setField(self.urltemplateentry, self.urltemplate)
			self.setField(self.posttemplateentry, "")
			self.setField(self.nameentry, "")
			self.redrawAll()

	def delfile(self, *dummy):
		# remove a dynamic webpage to the configuration
		self.saveArgumentInfoAndRedraw(dummy)
		if self.currentfile!=None:
			if tkMessageBox.askyesno("Confirm", "Do you really want to delete the dynamic webpage ''%s'' from the configuration?" % (self. currentfile, )):
				index						= self.localconfig.keys().index(self.currentfile)
				del self.localconfig[self.currentfile]
				configkeys					= self.localconfig.keys()
				if len(configkeys)>0:
					newindex				= min(index, len(configkeys)-1)
					self.currentfile		= configkeys[newindex]
					self.urltemplate		= self.localconfig[self.currentfile]['urltemplate']
					self.posttemplate		= self.localconfig[self.currentfile]['posttemplate']
				else:
					self.currentfile		= None
					self.urltemplate		= None
					self.setField(self.urltemplateentry, "")
					self.setField(self.posttemplateentry, "")
					self.setField(self.nameentry, "")
					self.setWidgetStates(DISABLED, include_argumentsbuttons=1)

				self.redrawAll()

	def previousfile(self, *dummy):
		self.saveArgumentInfoAndRedraw(dummy)
		keys					= self.localconfig.keys()
		this					= keys.index(self.currentfile)
		if this+1<len(keys):
			self.currentfile	= keys[this+1]
		self.urltemplate		= self.localconfig[self.currentfile]['urltemplate']
		self.posttemplate		= self.localconfig[self.currentfile]['posttemplate']
		self.redrawAll()

	def nextfile(self, *dummy):
		self.saveArgumentInfoAndRedraw(dummy)
		keys					= self.localconfig.keys()
		this					= keys.index(self.currentfile)
		if this-1>=0:
			self.currentfile	= keys[this-1]
		self.urltemplate		= self.localconfig[self.currentfile]['urltemplate']
		self.posttemplate		= self.localconfig[self.currentfile]['posttemplate']
		self.redrawAll()

	def addargument(self):
		self.saveArgumentInfoAndRedraw()
		args	= self.localconfig[self.currentfile]['arguments']
		entry	= {'name':'',
				 'method':'get',
				 'argumentsource':'database',
				 'value':'',
				 'location':'',
				 'dependent_on':[],
				 'query':''}

		# create new argument
		args.append(entry)

		# show widgets
		self.setWidgetStates(NORMAL)

		# update listbox
		self.updateListboxContents()

		# default to first radiobutton for 'value' field
		self.argumentsource.set("database")
		self.argumentsourcebutton1command()

		# default to first radiobutton for 'location' field
		self.method.set("get")
		self.locationbutton1command()

		# display "Click to change" text
		self.dbsource.set(self.clicktext)

        # select the newly added argument
		self.listbox.selection_set(END, END)

		# redraw
		self.redrawArgumentFrame()

		# and select the 'name' entryfield
		self.nameentry.focus()

	def delargument(self):
		# TODO: Delete references to the deleted argument (done?)
		try:
			selected	= int(self.listbox.curselection()[0]) - 1
		except:
			selected	= 0

		args		= self.localconfig[self.currentfile]['arguments']
		newargs		= []
		for arg in args:
			if arg['name'] != self.currentargument:
				if self.currentargument in arg['dependent_on']:
					arg['dependent_on'].remove(self.currentargument)
				newargs.append(arg)

		self.localconfig[self.currentfile]['arguments']	= newargs
		self.updateListboxContents()
		self.listbox.selection_set(selected, selected)
		if self.listbox.size()>0:
			self.redrawArgumentFrame()
		else:
			self.setWidgetStates(DISABLED)

	def test(self, *dummy):
		for arg in self.localconfig[self.currentfile]['arguments']:
			if len(arg['name'])==0 or len(arg['value'])==0:
				tkMessageBox.showerror("Error", "Each argument has to have both a name and a value. Arguments that do not \nsatisfy this condition are marked red.\n\nPlease correct this error.")
				return

		# replace potentially stored information about the dynamic pages from the main-config with
		# information from the form that might not have been placed in that config yet

 		config			= self.parent.config
		for item in config:
			if item['__pagenumber']==9:
				config.remove(item)
		config.append({'__pagenumber':9, 'config':self.getConfigData()})

		tmpconfigfile	= makeConfig.makeTestXMLConfig(config, self.currentfile)
		xmlconfig		= XMLConfig.parse(text=tmpconfigfile)

# 		print "screen_9.py: Have constructed"
# 		for line in tmpconfigfile:
# 			print line
# 
# 		print "screen_9.py: Testing"
# 		XMLConfig.printConfigtree(xmlconfig)

		try:
			urls		= engine.getCombinations(0, 20, xmlconfig, nostorage=1)
#			pprint.pprint(urls)
		except:
			errorstring, exception, traceback = sys.exc_info()
#			tkMessageBox.showerror("Error", "Error %s: %s" % (errorstring, traceback))
			return

		score			= urlTesterDialog(self.root, urls=urls).result

	def argumentsourcebutton1command(self, event=None):
		self.argumentsourcebutton1.select()
		self.dbsourcebutton.winfo_children()[0].config(state=NORMAL)
		self.constvalueentry.config(state=DISABLED)

	def argumentsourcebutton2command(self, event=None):
		self.argumentsourcebutton2.select()
		self.dbsourcebutton.winfo_children()[0].config(state=DISABLED)
		self.constvalueentry.config(state=NORMAL)

	def locationbutton1command(self, event=None):
		self.saveArgumentInfoAndRedraw()
		self.deriveURLandPOSTtemplates()

	def locationbutton2command(self, event=None):
		self.saveArgumentInfoAndRedraw()
		self.deriveURLandPOSTtemplates()

	#################################################################################################################
	### Functions related to re-drawing the screen
	###
	###
	#################################################################################################################
	#################################################################################################################

	def redrawAll(self):
		self.updateListboxContents()
		self.redrawUpperHalf()
		self.redrawLowerHalf()

	def updateListboxContents(self):

		# backup current selection
		try:
			selected	= int(self.listbox.curselection()[0])
		except:
			selected	= 0

		# delete all elements from listbox
		self.listbox.delete(0, END)

		# if there is a current file
		if self.currentfile!=None:

			# insert new elements into listbox
			config			= self.localconfig[self.currentfile]

			for arg in config['arguments']:
				self.listbox.insert(END, arg['name'])
				if len(arg['name'])>0 and len(arg['value'])>0:
					# set colors for entry that is OK
					selectbackground	= "#34DD34"
					foreground 			= "#000000"
				else:
					# set colors for entry that is not OK
					selectbackground	= "#FF1800"
					foreground			= selectbackground

				self.listbox.itemconfig(END, foreground=foreground, selectbackground=selectbackground)

			# restore selection
			self.listbox.activate(selected)

			# decide on scrollbar
			if self.listbox.size()<int(self.listbox.configure()['height'][4]):
				self.vscroll.grid_remove()
			else:
				self.vscroll.grid()

	def	redrawUpperHalf(self):
		master	= self.contentcanvas

		if self.currentfile!=None:
			self.currentfilevar.set(self.currentfile)
		else:
			self.currentfilevar.set("")

		self.urltemplateentry.delete(0, END)
		if self.urltemplate!=None:
			self.urltemplateentry.insert(0, self.urltemplate)

		self.posttemplateentry.delete(0, END)
		if self.posttemplate!=None:
			self.posttemplateentry.insert(0, self.posttemplate)

	def redrawLowerHalf(self, *dummy):
		# force a redraw of the listbox by re-setting the active selection to itself (hack #2)
		try:
			before	= self.listbox.curselection()
		except:
			return
		self.listbox.selection_set(ACTIVE, ACTIVE)
		after	= self.listbox.curselection()

		# The above code introduces 'duplicates' if the listbox is clicked (comment code below to see what I mean)
		# The following code repairs this. (hack #3)
		if len(after)>1:
			for selected in after:
				if not selected in before:
					number	= int(selected)
					self.listbox.selection_clear(number, number)

		# if the listbox is empty, then disable most of the widgets
		if self.listbox.size()==0:
			self.setWidgetStates(NORMAL, include_argumentsbuttons=1)
			self.setWidgetStates(DISABLED, include_argumentsbuttons=0)
		else:
			self.setWidgetStates(NORMAL, include_argumentsbuttons=1)

		# set the correct state for the 'add'/'modify' dependencies button
		if self.argumentsource.get()=="database":
			self.argumentsourcebutton1command()
		else:
			self.argumentsourcebutton2command()

		self.redrawArgumentFrame()

	def redrawArgumentFrame(self, force=0):
		# redraw the argumentframe (if necessary)

		# check to see if we have to redraw the contents of the argumentframe
		self.lastargument			= self.currentargument
		try:
			self.currentargument	= self.listbox.get(int(self.listbox.curselection()[0]))
		except:
			self.currentargument	= ""

		if (self.currentargument!=self.lastargument) or (force==1):

			## display dependencies
			#############################################

			# - allow writing to Text-object
			self.dependenttext.config(state=NORMAL)

			# - delete current text
	 		self.dependenttext.delete("1.0", END)

			# - get dependent arguments
			dependentargs		= self.getDependentArgs(self.currentargument)

			# - if there are none, adjust text accordingly
			if len(dependentargs)==0:
				dependentargs	= ['None.']
				self.argumentsbuttontext.set("Add")
			else:
				self.argumentsbuttontext.set("Modify")

			# - display text
			self.dependenttext.insert(END, "will also change value: " + string.join(dependentargs, ", "))
			self.dependenttext.tag_add("bold", "1.24", END)

			# - disallow writing to Text-object
			self.dependenttext.config(state=DISABLED)

			## display name, source and position
			#############################################

			self.nameentry.delete(0, END)
			self.nameentry.insert(0, self.currentargument)

			# find information about the current argument
			info	= self.getLocalConfig(self.currentfile, self.currentargument)

			if info!=None:
				self.argumentsource.set(info['argumentsource'])
				self.method.set(info['method'])
				self.setField(self.locationentry, info['location'])
				if info['argumentsource']=='database':
					self.constvalueentry.delete(0, END)
					self.argumentsourcebutton1command()
					if len(info['value'])!=0:
						self.dbsource.set(info['value'])
					else:
						self.dbsource.set(self.clicktext)
				else:
					self.argumentsourcebutton2command()
					self.constvalueentry.delete(0, END)
					self.constvalueentry.insert(0, info['value'])

	def setWidgetStates(self, state, include_argumentsbuttons=0):
		widgetlist	= [self.nameentry, self.argumentsourcebutton1, self.argumentsourcebutton2, self.constvalueentry]
		freesizebuttonlist = [self.dependenciesbutton, self.dbsourcebutton]
		if include_argumentsbuttons:
			freesizebuttonlist.append(self.addargbutton)
			freesizebuttonlist.append(self.delargbutton)

		for widget in widgetlist:
			widget.config(state=state)

		for button in freesizebuttonlist:
			for kid in button.winfo_children():
				kid.config(state=state)

	def deriveURLandPOSTtemplates(self, event=None):
		self.saveArgumentInfoAndRedraw()
		config				= self.localconfig[self.currentfile]
		self.urltemplate	= self.deriveURLtemplate(config['basetemplate'], config['arguments'], 'get')
		self.posttemplate	= self.deriveURLtemplate("", config['arguments'],  'post')
		self.saveArgumentInfoAndRedraw()
		self.redrawUpperHalf()

	#################################################################################################################
	### Functions related to saving and editing the information, and miscellaneous functions
	###
	###
	#################################################################################################################
	#################################################################################################################

	def saveArgumentInfoAndRedraw(self, *dummy):
		# save the data entered for name, value and place and redraw the page

		file				= self.localconfig[self.currentfile]
		file['urltemplate']	= self.urltemplateentry.get()
		file['posttemplate']= self.posttemplateentry.get()

		argument			= self.getLocalConfig(self.currentfile, self.currentargument)
		if argument!=None:
			argument['name']			= self.nameentry.get()
			argument['argumentsource']	= self.argumentsource.get()
			argument['method']			= self.method.get()
			argument['location']		= self.locationentry.get()

			if argument['argumentsource']=='database':
				argument['value']		= self.dbsource.get()

	       		# do not save the clicktext ("Click to change") as a database-source
				if argument['value'] == self.clicktext:
					argument['value']	= ""
			else:
				argument['value']		= self.constvalueentry.get()

		self.redrawArgumentFrame()
		self.updateListboxContents()

	def deriveURLtemplate(self, basetemplate, arguments, method):
		# derive an URL template on basis of the base-template and the provided arguments
		arglist		= []
		done		= []
		separator	= "&" # TODO: make user-specified?

		def makeURLpart(argument):
			if argument['argumentsource']=="database":
				return '%s={%s.value}' % (argument['name'], argument['name'])
			else:
				return '%s=%s' % (argument['name'], argument['value'])

		# locations range from 0..#arguments
		# try to find a match for each location
		for placenr in range(len(arguments)):
			found			= 0
			nolocationarg	= None

			# try to find an argument for this specific location
			for arg in arguments:
				if arg['method']!=method:
					continue

				if arg['name'] in done:
					continue

				if len(arg['location'])>0:

					# if found, then append to the 'arglist'
					if (int(arg['location'])==placenr):
						found	= 1
						arglist.append(makeURLpart(arg))
						done.append(arg['name'])
						break
				else:
					# if this argument has no preferred location, then possibly include it
					# in case no 'match' is found
					nolocationarg	= arg

			# if no match is found, then include an argument that has no preferred location
			if found==0 and nolocationarg!=None:
				arglist.append(makeURLpart(nolocationarg))
				done.append(nolocationarg['name'])

		# insert arguments that have not yet been inserted
		for arg in arguments:
			if arg['method']!=method:
				continue

			if arg['name'] in done:
				continue

			arglist.append(makeURLpart(arg))

		# create url
		return basetemplate + string.join(arglist, separator)

	def getLocalConfig(self, file, argument):
		# get current config for a specific file and argument
		if file!=None:
			arguments	 = self.localconfig[file]['arguments']
			config		 = None
			for arg in arguments:
				if arg['name'] == argument:
					config = arg
			return config
		else:
			return None

	def getDependentArgs(self, argname):
		# collect info on which arguments depend on this argument
		dependentargs		= []
		if self.currentfile!=None:
			for arg in self.localconfig[self.currentfile]['arguments']:
				include			= 0
				if argname in arg['dependent_on']:
					include		= 1
				if len(re.findall(argname, arg['query']))>0:
					include		= 1

				if include == 1:
					if not argname in dependentargs:
						dependentargs.append(arg['name'])

		return dependentargs

	def __convertLogfileOutput(self, logfileoutput):
		output	= {}

		# process data from each logfile
		for logfile in logfileoutput:

			# check entries in both 'get' and 'post' sections
			for method in logfile['entries'].keys():

				# process each file in this section
				for file in logfile['entries'][method].keys():

					# make sure there is a dictionary to convert to
					if not output.has_key(file):
						output[file]				= {}

					# setup a list of arguments for this file
					if not output[file].has_key('arguments'):
						output[file]['arguments']	= []

					if not output[file].has_key('basetemplate'):
						output[file]['basetemplate']	= 'http://' + logfile['server'] + file + "?"

					if not output[file].has_key('posttemplate'):
						output[file]['posttemplate']	= ''

					# finally, we're can begin converting the arguments. Do 'em all :)
					for argument in logfile['entries'][method][file].keys():

                    	# check if this argument is not yet present in the new datastructure
						exists	= 0
						for existingargument in output[file]['arguments']:
							if existingargument['name'] == argument:
								exists	= 1

						if exists == 0:
							entry					= {}
							entry['name']			= argument
							entry['method']			= method
							entry['location']		= ''
							entry['value']			= ''
							entry['dependent_on']	= []
							entry['query']			= ''
							entry['argumentsource']	= 'database'
							output[file]['arguments'].append(entry)

					output[file]['urltemplate']		= self.deriveURLtemplate(output[file]['basetemplate'], output[file]['arguments'], 'get')
					output[file]['posttemplate']	= self.deriveURLtemplate("", output[file]['arguments'], 'post')

		# we're done. Yippiayee.
		return output

# For dynamic-webpage-screen:
#
# try 2 ---------------------------------------------------------------------------
# file		index.php 		(file 1/12)
# URL			http://www.14hoog.net/{file}?{arguments}
#   		    [ Test ] -> example URLs
# 			text: 'arg3' and 'arg6' are not ok
# arguments
# +-white+
# |[arg1]| ^	Name:	   	   arg1
# | arg2 | |	Source:        table1.column1
# | arg3 |    If this value changes, then these also change: arg2, arg3, arg4 [modify]
# | arg4 |    Relationship:  () direct
# | arg5 |                   () custom: (help)
# | arg6 | |                     [_______________________]
# |      | v
# +------+
#  ^^^ [rood/groen]
# 			[ Accept ] [ Skip ]
# ---------------------------------------------------------------------------------
#
# try 1 ---------------------------------------------------------------------------
# base		http://www.14hoog.net/index.php?arg1=...&arg2=...&arg3=...
#
# 		source:			  if this value
# 					  changes, then these
# 					  values also change:
#
# arguments	arg1=<db1.table1.column2> [] arg2 [] arg3	[ advanced ]
# 		arg2=<db1.table1.column1> [] arg1 [] arg3	[ advanced ]
# 		arg3=<db1.table1.column3> [] arg1 [] arg2	[ advanced ]
#
# 		[ Test ]
#
# example URLs:	lijstje URLs	[valid] / [invalid]
#
# buttons: [ Accept ] [ Skip ]
# ---------------------------------------------------------------------------------

#          Nu: als arg1 verandert dan veranderen arg2 en arg3 ook
# 	in config: - de waarde van arg2 is afhankelijk van arg1 (en wel op deze wijze: ...)
# 			   - de waarde van arg3 is afhankelijk van arg1 (en wel op deze wijze: ...)
#
# 	als dn verandert, dan ook datumq (direct). datumq is dependent op dn, en wel op deze wijze: direct
