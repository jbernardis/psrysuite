import wx
import os, winshell, sys
import configparser
import glob

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

# ofp = open("config.out", "w")
# efp = open("config.err", "w")
#
# sys.stdout = ofp
# sys.stderr = efp


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


class CleanDlg(wx.Dialog):
	def __init__(self, parent, choices):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Clean up Shortcuts")
		self.Bind(wx.EVT_CLOSE, self.onCancel)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		self.choices = [l for l in choices]

		self.lbLinks = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices)
		vsz.Add(self.lbLinks, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def GetResults(self):
		return [self.choices[i] for i in self.lbLinks.GetCheckedItems()]
		
GENBTNSZ = (170, 40)

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Configurator")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.settings = Settings()

	
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		genBox = wx.StaticBox(self, wx.ID_ANY, "Generate Shortcuts")
		topBorder = genBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder)
		
		self.bGenDispatch = wx.Button(genBox, wx.ID_ANY, "Dispatcher", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDispatch, self.bGenDispatch)
		boxsizer.Add(self.bGenDispatch, 0, wx.ALL, 10)
				
		self.bGenRemoteDispatch = wx.Button(genBox, wx.ID_ANY, "Remote Dispatcher", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenRemoteDispatch, self.bGenRemoteDispatch)
		boxsizer.Add(self.bGenRemoteDispatch, 0, wx.ALL, 10)
					
		self.bGenSimulation = wx.Button(genBox, wx.ID_ANY, "Simulation", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenSimulation, self.bGenSimulation)
		boxsizer.Add(self.bGenSimulation, 0, wx.ALL, 10)
					
		self.bGenDisplay = wx.Button(genBox, wx.ID_ANY, "Display", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDisplay, self.bGenDisplay)
		boxsizer.Add(self.bGenDisplay, 0, wx.ALL, 10)
					
		self.bGenServerOnly = wx.Button(genBox, wx.ID_ANY, "Server Only", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenServerOnly, self.bGenServerOnly)
		boxsizer.Add(self.bGenServerOnly, 0, wx.ALL, 10)
					
		self.bGenDispatcherOnly = wx.Button(genBox, wx.ID_ANY, "Dispatcher Only", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDispatcherOnly, self.bGenDispatcherOnly)
		boxsizer.Add(self.bGenDispatcherOnly, 0, wx.ALL, 10)
					
		self.bGenThrottle = wx.Button(genBox, wx.ID_ANY, "Throttle", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenThrottle, self.bGenThrottle)
		boxsizer.Add(self.bGenThrottle, 0, wx.ALL, 10)
					
		self.bGenTracker = wx.Button(genBox, wx.ID_ANY, "Tracker", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenTracker, self.bGenTracker)
		boxsizer.Add(self.bGenTracker, 0, wx.ALL, 10)
					
		self.bGenEditor = wx.Button(genBox, wx.ID_ANY, "Train Editor", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenEditor, self.bGenEditor)
		boxsizer.Add(self.bGenEditor, 0, wx.ALL, 10)
					
		self.bGenTester = wx.Button(genBox, wx.ID_ANY, "Tester", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenTester, self.bGenTester)
		boxsizer.Add(self.bGenTester, 0, wx.ALL, 10)
		
		genBox.SetSizer(boxsizer)
		
		vszr.Add(genBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(20)
		
		self.bClean = wx.Button(self, wx.ID_ANY, "Clean up Shortcuts", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBClean, self.bClean)
		vszr.Add(self.bClean, 0, wx.ALIGN_CENTER_HORIZONTAL)
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
		
	def OnBGenRemoteDispatch(self, _):
		module = {
			"name": "PSRY Remote Dispatcher",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Remote Dispatcher",
			"icon": "dispatch.ico",
			"parameter": "remotedispatcher"
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
		
	def OnBGenDisplay(self, _):
		module = {
			"name": "PSRY Display",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Display",
			"icon": "dispatch.ico",
			"parameter": "display"
		}
		self.GenShortcut(module)
		
	def OnBGenServerOnly(self, _):
		module = {
			"name": "PSRY Server Only",
			"dir":  "rrserver",
			"main": "main.py",
			"desc": "Railroad Server",
			"icon": "server.ico"
		}	
		self.GenShortcut(module)
		
	def OnBGenDispatcherOnly(self, _):
		module = {
			"name": "PSRY Dispatcher Only",
			"dir":  "dispatcher",
			"main": "main.py",
			"desc": "Dispatcher Only",
			"icon": "dispatch.ico"
		}	
		self.GenShortcut(module)
		
	def OnBGenThrottle(self, _):
		module = {
			"name": "PSRY Throttle",
			"dir":  "throttle",
			"main": "main.py",
			"desc": "Throttle",
			"icon": "throttle.ico"
		}	
		self.GenShortcut(module)
		
	def OnBGenEditor(self, _):
		module = {
			"name": "PSRY Train Editor",
			"dir":  "traineditor",
			"main": "main.py",
			"desc": "Train Editor",
			"icon": "editor.ico"
		}
		self.GenShortcut(module)

	def OnBGenTester(self, _):
		module = {
			"name": "PSRY Tester Utility",
			"dir":  "tester",
			"main": "main.py",
			"desc": "Tester",
			"icon": "tester.ico"
		}
		self.GenShortcut(module)

	def OnBGenTracker(self, _):
		module = {
			"name": "PSRY Train Tracker",
			"dir":  "tracker",
			"main": "traintracker.py",
			"desc": "Tracker",
			"icon": "tracker.ico"
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
			
	def OnBClean(self, _):
		desktop = winshell.desktop()
		pathname = os.path.join(desktop, "PSRY*.lnk")
		scList = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(pathname)]
		if len(scList) == 0:
			dlg = wx.MessageDialog(self, "No shortcut files found",
					'No Shortcuts', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		dlg = CleanDlg(self, scList)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			rv = dlg.GetResults()

		dlg.Destroy()			
		if rc != wx.ID_OK:
			return 
		
		for p in rv:
			path = os.path.join(desktop, p+".lnk")
			os.unlink(path)
		
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

