import configparser
import os
import wx
import logging

INIFILE = "psry.ini"
GLOBAL = "global"

def parseBoolean(val, defaultVal):
	lval = val.lower();
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Settings:
	def __init__(self, parent):
		self.parent = parent
		
		self.inifile = os.path.join(os.getcwd(), "data", INIFILE)
		self.section = "tracker"	
		
		self.ipaddr = "192.168.1.144"
		self.serverport = 9000
		self.socketport = 9001
		self.dccsnifferport = "COM5"
		self.dccsnifferbaud = 38400
		self.backupdir = os.getcwd()
		
		self.browser = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"

		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			dlg = wx.MessageDialog(self.parent, "Settings file %s does not exist.  Using default values" % INIFILE,
									'File Not Found',
									wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			self.modified = True
			return

		msgs = []
		self.modified = False	
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == "dccsnifferport":
					self.dccsnifferport = value
				elif opt == "dccsnifferbaud":
					self.dccsnifferbaud = int(value)
				elif opt == "browser":
					self.browser = value

		else:
			logging.warning("INI file: missing %s section - assuming defaults" % self.section)
			
				
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
						
				elif opt == 'backupdir':
					self.backupdir = value

		else:
			logging.warning("Missing global section - assuming defaults")

			
		if len(msgs) > 0:				
			dlg = wx.MessageDialog(self.parent, "\n".join(msgs),
									'Errors reading settings',
									wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

	def setModified(self):
		self.modified = True
		
	def checkModified(self):
		return self.modified
