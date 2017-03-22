from wizard import *
import os
import tkFileDialog
import sys
import string

class screen_2(wizard):

	def setContents(self):
		# display welcome text
		master	= self.contentcanvas
		self.hasApprovedOverwrite	= None
		self.defaultHeader(master, "Configuration details").grid(row=0, columnspan=6)

		text	=	"WebIndex can cope with multiple configuration files. Which configuration file do you want to setup?\n\n"
		text	+=	"If you choose to overwrite an existing configuration file, then all the information stored in that "
		text	+=	"configuration file will be lost.\n\nWhich configuration file do you want to create?"

		self.defaultText(master, text, pady=0).grid(row=1, columnspan=6, sticky=W)

		text	=	"Configuration file: "
		self.defaultText(master, text).grid(row=2, column=0, sticky=W)

		self.entry	= Entry(master, width=30, font=defaultFont)
		self.entry.focus()
		self.entry.grid(row=2, column=1, sticky=EW)

		self.filename	= ""

		self.freesizeButton(master, label='...', command=self.chooseFile, width=20, height=20).grid(row=2, column=2, sticky=W)

		text	= "What is the external DNS-name of this computer (e.g.: www.myhost.com or myhost.dyndns.org)?"
		self.defaultText(master, text).grid(row=3, columnspan=3, sticky=W)

		self.defaultText(master, "Hostname:").grid(row=4, column=0, sticky=W)

		self.hostname	= StringVar()
		Entry(master, textvariable=self.hostname, width=30, font=defaultFont).grid(row=4, column=1, sticky=EW)

		defaultconfig	= string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep) + os.sep + "webindex.ini"

		self.setConfigData({'filename':defaultconfig, 'approved':None, 'hostname':self.getHostname()})

	def chooseFile(self):
		new		= tkFileDialog.asksaveasfilename()
		if len(new)>0:
			self.entry.delete(0, END)
			self.entry.insert(0, new)
			self.hasApprovedOverwrite = 1

	def setConfigData(self, configdata):
		self.setField(self.entry, configdata['filename'])
		self.hostname.set(configdata['hostname'])
		self.hasApprovedOverwrite = configdata['approved']

	def getConfigData(self):
		return {'filename': self.entry.get(), 'approved': self.hasApprovedOverwrite, 'hostname':self.hostname.get()}

	def nextButtonPressed(self):
		validfilename	= 1
		
		if self.hostname.get()=="":
			tkMessageBox.showerror("Error", "You must provide a hostname")
			return

		self.filename	= self.entry.get()

		# check for existing file
		if self.hasApprovedOverwrite == None:
			try:
				x	= file(self.filename, "r")
			except:
				pass
			else:
				x.close()
				warning	= "You have chosen to write to a file that already exists. Do you want to overwrite the contents of '" + self.filename + "'?"
				if not tkMessageBox.askyesno("Overwrite existing file", warning):
					validfilename	= 0
					self.hasApprovedOverwrite = 0
				else:
					self.hasApprovedOverwrite = 1
		else:
			if self.hasApprovedOverwrite == 0:
				validfilename = 0

		# check for nothing entered:
		if len(self.filename)==0:
			tkMessageBox.showerror("No file", "You must enter a valid filename")
			validfilename	= 0

		# check if we have write access # TODO: Make non-destructive
		if validfilename == 1:
			try:
				x	= file(self.filename, "w")
			except:
				tkMessageBox.showerror("Error", "Could not write to file, please set permissions correctly and try again.")
				validfilename = 0
			else:
				x.close()

		# only proceed if we have a valid filename
		if validfilename == 1:
			wizard.nextButtonPressed(self)

	def getHostname(self):
		if sys.platform[:3]=="win":
			import socket
			return socket.getfqdn() # half-assed solution
		else:
			# Retrieve this server's online ip-address
			# Do this by fetching the ip-addresses for each network-interface
			pipe		= os.popen('/sbin/ifconfig | grep inet | cut -d ":" -f 2 | cut -d " " -f 1')
			IPaddresses	= string.split(string.strip(pipe.read()), "\n")
			pipe.close()

			# filter out the 'local' ip-addresses
			for address in IPaddresses:
				parts	= string.split(address, ".")
				if (not ((parts[0]=="127") or (parts[0]=="192" and parts[1]=="168") or (parts[0]=="10"))):
					ip	 = address

			# The last non-local ip-address is considered the true online ip-address
			# do a DNS-lookup to find out which server-address belongs to this ip-address
			pipe		= os.popen("nslookup "+ip+" 2>&1 | grep name | grep -v nameserver | cut -d \"=\" -f 2")
			rawname		= string.strip(pipe.read())
			pipe.close()
			servername	= rawname[:-1]

			return servername
