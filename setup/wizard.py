from Tkinter import *

import string
import webindex
import pprint
import tkMessageBox

# strangely enough, the following code is necessary to find modules in the parent-directory
# (despite what is said in http://www.python.org/doc/current/tut/node8.html)
# it adds the parent directory to the sys.path variable that determines which directories to
# search for modules
import sys, os
sys.path.append(string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep))

maxpagenumber	= 12
startpage		= 1

if sys.platform[:3]=="win":
	linuxOffset	= 0
else:
	linuxOffset	= 3

font			= ("Helvetica", )
#font			= ("Courier", )
bold			= ("bold", )
smallFont		= font + (7+linuxOffset, )
smallboldFont	= font + (8+linuxOffset, ) + bold
defaultFont		= font + (9+linuxOffset, )
smallheaderFont	= font + (10+linuxOffset, ) + bold
headerFont		= font + (14+linuxOffset, ) + bold

class wizard:
	# Beware, bizarre memory leak included :(

	def __init__(self, pagenumber=1, newwizard=1):

		# initialize some constants
		self.buttonwidth		= 80
		self.buttonheight		= 24
		self.windowwidth		= 600
		self.windowheight		= 400
		self.bottomframeheight	= self.buttonheight + 8
		self.topframeheight		= self.windowheight-self.bottomframeheight
		self.imageframewidth	= 160
		self.padding			= 10
		self.pagenumber			= pagenumber
		self.page				= self
		self.parent				= self
		self.config				= []

		# if no handles (for the rootwindow or the frames within)
		# are provided, then start a 'new' wizard
		if newwizard == 1:
			self.startWizard()
			self.setpage(startpage)
			self.display()

	def __del__(self):
