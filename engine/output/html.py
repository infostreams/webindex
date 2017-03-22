#display html from=0 to=10 caller=http://www.14hoog.net/~edward/afstuderen/index.php?output=html

import output
import string
import pprint
import common
from shared import XMLConfig


class html(output.output):
	def __init__(self, config):
		output.output.__init__(self, config)
		templatename		= XMLConfig.getUnnamedEntryVariable('html', 0, 'template', config)
		try:
			self.chunksize	= atoi(XMLConfig.getUnnamedEntryVariable('html', 0, 'chunksize', config))
		except:
			self.chunksize	= None
		if self.chunksize == None:	# also the case if no 'chunksize' variable was found
			self.chunksize	= 100

		self.printeditems	= 0
		try:
			f				= open(templatename, 'r')
			self.template	= f.readlines()
			f.close()
#			pprint.pprint(self.template)
		except:
			# hard-coded default template :)
			self.template	= ['[header]\n', '<html>\n', '<head>\n', '\t<title>Site overview</title>\n', '\t<style>\n', '\t\ta\t{font-face:verdana, arial, helvetica; font-weight: bold; text-decoration: none; color:black}\n', '\t\ta:hover\t{text-decoration: underline; }\n', '\t\ta.white\t{font-face:verdana, arial, helvetica; font-weight: bold; text-decoration: none; color:white}\n', '\t\ta.white:hover\t{text-decoration: underline; }\n', 'hr { border: 0px #D42424 solid; border-top-width: 2px; height: 2px; }',
			 '\t</style>\n', '</head>\n', "<body topmargin='0' leftmargin='0' marginwidth='0' marginheight='0'>\n", '\n', '<!-- Define table -->\n', "<table cellspacing='0' cellpadding='0' height='100%' width='100%'>\n", '<tr>\n', '\t<!-- Left column -->\n', "\t<td bgcolor='#D42424' width='250' valign='top'>\n", "\t\t<table cellspacing='0' cellpadding='0' height='100%' width='100%'>\n", '\t\t<tr>\n', "\t\t\t<td valign='top'>\n", '\t\t\t\t<center>\n', '\t\t\t\t<br><br>\n',
			 "\t\t\t\t<font face='verdana, arial, helvetica' size='5' color='white'><b><u>&nbsp;&nbsp;WebIndex&nbsp;&nbsp;</u></b></font>\n", '\t\t\t\t</center>\n', '\n', '\t\t\t\t<table cellspacing=10 cellpadding=10>\n', '\t\t\t\t<tr>\n', '\t\t\t\t<td>\n', "\t\t\t\t\t<font face='verdana, arial, helvetica' color='white' size='2'>\n","\t\t\t\t\t<p align='justify'>\n", "\t\t\t\t\t<b><a href='http://webindex.sourceforge.net/' target='_new2' class='white'><u>WebIndex</u></a> is a software tool\n",
			 '\t\t\t\t\tthat helps people and organisations maintain a complete and up-to-date index of web\n', '\t\t\t\t\tpages on their web site. Having such an index is helpful for both the web site\n', '\t\t\t\t\tmaintainer and the (potential) visitor of the web site.</b>\n', '\t\t\t\t\t<br><br>\n', '\n', '\t\t\t\t\tFor web site maintainers, it means that a larger part of the web site can be\n', '\t\t\t\t\tindexed by search engines. If more of your web pages are visited by a search\n',
			 '\t\t\t\t\tengine, such as Google, it is less likely that information you provide on your\n', '\t\t\t\t\tweb site is overlooked. It might even help you attract more visitors to your\n', '\t\t\t\t\tweb site.<br><br>\n', '\n', '\t\t\t\t\tFor web site visitors, it means that it is more likely to find the information\n', '\t\t\t\t\tyou are searching for. Why is this? Well, since more web pages are found by\n', '\t\t\t\t\tsearch engines, it is more likely that the web page of your likings turns up.\n',
			 '\t\t\t\t\t<br><br>\n', '\n', '\t\t\t\t\tIf you are interested in WebIndex, then feel free to\n', "\t\t\t\t\t<a href='http://webindex.sourceforge.net/' target='_new3' class='white'>visit our web site</a>.\n", '\t\t\t\t\tWebIndex is a free (open source) program that runs on both Windows and Linux web servers\n', '\t\t\t\t\tand was originally developed at the\n', "\t\t\t\t\t<a href='http://www.tudelft.nl/' target='_new4' class='white'>Delft University of Technology</a>\n",
			 '\t\t\t\t\tin the Netherlands.<br><br>\n', '\n', '\t\t\t\t\tWebIndex is &copy; 2003 Edward Akerboom<br>\n', '\t\t\t\t\t</font>\n', '\t\t\t\t</td>\n', '\t\t\t\t</tr>\n', '\t\t\t\t</table>\n', '\t\t</tr>\n', '\t\t</table>\n', '\t</td>\n', '\n', '\t<!-- Right column -->\n', "\t<td bgcolor='#FFFFFF' valign='top'>\n", '\n', '\t\t<!-- Top line -->\n', "\t\t<table cellspacing='0' cellpadding='0' width='100%'>\n", '\t\t<tr>\n', "\t\t\t<td width='10'>&nbsp;</td>\n",
			 "\t\t\t<td width='500'>\n", "\t\t\t\t<font face='verdana, arial, helvetica' size='7' color='black'>Site overview</font>\n", '\t\t\t</td>\n', '\t\t</tr>\n', '\t\t</table>\n', '\n', '\t\t<!-- First horizontal line -->\n', "\t\t<hr color='#D42424' width='100%'>\n", '\n', "\t\t<table cellspacing='0' cellpadding='0' width='100%'>\n", '\t\t<tr>\n', "\t\t\t<td width='10'>&nbsp;</td>\n", "\t\t\t<td width='500'>\n", "\t\t\t\t<font face='verdana, arial, helvetica' size='2' color='black'>\n",
			 '\t\t\t\tThis page contains an overview of all the web pages on this web site. While this\n', '\t\t\t\t"sitemap" is primarily intended for search engines it might also be of use to you.\n', '\t\t\t\t<br><br>\n', '\t\t\t\tThis web site contains the following web pages:<br>\n', '\t\t\t</font>\n', '\t\t\t</td>\n', '\n', '\t\t</tr>\n', '\t\t</table>\n', '\n', '\t\t<!-- Second horizontal line -->\n', "\t\t<hr color='#D42424' width='25%' align='left'>\n", '\n',
			 "\t\t<table cellspacing='0' cellpadding='0' width='100%'>\n", '\t\t<tr>\n', "\t\t\t<td width='20' rowspan='2' >&nbsp;</td>\n", '\t\t\t<td>\n', "\t\t\t\t<font face='verdana, arial, helvetica' size='2' color='black'>\n", '[/header]\n', '[item]\n', "\t\t\t\t\t<a href='[url]'>[url]</a><br>\n", '[/item]\n', '[enditem]\n', '\t\t\t\t</font>\n', '\t\t\t</td>\n', '\t\t</tr>\n', '\t\t<tr>\n', '\t\t\t<td>\n', "\t\t\t\t<table width='100%' cellspacing='0' cellpadding='0'>\n", '\t\t\t\t<tr>\n',
			 "\t\t\t\t\t<td colspan='2' height='20'>&nbsp;</td>\n", '\t\t\t\t</tr>\n', '\t\t\t\t<tr>\n', '[/enditem]\n', '[previouspage]\n', '\t\t\t\t\t<td>\n', "\t\t\t\t\t\t<font face='verdana, arial, helvetica' size='2' color='black'>\n", "\t\t\t\t\t\t<a href='[previouspageurl]'>&lt;&lt; Previous</a>\n", '\t\t\t\t\t\t</font>\n', '\t\t\t\t\t</td>\n', '[/previouspage]\n', '[nextpage]\n', '\t\t\t\t\t<td>\n', "\t\t\t\t\t\t<font face='verdana, arial, helvetica' size='2' color='black'>\n",
			 "\t\t\t\t\t\t<a href='[nextpageurl]'>Next &gt;&gt;</a>\n", '\t\t\t\t\t\t</font>\n', '\t\t\t\t\t</td>\n', '[/nextpage]\n', '[footer]\n', '\t\t\t\t</tr>\n', '\t\t\t\t</table>\n', '\t\t\t</td>\n', '\t\t</tr>\n', '\t\t</table>\n', '\n', '\t\t<!-- Last horizontal line -->\n', "\t\t<hr color='#D42424' width='25%' align='left'>\n", "\t\t<table cellspacing='0' cellpadding='0' width='100%'>\n", '\t\t<tr>\n', "\t\t\t<td width='10'>&nbsp;</td>\n", "\t\t\t<td width='500'>\n",
			 "\t\t\t\t<font face='verdana, arial, helvetica' size='2' color='black'>\n", "\t\t\t\tThis sitemap was generated with <a href='#webindex'>WebIndex</a>, the free open source\n", '\t\t\t\tweb indexing tool.\n', '\t\t\t\t</font>\n', '\t\t\t</td>\n', '\t\t</tr>\n', '\t\t</table>\n', '\t</td>\n', '</tr>\n', '</table>\n', '\n', '</body>\n', '</html>\n', '[/footer]\n']

	def parseRequest(self, parameters):
		# identical to output.parseRequest, but stores answer
		answer		= {}

		try:
			answer['from']	= string.atoi(common.getHTTPValue('from', parameters))
			answer['to']	= string.atoi(common.getHTTPValue('to', parameters))
		except:
			answer			= {'from':0, 'to': self.chunksize}

		self.answer			= answer
		self.caller			= common.getHTTPValue('caller', parameters)
		return answer

	def getHTMLforSection(self, name):
		if self.template != None:
			include = 0
			answer	= ""
			name	= string.lower(name)
			for line in self.template:
				linecontents	= string.strip(string.lower(line))
				if linecontents == "[/" + name + "]":
					include = 0

				if include == 1:
					answer += line

				if linecontents == "[" + name + "]":
					include = 1
