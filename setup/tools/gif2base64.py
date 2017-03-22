# gif2base64 (c) 2003 Edward Akerboom
# released under the GPL

import string
import os.path
import os
import base64
import pprint

# define image to use
file	= "d:\\prog\\python\\setup\\line.gif"

# create output filename
dir, name= os.path.split(file)
out		= dir + os.sep + string.split(name, ".")[0] + ".py"

# open both input and outputfiles
gif		= os.open(file, os.O_BINARY)
b64		= open(out, "w")

# read the data from the inputfile
data	= os.read(gif, 1024)
newdata	= "not-zero"
while len(newdata)>0:
	newdata	= os.read(gif, 1024)
	data	+= newdata

# encode it to base64 and convert this data to an array of lines
b64data	= string.split(base64.encodestring(data), "\n")

# remove potential empty lines from it (ugly in outputfile)
for line in b64data:
	if len(line)==0:
		b64data.remove(line)

# write an aptly named variable-declaration
# (so you can use webindex.gif to refer to the base64 data, instead of "webindex.gif" :))
b64.write("gif	= ")

# write most of the base64-data....
for line in b64data[:-1]:
	b64.write('"' + line + '" \\\n')

# but don't write a '\' after the last line
b64.write('"' + b64data[-1] + '"')

# done!
b64.close()
os.close(gif)
