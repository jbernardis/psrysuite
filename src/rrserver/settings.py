import os
import configparser
import logging

INIFILE = "psry.ini"
GLOBAL = "global"

def parseBoolean(val, defaultVal):
	lval = val.lower()
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "server"	
		
		self.echoTurnout = True
		self.simulation = True
		self.serverport = 9000
		self.socketport = 9001
		self.tty = "COM4"
		self.busInterval = 0.4
		self.topulselen = 4
		self.nxbpulselen = 4

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return

		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'echoturnout':
					self.echoTurnout = parseBoolean(value, False)

				elif opt == 'simulation':
					self.simulation = parseBoolean(value, False)

				elif opt == "tty":
					self.tty = value

				elif opt == "businterval":
					self.businterval = float(value)

				elif opt == "topulselen":
					self.topulselen = int(value)

				elif opt == "nxbpulselen":
					self.nxbpulselen = int(value)

		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
			
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'socketport':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for socket port: (%s)" % value)
						s = 9001
					self.socketport = s
						
				elif opt == 'serverport':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for server port: (%s)" % value)
						s = 9000
					self.serverport = s
		else:
			logging.warning("Missing global section - assuming defaults")
