import _winreg
import string

class fileIndexer:

	def __init__(self):
		pass

	def getPublicDirs(self, configfilename=None):
		# get the public dirs serviced by IIS from the registry.
		#
		# this information is (on my own machine :)) located at
		# HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters\Virtual Roots
		#
		# TODO: Add support for user-specified directories
		key	= _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\W3SVC\\Parameters\\Virtual Roots")
		i	= 0
		dirs= []

		try:
			while (1):
				value			= _winreg.EnumValue(key, i)
				parts			= string.split(value[1], ",")
				dir				= {}
				dir['local']	= parts[0]
				dir['public']	= value[0]
				dirs.append(dir)
				i	= i + 1
		except EnvironmentError:
			pass
		return dirs