#			return string.rstrip(answer)
			return answer
		else:
			return ""

	def getHTMLforItem(self, item):
		html	= self.getHTMLforSection('item')

		if item.has_key('url'):
			html	= string.replace(html, '[url]', item['url'])
		else:
			html	= string.replace(html, '[url]', "")

		if item.has_key('post'):
			html	= string.replace(html, '[post]', item['post'])
		else:
			html	= string.replace(html, '[post]', "")

		self.printeditems	+= 1
		return html

	def getHTMLforPreviousPage(self):
		if self.answer['from']<self.chunksize:
			_from	= 0
		else:
			_from 	= self.answer['from'] - self.chunksize
		url		= "%s&from=%d&to=%d" % (self.caller, _from, _from+self.chunksize)

		previous= self.getHTMLforSection('previouspage')
		previous= string.replace(previous, "[previouspageurl]", url)
		return previous

	def getHTMLforNextPage(self):
		_from 	= self.answer['from'] + self.chunksize
		url		= "%s&from=%d&to=%d" % (self.caller, _from, _from+self.chunksize)

		next	= self.getHTMLforSection('nextpage')
		next	= string.replace(next, "[nextpageurl]", url)
		return next

	def display(self, items):

		# display header
		html	= self.getHTMLforSection('header')

		# display items
		for item in items:
			html	+= self.getHTMLforItem(item)

		# display 'enditem'
		html	+= self.getHTMLforSection('enditem')

		# if necessary, display 'previous page'
		if self.answer['from']>0:
			html	+= self.getHTMLforPreviousPage()

		# if necessary, display 'next page'
		if self.printeditems==self.chunksize:
			html	+= self.getHTMLforNextPage()

        # display footer
		html	+= self.getHTMLforSection('footer')

		print string.rstrip(html),

	def help(self):
		output.output.default_help(self, __name__)
