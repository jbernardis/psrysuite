import os
import wx
import requests

from monitor.getbitsdlg import GetBitsDlg
from monitor.setinputbitsdlg import SetInputBitsDlg
from monitor.settings import Settings
from monitor.sessionsdlg import SessionsDlg
from monitor.trainsdlg import TrainsDlg


'''
http://192.168.1.144:9000/simulate?action=breaker&breaker=CBLatham&state=1
'''

Nodes = [
	["Yard", 0x11],
	["Kale", 0x12],
	["East Jct", 0x13],
	["Cornell", 0x14],
	["Yard SW", 0x15],
	["Parsons", 0x21],
	["Port A", 0x22],
	["Port B", 0x23],
	["Latham", 0x31],
	["Carlton", 0x32],
	["Dell", 0x41],
	["Foss", 0x42],
	["Hyde Jct", 0x51],
	["Hyde", 0x52],
	["Shore", 0x61],
	["Krulish", 0x71],
	["Nassau W", 0x72],
	["Nassau E", 0x73],
	["Nassau NX", 0x74],
	["Bank", 0x81],
	["Cliveden", 0x91],
	["Green Mtn", 0x92],
	["Cliff", 0x93],
	["Sheffield", 0x95]
]

breakerNames = {
	"CBBank":           "Bank",
	"CBCliveden":       "Cliveden",
	"CBLatham":         "Latham",
	"CBCornellJct":     "Cornell Junction",
	"CBParsonsJct":     "Parson's Junction",
	"CBSouthJct":       "South Junction",
	"CBCircusJct":      "Circus Junction",
	"CBSouthport":      "Southport",
	"CBLavinYard":      "Lavin Yard",
	"CBReverserP31":    "Reverser P31",
	"CBReverserP41":    "Reverser P41",
	"CBReverserP50":    "Reverser P50",
	"CBReverserC22C23": "Reverser C22/C23",
	"CBKrulish":		"Krulish",
	"CBKrulishYd":		"Krulish Yard",
	"CBNassauW":		"Nassau West",
	"CBNassauE":		"Nassau East",
	"CBSptJct":			"Southport Junction",
	"CBWilson":			"Wilson City",
	"CBThomas":			"Thomas Yard",
	"CBFoss":			"Foss",
	"CBDell":			"Dell",
	"CBSouthBank":		"Couth Bank",
	"CBKale":			"Kale",
	"CBWaterman":		"Waterman Yard",
	"CBEngineYard":		"Engine Yard",
	"CBEastEndJct":		"East End Junction",
	"CBShore":			"Shore",
	"CBRockyHill":		"Rocky Hill",
	"CBHarpersFerry":	"Harpers Ferry",
	"CBBlockY30":		"Block Y30",
	"CBBlockY81":		"Block Y81",
	"CBGreenMtnStn":	"Green Mountain Station",
	"CBSheffieldA":		"Sheffield A",
	"CBGreenMtnYd":		"Green Mountain Yard",
	"CBHydeJct":		"Hyde Junction",
	"CBHydeWest":		"Hyde West",
	"CBHydeEast":		"Hyde East",
	"CBSouthportJct":	"Southport Junction",
	"CBCarlton":		"Carlton",
	"CBSheffieldB":		"Sheffield B",
}

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Monitor for Railroad Server")
		
		self.connected = False
		
		self.dlgSetBits = None
		self.dlgGetBits = None
		
		self.settings = Settings()
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "monitor.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(20)
		
		self.bConnect = wx.Button(self, wx.ID_ANY, "Connect", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnConnect, self.bConnect)
		bsz.Add(self.bConnect)
		
		bsz.AddSpacer(20)
		
		self.bQuit = wx.Button(self, wx.ID_ANY, "Shutdown\nServer", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnQuit, self.bQuit)
		bsz.Add(self.bQuit)
		
		bsz.AddSpacer(20)
		
		self.bSessions = wx.Button(self, wx.ID_ANY, "Sessions", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnSessions, self.bSessions)
		bsz.Add(self.bSessions)
		
		bsz.AddSpacer(20)
		
		self.bTrains = wx.Button(self, wx.ID_ANY, "Trains", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnTrains, self.bTrains)
		bsz.Add(self.bTrains)
		
		bsz.AddSpacer(20)
		
		vsz.Add(bsz)
		vsz.AddSpacer(20)
		

		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		self.bGetBits = wx.Button(self, wx.ID_ANY, "Get O/I Bits", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnGetBits, self.bGetBits)
		hsz.Add(self.bGetBits)
		
		hsz.AddSpacer(10)
		vsz.Add(hsz)
		
		vsz.AddSpacer(20)
		
		if self.settings.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
	
			self.bSetInputBit = wx.Button(self, wx.ID_ANY, "Set Input Bits", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSetInputBit, self.bSetInputBit)
			hsz.Add(self.bSetInputBit)
					
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bOccupy = wx.Button(self, wx.ID_ANY, "Occupy\nBlock", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnOccupy, self.bOccupy)
			hsz.Add(self.bOccupy)
			
			hsz.AddSpacer(20)
			self.chBlock = wx.Choice(self, wx.ID_ANY, choices=[])
			self.chBlock.SetSelection(0)
			hsz.Add(self.chBlock, 0, wx.TOP, 10)
			
			hsz.AddSpacer(20)
			
			self.cbOccupy = wx.CheckBox(self, wx.ID_ANY, "Occupy")
			self.cbOccupy.SetValue(True)
			hsz.Add(self.cbOccupy, 0, wx.TOP, 15)
			
			hsz.AddSpacer(20)
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
	
			self.bBreaker = wx.Button(self, wx.ID_ANY, "Breaker", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnBreaker, self.bBreaker)
			hsz.Add(self.bBreaker)
			
			hsz.AddSpacer(20)
			self.chBreaker = wx.Choice(self, wx.ID_ANY, choices=sorted([x for x in breakerNames.keys()]))
			hsz.Add(self.chBreaker, 0, wx.TOP, 10)
			self.chBreaker.SetSelection(0)
			
			hsz.AddSpacer(20)
			self.cbBreaker = wx.CheckBox(self, wx.ID_ANY, "OK")
			self.cbBreaker.SetValue(True)
			hsz.Add(self.cbBreaker, 0, wx.TOP, 15)
			
			hsz.AddSpacer(20)
			self.bClearAll = wx.Button(self, wx.ID_ANY, "Clear All", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnClearBreakers, self.bClearAll)
			hsz.Add(self.bClearAll)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)

		if self.settings.simulation:			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bTurnoutPos = wx.Button(self, wx.ID_ANY, "TurnoutPos", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnTurnoutPos, self.bTurnoutPos)
			hsz.Add(self.bTurnoutPos)
			
			hsz.AddSpacer(20)
			self.chTurnout = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chTurnout, 0, wx.TOP, 10)
			self.chTurnout.SetSelection(wx.NOT_FOUND)
			
			hsz.AddSpacer(20)
			self.cbNormal = wx.CheckBox(self, wx.ID_ANY, "Normal")
			hsz.Add(self.cbNormal, 0, wx.TOP, 15)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()
		
		wx.CallAfter(self.Initialize)
		
	def EnableButtons(self, flag=True):
		self.bSessions.Enable(flag)
		self.bTrains.Enable(flag)
		self.bGetBits.Enable(flag)
		if self.settings.simulation:
			self.bOccupy.Enable(flag)
			self.bBreaker.Enable(flag)
			self.bClearAll.Enable(flag)
			self.bQuit.Enable(flag)
			self.bTurnoutPos.Enable(flag)
			self.bSetInputBit.Enable(flag)
		
	def OnConnect(self, _):
		self.ConnectToServer()
			
	def OnOccupy(self, _):
		chx = self.chBlock.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.rrServer.SendRequest({"simulate": {"action": "occupy", "block": self.chBlock.GetString(chx), "state": 1 if self.cbOccupy.IsChecked() else 0}})
		
	def OnGetBits(self, _):
		if self.dlgGetBits is None:
			self.dlgGetBits = GetBitsDlg(self, self.DlgGetBitsExit, self.rrServer, Nodes)
			self.dlgGetBits.Show()
			
	def DlgGetBitsExit(self):
		self.dlgGetBits.Destroy()
		self.dlgGetBits = None
		
	def OnBreaker(self, _):
		chx = self.chBreaker.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.rrServer.SendRequest({"simulate": {"action": "breaker", "breaker": self.chBreaker.GetString(chx), "state": 0 if self.cbBreaker.IsChecked() else 1}})
		
	def OnClearBreakers(self, _):
		for brkrname in breakerNames.keys():
			self.rrServer.SendRequest({"simulate": {"action": "breaker", "breaker": brkrname, "state": 0}})
		
	def OnTurnoutPos(self, _):
		chx = self.chTurnout.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.rrServer.SendRequest({"simulate": {"action": "turnoutpos", "turnout": self.chTurnout.GetString(chx), "normal": 1 if self.cbNormal.IsChecked() else 0}})

	def OnSetInputBit(self, _):
		if self.dlgSetBits is None:
			self.dlgSetBits = SetInputBitsDlg(self, self.DlgSetBitsExit, self.rrServer, Nodes)
			self.dlgSetBits.Show()
			
	def DlgSetBitsExit(self):
		self.dlgSetBits.Destroy()
		self.dlgSetBits = None

	def OnTrains(self, _):
		dlg = TrainsDlg(self, self.rrServer)
		dlg.ShowModal()
		dlg.Destroy()
				
	def OnSessions(self, _):
		dlg = SessionsDlg(self, self.rrServer)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnQuit(self, _):
		self.rrServer.SendRequest({"quit": {}})
		self.connected = False
		self.EnableButtons(False)			
				
	def Initialize(self):
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.EnableButtons(False)			

	def ConnectToServer(self):		
		layout = self.rrServer.Get("getlayout", {})
		if layout is None:
			self.connected =False
			dlg = wx.MessageDialog(self, "Unable to establish a connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return self.connected
		else:
			self.connected = True

		if self.settings.simulation:			
			b = layout["blocks"]
			
			bl = [bn for bn in b.keys()]
			for bn in b.keys():
				if b[bn]["sbeast"] is not None:
					bl.append(b[bn]["sbeast"])
				if b[bn]["sbwest"] is not None:
					bl.append(b[bn]["sbwest"])
					
			self.blockList = sorted(bl)
			self.chBlock.SetItems(self.blockList)
			self.chBlock.SetSelection(0)
	
			tolist = {"NSw13": 1, "NSw15": 1, "NSw17": 1}		
			r = layout["routes"]
			for rt in r.values():
				for tnm, st in rt["turnouts"]:
					tolist[tnm] = 1
					
			self.turnoutList = sorted([t for t in tolist.keys()])
			self.chTurnout.SetItems(self.turnoutList)
			self.chTurnout.SetSelection(0)

		self.EnableButtons(self.connected)			
		return self.connected


	def Request(self, req):
		if self.connected:
			self.rrServer.SendRequest(req)
		else:
			dlg = wx.MessageDialog(self, "No connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			

	def OnClose(self, evt):
		self.Destroy()


class RRServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except requests.exceptions.ConnectionError:
				return None
			
		return True
				
	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			return None
		
		if r.status_code >= 400:
			#print("HTTP Error %d" % r.status_code)
			return None
		
		return r.json()