#		print "calling del"
		self.page			= None
		self.parent			= None
		self.root			= None
		self.imageframe 	= None
		self.contentframe 	= None
		self.bottomframe 	= None
		self.contentcanvas	= None

	def setpage(self, pagenumber):
		# display a particular page from the wizard

        ###
		### Store configurationdetails entered on this page
        ###

		if id(self.page)!=id(self):
			self.page.setParent(None)
			self.page.__del__()

		# remove stored configuration for this page
		for configdata in self.config:
			if configdata['__pagenumber'] == self.pagenumber:
				self.config.remove(configdata)

		# store configuration for later reference
		self.config.append({'config': self.page.getConfigData(), '__pagenumber': self.pagenumber})

		###
		### Clear canvas and initialize new page
		###

		# clear contentcanvas
		self.clearContents()

		# set pagenumber
		self.pagenumber	= pagenumber

		# import screen_$pagenumber
		exec "from screen_%d import *" % (pagenumber, )

		# re-evaluate self.page
		code			= "self.page	= screen_%d(pagenumber=%d, newwizard=0)" % (pagenumber, pagenumber)
		exec code

		self.page.setParent(self)

		# reset the contentframe and contentcanvas options (they somehow resized)
		self.contentframe.config(height=self.topframeheight, width=self.windowwidth-self.imageframewidth, bd=0, relief=RAISED)
		self.contentcanvas.config(width=self.contentframe.winfo_reqwidth()-self.padding, height=self.contentframe.winfo_reqheight()-self.padding, highlightthickness=0, bd=0, relief=RAISED)

		# pass on the window and frame-handles
		self.page.setHandles(self.getHandles())

		# call the setcontent-function
		self.page.setContents()

		# draw buttons
		self.page.drawButtons()

		# find potentially stored configurationdetails and restore those details
		for configdata in self.config:
			if configdata['__pagenumber'] == pagenumber:
				self.page.setConfigData(configdata['config'])

		###
		### Done
		###

	def startWizard(self):
		# create root window
		self.root				= Tk()

		# set title
		self.root.title("WebIndex 0.1 Setup Wizard")

		# do not resize
		self.root.resizable(0, 0)

		# set size
		position	= string.join(string.split(self.root.geometry(), " ")[1:], " ")
		self.root.geometry("%dx%d%s" % (self.windowwidth, self.windowheight, position))

		# create frames
		borderwidth	= 0
		self.imageframe		= Frame(self.root, height=self.topframeheight, width=self.imageframewidth, bd=borderwidth, relief=RAISED)
		self.contentframe	= Frame(self.root, height=self.topframeheight, width=self.windowwidth-self.imageframewidth, bd=borderwidth, relief=RAISED)
		self.bottomframe	= Frame(self.root, height=self.bottomframeheight, width=self.windowwidth, bd=borderwidth, relief=RAISED)

		# create drawing board (canvas)
		self.contentcanvas	= Canvas(self.contentframe, width=self.contentframe.winfo_reqwidth()-self.padding, height=self.contentframe.winfo_reqheight()-self.padding, highlightthickness=0, bd=0, relief=RAISED)
		self.contentcanvas.place(x=0, y=0)

	def setHandles(self, handles):
		self.root, self.imageframe, self.contentframe, self.bottomframe, self.contentcanvas	= handles

	def getHandles(self):
		return (self.root, self.imageframe, self.contentframe, self.bottomframe, self.contentcanvas)

	def __button(self, label, x, y, command, state=NORMAL):
		# create a button
		button	= Button(self.bottomframe, text=label, command=command, borderwidth=2, state=state, font=defaultFont)
		button.place(x=x, y=y, width=self.buttonwidth, height=self.buttonheight, anchor=NE)

	def display(self):
		""" show window """

		self.imageframe.grid(row=0, column=0)
		self.contentframe.grid(row=0, column=1)
		self.bottomframe.grid(row=1, columnspan=2)

		# do main loop
		self.root.mainloop()

	def drawButtons(self):
		""" Create 'previous', 'next' and 'cancel' buttons """

		gap	= 5 	# amount of pixels between [previous, next] and [cancel]
		if self.pagenumber == 1:
			prevstate 	= DISABLED
		else:
			prevstate	= NORMAL

		if self.pagenumber == maxpagenumber:
			nextname	= "Finish"
			cancelname	= "Close"
		else:
			nextname	= "Next >>"
			cancelname	= "Cancel"

		x	= self.windowwidth - self.padding - gap - 2*self.buttonwidth
		self.__button('<< Previous', x, 0, self.previousButtonPressed, prevstate)

		x	= self.windowwidth - self.padding - gap - self.buttonwidth
		self.__button(nextname, x, 0, self.nextButtonPressed)

		x	= self.windowwidth - self.padding
		self.__button(cancelname, x, 0, self.cancelButtonPressed)

	def drawImage(self, imagename=None):
		# create an 'image' variable that contains the image
		if imagename != None:
			image	= PhotoImage(file=imagename)
		else:
			image	= PhotoImage(data=webindex.gif)

		# create canvas
		canvas 		= Canvas(self.imageframe, width=image.width()+self.padding, height=image.height()+self.padding)

		# create a reference to the image so it is not garbage collected
		canvas.image= image

		# add the image to the canvas and place it
		item		= canvas.create_image(self.padding, self.padding, anchor=NW, image=canvas.image)
		canvas.place(x=0, y=0, width=image.width()+self.padding, anchor=NW)

	def defaultText(self, master, text, padx=None, pady=None, color="#000000", wraplength=None, font=defaultFont):
		""" use this to create 'default' text """
		if padx==None:
			padx=self.padding
		if pady==None:
			pady=self.padding
		if wraplength==None:
			wraplength = master.winfo_reqwidth() - 2*self.padding
		return Label(master, text=text, padx=padx, pady=pady, wraplength=wraplength,
				justify=LEFT, anchor=NW, font=font, fg=color)

	def defaultHeader(self, master, text):
		""" use this to create a 'default' header """
		return Label(master, text=text, padx=self.padding, pady=self.padding, justify=CENTER, anchor=NW, font=headerFont)

	def freesizeButton(self, master, label=None, textvariable=None, command=None, height=32, width=32, borderwidth=2, state=NORMAL, font=defaultFont):
		""" Use this to insert a button of which width and height can be specified in pixels.
			Please note that the frame containing the button is returned, not the button itself. """
		f = Frame(master, height=height, width=width)
		f.pack_propagate(0) # don't shrink
		b = Button(f, text=label, textvariable=textvariable, command=command, borderwidth=borderwidth, state=state, font=font)
		b.bind("<Return>", b.tkButtonInvoke)
		b.pack(fill=BOTH, expand=1)
		return f

	def previousButtonPressed(self, step=1):
		if self.pagenumber - step >= 1:
			if id(self.page) != id(self):
				if self.page != None:
					self.page.__del__()
			self.parent.setpage(self.pagenumber - step)

	def nextButtonPressed(self, step=1):
		if self.pagenumber + step <= maxpagenumber:
			if id(self.page) != id(self):
				if self.page != None:
					self.page.__del__()
			self.parent.setpage(self.pagenumber + step)
		else:
			self.cancelButtonPressed() # close setup

	def cancelButtonPressed(self):
		if self.pagenumber != maxpagenumber:
			if tkMessageBox.askyesno("Cancel setup", "Do you want to stop configuring WebIndex?\nThis will probably cause WebIndex not to function."):
				self.root.destroy()
		else:
			# store config for last page:

			# - remove stored configuration for this page (might occur)
			for configdata in self.parent.config:
				if configdata['__pagenumber'] == self.pagenumber:
					self.parent.config.remove(configdata)

			# - get config for last page
			self.parent.config.append({'config': self.page.getConfigData(), '__pagenumber': self.pagenumber})
#			print "obtained config (in wizard.py, line 266):"
#			pprint.pprint(self.parent.config)
			self.root.destroy()

	def getConfigData(self):
		pass

	def setConfigData(self, configdata):
		pass

	def setContents(self):
		pass

	def setField(self, field, text):
		""" set the value of a widget 'field' to 'text' """
		field.delete(0, END)
		if text==None:
			field.insert(0, "")
		else:
			field.insert(0, text)

	def clearContents(self, master=None):
		""" clear the contents of the content canvas """
		kids	= self.contentcanvas.winfo_children()
		for kid in kids:
			kid.destroy()

	def setParent(self, parent):
		self.parent	= parent

	def getConfigForPage(self, pagenr):
		for configdata in self.parent.config:
			if configdata['__pagenumber']==pagenr:
				return configdata['config']
