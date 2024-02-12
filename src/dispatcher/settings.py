import configparser
import os
import logging
import wx

INIFILE = "psry.ini"
GLOBAL = "global"


def parseBoolean(val, defaultVal):
	lval = val.lower()
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Debug:
	def __init__(self):
		self.showaspectcalculation = False
		self.loglevel = "DEBUG"


class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "dispatcher"
		
		self.pages = 3
		self.dispatch = True
		self.ipaddr = "192.168.1.138"
		self.serverport = 9000
		self.socketport = 9001
		self.showcameras = False
		self.allowatcrequests = True
		self.precheckshutdownserver = True
		self.activesuppressyards = True
		self.activesuppressunknown = False
		self.activeonlyatc = False
		self.activeonlyassigned = False
		self.activeonlyassignedorunknown = False
		self.clockstarttime = 355
		self.matrixturnoutdelay = 2
		self.showevents = False
		self.showadvice = False
		
		self.debug = Debug()
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return

		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'pages':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for pages: (%s)" % value)
						s = 3

					if s not in [1, 3]:
						logging.warning("Invalid values for pages: %d" % s)
						s = 3
					self.pages = s

				elif opt == 'dispatch':
					self.dispatch = parseBoolean(value, False)

				elif opt == 'precheckshutdownserver':
					self.precheckshutdownserver = parseBoolean(value, True)

				elif opt == 'activesuppressyards':
					self.activesuppressyards = parseBoolean(value, True)

				elif opt == 'activesuppressunknown':
					self.activesuppressunknown = parseBoolean(value, False)

				elif opt == 'activeonlysassignedorunknown':
					self.activeonlyassignedorunknown = parseBoolean(value, False)

				elif opt == 'activeonlysassigned':
					self.activeonlyassigned = parseBoolean(value, False)

				elif opt == 'activeonlyatc':
					self.activeonlyatc = parseBoolean(value, False)

				elif opt == 'showcameras':
					self.showcameras = parseBoolean(value, False)
					
				elif opt == 'matrixturnoutdelay':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for matrix turnout delay: %s" % value)
						s = 2
					self.matrixturnoutdelay = s
					
				elif opt == 'clockstarttime':
					try:
						s = int(value)
					except:
						logging.warning("invalid value in ini file for clock start timer: %s" % value)
						s = 355
					self.clockstarttime = s


		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
			
		if self.cfg.has_section("display"):
			for opt, value in self.cfg.items("display"):
				if opt == 'allowatcrequests':
					self.allowatcrequests = parseBoolean(value, False)
				elif opt == 'showevents':
					self.showevents = parseBoolean(value, False)
				elif opt == 'showadvice':
					self.showadvice = parseBoolean(value, False)
			
		if self.cfg.has_section("debug"):
			for opt, value in self.cfg.items("debug"):
				if opt == 'showaspectcalculation':
					self.debug.showaspectcalculation = parseBoolean(value, False)
				elif opt == 'loglevel':
					self.debug.loglevel = value
				
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
						
				elif opt == 'ipaddr':
					self.ipaddr = value

		else:
			logging.warning("Missing global section - assuming defaults")
