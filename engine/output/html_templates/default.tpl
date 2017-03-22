# This is a HTML template for the WebIndex indexing engine
# --------------------------------------------------------
#
# The resulting HTML is composed by inserting the HTML from the
# sections below as follows:
#
# [header]
# [item]
# [item]
# [item]
# .... (etc)
# [item]
# [previouspage]
# [nextpage]
# [footer]
#
#
# You can specify which HTML template to use in the webindex.ini
# configuration file, in the following manner:
#
# <html>
#  template = "template-filename"
#  chunksize= 25
# </html>
##################

# The section between the [header] and [/header] tags
# define the header of the HTML page
##################
[header]
<html>
<head>
	<title>Site overview</title>
	<style>
		a	{font-face:verdana, arial, helvetica; font-weight: bold; text-decoration: none; color:black}
		a:hover	{text-decoration: underline; }
		a.white	{font-face:verdana, arial, helvetica; font-weight: bold; text-decoration: none; color:white}
		a.white:hover	{text-decoration: underline; }
		hr { border: 0px #D42424 solid; border-top-width: 2px; height: 2px; }
	</style>
</head>
<body topmargin='0' leftmargin='0' marginwidth='0' marginheight='0'>

<!-- Define table -->
<table cellspacing='0' cellpadding='0' height='100%' width='100%'>
<tr>
	<!-- Left column -->
	<td bgcolor='#D42424' width='250' valign='top'>
		<table cellspacing='0' cellpadding='0' height='100%' width='100%'>
		<tr>
			<td valign='top'>
				<center>
				<br><br>
				<font face='verdana, arial, helvetica' size='5' color='white'><b><u>&nbsp;&nbsp;WebIndex&nbsp;&nbsp;</u></b></font>
				</center>

				<table cellspacing=10 cellpadding=10>
				<tr>
				<td>
					<font face='verdana, arial, helvetica' color='white' size='2'>
					<p align='justify'>
					<b><a href='http://webindex.sourceforge.net/' target='_new2' class='white'><u>WebIndex</u></a> is a software tool
					that helps people and organisations maintain a complete and up-to-date index of web
					pages on their web site. Having such an index is helpful for both the web site
					maintainer and the (potential) visitor of the web site.</b>
					<br><br>

					For web site maintainers, it means that a larger part of the web site can be
					indexed by search engines. If more of your web pages are visited by a search
					engine, such as Google, it is less likely that information you provide on your
					web site is overlooked. It might even help you attract more visitors to your
					web site.<br><br>

					For web site visitors, it means that it is more likely to find the information
					you are searching for. Why is this? Well, since more web pages are found by
					search engines, it is more likely that the web page of your likings turns up.
					<br><br>

					If you are interested in WebIndex, then feel free to
					<a href='http://webindex.sourceforge.net/' target='_new3' class='white'>visit our web site</a>.
					WebIndex is a free (open source) program that runs on both Windows and Linux web servers
					and was originally developed at the
					<a href='http://www.tudelft.nl/' target='_new4' class='white'>Delft University of Technology</a>
					in the Netherlands.<br><br>

					WebIndex is &copy; 2003 Edward Akerboom<br>
					</font>
				</td>
				</tr>
				</table>
		</tr>
		</table>
	</td>

	<!-- Right column -->
	<td bgcolor='#FFFFFF' valign='top'>

		<!-- Top line -->
		<table cellspacing='0' cellpadding='0' width='100%'>
		<tr>
			<td width='10'>&nbsp;</td>
			<td width='500'>
				<font face='verdana, arial, helvetica' size='7' color='black'>Site overview</font>
			</td>
		</tr>
		</table>

		<!-- First horizontal line -->
		<hr bgcolor='#D42424' width='100%'>

		<table cellspacing='0' cellpadding='0' width='100%'>
		<tr>
			<td width='10'>&nbsp;</td>
			<td width='500'>
				<font face='verdana, arial, helvetica' size='2' color='black'>
				This page contains an overview of all the web pages on this web site. While this
				"sitemap" is primarily intended for search engines it might also be of use to you.
				<br><br>
				This web site contains the following web pages:<br>
			</font>
			</td>

		</tr>
		</table>

		<!-- Second horizontal line -->
		<hr color='#D42424' width='25%' align='left'>

		<table cellspacing='0' cellpadding='0' width='100%'>
		<tr>
			<td width='20' rowspan='2' >&nbsp;</td>
			<td>
				<font face='verdana, arial, helvetica' size='2' color='black'>
[/header]

# The following section is included for each item
# Allowed 'variables': [url] and [post]
##################
[item]
					<a href='[url]'>[url]</a><br>
[/item]

# The following section is included after the 'items' section
# Allowed 'variable': none
##################
[enditem]
				</font>
			</td>
		</tr>
		<tr>
			<td>
				<table width='100%' cellspacing='0' cellpadding='0'>
				<tr>
					<td colspan='2' height='20'>&nbsp;</td>
				</tr>
				<tr>
[/enditem]

# The following section is included on the bottom of the page
# if a previous page of URLs is present
# Allowed 'variable': [previouspageurl]
##################
[previouspage]
					<td>
						<font face='verdana, arial, helvetica' size='2' color='black'>
						<a href='[previouspageurl]'>&lt;&lt; Previous</a>
						</font>
					</td>
[/previouspage]

# The following section is included on the bottom of the page
# if a next page of URLs is present
# Allowed 'variable': [nextpageurl]
##################
[nextpage]
					<td>
						<font face='verdana, arial, helvetica' size='2' color='black'>
						<a href='[nextpageurl]'>Next &gt;&gt;</a>
						</font>
					</td>
[/nextpage]

# The section between the [footer] and [/footer] tags
# define the footer of the HTML page
##################
[footer]
				</tr>
				</table>
			</td>
		</tr>
		</table>

		<!-- Last horizontal line -->
		<hr color='#D42424' width='25%' align='left'>
		<table cellspacing='0' cellpadding='0' width='100%'>
		<tr>
			<td width='10'>&nbsp;</td>
			<td width='500'>
				<font face='verdana, arial, helvetica' size='2' color='black'>
				This sitemap was generated with <a href='#webindex'>WebIndex</a>, the free open source
				web indexing tool.
				</font>
			</td>
		</tr>
		</table>
	</td>
</tr>
</table>

</body>
</html>
[/footer]
