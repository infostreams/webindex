import	timeoutsocket
import 	urllib
import	string

def _error(filehandle):
	connectionhandle	= urllib.getConnectionHandle()
	try:
		connectionhandle.close()
	except:
		pass
	try:
		filehandle.close()
	except:
		pass

	return 0

def testURL(url, timeout=10):
	if url.has_key('post'):
		if url['post']!='':
			post	= url['post']
		else:
			post	= None
	else:
		post	= None

	if url.has_key('url'):
		url		= url['url']
	else:
		url		= None

	timeoutsocket.setDefaultSocketTimeout(timeout)

#	print "testing %s with post %s" % ( url, post)
	handle		= None
	try:
		handle	= urllib.urlopen(url, post)
	except IOError:
		print "IOError"
		return _error(handle)
	except timeoutsocket.Timeout:
		print "timeout"
		return _error(handle)
	else:
		html		= handle.readlines()
		errors		= ["404", "error", "not found", "fatal error", "document not found", "page not found"]
		handle.close()

		errorcount	= 0
		for line in html:
			line			= string.lower(line)
			for error in errors:
				if string.find(line, error)>-1:
					errorcount	+= 1

		if errorcount>2:
			return 0
		else:
			return 1

if __name__=="__main__":
#	print testURL({'url':"http://www.14hoog.net/", 'post':''})
#	for arg	in [108, 120, 123, 127, 104, 125, 103, 998, 120, 1, 35]:
	for arg	in range(1,5):
#		url	= "http://www.14hoog.net/test.php"
#		url	= "http://localhost/?pagina=%d&sub=1" % arg
		url	= "http://beestje/index.shtml?pagina=x&pagina=%d" % arg
#		url	= "http://www.14hoog.net/index.php"
		print "%s: %s" % (url, testURL({'url':url, 'post':''}))
#		testURL({'url':url, 'post':''})
