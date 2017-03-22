# Dynamic web pages, autodetection
from 	wizard import *
from 	engine import engine
from	shared import logfilePredictor
from	shared import XMLConfig

import	tkSimpleDialog
import	tkMessageBox
import	testURL
import	shutil
import	copy
import	sys
import	urlparse
import	os.path

class screen_8(wizard):
	def setContents(self):
		master						= self.contentcanvas
		self.hasrunautodetection	= 0
		self.hasmadebackup			= 0
		self.screen9config			= None
		self.drawImage()
		self.defaultHeader(master, text="Dynamic web pages\n- autodetection -").grid(row=0)

		text	= "WebIndex will now try to detect which dynamic web pages (for example PHP or ASP files) exist " + \
					"on your server, which parameters are passed to these web pages and what these parameters mean.\n\n" + \
					"This may cause a significant stress on your web server. Also, it may pollute your web server logs." + \
					"This can lead to reduced autodetection results if you run this program again. If you want to " + \
					"prevent such things, it may be wise to backup your web server logs before proceeding."
		self.defaultText(master, text=text).grid(row=1, sticky=W)

		Button(master, text='Backup web server logs', command=self.backup, width=22, font=defaultFont).grid(row=2)

		self.defaultText(master, text="You may also directly start the auto-detection process. This will " + \
				"put significant stress on your web server.").grid(row=3, sticky=W)

		Button(master, text='Start auto-detection', command=self.autodetect, width=22, font=defaultFont).grid(row=4)

		self.getDatabaseAndLogfileInfo()

	def backup(self):
		thatconfig		= self.getConfigForPage(6)
		destination		= os.getcwd() + os.sep + "backup_webserverlogs"
		error			= 0
		errorinfo		= ""
		try:
			os.mkdir(destination)
		except:
			pass
		for file in thatconfig:
			try:
				shutil.copy2(file['log'], destination)
			except:
				type, errorinfo, traceback	= sys.exc_info( )
				error	= 1

		if error==0:
			tkMessageBox.showinfo("Backup", "Backup of webserver logs is complete and can be found in\n\n"+destination)
			self.hasmadebackup	= 1
		else:
			tkMessageBox.showerror("Error", "An error occurred while trying to backup the webserver logfiles:\n%s" % (errorinfo, ))

	def restorebackup(self):	# Not tested
		# restore the backup that was made
		thatconfig		= self.getConfigForPage(6)
		source			= os.getcwd() + os.sep + "backup_webserverlogs"
		error			= 1
		while error!=0:

			error		= 0
			for file in thatconfig:
				try:
					shutil.copy2(source + os.sep + os.path.basename(file['log']), os.path.dirname(file['log']))
				except:
					type, errorinfo, traceback	= sys.exc_info( )
					error	= 1

			if error==1:
				message		= "An error occurred while trying to restore the backups of the webserver logfiles:\n\n%s\n\nRetry?" % (errorinfo, )
				if tkMessageBox.askyesno("Error", message):
					error	= 1
				else:
					error	= 0
			else:
				tkMessageBox.showinfo("Success", "The webserver logfiles were successfully restored")

	def getDatabaseAndLogfileInfo(self):
		dbconfig			= self.getConfigForPage(3)
		l					= logfilePredictor.logfilePredictor()
		self.dbstructure	= l.getDatabaseStructure(dbconfig['dbclient'], dbconfig['user'], dbconfig['password'],
				dbconfig['dsn'], dbconfig['dbname'], dbconfig['connstr'])

		logfilenames		= self.getConfigForPage(6)
		hostname			= self.getConfigForPage(2)['hostname']
		self.logfiles		= l.getGroupedLogfileEntries(logfilenames, hostname)

#		pprint.pprint(self.logfiles)

	def autodetect(self):
		self.hasrunautodetection	= 1
		l			= logfilePredictor.logfilePredictor()
