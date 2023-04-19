import os
import configparser
import logging

INIFILE = "psry.ini"
GLOBAL = "global"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)

		self.ipaddr = "192.168.1.138"
		self.serverport = 9000
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			logging.warning("Settings file %s does not exist.  Using default values" % INIFILE)
			return
			
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'serverport':
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
			
	def SetSimulation(self, flag=True):
		self.cfg.set("rrserver", "simulation", "True" if flag else "False")
		self.saveSettings()
		
	def SetDispatcher(self, flag=True):
		self.cfg.set("dispatcher", "dispatch", "True" if flag else "False")		
		self.saveSettings()
		
	def saveSettings(self):
		with open(self.inifile, 'w') as cfp:
			self.cfg.write(cfp)

		

