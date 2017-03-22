import sys
import os
import os.path
import string

sys.path.append(string.join(string.split(os.getcwd(), os.sep)[:-1], os.sep))
if sys.platform[:3]=="win":
	from shared.fileIndexation import windows
else:
	from shared.fileIndexation import linux

class fileIndexer:

	def __init__(self):
		if sys.platform[:3]=="win":
			self.data		= windows.fileIndexer()
			self.localslash	= "\\"
		else:
			self.data		= linux.fileIndexer()
			self.localslash	= "/"

		self.publicslash= "/"
		self.dirs		= []
		self.dircontent	= None

	def __getitem__(self, index):
		item	= self.getNext()
		if item!=None:
			return item
		else:
			raise IndexError

	def addPublicDirs(self):
#		print "addpublicdirs"
		self.dirs = self.data.getPublicDirs()

	def addDir(self, local, public):
		""" add a directory to be processed """
		entry			= {}
		entry['local']	= local
		entry['public'] = public
		self.dirs.append(entry)
		self.dircontent	= self.processDirectory(entry)

	def processDirectory(self, directory):

		dircontent	= os.listdir(directory['local'])

		# since removing items from a structure while iterating it
		# poses some troubles, a different approach is used:
		# first, create an actual copy (impossible with a simple a=b statement)
		# then, remove the items that need to be removed from _this_
		# structure, not from the structure being iterated
		newdircontent	= os.listdir(directory['local'])
		for item in dircontent:
			if os.path.isdir(directory['local']+self.localslash+item):
				newItem				= {}
				newItem['local']	= directory['local'] + self.localslash + item
				newItem['public']	= directory['public'] + self.publicslash + item
				self.dirs.append(newItem)
				newdircontent.remove(item)

		return newdircontent

	def getNext(self):
		""" return the next file from the directories set
			by either setDirs or addPublicDirs """
		if len(self.dirs) == 0:
			self.dirs		= self.addPublicDirs()

			if self.dirs != None:
				self.dircontent	= self.processDirectory(self.dirs[0])

		if self.dirs != None:
			while (self.dircontent==None) or (len(self.dircontent)==0):
				self.dirs.remove(self.dirs[0])
	
				if len(self.dirs) == 0:
					return None
				else:
					self.dircontent	= self.processDirectory(self.dirs[0])
	
			if len(self.dircontent)>0:
				item 	= self.dircontent[0]
				self.dircontent.remove(item)
	
				answer			= {}
				answer['local']	= self.dirs[0]['local'] + self.localslash + item
				answer['public']= self.dirs[0]['public'] + self.publicslash + item
	
				return	answer
			else:
				return 	None # should not occur
		else:
			return None


if __name__=="__main__":
	fileindex	= fileIndexer()

#	fileindex.addPublicDirs()
	fileindex.addDir(u'd:\\download', "http://www.14hoog.net/download")

 	for dir in fileindex.dirs:
 		print "DIR:", dir['local']
	i	= 0
	print fileindex.dirs
	for file in fileindex:
		i	= i+1
		print file['local']
		print file['public']

	print "Aantal:", i
