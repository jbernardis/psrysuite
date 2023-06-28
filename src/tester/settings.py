import os
import configparser
import logging

INIFILE = "psry.ini"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "rrserver"	
		
		self.rrtty = "COM5"

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return

		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == "rrtty":
					self.rrtty = value
		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
