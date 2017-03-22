# Output plugins

from 	wizard import *
from	Tkinter import *
import	tkFileDialog
import	os
import	sys

class screen_10(wizard):

	def setContents(self):
		master	= self.contentcanvas
		self.drawImage()

		self.defaultHeader(master, text="Output plugins").grid(row=0, column=0, columnspan=4)

		body	= "The following information is needed for the output-plugins to function correctly."
		self.defaultText(master, text=body).grid(row=1, column=0, columnspan=4, sticky=W)

		# HTML output
		self.defaultText(master, text="HTML output plugin", font=defaultFont + bold, pady=0).grid(row=2, column=0, columnspan=4, sticky=W)
		self.defaultText(master, text="Template:", pady=0).grid(row=3, column=0, sticky=W)

		self.htmltemplatevar	= StringVar()
		defaulthtmltemplate		= string.join(string.split(os.getcwd(), os.sep)[:-1] + ['engine', 'output', 'html_templates'], os.sep) + os.sep + "default.tpl"
		self.htmltemplatevar.set(defaulthtmltemplate)
		Entry(master, textvariable=self.htmltemplatevar, font=defaultFont).grid(row=3, column=1, sticky=EW)
		self.freesizeButton(master, label='...', width=24, height=20, command=self.getHTMLtemplate).grid(row=3, column=2, sticky=W)

		self.defaultText(master, text="URLs per page:", pady=0).grid(row=4, column=0, sticky=W)
		self.chunksizevar	= StringVar()
		self.chunksizevar.set("100")
		Entry(master, textvariable=self.chunksizevar, width=4, font=defaultFont).grid(row=4, column=1, sticky=W)

		# create empty space (I know, I know)
		self.defaultText(master, text="", pady=5).grid(row=5, column=0)

		# OAI-PMH output
		self.defaultText(master, text="OAI-PMH output plugin", font=defaultFont + bold, pady=0).grid(row=6, column=0, columnspan=4, sticky=W)

		self.defaultText(master, text="Repository name:", pady=0).grid(row=7, column=0, sticky=W)
		self.repositorynamevar	= StringVar()
		self.repositorynamevar.set("A WebIndex URL repository")
		Entry(master, textvariable=self.repositorynamevar, font=defaultFont).grid(row=7, column=1, sticky=EW, columnspan=2)

		self.defaultText(master, text="Administrator email:", pady=0).grid(row=8, column=0, sticky=W)
		self.adminemailvar	= StringVar()
		self.adminemailvar.set("webmaster@" + self.getConfigForPage(2)['hostname'])
		Entry(master, textvariable=self.adminemailvar, font=defaultFont).grid(row=8, column=1, sticky=EW, columnspan=2)
		self.defaultText(master, text="*", pady=0, padx=0, color="#FF0000").grid(row=8, column=3, sticky=W)
		self.defaultText(master, text="  (optional)", pady=0).grid(row=9, column=1, sticky=W)
		self.defaultText(master, text="*", pady=0, padx=0, color="#FF0000").grid(row=9, column=1, sticky=W)

	def getConfigData(self):
		return {'htmltemplate':self.htmltemplatevar.get(),
				'chunksize':self.chunksizevar.get(),
				'repositoryname':self.repositorynamevar.get(),
				'adminemail':self.adminemailvar.get()}

	def setConfigData(self, configdata):
		self.htmltemplatevar.set(configdata['htmltemplate'])
		self.chunksizevar.set(configdata['chunksize'])
		self.repositorynamevar.set(configdata['repositoryname'])
		self.adminemailvar.set(configdata['adminemail'])

	def getHTMLtemplate(self):
		new		= tkFileDialog.askopenfilename()
		if len(new)>0:
			self.htmltemplatevar.set(new)
