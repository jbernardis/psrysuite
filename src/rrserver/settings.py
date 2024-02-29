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

class Debug:
	def __init__(self):
		self.showaspectcalculation = False
		self.loglevel = "DEBUG"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)
		self.section = "rrserver"	
		
		self.simulation = False
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
		self.ioerrorthreshold = 5
		self.pendingdetectionlosscycles = 2
		self.controlnassau = 2
		self.controlcliff = 0
		self.controlyard = 0
		self.controlsignal4l = 0
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		
		self.debug = Debug()
		
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return

		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'simulation':
					self.simulation = parseBoolean(value, False)

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

				elif opt == "ioerrorthreshold":
					self.ioerrorthreshold = int(value)

				elif opt == "pendingdetectionlosscycles":
					self.pendingdetectionlosscycles = int(value)

		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
			
		section = "control"
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'cliff':
					v = int(value)
					if v < 0 or v > 2:
						print("value for controlcliff out of range - assuming 0")
						v = 0
					self.controlcliff = v

				elif opt == 'nassau':
					v = int(value)
					if v < 0 or v > 2:
						print("value for controlnassau out of range - assuming 0")
						v = 0
					self.controlnassau = v

				elif opt == 'yard':
					v = int(value)
					if v < 0 or v > 1:
						print("value for controlyard out of range - assuming 0")
						v = 0
					self.controlyard = v
					
				elif opt == 'signal4l':
					v = int(value)
					if v < 0 or v > 1:
						print("value for controlsignal4l out of range - assuming 0")
						v = 0
					self.controlsignal4l = v



		else:
			logging.warning("Missing %s section - assuming defaults" % self.section)
			
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
