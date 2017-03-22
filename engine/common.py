import string

def newItem(url=None, post=None, metatags=None):
	""" return a new 'item' """
	
	# This is not the only place where items are made. In
	# the main sourcefile, check out the __getItems() function
	item	= {}
	item['url']		= url
	if post != None:
		item['post']	= post
	return item
	
def getHTTPValue(argumentname, parameters):
	""" get a specific value from a 'name=value'-list """
	argumentname	= string.strip(string.lower(argumentname))
	if parameters!=None:
		for parameter in parameters:
			parts	= string.split(parameter, "=")
			if string.lower(string.strip(parts[0])) == argumentname:
				return string.join(parts[1:], "=")

def justify(text, width):
	""" return a string where 'text' is split over multiple justified
		lines with a maximum length of 'width'. """
		# and most of the time, that maximum-length is actually correct :)

	def __wordlen(words):
		return reduce(lambda x,y:x + len(y), words, 0)

	answer	= ""

	while len(text)>width:
		line	= text[:width]
		line	= line[:string.rfind(line, " ")]
		words	= string.split(line)

        # determine how much spaces we have to add
		addspaces= width - __wordlen(words)

		# and how much gaps we have
		gaps	= len(words) - 1
		extra	= addspaces - gaps

		# calculate how much space we have to
		# distribute per gap
		pergap	= float(100*extra) / float(gaps)

		# keep a sum handy
		pergap_sum	= 0.0
		aligned		= ""
		for word in words:
			aligned 	+= word + " "
			pergap_sum 	+= pergap

			while pergap_sum > 102: # allow a 2% error-margin
				aligned 	+= " "
				pergap_sum 	-= 100

		text	= text[len(line)+1:]

		answer	= "%s%s\n" % (answer, aligned)

	answer	= "%s%s" % (answer, text)

	return answer
