[skip to claim about Google Sitemaps](#sitemaps)

What is WebIndex?
-----------------

WebIndex is a software tool that helps people and organisations
maintain a complete and up-to-date index of web pages on their
web site. Having such an index is helpful for both the web site
maintainer and the (potential) visitor of the web site.

For web site maintainers, it means that a larger part of the web
site can be indexed by search engines. If more of your web pages
are visited by a search engine, such as Google, it is less likely
that information you provide on your web site is overlooked. It
might even help you attract more visitors to your web site.

For web site visitors, it means that it is more likely to find
the information you are searching for. Why is this? Well, since
more web pages are found by search engines, it is more likely
that the web page of your likings turns up.

If you are interested in WebIndex, then feel free to visit our
web site. WebIndex is a free (open source) program that runs on
both Windows and Linux web servers and was originally developed
at the Delft University of Technology in the Netherlands.

WebIndex is © 2003 Edward Akerboom and is released under the GNU
Public License


Installation
------------

WebIndex has been written to be used in both Windows and Linux
environments, and was designed to efficiently cooperate with both
Apache and IIS webservers. WebIndex potentially supports a whole
range of different databases, but at the moment your choice is
limited to ODBC database connections.

Support for other webservers, databases, output plugins and
scripting languages can be added quite easily.

WebIndex is written in Python, a highly portable programming
language. If you want to mess around with the sourcecode, then
feel free to do so. Python 2.2, the ctypes module and a working
ODBC setup are required. In Linux, the only ODBC-package I have
tested this with is iODBC.

To install WebIndex, simply extract all files from the archive. To
create a valid configuration file, it is recommended that you run
'setup' first. This tries to ease the burden of creating a valid
setup, something which is not entirely trivial. The setup program
requires a graphical display. A setup program that can be run from
the command line is planned, but it is uncertain when these plans
will take shape.

If you prefer not to use the setup program (not recommended), you may
also resort to manually specifying a configuration file. An example
of a valid configuration file can be found in the same directory you 
found this README.TXT file, in a file named "webindex.ini". If you
do not use the setup program, you will also need to manually install
a 'stub' file in a location accessible from the web.


Testing the setup
-----------------

If you have either run the setup program or manually installed
WebIndex, then now is the time to test your setup. Open a browser
and type in the URL that points to where you installed the stub
file (webindex.php). You can also copy-paste the URL that was given
to you by the setup program.

If all is well, then you should be presented with a nice Site
Overview that lists (a subsection of) all available URLs on your
web site. Instead, you might also get an errormessage. It is
possible that you get some complaints about not being able to
write to the cache-file. This can be fixed by editing your 
webindex.ini configurationfile, uncommenting the 'file' variable 
in the 'cache' section, and pointing it to some location where
anyone has write-access (for example, /tmp/webindex.web).

If this doesn't fix the problem, then try to validate your database
setup. If both your database- and your cache-setup are correct,
then WebIndex should be able to at least list the contents of the 
directories you specified in the 'directory' section.

Other problems might pop up. In that case, you're on your own.

In the end, if you have everything up and running, you have a nice
system that maintains an up-to-date index of all the files and
dynamic web pages on your web server. If properly linked to, this
can help you gain visibility with the major search engines. Also, 
you will help decrease the size of the ever expanding Deep Web (see
http://www.brightplanet.com/technology/deepweb.asp, for example).


Future work
-----------

Please remember that this software is still very very beta.
Although I have put in months of work, I think it is unavoidable
that this program still contains a lot of bugs. For now, I will 
not fix these bugs; writing my master's thesis is more important 
at the moment. FYI, my master's thesis will be based on the
concept and implementation of this piece of software.

I will probably have time for this program after I have written
my master's thesis and have taken a few months off. I will still
put effort into this program, since I think it is the only way
to effectively create an infrastructure that allows an efficient
manner of indexing the web. Webcrawlers are a hack, outdated,
inefficient and insufficient. Without webcrawlers, there wouldn't
be a deep web (how 'bout that? ;))

There is still a loooooot of room for improvement. Here, I will 
name the most important. Feel free to start implementing these
without me :)

- A command line setup tool
- A mySQL database interface
- An ASP 'stub'
- Speed improvements
- A useful and well designed XML output format + -plugin
- Raising awareness (do some marketing)


License
-------
This program is licensed under the GNU Public License.


<a name='sitemaps'></a>

Google Sitemaps?
================

Background (updated 2017)
-------------------------
As said, I wrote this code for my Master's thesis way back in 2003.  
After I finished my thesis and got a job, I went for dinner with 
some study friends and some guys from Google who were visiting 
Europe on a study trip. I told the Google guys about this project 
and what I tried to achieve. They were very interested, but I never
heard from them again.

However, half a year later I heard about a new Google initiative called
"Google Sitemaps". It basically did everything I had told these guys,
and a very basic first version of their code, only a few hundred lines 
long, was released 6 (!!) days after my conversation with them. 
 
Uncharacteristically, they released their source on Sourceforge, which
was very odd even back then. The whole thing was very suspicious to me,
and it still is now (14 years later).

Based on this I suspect that my Master's thesis, and the code in this 
repository, was the initial inspiration for what is now known as Google 
Sitemaps.
  
How do I feel about that? Hmm. Good question! Slightly bitter, I guess. 
Mostly because I went uncredited and because I didn't get a fancy job
at Google in return. But I can't prove that this is how it went down,
so there's that. So, if any Googler is reading this: hit me up ;-)