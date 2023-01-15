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
		self.traindir = "."
		self.locodir = "."

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

				elif opt == 'showcameras':
					self.showcameras = parseBoolean(value, False)

				elif opt == "traindir":
					self.traindir = value

				elif opt == "locodir":
					self.locodir = value

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
						
				elif opt == 'ipaddr':
					self.ipaddr = value

		else:
			logging.warning("Missing global section - assuming defaults")

	def SetTrainDir(self, tdir):
		self.traindir = tdir

	def SetLocoDir(self, ldir):
		self.locodir = ldir

	def save(self):
		try:
			self.cfg.add_section(self.section)
		except configparser.DuplicateSectionError:
			pass

		self.cfg.set(self.section, "pages", str(self.pages))
		self.cfg.set(self.section, "dispatch", "True" if self.dispatch else "False")
		self.cfg.set(self.section, "showcameras", "True" if self.showcameras else "False")
		self.cfg.set(self.section, "traindir", str(self.traindir))
		self.cfg.set(self.section, "locodir", str(self.locodir))

		try:
			cfp = open(self.inifile, 'w')
		except:
			dlg = wx.MessageDialog(None, "Unable to open settings file %s for writing" % self.inifile,
									'Errors writing settings',
									wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self.cfg.write(cfp)
		cfp.close()
