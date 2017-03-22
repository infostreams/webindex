# Static directories

import 	tkSimpleDialog
import 	multilistbox
import 	tkFileDialog
import 	tkMessageBox
import 	urlparse
import	sys
from 	wizard import *

if sys.platform[:3]=="win":
	from shared.fileIndexation import windows
else:
	from shared.fileIndexation import linux

class screen_7(wizard):
	def setContents(self):
		master	= self.contentcanvas
		self.defaultHeader(master, "Static directories").grid(row=0, columnspan=3)

		text	=	"Your web server configuration has provided information about which directories are accessible online. "
		text	+=	"The following directories have been identified and will be used as such.\n\nPlease correct and/or complete "
		text	+=	"this information."

		self.defaultText(master, text).grid(row=1, columnspan=3, sticky=W)

		# insert MultiListbox
		self.mlb= multilistbox.MultiListbox(master, (('Directory', 25), ('Available as', 25)), height=8, font=defaultFont)
		self.mlb.grid(row=2, padx=self.padding)
		self.mlb.bind("<Double-Button-1>", self.edit)

		# create defaults --> 'publicdirs'
		if sys.platform[:3]=="win":
			indexer	= windows.fileIndexer()
		else:
			indexer	= linux.fileIndexer()

		# get configfilename from page 5
		thatconfig	= self.getConfigForPage(5)
		if thatconfig != None:
			configfilename	= thatconfig['filename']
		else:
			configfilename	= None

		try:
			self.publicdirs	= indexer.getPublicDirs(configfilename)
		except:
			self.publicdirs	= []

		for entry in self.publicdirs:
			parts	= list(urlparse.urlparse(entry['public']))
			if parts[0]=='':
				parts[0]	= "http"
			if parts[1]=='':
				parts[1]	= self.getConfigForPage(2)['hostname']
			entry['public']	= urlparse.urlunparse(tuple(parts))

		# insert default values
		self.defaults()

		# place buttons
		frame	= Frame(master)
		buttonwidth = 10
		remove	= Button(frame, text="Delete", command=self.delete, width=buttonwidth, font=defaultFont)
		remove.grid(row=0, column=0, sticky=W)

		add		= Button(frame, text="Add", command=self.add, width=buttonwidth, font=defaultFont)
		add.grid(row=0, column=1, sticky=W, padx=self.padding)

		add		= Button(frame, text="Edit", command=self.edit, width=buttonwidth, font=defaultFont)
		add.grid(row=0, column=2, sticky=W)

		default	= Button(frame, text="Defaults", command=self.defaults, width=buttonwidth, font=defaultFont)
		default.grid(row=0, column=3, sticky=W, padx=self.padding)

		frame.grid(row=3, column=0, padx=self.padding, pady=self.padding)

	def add(self):
		answer	= staticDirDialog(self.contentcanvas, local="", public="").result
		if answer!=None:
			self.mlb.insert(0, (answer['local'], answer['public']))

	def edit(self, event=None):
		active	= int(self.mlb.curselection()[0])
		current	= self.mlb.get(active)
		answer	= staticDirDialog(self.contentcanvas, local=current[0], public=current[1]).result
# 		print "Edit.answer:"
# 		print answer
		if answer!=None:
			self.mlb.insert(active+1, (answer['local'], answer['public']))
			self.mlb.delete(active)
		self.mlb.selection_set(active, active)

	def delete(self):
		self.mlb.delete(ACTIVE)
		self.mlb.selection_set(0, 0)

	def defaults(self):
		self.mlb.delete(0, END)
		for dir in self.publicdirs:
			self.mlb.insert(END, (dir['local'], dir['public']))
		self.mlb.selection_set(0, 0)

	def setConfigData(self, configdata):
		self.mlb.delete(0, END)
		for item in configdata:
			self.mlb.insert(END, item)
		self.mlb.selection_set(0, 0)

	def getConfigData(self):
		return self.mlb.get(0, END)

	def nextButtonPressed(self):
		fail	= 0
		for item in self.mlb.get(0, END):
			urlparse.urlparse(item[1])
			try:
				test	= urlparse.urlparse(item[1])
			except:
				fail	= 1
				continue
			if test[0]=='' or test[1]=='':
				fail	= 1

		if fail==0:
			wizard.nextButtonPressed(self)
		else:
			tkMessageBox.showerror("Error", "Please give each local directory a valid 'public' address (such as, for example, http://www.myhost.com/directory1)")

class staticDirDialog(tkSimpleDialog.Dialog):
	# dialog for screen_6
	#
	# magically crashes if 'enter' or 'escape' is pressed
	# (No more? No more!)
	#
	# After 2 hours of frustration I finally found the cause of this odd behaviour:
	# I used a variable called self.master, which also seems to be an internal variable
	# for the 'TopLevel' class. If you overwrite it, you are fucked. (grrrrr)
	def __init__(self, parent, title=None, local=None, public=None):
		self._local		= local
		self._public	= public
		tkSimpleDialog.Dialog.__init__(self, parent, title)

	def body(self, master):
		self.mymaster	= master
		Label(master, text='You have to specify which directory is available, as well as the base address of '
				'how the contents of this directory can be reached from the web.', justify=LEFT, wraplength=300, font=defaultFont).grid(row=0, columnspan=4, sticky=W)
		Label(master, text='Directory', font=defaultFont).grid(row=1, column=0, sticky=W)
		self.local	= Entry(master, width=30)
		self.local.grid(row=1, column=1)
		if self._local!=None:
			self.local.insert(0, self._local)
		self.browse	= Button(master, text='...', command=self.chooseFile, width=1, height=1)
 		self.browse.grid(row=1, column=2, sticky=W)

		Label(master, text='Available as', font=defaultFont).grid(row=2, column=0, sticky=W)
		self.public	= Entry(master, width=30)
		if self._public!=None:
			self.public.insert(0, self._public)
		else:
			self.public.insert(0, 'http://')
		self.public.grid(row=2, column=1)

		return self.local

	def chooseFile(self):
		dir			= tkFileDialog.askdirectory(parent=self.mymaster, mustexist=1)
		if dir!="":
			self.local.delete(0, END)
			self.local.insert(0, dir)

	def validate(self):
		try:
			self.result	= self.getResult()
			return 1
		except:
			self.result	= None
			return 0

	def getResult(self):
		return {'local': self.local.get(), 'public': self.public.get()}
