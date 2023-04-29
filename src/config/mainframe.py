import wx
import os
import sys
import winshell

from config.settings import Settings
from config.generatedlg import GenerateDlg

		
class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Configuration Utility")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
		self.settings = Settings()
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "config.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
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

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Railroad COM Port: ", size=(130, -1)))		
		self.teRRComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teRRComPort.SetValue(self.settings.rrtty)
		hsz.Add(self.teRRComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Cmd Station COM port: ", size=(130, -1)))		
		self.teDCCComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teDCCComPort.SetValue(self.settings.dcctty)
		hsz.Add(self.teDCCComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "DCC Sniffer COM port: ", size=(130, -1)))		
		self.teSnifferComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teSnifferComPort.SetValue(self.settings.dccsniffertty)
		hsz.Add(self.teSnifferComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		commBox.SetSizer(boxsizer)
		
		vszr.Add(commBox, 0, wx.EXPAND)
		
		vszr.AddSpacer(20)

		
		dispBox = wx.StaticBox(self, wx.ID_ANY, "Dispatcher/Display")
		topBorder = dispBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		self.rbPages = wx.RadioBox(dispBox, wx.ID_ANY, "Pages", choices=["1", "3"])
		boxsizer.Add(self.rbPages, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.rbPages.SetSelection(0 if self.settings.pages == 1 else 1)
		
		boxsizer.AddSpacer(10)
		
		self.cbShowCameras = wx.CheckBox(dispBox, wx.ID_ANY, "Show Cameras")
		boxsizer.Add(self.cbShowCameras, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.cbShowCameras.SetValue(self.settings.showcameras)
		
		boxsizer.AddSpacer(10)
		
		dispBox.SetSizer(boxsizer)
		
		vszr.Add(dispBox, 0, wx.EXPAND)
		
		vszr.AddSpacer(20)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=(200, 60))
		vszr.Add(self.bSave, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
		vszr.AddSpacer(30)
		
		self.bGenerate = wx.Button(self, wx.ID_ANY, "Generate Shortcuts/Start Menu", size=(200, 60))
		vszr.Add(self.bGenerate, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.OnBGenerate, self.bGenerate)
		vszr.AddSpacer(20)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()
		
	def GenConfigShortcut(self):
		module = {
			"name": "PSRY Suite Configuration",
			"dir":  "config",
			"main": "main.py",
			"desc": "Configuration Tool",
			"icon": "config.ico"
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

		
	def OnBGenerate(self, _):
		dlg = GenerateDlg(self, self.GenShortcut)
		dlg.ShowModal()
		dlg.Destroy
		
	def OnBSave(self, _):
		print("save")
		
	def OnClose(self, _):
		self.Destroy()

