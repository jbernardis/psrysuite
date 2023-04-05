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
		self.section = "rrserver"	
		
		self.simulation = True
		self.ipaddr = None
		self.serverport = 9000
		self.socketport = 9001
		self.dccserverport = 9002
		self.rrtty = "COM5"
		self.dcctty = "COM6"
		self.busInterval = 0.4
		self.topulselen = 2
		self.topulsect = 3
		self.nxbpulselen = 4
		self.nxbpulsect = 2
		self.startDispatch = False
		self.hide = False
		self.viewiobits = False

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return

		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'simulation':
					self.simulation = parseBoolean(value, False)

				elif opt == 'startdispatch':
					self.startDispatch = parseBoolean(value, False)

				elif opt == 'hide':
					self.hide = parseBoolean(value, False)

				elif opt == 'viewiobits':
					self.viewiobits = parseBoolean(value, False)

				elif opt == "rrtty":
					self.rrtty = value

				elif opt == "dcctty":
					self.dcctty = value

				elif opt == "businterval":
					self.businterval = float(value)

				elif opt == "topulselen":
					self.topulselen = int(value)

				elif opt == "topulsect":
					self.topulsect = int(value)

				elif opt == "nxbpulselen":
					self.nxbpulselen = int(value)

				elif opt == "nxbpulsect":
					self.nxbpulsect = int(value)

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
						
				elif opt == 'dccserverport':
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
