import os
import configparser
import logging

INIFILE = "psry.ini"
GLOBAL = "global"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "simulator"	

		self.ipaddr = "192.168.1.144"
		self.dccserverport = 9002
		self.serverport = 9000

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
						logging.warning("invalid value in ini file for dcc server port: (%s)" % value)
						s = 9002
					self.dccserverport = s
						
				elif opt == 'serverport':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for server port: (%s)" % value)
						s = 9000
					self.serverport = s
						
				elif opt == 'ipaddr':
					self.ipaddr = value

		else:
			logging.warning("Missing global section - assuming defaults")