#		config		= outputfilefromlogfilepredictorunderlinux.parentconfig	# TODO: replace with self.parent.config
#		pprint.pprint(config)

		testresult	= autoTesterDialog(self.root, logfiles=self.logfiles, dbstructure=self.dbstructure).result

		self.screen9config	 = testresult

	def doNextButton(self):
		x			= self.parent
		self.parent.setpage(self.pagenumber + 1)
		if self.screen9config!=None:
			files	= self.screen9config.keys()
			config	= {'currentfile':files[len(files)-1], 'config':self.screen9config, 'dbstructure':self.dbstructure}
		else:
			config	= {'currentfile':None, 'config':{}, 'dbstructure':self.dbstructure}

		if id(self.page) != id(self):
			if self.page != None:
				self.page.__del__()
		x.page.setConfigData(config)

	def nextButtonPressed(self):
		if self.hasmadebackup == 1:
			title		= "Question"
			message		= "Do you want to restore the original web server logfiles that you backed up earlier?"
			if tkMessageBox.askyesno(title, message):
				self.restorebackup()
		if self.hasrunautodetection == 0:
			title		= "Question"
			message		= "You have not run the autodetection process. This means\nyou will have to " + \
							"configure your dynamic web pages manually.\n\nAre you sure you want to skip autodetection?"
			if tkMessageBox.askyesno(title, message):
				self.doNextButton()
			else:
				pass
		else:
			tkMessageBox.showinfo("Info", "The following screen allows you to tweak your configuration")
			self.doNextButton()

class autoTesterDialog(tkSimpleDialog.Dialog):
	def __init__(self, parent, title=None, logfiles=None, dbstructure=None):
		self.dbstructure= dbstructure
		self.data		= None
		self.hastested	= 0
		self.newtest	= 0

		# merge multiple logfiles into one structure, if possible
		# what a mess :(
		self.logfile	= {'entries':{'get':{}, 'post':{}}, 'log':None, 'server':logfiles[0]['server']}
		for log in logfiles:
			if log['server']==self.logfile['server']:
				for method in ['get', 'post']:
					source	= log['entries'][method]
					target	= self.logfile['entries'][method]

					for file in source:
						if target.has_key(file):
							for arg in source[file].keys():
								if target[file].has_key(arg):
									for value in source[file][arg]:
										if not value in target[file][arg]:
											target[file][arg]	+= (value, )
						else:
							target[file]	= source[file]

		tkSimpleDialog.Dialog.__init__(self, parent, title)

	def body(self, master):
		self.mymaster		= master

		text="The following files were identified as 'dynamic web pages'. Please select " + \
			"which files you want to enlist for autodetection.\n\nIf you enlist a file that updates or inserts " + \
			"data in the database, then your database may contain bogus-data after autodetection. "
