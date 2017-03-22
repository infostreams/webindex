import output

class text(output.output):
	def displayItem(self, item):
		print "--------"
#		print "<item>"
		for key in item.keys():
			print "	%s = %s" % (key, item[key])
#		print "</item>"

	def help(self):
		output.output.default_help(self, __name__)
