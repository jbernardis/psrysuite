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
		
  # self.traindir = os.path.join(os.getcwd(), "trains")
  # self.trainfile = "trains.json"
  # self.locodir = os.path.join(os.getcwd(), "locos")
  # self.locofile = "locos.json"
  # self.engineerdir = os.path.join(os.getcwd(), "engineers")
  # self.engineerfile = "engineers.txt"
  # self.orderdir = os.path.join(os.getcwd(), "orders")
  # self.orderfile = "order.json"
  # self.scheduledir = os.path.join(os.getcwd(), "schedules")
  # self.logdir = os.path.join(os.getcwd(), "logs")
  # self.dispatchip = "192.168.1.157"
  # self.dispatchport = "5204"
  # self.dccsnifferport = "COM5"
  # self.dccsnifferbaud = 38400
  # self.savelogonexit = True
  # self.allowextrarerun = False


		self.browser = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
		self.unstartedthreshold = 600
		self.stoppedthreshold = 120

		
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
				if opt == 'trainxxdir':
					self.traindir = value
    # elif opt == 'trainfile':
    # 	self.trainfile = value
    # elif opt == 'locodir':
    # 	self.locodir = value
    # elif opt == 'locofile':
    # 	self.locofile = value
    # elif opt == 'engineerdir':
    # 	self.engineerdir = value
    # elif opt == "engineerfile":
    # 	self.engineerfile = value;
    # elif opt == "orderdir":
    # 	self.orderdir = value
    # elif opt == "orderfile":
    # 	self.orderfile = value
    # elif opt == "scheduledir":
    # 	self.scheduledir = value
    # elif opt == "logdir":
    # 	self.logdir = value
    # elif opt == "dispatchip":
    # 	self.dispatchip = value
    # elif opt == "dispatchport":
    # 	self.dispatchport = value
    # elif opt == "dccsnifferport":
    # 	self.dccsnifferport = value
    # elif opt == "dccsnifferbaud":
    # 	self.dccsnifferbaud = int(value)
    # elif opt == "savelogonexit":
    # 	self.savelogonexit = parseBoolean(value, True)
    # elif opt == "allowextrarerun":
    # 	self.allowextrarerun = parseBoolean(value, True)

				elif opt == "unstartedthreshold":
					self.unstartedthreshold = int(value)
				elif opt == "stoppedthreshold":
					self.stoppedthreshold = int(value)
				elif opt == "browser":
					self.browser = value
	
    # else:
    # 	msgs.append("INI file: Unknown %s option: %s - ignoring" % (self.section, opt))
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
		
	def save(self):
		try:
			self.cfg.add_section(self.section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(self.section, "traindir", str(self.traindir))
		self.cfg.set(self.section, "trainfile", str(self.trainfile))
		self.cfg.set(self.section, "locodir", str(self.locodir))
		self.cfg.set(self.section, "locofile", str(self.locofile))
		self.cfg.set(self.section, "engineerdir", str(self.engineerdir))
		self.cfg.set(self.section, "engineerfile", str(self.engineerfile))
		self.cfg.set(self.section, "orderdir", str(self.orderdir))
		self.cfg.set(self.section, "orderfile", str(self.orderfile))
		self.cfg.set(self.section, "scheduledir", str(self.scheduledir))
		self.cfg.set(self.section, "logdir", str(self.logdir))
		self.cfg.set(self.section, "dispatchip", str(self.dispatchip))
		self.cfg.set(self.section, "dispatchport", str(self.dispatchport))
		self.cfg.set(self.section, "dccsnifferport", str(self.dccsnifferport))
		self.cfg.set(self.section, "dccsnifferbaud", str(self.dccsnifferbaud))
		self.cfg.set(self.section, "browser", str(self.browser))
		self.cfg.set(self.section, "savelogonexit", "True" if self.savelogonexit else "False")
		self.cfg.set(self.section, "allowextrarerun", "True" if self.allowextrarerun else "False")
		self.cfg.set(self.section, "unstartedthreshold", str(self.unstartedthreshold))
		self.cfg.set(self.section, "stoppedthreshold", str(self.stoppedthreshold))

		try:		
			cfp = open(self.inifile, 'w')
		except:
			dlg = wx.MessageDialog(self.parent, "Unable to open settings file %s for writing" % self.inifile,
									'Errors writing settings',
									wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
			
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False
