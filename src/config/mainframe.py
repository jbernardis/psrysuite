import wx
import os
import sys
import winshell

from dispatcher.settings import Settings
from config.generatedlg import GenerateDlg
from utilities.backup import saveData, restoreData

		
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Configuration Utility")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
		self.settings = Settings()
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "config.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
		
		vszrl = wx.BoxSizer(wx.VERTICAL)
		vszrl.AddSpacer(20)
		
		commBox = wx.StaticBox(self, wx.ID_ANY, "Communications")
		topBorder = commBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "IP Address: ", size=(130, -1)))		
		self.teIpAddr = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teIpAddr.SetValue(self.settings.ipaddr)
		hsz.Add(self.teIpAddr)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "RR Server Port: ", size=(130, -1)))		
		self.teRRPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teRRPort.SetValue("%d" % self.settings.serverport)
		hsz.Add(self.teRRPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "DCC Server Port: ", size=(130, -1)))		
		self.teDCCPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teDCCPort.SetValue("%d" % self.settings.dccserverport)
		hsz.Add(self.teDCCPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Broadcast port: ", size=(130, -1)))		
		self.teBroadcastPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teBroadcastPort.SetValue("%d" % self.settings.socketport)
		hsz.Add(self.teBroadcastPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		commBox.SetSizer(boxsizer)
		
		vszrl.Add(commBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		
		commBox = wx.StaticBox(self, wx.ID_ANY, "Server")
		topBorder = commBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Railroad COM Port: ", size=(130, -1)))		
		self.teRRComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teRRComPort.SetValue(self.settings.rrserver.rrtty)
		hsz.Add(self.teRRComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Cmd Station COM port: ", size=(130, -1)))		
		self.teDCCComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teDCCComPort.SetValue(self.settings.rrserver.dcctty)
		hsz.Add(self.teDCCComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "DCC Sniffer COM port: ", size=(130, -1)))		
		self.teSnifferComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teSnifferComPort.SetValue(self.settings.dccsniffer.tty)
		hsz.Add(self.teSnifferComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		commBox.SetSizer(boxsizer)
		
		vszrl.Add(commBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		
		dispBox = wx.StaticBox(self, wx.ID_ANY, "Dispatcher/Display")
		topBorder = dispBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		self.rbPages = wx.RadioBox(dispBox, wx.ID_ANY, "Pages", choices=["1", "3"])
		boxsizer.Add(self.rbPages, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbPages.SetSelection(0 if self.settings.dispatcher.pages == 1 else 1)
		
		boxsizer.AddSpacer(10)
		
		self.cbShowCameras = wx.CheckBox(dispBox, wx.ID_ANY, "Show Cameras")
		boxsizer.Add(self.cbShowCameras, 0, wx.LEFT, 40)
		self.cbShowCameras.SetValue(self.settings.dispatcher.showcameras)
		
		boxsizer.AddSpacer(10)
		
		dispBox.SetSizer(boxsizer)
		
		vszrl.Add(dispBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		
		dispBox = wx.StaticBox(self, wx.ID_ANY, "Display")
		topBorder = dispBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)
		
		self.cbAllowATCRequests = wx.CheckBox(dispBox, wx.ID_ANY, "Allow ATC Requests")
		boxsizer.Add(self.cbAllowATCRequests, 0, wx.LEFT, 40)
		self.cbAllowATCRequests.SetValue(self.settings.display.allowatcrequests)
		
		boxsizer.AddSpacer(10)
		
		self.cbShowEvents = wx.CheckBox(dispBox, wx.ID_ANY, "Show Events")
		boxsizer.Add(self.cbShowEvents, 0, wx.LEFT, 40)
		self.cbShowEvents.SetValue(self.settings.display.showevents)
		
		boxsizer.AddSpacer(10)
		
		self.cbShowAdvice = wx.CheckBox(dispBox, wx.ID_ANY, "Show Advice")
		boxsizer.Add(self.cbShowAdvice, 0, wx.LEFT, 40)
		self.cbShowAdvice.SetValue(self.settings.display.showadvice)
		
		boxsizer.AddSpacer(10)
		
		dispBox.SetSizer(boxsizer)
		
		vszrl.Add(dispBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)
		
		vszrl.Add(wx.StaticText(self, wx.ID_ANY, "Backup Directory:"))
		
		self.teBackupDir = wx.TextCtrl(self, wx.ID_ANY, self.settings.backupdir, size=(200, -1), style=wx.TE_READONLY)
		self.bBackupDir = wx.Button(self, wx.ID_ANY, "...", size=(50, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBBackupDir, self.bBackupDir)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBackupDir)
		hsz.AddSpacer(10)
		hsz.Add(self.bBackupDir)
		
		vszrl.AddSpacer(5)
		vszrl.Add(hsz)
		

		
		

		vszrr = wx.BoxSizer(wx.VERTICAL)
		vszrr.AddSpacer(20)
			
		atBox = wx.StaticBox(self, wx.ID_ANY, "Active Trains")
		topBorder = atBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)
		
		self.cbSuppressYards = wx.CheckBox(atBox, wx.ID_ANY, "Suppress Yards")
		boxsizer.Add(self.cbSuppressYards, 0, wx.LEFT, 40)
		self.cbSuppressYards.SetValue(self.settings.activetrains.suppressyards)
	
		boxsizer.AddSpacer(10)
		
		self.showonly = ["All", "Known", "ATC", "Assigned", "Assigned or Unknown"]	
		self.rbShowOnly = wx.RadioBox(atBox, wx.ID_ANY, "Show Only", choices=self.showonly,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbShowOnly, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		ix = 0
		if self.settings.activetrains.suppressunknown:
			ix = 1
		elif self.settings.activetrains.onlyatc:
			ix = 2
		elif self.settings.activetrains.onlyassigned:
			ix = 3
		elif self.settings.activetrains.onlyassignedorunknown:
			ix = 4
		self.rbShowOnly.SetSelection(ix)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(atBox, wx.ID_ANY, "Lines: ", size=(130, -1)))		
		self.teLines = wx.TextCtrl(atBox, wx.ID_ANY, "", size=(100, -1))
		self.teLines.SetValue("%d" % self.settings.activetrains.lines)
		hsz.Add(self.teLines)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)
		
		atBox.SetSizer(boxsizer)
		
		vszrr.Add(atBox, 0, wx.EXPAND)
	
		vszrr.AddSpacer(20)
		
			
		controlBox = wx.StaticBox(self, wx.ID_ANY, "Control")
		topBorder = controlBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		boxsizer.AddSpacer(10)
		
		self.ctlCliff = ["Cliff", "Dispatcher Bank/Cliveden", "Dispatcher All"]	
		self.rbCtlCliff = wx.RadioBox(controlBox, wx.ID_ANY, "Cliff", choices=self.ctlCliff,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlCliff, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlCliff.SetSelection(self.settings.control.cliff)

		boxsizer.AddSpacer(10)
		
		self.ctlNassau = ["Nassau", "Dispatcher Main", "Dispatcher All"]	
		self.rbCtlNassau = wx.RadioBox(controlBox, wx.ID_ANY, "Nassau", choices=self.ctlNassau,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlNassau, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlNassau.SetSelection(self.settings.control.nassau)
		
		boxsizer.AddSpacer(10)
	
		self.ctlYard = ["Yard", "Dispatcher"]	
		self.rbCtlYard = wx.RadioBox(controlBox, wx.ID_ANY, "Yard", choices=self.ctlYard,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlYard, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlYard.SetSelection(self.settings.control.yard)
		
		boxsizer.AddSpacer(10)
	
		self.ctlSignal4L = ["Port", "Dispatcher"]	
		self.rbCtlSignal4L = wx.RadioBox(controlBox, wx.ID_ANY, "Signal 4L", choices=self.ctlSignal4L,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlSignal4L, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlSignal4L.SetSelection(self.settings.control.signal4l)
		
		boxsizer.AddSpacer(10)

		controlBox.SetSizer(boxsizer)
		
		vszrr.Add(controlBox, 0, wx.EXPAND)


		vszr = wx.BoxSizer(wx.VERTICAL)
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.Add(vszrl, 1, wx.EXPAND)
		hszr.AddSpacer(30)
		hszr.Add(vszrr, 1, wx.EXPAND)
		
		vszr.Add(hszr)

		vszr.AddSpacer(20)

		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=(200, 60))
		vszr.Add(self.bSave, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
		vszr.AddSpacer(20)
		
		self.bGenerate = wx.Button(self, wx.ID_ANY, "Generate Shortcuts/Start Menu", size=(200, 60))
		vszr.Add(self.bGenerate, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.OnBGenerate, self.bGenerate)
		vszr.AddSpacer(30)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
				
		self.bBackup = wx.Button(self, wx.ID_ANY, "Backup\nData Files", size=(100, 50))
		hsz.Add(self.bBackup)		
		hsz.AddSpacer(30)
		self.Bind(wx.EVT_BUTTON, self.OnBBackup, self.bBackup)
		self.bRestore = wx.Button(self, wx.ID_ANY, "Restore\nData Files", size=(100, 50))
		hsz.Add(self.bRestore)
		self.Bind(wx.EVT_BUTTON, self.OnBRestore, self.bRestore)
		
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(30)
		
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()
		
		self.GenConfigShortcut()
		
	def GenConfigShortcut(self):
		module = {
			"name": "PSRY Suite Configuration",
			"dir":  "config",
			"main": "main.py",
			"desc": "Configuration Tool",
			"icon": "config.ico",
		}
		self.GenShortcut(module, True)
		module = {
			"name": "PSRY Suite - save logs",
			"dir":  "savelogs",
			"main": "main.py",
			"desc": "Save Logs and output for debugging",
			"icon": "savelogs.ico",
		}
		self.GenShortcut(module, True)
		
	def GenShortcut(self, module, forceStartMenu=False):
		psrypath = os.getcwd()
		python = sys.executable.replace("python.exe", "pythonw.exe")

		paths = []		
		paths.append(os.path.join(winshell.desktop(), "%s.lnk" % module["name"]))
		
		if forceStartMenu:
			smdir = os.path.join(winshell.start_menu(), "Programs", "PSRY")
			try:
				os.mkdir(smdir)
			except FileExistsError:
				pass
			
			paths.append(os.path.join(smdir, "%s.lnk" % module["name"]))
		
		for link_path in paths:
			if module["dir"] is None:
				pyfile = os.path.join(psrypath, module["main"])
			else:
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

	def OnBBackupDir(self, _):
		startDir = self.teBackupDir.GetValue()
		dlg = wx.DirDialog(self, "Choose a backup directory:", defaultPath=startDir, style=wx.DD_DEFAULT_STYLE)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		self.teBackupDir.SetValue(path)

		
		
	def OnBGenerate(self, _):
		dlg = GenerateDlg(self, self.GenShortcut)
		dlg.ShowModal()
		dlg.Destroy

	def OnBBackup(self, _):
		saveData(self, self.settings)
				
	def OnBRestore(self, _):
		restoreData(self, self.settings)
		
	def OnBSave(self, _):
		self.settings.ipaddr = self.teIpAddr.GetValue()
		self.settings.serverport = int(self.teRRPort.GetValue())
		self.settings.dccserverport = int(self.teDCCPort.GetValue())
		self.settings.socketport = int(self.teBroadcastPort.GetValue())
		self.settings.backupdir = self.teBackupDir.GetValue()
		
		self.settings.rrserver.rrtty = self.teRRComPort.GetValue()
		self.settings.rrserver.dcctty = self.teDCCComPort.GetValue()
		self.settings.dccsniffer.tty = self.teSnifferComPort.GetValue()
		
		self.settings.dispatcher.pages = 1 if self.rbPages.GetSelection() == 0 else 3
		self.settings.dispatcher.showcameras = self.cbShowCameras.IsChecked()
		
		self.settings.display.allowatcrequests = self.cbAllowATCRequests.IsChecked()
		self.settings.display.showevents = self.cbShowEvents.IsChecked()
		self.settings.display.showadvice = self.cbShowAdvice.IsChecked()
		
		self.settings.activetrains.suppressyards = self.cbSuppressYards.IsChecked()		
		ix = self.rbShowOnly.GetSelection()
		self.settings.activetrains.suppressunknown = False
		self.settings.activetrains.onlyatc = False
		self.settings.activetrains.onlyassigned = False
		self.settings.activetrains.onlyassignedorunknown = False
		if ix == 1:
			self.settings.activetrains.suppressunknown = True
		elif ix == 2:
			self.settings.activetrains.onlyatc = True
		elif ix == 3:
			self.settings.activetrains.onlyassigned = True
		elif ix == 4:
			self.settings.activetrains.onlyassignedorunknown = True
		cv = self.settings.activetrains.lines
		try:
			self.settings.activetrains.lines = int(self.teLines.GetValue())
		except:
			self.settings.activetrains.lines = cv
		
		self.settings.control.cliff = self.rbCtlCliff.GetSelection()
		self.settings.control.nassau = self.rbCtlNassau.GetSelection()
		self.settings.control.yard = self.rbCtlYard.GetSelection()
		self.settings.control.signal4l = self.rbCtlSignal4L.GetSelection()
		
		
		
		if self.settings.SaveAll():		
			dlg = wx.MessageDialog(self, "Configuration Data has been saved", "Data Saved", wx.OK | wx.ICON_INFORMATION)
		else:
			dlg = wx.MessageDialog(self, "Unable to save configuration data", "Save Failed", wx.OK | wx.ICON_ERROR)
			
		dlg.ShowModal()
		dlg.Destroy()

		
	def OnClose(self, _):
		self.Destroy()