#			"Files that are suspected to alter the contents of the database have been deselected by default."
		Label(master, text=text, font=defaultFont, wraplength=400, justify=LEFT).grid(row=0, columnspan=2, sticky=W)

		row					= 0
		startrow			= 1
		self.widgetsperrow	= 2
		self.check			= [None]
		self.checkvalue		= [StringVar()]
		self.successvalue	= [StringVar()]
		self.filename		= [None]
		for file in self.logfile['entries']['get'].keys():	# conveniently skipping files with only 'post' variables. TODO: Fix?
			if self.validFile(file):
				# save filename
				self.filename[row]	= file

				# show checkbox
				self.check[row]		= Checkbutton(master, text=file, variable=self.checkvalue[row], pady=0)
				self.check[row].bind("<Button-1>", self.checkboxcommand)
				self.check[row].bind("<space>", self.checkboxcommand)
				self.check[row].grid(row=startrow+row, column=0, sticky=W, pady=0)

 				# display success-percentage
 				Label(master, textvariable=self.successvalue[row], font=defaultFont, pady=0, justify=LEFT).grid(row=startrow+row, column=1, sticky=W, pady=0)

				# set defaults
				self.checkvalue[row].set(0)
 				self.successvalue[row].set("Not yet tested")

				# create new entries in widget-lists
				self.check.append(None)
				self.checkvalue.append(StringVar())
				self.successvalue.append(StringVar())
				self.filename.append(None)

				# increase rownr
				row	= row+1

		frame	= Frame(master)
		self.filevar		= StringVar()
		Label(frame, text='Processing file:', font=defaultFont).grid(row=0, column=0, sticky=W)
		Label(frame, textvariable=self.filevar, font=defaultFont).grid(row=0, column=1, sticky=W)

		self.descriptionvar	= StringVar()
 		Label(frame, text='Status:', font=defaultFont).grid(row=1, column=0, sticky=W)
		Label(frame, textvariable=self.descriptionvar, font=defaultFont).grid(row=1, column=1, sticky=W)

		self.progressvar	= StringVar()
		Label(frame, text='Detection progress:', font=defaultFont).grid(row=2, column=0, sticky=W)
		Label(frame, textvariable=self.progressvar, font=defaultFont).grid(row=2, column=1, sticky=W)
		frame.grid(row=startrow+row, columnspan=3, sticky=W)

	def buttonbox(self):
		box = Frame(self)

		self.startbuttonvar	= StringVar()
		self.startbuttonvar.set("Start test")
		w = Button(box, textvariable=self.startbuttonvar, width=10, command=self.autodetect, default=ACTIVE)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Close", width=10, command=self.ok)
		w.pack(side=LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def findWidgetRow(self, event):
		# find the row on which the clicked widget resides
		thiswidgetid	= event.widget.winfo_id()
		widgetnr		= 0
		for kid in self.mymaster.winfo_children():
			if kid.winfo_id()==thiswidgetid:
				break
			widgetnr	+= 1

		row	= int((widgetnr-1) / self.widgetsperrow) # -n because of the other widgets in the dialog
		return row

	def checkboxcommand(self, event):
		row				= self.findWidgetRow(event)
		checkboxvalue	= int(self.checkvalue[row].get())
		self.newtest	= 1
		self.startbuttonvar.set("Start test")

	def validFile(self, filename):
		if filename[:2]!="__":
			return 1
		else:
			return 0

	def toCondition(self, dependency):
		argname	= dependency
		return "({%s.table}.{%s.column}={%s.value} OR {%s.table}.{%s.column}=\"{%s.value}\")" % (argname, argname, argname, argname, argname, argname)

	def autodetect(self, event=None):
		# do some autodetection
		# my apologies for the inexcusable spaghetti-code :)

		if self.hastested==1:
			if self.newtest==1:
				if tkMessageBox.askyesno("Question", "Do you want to do a re-test?"):
					pass
				else:
					return self.ok()
			else:
				return self.ok()

		# create a logfilepredictor-instance
		l			= logfilePredictor.logfilePredictor()

		# only test the files that are selected by the user
		# therefore, make a copy of the logfile-datastructure containing
		# only information for the selected files
		logfilecopy	= copy.deepcopy(self.logfile)
		delcount	= 0
		for nr in range(0, len(self.filename)-1):
			file	= self.filename[nr]
			value	= int(self.checkvalue[nr].get())
 			if value==0:
 				for method in ['post', 'get']:
		 			if logfilecopy['entries'][method].has_key(file):
		 				del logfilecopy['entries'][method][file]
		 				delcount += 1

		# prompt messagebox and exit function if no files have been selected
		if logfilecopy['entries']['get']=={} and logfilecopy['entries']['post']=={}:
			tkMessageBox.showerror("Error", "You have to select at least one file in order to run the autodetection process")
			return

		# this motherfucker takes a long time:
		# try to find a mapping which maps each dynamic web page's arguments to columns in the database
#		self.mapping	= l.findMapping(logfilecopy, self.dbstructure, self.progressvar, self.descriptionvar, self.filevar, self)
		self.mapping	= l.findMapping(self.logfile, self.dbstructure, self.progressvar, self.descriptionvar, self.filevar, self)

		# create URL templates using that mapping
		self.data		= l.getLikelyURLTemplates(self.mapping, self.logfile['server'], self.dbstructure, 2)

		##
		## Do the actual testing
		##
		## This is done by using a dumb hack:
		##	- For each possible URL template, generate an XMLConfig-compatible configfile
		##	- Send this configfile to the combination-engine
		##	- Fetch the URLs this engine generates and test if they are valid
		##	- Keep track of the best scoring URL template. This is fed to the next setup-page
		##	  (the 'advanced' manual setup page) as the defaults for the various arguments
		##
		########################################################################################

		# setup the database-config
		self.dbconfig	= ["<database %s>" % (self.data['__database']['handle'], )]
		db				= self.data['__database']['config']
		for property in db.keys():
			if db[property]!=None:
				self.dbconfig.append("%s=%s" % (property, db[property]))
		self.dbconfig.append("</database>")

# 		print "autodetect: Creating databaseconfig:"
# 		print (self.dbconfig)

		self.newtest= 0
		errors		= "While trying to generate URLs, the following errors occurred: "
		for nr in range(0, len(self.filename)-1):
			file	= self.filename[nr]
			value	= int(self.checkvalue[nr].get())
			if value==1:
				self.successvalue[nr].set("Testing")
				errors	+= "\n\nIn file " + file + ":\n---------------------\n"
				self.data[file]['winner']			= {}
				self.data[file]['winner']['set']	= self.data[file]['argumentsets'][0]
				self.data[file]['winner']['score']	= 0
				argumentsetcounter					= 0
				for argumentset in self.data[file]['argumentsets']:

					argumentsetcounter				+= 1

					# convert the argumentset we're testing to a valid XMLConfig-like configuration
					config		= []
					config		+= self.dbconfig
					config		+= ["<dynamic>", "url="+self.data[file]['urltemplate']]
					for argument in argumentset:
						config	+= ["<argument %s>" % (argument['name'], )]
						config	+= ["name=" + argument['name']]
						config	+= ["source=%s.%s.%s" % (argument['database'], argument['table'], argument['column'])]
						if len(argument['dependent_on'])>0:
							config += ["condition=" + string.join(map(self.toCondition, argument['dependent_on']), " and ")]	# yihaa!

						config	+= ["</argument>"]
					config		+= ["</dynamic>"]

					# throwing around datastructures tralalala  :(
					xmlconfig	= XMLConfig.parse(text=config)
					
# 					print "screen_8.py: Have constructed:"
# 					for line in config:
# 						print line
# 
# 					print "screen_8.py: Testing the following..."
# 					XMLConfig.printConfigtree(xmlconfig)

					self.descriptionvar.set("Creating possible setup #%d (of %d)" % (argumentsetcounter, len(self.data[file]['argumentsets'])))
					self.update_idletasks()

					try:

						urls	= engine.getCombinations(0, 10, xmlconfig, nostorage=1)

# 						print "Generated urls:"
# 						pprint.pprint(urls)
# 						print "---"*50
					except:
						self.descriptionvar.set("Unsuccessful")
						self.update_idletasks()
						valid	= 0
						errorstring, exception, traceback = sys.exc_info()
						try:
							errors	+= "\n" + errorstring
						except:
							pass
					else:
						success	= 0
						for url in urls:
							urlstring	= url['url']
							if url.has_key('post'):
								urlstring	= "%s with POST=%s" % (urlstring, url['post'])
							if len(urlstring)>40:
								scheme		= urlparse.urlparse(urlstring)[0]
								urlstring	= scheme + "://..." + urlstring[-(40-len(scheme)-6):]
							self.descriptionvar.set("Testing "+urlstring)
							self.update_idletasks()
							self.update()

							timeout		= 5	# todo: Link to entry-field on form?
							if testURL.testURL(url, timeout):
								success	+= 1

						if len(urls)>0:
							score	= 100*success / len(urls)
						else:
							score	= 0

						if score>self.data[file]['winner']['score']:
							self.data[file]['winner']['score']	= score
							self.data[file]['winner']['set']	= argumentset

				self.descriptionvar.set("Done")

				winner	= self.data[file]['winner']
				if winner['score']!=0:
					self.successvalue[nr].set("Best bet has %d%% correct" % (winner['score'], ))
				else:
					self.successvalue[nr].set("No valid setup found")


		self.hastested	= 1
		self.startbuttonvar.set("Accept")

#		tkMessageBox.showerror("Error", errors) # unneccesary, but funny :)

	def convertArguments(self, arguments, fileconfig):
		# convert the argument storage container used within screen_8
		# to the format used in screen_9 (sigh)
		#
		# This must be (at least) the fourth or fifth roughly equivalent
		# datastructure I have 'invented' to store rougly the same data :((
		answer	= []
		for arg in arguments:
			entry					= {}
			entry['argumentsource']	= 'database'
			entry['value']			= arg['table'] + "." + arg['column']
			entry['dependent_on']	= arg['dependent_on']
			entry['location']		= ''
			if string.find(fileconfig['urltemplate'], '{' + arg['name'] + '.value}')!=-1:
				entry['method']		= 'get'
			else:
				entry['method']		= 'post'
			entry['name']			= arg['name']
			entry['query']			= ''
			answer.append(entry)

		return answer

	def apply(self):
		self.result	= {}
		if self.data!=None:
			for file in self.data.keys():
				if file[:2]!="__":
					entry					= {}
					entry['basetemplate']	= self.data[file]['basetemplate']
					entry['urltemplate']	= self.data[file]['urltemplate']
					entry['posttemplate']	= self.data[file]['posttemplate']

					if self.data[file].has_key('winner'):
						winner				= self.data[file]['winner']
						entry['score']		= winner['score']
						entry['arguments']	= self.convertArguments(winner['set'], entry)
					else:
						entry['score']		= 0
						entry['arguments']	= self.convertArguments(self.data[file]['argumentsets'][0], entry)

					self.result[file]		= entry
