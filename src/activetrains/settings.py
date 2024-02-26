import configparser
import os
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

class Debug:
	def __init__(self):
		self.showaspectcalculation = False
		self.loglevel = "DEBUG"


class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "dispatcher"
		
		self.ipaddr = "192.168.1.138"
		self.serverport = 9000
		self.socketport = 9001
		self.activesuppressyards = True
		self.activesuppressunknown = False
		self.activeonlyatc = False
		self.activeonlyassigned = False
		self.activeonlyassignedorunknown = False
		self.activetrainlines = 10
		
		self.debug = Debug()
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return
			
		if self.cfg.has_section("debug"):
			for opt, value in self.cfg.items("debug"):
				if opt == 'showaspectcalculation':
					self.debug.showaspectcalculation = parseBoolean(value, False)
				elif opt == 'loglevel':
					self.debug.loglevel = value

		section = "activetrains"           
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
					if opt == 'lines':
						self.activetrainlines = int(value)
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

		
		else:
			print("Missing %s section - assuming defaults" % section)
			
		"""
		verify mutual exclusion of active train options
		"""
		ct = 0
		ct += 1 if self.activesuppressunknown else 0
		ct += 1 if self.activeonlyassignedorunknown else 0
		ct += 1 if self.activeonlyassigned else 0
		ct += 1 if self.activeonlyatc else 0
		if ct > 1:
			if self.activeonlyassignedorunknown:
				self.activesuppressunknown = False
				self.activeonlyassigned = False
				self.activeonlyatc = False
			elif self.activeonlyassigned:
				self.activesuppressunknown = False
				self.activeonlyatc = False
			elif self.activesuppressunknown:
				self.activeonlyatc = False				
				
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
