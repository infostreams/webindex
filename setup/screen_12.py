from	wizard import *
import	tkMessageBox

class screen_12(wizard):
	def setContents(self):
		master		= self.contentcanvas

		# derive installation-url
		public		= self.getConfigForPage(11)['public']
		while public[-1]=="/":
			public	= public[:-1]
		self.url	= public + "/webindex." + self.getConfigForPage(11)['scriptlanguage']
		
		# create some nice HTML
		self.html	= "<font size='-2'>This site maintains an automated <a href='%s'>site map</a> that was created with " % (self.url, ) + \
					"the open source <a href='http://webindex.sourceforge.net/'>WebIndex</a> program.</font>"

		self.defaultHeader(master, "Finished").grid(row=0, columnspan=3)

		text	= "Setup has finished configuring WebIndex.\n\nYou can use the following information to " + \
				"link to the web interface. If you want to have any benefit of using WebIndex, you " + \
				"should do that. Without it, you will remain as visible (or invisible) for search engines " + \
				"as you were before.\n\nYou can copy-paste the information below to your main web page to " + \
				"finish the installation of WebIndex."
		self.defaultText(master, text=text).grid(row=1, columnspan=3, sticky=W)

		master.unbind_class("Text", "<Return>")
		master.unbind_class("Text", "<Any-KeyPress>")
		master.unbind_class("Text", "<Any-KeyRelease>")

		self.defaultText(master, "Link to this URL:", pady=0).grid(row=2, column=0, sticky=W)
		url		= Text(master, font=defaultFont, height=1, width=len(self.url), wrap=WORD, pady=0, spacing1=2,
						borderwidth=2, background="#FFFFFF")
		url.insert(END, self.url)
		url.grid(row=2, column=1, sticky=EW)

		self.defaultText(master, "Or use this HTML:", pady=0).grid(row=3, column=0, sticky=NW)
		html	= Text(master, font=defaultFont, height=6, width=len(self.url), pady=0, spacing1=2,
						borderwidth=2, background="#FFFFFF")
		html.insert(END, self.html)
		html.grid(row=3, column=1, sticky=EW)

	def select(self, event=None):
		self.x.config(state=NORMAL)
		self.x.select_range(0, 2)
#		self.x.config(state=DISABLED)

	def nextButtonPressed(self, step=1):
		text = "You might be aware that this software is still in its early testing phase. " + \
			"This means that this software may still contain unwanted programming errors. In some cases, " + \
			"this setup program will produce an error message after you have clicked the OK button below. " + \
			"Do not be alarmed by it, this error is not harmful in any way."
		tkMessageBox.showinfo("For your information", text)
		try:
			wizard.nextButtonPressed(self, step)
		except:
			pass
