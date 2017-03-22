import output
import string
#import urllib

class xml(output.output):

	def displayItem(self, item):
		print "<item>"
		for key in item.keys():
			cleaned	= string.replace(item[key], "&", "&amp;")
#			cleaned	= urllib.quote(item[key])

			print "	<%s>%s</%s>" % (key, cleaned, key)
		print "</item>"

	def displayHeader(self):
		print "<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>"
		print "<druid>"

	def displayFooter(self):
		print "</druid>"

	def displayHTTPHeader(self):
		print "Content-type: text/xml; charset=utf-8"

	def help(self):
		output.output.default_help(self, __name__)
