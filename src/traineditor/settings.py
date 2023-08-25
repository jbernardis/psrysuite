import os
import configparser

INIFILE = "psry.ini"
GLOBAL = "global"

class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)

		self.ipaddr = "192.168.1.144"
		self.serverport = 9000
		self.backupdir = os.getcwd()

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			return
			
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'serverport':
					try:
						s = int(value)
					except:
						print("invalid value in ini file for socket port: (%s)" % value)
						s = 9000
					self.socketport = s
						
				elif opt == 'ipaddr':
					self.ipaddr = value
						
				elif opt == 'backupdir':
					self.backupdir = value

		else:
			print("Missing global section - assuming defaults")
