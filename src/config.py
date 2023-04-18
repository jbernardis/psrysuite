import wx
import os, winshell, sys
import configparser

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

# ofp = open("config.out", "w")
# efp = open("config.err", "w")
#
# sys.stdout = ofp
# sys.stderr = efp

modules = {
	"launcher": {
		"name": "PSRY Launsher",
		"dir":  "launcher",
		"main": "main.py",
		"desc": "Launcher",
		"icon": "dispatch.ico"
	},
	"server": {
		"name": "PSRY Server",
		"dir":  "rrserver",
		"main": "main.py",
		"desc": "Railroad Server",
		"icon": "server.ico"
	},
	"dispatch": {
		"name": "PSRY Dispatcher",
		"dir":  "dispatcher",
		"main": "main.py",
		"desc": "Dispatcher",
		"icon": "dispatch.ico"
	},
	"throttle": {
		"name": "PSRY Throttle",
		"dir":  "throttle",
		"main": "main.py",
		"desc": "Throttle",
		"icon": "throttle.ico"
	},
	"simulator": {
		"name": "PSRY Simulator",
		"dir":  "simulator",
		"main": "main.py",
		"desc": "Simulator",
		"icon": "simulator.ico"
	},
	"trainedit": {
		"name": "PSRY Train Editor",
		"dir":  "traineditor",
		"main": "main.py",
		"desc": "Train Editor",
		"icon": "editor.ico"
	},
	"tester": {
		"name": "PSRY Tester Utility",
		"dir":  "tester",
		"main": "main.py",
		"desc": "Tester",
		"icon": "tester.ico"
	},
	"tracker": {
		"name": "PSRY Train Tracker",
		"dir":  "tracker",
		"main": "traintracker.py",
		"desc": "Tracker",
		"icon": "tracker.ico"
	}
}

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
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			return
			
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'serverport':
					try:
						s = int(value)
					except:
						print("invalid value in ini file for server port: (%s)" % value)
						s = 9000
					self.serverport = s
						
				elif opt == 'ipaddr':
					self.ipaddr = value		
		
		else:
			print("Missing global section - assuming defaults")
			
	def SetSimulation(self, flag=True):
		self.cfg.set("rrserver", "simulation", "True" if flag else "False")
		self.saveSettings()
		
	def SetDispatcher(self, flag=True):
		self.cfg.set("dispatcher", "dispatch", "True" if flag else "False")
		
		self.saveSettings()
		
	def saveSettings(self):
		with open(self.inifile, 'w') as cfp:
			self.cfg.write(cfp)		

GENBTNSZ = (300, 50)

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Configurator")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.settings = Settings()

	
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		self.bGenDispatch = wx.Button(self, wx.ID_ANY, "Generate Dispatcher Shortcut", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDispatch, self.bGenDispatch)
		vszr.Add(self.bGenDispatch)
		vszr.AddSpacer(20)
		
			
		self.bGenSimulation = wx.Button(self, wx.ID_ANY, "Generate Simulation Shortcut", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenSimulation, self.bGenSimulation)
		vszr.Add(self.bGenSimulation)
		vszr.AddSpacer(20)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()
		
	def OnBGenDispatch(self, _):
		module = {
			"name": "PSRY Dispatcher",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Local Dispatcher",
			"icon": "dispatch.ico",
			"parameter": "dispatcher"
		}

		self.GenShortcut(module)
		
	def OnBGenSimulation(self, _):
		module = {
			"name": "PSRY Simulation",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Simulation",
			"icon": "simulator.ico",
			"parameter": "simulation"
		}

		self.GenShortcut(module)
		
	def GenShortcut(self, module):
		psrypath = os.getcwd()
		python = sys.executable.replace("python.exe", "pythonw.exe")
		
		desktop = winshell.desktop()
		link_path = os.path.join(desktop, "%s.lnk" % module["name"])
		pyfile = os.path.join(psrypath, module["dir"], module["main"])
	
		with winshell.shortcut(link_path) as link:
			link.path = python
			if "parameter" in module:
				link.arguments = "\"%s\" \"%s\"" % (pyfile, module["parameter"])
			else:
				link.arguments = "\"%s\"" % pyfile
			link.working_directory = psrypath
			link.description = module["desc"]
			link.icon_location = (os.path.join(psrypath, "icons", module["icon"]), 0)
			link.dump(1)
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()

