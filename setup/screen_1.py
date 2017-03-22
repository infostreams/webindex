from wizard import *

class screen_1(wizard):

	def setContents(self):
		# draw default image
		self.drawImage()

		# display 'welcome' header
		master	= self.contentcanvas
		self.defaultHeader(master, "Welcome to the WebIndex Setup Wizard!").grid(row=0)

		# display introductory text
		text	=	"WebIndex is a tool that helps you create a complete index of all the web pages on your web site. "
		text	+=	"It is very likely that a lot of your web pages can't be found by search engines (such as Google). "
		text	+=	"This means that potential visitors cannot find these web pages, since the search engine is unaware "
		text	+=	"of their existence.\n\n"

		text	+=	"WebIndex can help you solve this problem. This program will try to configure WebIndex correctly for "
		text	+= 	"this machine, but it might still be necessary to do some handwork to obtain an optimal configuration.\n\n"

		text	+= 	"This program is free for use and licensed under the GNU Public License (GPL).\n\n"

		text	+= 	"Check out http://webindex.sf.net/ for the latest release.\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
		self.defaultText(master, text, pady=0).grid(row=1)

		# display copyright statement
		copy	= "Webindex is (c) 2003 by Edward Akerboom\n"
		label	= Label(master, text=copy, padx=self.padding, pady=self.padding, font=smallFont, fg='#808080')
		label.place(x=0, y=self.topframeheight-self.bottomframeheight-7, anchor=NW)
