import	tkSimpleDialog
import	re
import	string
import	testURL
import	tkMessageBox

from	wizard 		import *
from	Tkinter 	import *
from	engine		import engine
from	shared		import XMLConfig
from 	shared.logfilePredictor import *

### Dialog #1: Ask table and column from database
###
#################################################################################

class databaseSourceDialog(tkSimpleDialog.Dialog):
	def __init__(self, parent, title=None, databasestructure=None, argument=None, currentvalue=None, top=None):
		self.dbstructure	= databasestructure
		self.initialvalue	= 0
		self.wraplength		= 400
		self.argument		= argument
		self.top			= top

		# define defaults for optionmenu's
		if top!=None:
			table			= top[0]['table']
			column			= top[0]['column']
		else:
			table           = self.dbstructure.keys()[0]
			column			= self.dbstructure[table][0]

		try:
			self.tabledefault, self.columndefault 	= string.split(currentvalue, ".")
		except:
			self.tabledefault, self.columndefault   = table, column

		tkSimpleDialog.Dialog.__init__(self, parent, title)

	def body(self, master):
		self.mymaster		= master
		table				= self.dbstructure.keys()
		column				= self.dbstructure[table[0]]

		Label(master, text='To which table and column does a value for the argument "%s" refer to?' % (self.argument, ),
			font=defaultFont, justify=LEFT, wraplength=self.wraplength).grid(row=0, column=0, columnspan=3, sticky=W)

		# Define 'table' row
		Label(master, text='Table', font=defaultFont).grid(row=1, column=0, sticky=W)
		self.table 			= StringVar()
		self.table.set(self.tabledefault) # default value

		tablewidget			= apply(OptionMenu, (master, self.table) + tuple(table))
		tablewidget.config(font=defaultFont)
		tablewidget.bind("<Configure>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.bind("<Button-1>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.bind("<ButtonRelease-1>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.bind("<B1-Motion>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.bind("<Enter>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.bind("<Leave>", self.changetablesetting, add=1)	# 'onChange' event
		tablewidget.grid(row=1, column=1, sticky=W)

		# Define 'column' row
		Label(master, text='Column', font=defaultFont).grid(row=2, column=0, sticky=W)
		self.column			= StringVar()
		self.column.set(self.columndefault) # default value

		self.columnwidget	= apply(OptionMenu, (master, self.column) + tuple(column))
		self.columnwidget.config(font=defaultFont)
		self.columnwidget.grid(row=2, column=1, sticky=W)	# beware, also defined in 'changetablesetting'

		topstring			= "\nWebIndex has put together a list of the most likely sources for this argument. " \
						"In this list, printed below, you can see how much of the recorded values for this " \
						"argument are present in that particular source:\n"
		Label(master, text=topstring, font=defaultFont, justify=LEFT, wraplength=self.wraplength, pady=0).grid(row=3, column=0, columnspan=3, sticky=W)

		topstring			= ""
		if self.top!=None:
			for argument in self.top:
				topstring	+= "%.2f%% of its assigned values are present in %s.%s\n" % (argument['score'], argument['table'], argument['column'])
#				topstring	+= "%.2f%% of the recorded values are present in %s.%s contains %.2f%% of the values\n" % (argument['table'], argument['column'], argument['score'])

		Label(master, text=topstring, font=smallboldFont, justify=LEFT, wraplength=self.wraplength, pady=0).grid(row=4, column=0, columnspan=3, sticky=W)

		# Define 'alternative' row
		Label(master, text="You can specify an alternative location using the 'table.column' syntax:", justify=LEFT,
			font=defaultFont, wraplength=self.wraplength).grid(row=5, column=0, columnspan=3, sticky=W)
		Label(master, text='Alternative', font=defaultFont).grid(row=6, column=0, sticky=W)
		self.alternative	= Entry(master, font=defaultFont)
		self.alternative.grid(row=6, column=1, sticky=W)

		return self.alternative

	def changetablesetting(self, event=None): # pun intended :)
		column				= self.dbstructure[self.table.get()]
		self.columnwidget.destroy()
		self.columnwidget	= apply(OptionMenu, (self.mymaster, self.column) + tuple(column))
		self.columnwidget.config(font=defaultFont)
		self.columnwidget.grid(row=2, column=1, sticky=W)
		self.column.set(column[0])

	def apply(self):
		alt	= self.alternative.get()
		if len(alt)>0:
			self.result	= alt
		else:
			self.result	= self.table.get() + "." + self.column.get()

	def validate(self):
		alt	= self.alternative.get()
		if len(alt)>0:
			if len(re.findall(re.compile("^.+?\..+?$"), alt))>0:
				return 1
			else:
				return 0
		else:
			return 1

### Dialog #2: Ask dependencies for a specific argument
###
#################################################################################

class dependenciesDialog(tkSimpleDialog.Dialog):
	def __init__(self, parent, title=None, argument=None, arguments=None):
		self.argument	= argument
		self.arguments	= []
		for arg in arguments:
			if self.argument != arg['name']:
				entry		= { 'argument': arg,
								'dependent':IntVar(),
								'relationshiptype':StringVar(),
								'customrelationship': StringVar() }
				self.arguments.append(entry)

		if len(self.arguments)>0:
			tkSimpleDialog.Dialog.__init__(self, parent, title)
		else:
			self.result	= None

	def body(self, master):
		self.mymaster	= master
		Label(master, text="Which arguments change value if the argument ''%s'' changes value?\nWhich arguments depend on this argument?\n" % (self.argument, ),
			justify=LEFT, font=defaultFont).grid(row=1, columnspan=4, sticky=W)

		Label(master, text="Argumentname", font=smallboldFont).grid(row=2, column=0, sticky=W)
		Label(master, text="Relationship type", font=smallboldFont).grid(row=2, column=1, columnspan=2, sticky=W, padx=15)

		rownr			= 0
		startrow		= 3
		self.widgetsperrow	= 4
		self.check		= [None]
		self.button1	= [None]
		self.button2	= [None]
		self.entry		= [None]

		for argument in self.arguments:

			# checkbutton
			self.check[rownr]		= Checkbutton(master, text=argument['argument']['name'],
										variable=argument['dependent'], font=defaultFont)
			self.check[rownr].grid(row=rownr+startrow, column=0, sticky=W)
			self.check[rownr].bind("<Button-1>", self.checkboxcommand)
			self.check[rownr].bind("<space>", self.checkboxcommand)

			# radiobutton 1
			self.button1[rownr]	= Radiobutton(master, text='Direct', variable=argument['relationshiptype'],
										value='direct', font=defaultFont)
			self.button1[rownr].grid(row=rownr+startrow, column=1, sticky=W, padx=15)
			self.button1[rownr].bind("<Button-1>", self.button1command)
			self.button1[rownr].bind("<space>", self.button1command)

			# radiobutton 2
			self.button2[rownr]	= Radiobutton(master, text='Custom', variable=argument['relationshiptype'],
										value='custom', font=defaultFont)
			self.button2[rownr].grid(row=rownr+startrow, column=2, sticky=W)
			self.button2[rownr].bind("<Button-1>", self.button2command)
			self.button2[rownr].bind("<space>", self.button2command)

			# entry
			self.entry[rownr]		= Entry(master, width=20, textvariable=argument['customrelationship'], state=DISABLED, font=defaultFont)
			self.entry[rownr].grid(row=rownr+startrow, column=3, sticky=W)
			self.entry[rownr].bind("<Button-1>", self.entrycommand)
			self.entry[rownr].bind("<space>", self.entrycommand)

			# set defaults
			if self.argument in argument['argument']['dependent_on']:
				argument['dependent'].set(1)
				argument['relationshiptype'].set('direct')
				self.button1[rownr].config(state=NORMAL)
				self.button2[rownr].config(state=NORMAL)
				self.entry[rownr].config(state=DISABLED)
			elif len(re.findall(self.argument, argument['argument']['query']))>0:
				argument['dependent'].set(1)
				self.button1[rownr].config(state=NORMAL)
				self.button2[rownr].config(state=NORMAL)
				self.entry[rownr].config(state=NORMAL)
				argument['relationshiptype'].set('custom')
				argument['customrelationship'].set(argument['argument']['query'])
			else:
				argument['dependent'].set(0)
				self.button1[rownr].config(state=DISABLED)
				self.button2[rownr].config(state=DISABLED)
				self.entry[rownr].config(state=DISABLED)
				argument['relationshiptype'].set('direct')

			# increase both list-sizes and rownr
			self.check.append(None)
			self.button1.append(None)
			self.button2.append(None)
			self.entry.append(None)
			rownr		+= 1

	def findWidgetRow(self, event):
		# find the row on which the clicked widget resides
		thiswidgetid	= event.widget.winfo_id()
		widgetnr		= 0
		for kid in self.mymaster.winfo_children():
			if kid.winfo_id()==thiswidgetid:
				break
			widgetnr	+= 1

		row	= int((widgetnr-3) / self.widgetsperrow) # -n because of the other widgets in the dialog
		return row

	def checkboxcommand(self, event):
		# enable or disable whole row
		row				= self.findWidgetRow(event)

		checkboxvalue	= int(self.arguments[row]['dependent'].get())

		if checkboxvalue == 1:
			self.button1[row].config(state=DISABLED)
			self.button2[row].config(state=DISABLED)
			self.entry[row].config(state=DISABLED)
		else:
			self.button1[row].config(state=NORMAL)
			self.button2[row].config(state=NORMAL)
			if self.arguments[row]['relationshiptype'].get()=='direct':
				self.entry[row].config(state=DISABLED)
			else:
				self.entry[row].config(state=NORMAL)

	def button1command(self, event):
		# disable the 'entry' box on the same row
		row		= self.findWidgetRow(event)
		self.entry[row].config(state=DISABLED)

	def button2command(self, event):
		# enable the 'entry' box on the same row
		row		= self.findWidgetRow(event)
		self.entry[row].config(state=NORMAL)

	def entrycommand(self, event):
		# enable button2 if the entry-field is clicked
		row				= self.findWidgetRow(event)
		checkboxvalue	= int(self.arguments[row]['dependent'].get())
		if checkboxvalue == 1:
			self.button2[row].select()
			self.entry[row].config(state=NORMAL)

	def buttonbox(self):
		box = Frame(self)

		w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE, font=defaultFont)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Cancel", width=10, command=self.cancel, font=defaultFont)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Help", width=10, command=self.help, font=defaultFont)
		w.pack(side=LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def help(self):
		print "Popup a window that displays help"

	def apply(self):
		self.result	= []
		for arg in self.arguments:
			entry		= { 'argument': arg['argument'],
							'dependent':arg['dependent'].get(),
							'relationshiptype':arg['relationshiptype'].get(),
							'customrelationship': arg['customrelationship'].get() }
			self.result.append(entry)

### Dialog #3: Show URLs resulting from current config
###
#################################################################################

class urlTesterDialog(tkSimpleDialog.Dialog):
	def __init__(self, parent, title=None, urls=None):
		self.urls	= urls
		self.stop	= 0
		tkSimpleDialog.Dialog.__init__(self, parent, title)

	def body(self, master):
		self.mymaster	= master

		Label(master, text='Generated URLs:', justify=LEFT, font=defaultFont).grid(row=0, column=0, padx=10, columnspan=2, sticky=W)

		# create + draw a listbox and a scrollbar
		frame				= Frame(master, bd=0, relief=RAISED)

		listboxwidth		= 60
		self.vscroll		= Scrollbar(frame, orient=VERTICAL, width=8)
		self.hscroll		= Scrollbar(frame, orient=HORIZONTAL, width=16)
		self.listbox		= Listbox(frame, yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set, font=defaultFont,
								width=listboxwidth, height=8, borderwidth=1, selectborderwidth=0, highlightthickness=0,
								background=self.vscroll.config()['background'][4])
		self.listbox.grid(row=1, column=0, padx=10, sticky=EW)

		self.vscroll.config(command=self.listbox.yview)
		self.hscroll.config(command=self.listbox.xview)
		self.vscroll.grid(row=1, column=1, sticky=NS)
		self.hscroll.grid(row=2, column=0, columnspan=2, sticky=EW)
		self.hscroll.grid_remove()

		frame.grid(row=1, column=0, sticky=W, columnspan=2)

		# insert URLs
		for url in self.urls:
			item		= url['url']
			if url.has_key('post'):
				if len(url['post'])>0:
					item	+= "(with POST: " + url['post'] + ")"
			if len(item)>listboxwidth-15:
				self.hscroll.grid()
			self.listbox.insert(END, url['url'])

		self.urlvar		= StringVar()
		Label(master, text='URL:', justify=LEFT, font=defaultFont).grid(row=2, column=0, sticky=W)
		Label(master, textvariable=self.urlvar, justify=LEFT, font=defaultFont).grid(row=2, column=1, sticky=W)

		self.statusvar	= StringVar()
		Label(master, text='Status:', justify=LEFT, font=defaultFont).grid(row=3, column=0, sticky=W)
		Label(master, textvariable=self.statusvar, justify=RIGHT, font=defaultFont).grid(row=3, column=1, sticky=W)

		self.xofyvar	= StringVar()
		Label(master, textvariable=self.xofyvar, justify=RIGHT, font=defaultFont).grid(row=4, column=1, sticky=W)

	def test(self):
		if self.startbuttonvar.get() == "Stop":
			self.startbuttonvar.set("Start")
			self.stop = 1
			return
		else:
			self.startbuttonvar.set("Stop")
			self.stop = 0

		urlnumber		= 0
		urltotal		= len(self.urls)
		okcount			= 0
		for url in self.urls:
			if self.stop == 1:
				self.xofyvar.set("")
				self.statusvar.set("")
				self.urlvar.set("")
				break

			self.update()	# handle events
			self.update_idletasks()

			item		= url['url']
			if url.has_key('post'):
				if len(url['post'])>0:
					item	+= "(with POST: " + url['post'] + ")"
			self.urlvar.set(item)

			if testURL.testURL(url):
				status	= "Ok"
				self.listbox.itemconfig(urlnumber, foreground="#000000")
				okcount += 1
			else:
				status = "Not Ok"
				self.listbox.itemconfig(urlnumber, foreground="#DD3434")

			self.statusvar.set(status)
			self.xofyvar.set("%d of %d URLs are valid (%.2f%%)" % (okcount, urlnumber+1, 100*okcount/(urlnumber+1)))

			urlnumber	+= 1

		self.score	= 100*okcount / len(self.urls)
		self.startbuttonvar.set("Start")

	def buttonbox(self):
		box = Frame(self)

		self.startbuttonvar	= StringVar()
		self.startbuttonvar.set("Start")
		w = Button(box, textvariable=self.startbuttonvar, width=10, command=self.test, default=ACTIVE, font=defaultFont)
		w.pack(side=LEFT, padx=5, pady=5)
		w = Button(box, text="Close", width=10, command=self.ok, font=defaultFont)
		w.pack(side=LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def apply(self):
		self.result	= self.score
