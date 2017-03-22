def item(a, b):
	print "<item>"
	print "	url =", a
	print "	post =", b
	print "</item>"


for i in range(60):
	item("ed%d" % (i, ), "ja")

