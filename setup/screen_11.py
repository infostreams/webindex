from	wizard import *
import	pprint
import	makeConfig
import	os
import	string
import	tkFileDialog
import	tkMessageBox
import	urlparse

class screen_11(wizard):
	def setContents(self):
		master	= self.contentcanvas

		self.writeConfig()

		self.drawImage()
		self.defaultHeader(master, "Web interface").grid(row=0, columnspan=3)

		self.defaultText(master, "Setup has written the configuration file.", pady=0).grid(row=1, columnspan=3, sticky=W)

		self.defaultText(master, "Web interface", font=smallheaderFont).grid(row=2, columnspan=3, sticky=W)

		self.defaultText(master, "Where do you want to install the web interface?", pady=0).grid(row=3, columnspan=3, sticky=W)

		staticdirs	= self.getConfigForPage(7)
		if len(staticdirs)>0:
			local	= staticdirs[0][0]
			public	= staticdirs[0][1]
		else:
			local	= os.getcwd()
			public	= "http://" + self.getConfigForPage(2)['hostname'] + "/..........."

		self.local	= StringVar()
		self.local.set(local)
		self.defaultText(master, "Directory:", pady=0).grid(row=4, column=0, sticky=W)
		Entry(master, textvariable=self.local).grid(row=4, column=1, sticky=EW)
		self.freesizeButton(master, label="...", height=20, width=20, command=self.askDirectory).grid(row=4, column=2, sticky=W)

		self.public	= StringVar()
		self.public.set(public)
		self.defaultText(master, "Available as:", pady=0).grid(row=5, column=0, sticky=W)
		Entry(master, textvariable=self.public).grid(row=5, column=1, sticky=EW)

		self.defaultText(master, "\nWhich scripting language do you want to use?", pady=0).grid(row=6, columnspan=3, sticky=W)
		self.defaultText(master, "Scripting language", pady=0).grid(row=7, column=0, sticky=W)

		frame	= Frame(master, width	= master.winfo_reqwidth())
		scriptlanguages = ['php']	# TODO: Make dynamic, add more
		self.scriptlanguage	= StringVar()
		self.scriptlanguage.set(scriptlanguages[0])
		self.scriptwidget	= apply(OptionMenu, (frame, self.scriptlanguage) + tuple(scriptlanguages))
		self.scriptwidget.grid(row=0, column=0, sticky=W)
		self.defaultText(frame, text="*", color="#FF0000", pady=0, padx=0).grid(row=0, column=1, sticky=NW)
		frame.grid(row=7, column=1, sticky=W)

		frame	= Frame(master, width	= master.winfo_reqwidth())
		text	= "\n\n       If the scripting language of your preference is not available in the list above, then you might " + \
				"consider porting the required code. This is relatively straight-forward and not too much work. " + \
				"The PHP-version is less than 50 lines. Please contact me via   webindex.sourceforge.net   if you " + \
				"are considering this."
		self.defaultText(frame, text=text, pady=0).grid(row=0, sticky=NW)
		self.defaultText(frame, text="\n\n*", color="#FF0000", pady=0).grid(row=0, sticky=NW)
		frame.grid(row=8, column=0, columnspan=3, sticky=NW)

	def askDirectory(self):
		dir = tkFileDialog.askdirectory()
		if dir!="" and dir!=None:
			self.local.set(dir)

	def writeConfig(self):
		config		= self.parent.config
		xmlconfig	= makeConfig.makeFinalXMLConfig(config)
		filename	= makeConfig.getPage(config, 2)['filename']
		file		= open(filename, "w")
		for line in xmlconfig:
			file.write(line+"\n")
		file.close()

	def getConfigData(self):
		return {'local':self.local.get(), 'public':self.public.get(), 'scriptlanguage':self.scriptlanguage.get()}

	def setConfigData(self, config):
		self.local.set(config['local'])
		self.public.set(config['public'])
		self.scriptlanguage.set(config['scriptlanguage'])

	def installWebInterface(self):
		parts			= urlparse.urlparse(self.public.get())
		success			= 0

		# determine the sourcefile
		source			= os.getcwd() + os.sep + "stubs" + os.sep + "webindex." + self.scriptlanguage.get()

		# determine the targetfile
		target			= self.local.get() + os.sep + "webindex." + self.scriptlanguage.get()

		# open source and target files
		try:
			file		= open(source)
			contents	= file.readlines()
			file.close()
		except:
			success		= 0
			return success
		else:
			try:
				out		= open(target, "w")
			except:
				success	= 0
				return success

		# replace all '{installationdir}' occurences with the parent dir. (TODO: Fix that and ask user?)
		installationdir	= string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep)
		for line in contents:
			line		= string.replace(line, '{installationdir}', installationdir)
			out.write(line)

		out.close()

		success	= 1

		return success

	def nextButtonPressed(self):
		parts		= urlparse.urlparse(self.public.get())
		if parts[0]!='' and parts[1]!='' and self.local.get()!='':
			if self.installWebInterface()==1:
				wizard.nextButtonPressed(self)
			else:
				tkMessageBox.showerror("Error", "Could not install web interface. Please check your settings.")
		else:
			tkMessageBox.showerror("Error", "Please provide valid input in the 'directory' and 'available as' entry-boxes.")
