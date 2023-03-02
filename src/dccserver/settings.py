import os
import configparser
import logging

INIFILE = "psry.ini"
GLOBAL = "global"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "dccserver"	

		self.ipaddr = "192.168.1.144"
		self.dccserverport = 9002
		self.tty = "COM5"

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return
			
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'dccserverport':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for DCC server port: (%s)" % value)
						s = 9002
					self.dccserverport = s
						
				elif opt == 'ipaddr':
					self.ipaddr = value

		else:
			logging.warning("Missing global section - assuming defaults")
			
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'tty':
					self.tty = s

		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
