import os
import wx
import requests
import json
import time
import re

from monitor.getbitsdlg import GetBitsDlg
from monitor.setinputbitsdlg import SetInputBitsDlg
from dispatcher.settings import Settings
from monitor.sessionsdlg import SessionsDlg
from monitor.trainsdlg import TrainsDlg
from monitor.siglever import SigLever, SigLeverShowDlg
from monitor.buttonchoicedlg import ButtonChoiceDlg
from dispatcher.delayedrequest import DelayedRequests

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

def getNodeAddress(nm):
	for i in range(len(Nodes)):
		if nm == Nodes[i][0]:
			return Nodes[i][1]
		
	return None

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
	"CBWilson":			"Wilson City",
	"CBThomas":			"Thomas Yard",
	"CBFoss":			"Foss",
	"CBDell":			"Dell",
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
		
		self.connected = False
		
		self.dlgSessions = None
		self.dlgTrains = None
		self.dlgSigLvrs = None

		self.blockList = []
		self.routes = {}

		self.settings = Settings()
		if self.settings.rrserver.simulation:		
			self.SetTitle("PSRY Monitor for Railroad Server in simulation mode")
		else:
			self.SetTitle("PSRY Monitor for Railroad Server")
		
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
		
		self.bReopen = wx.Button(self, wx.ID_ANY, "Reopen port", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnReopen, self.bReopen)
		bsz.Add(self.bReopen)
		
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
		
		if self.settings.rrserver.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
	
			self.bSetInputBit = wx.Button(self, wx.ID_ANY, "Set Input Bits", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSetInputBit, self.bSetInputBit)
			hsz.Add(self.bSetInputBit)
					
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.rrserver.simulation:		
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
			
		if self.settings.rrserver.simulation:		
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

		if self.settings.rrserver.simulation:			
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

		if self.settings.rrserver.simulation:
			self.BuildMatrixMap()			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bMatrix = wx.Button(self, wx.ID_ANY, "NX Buttons", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnMatrix, self.bMatrix)
			hsz.Add(self.bMatrix)
			
			hsz.AddSpacer(20)
			self.chMatrixArea = wx.Choice(self, wx.ID_ANY, choices=list(self.matrixMap.keys()))
			hsz.Add(self.chMatrixArea, 0, wx.TOP, 10)
			self.chMatrixArea.SetSelection(0)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.rrserver.simulation:			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bSigLvr = wx.Button(self, wx.ID_ANY, "Signal Lever", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvr, self.bSigLvr)
			hsz.Add(self.bSigLvr)
			
			hsz.AddSpacer(20)
			self.chSigLvr = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chSigLvr, 0, wx.TOP, 10)
			self.chSigLvr.SetSelection(wx.NOT_FOUND)
			
			hsz.AddSpacer(20)
			self.cbLeft = wx.CheckBox(self, wx.ID_ANY, "Left")
			hsz.Add(self.cbLeft, 0, wx.TOP, 15)

			hsz.AddSpacer(20)
			self.cbRight = wx.CheckBox(self, wx.ID_ANY, "Right")
			hsz.Add(self.cbRight, 0, wx.TOP, 15)
			
			hsz.AddSpacer(20)
			
			self.bSigLvrShow = wx.Button(self, wx.ID_ANY, "Show", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvrShow, self.bSigLvrShow)
			hsz.Add(self.bSigLvrShow)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
		else:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bSigLvrShow = wx.Button(self, wx.ID_ANY, "Show\nSignal Levers", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvrShow, self.bSigLvrShow)
			hsz.Add(self.bSigLvrShow)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			self.bScript = wx.Button(self, wx.ID_ANY, "Script", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnScript, self.bScript)
			hsz.Add(self.bScript)

			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()


		wx.CallAfter(self.Initialize)
		
	def BuildMatrixMap(self):
		self.matrixMap = {
			"Waterman Yard": {
				"node": "Yard",
				"buttons": ["YWWB1", "YWWB2", "YWWB3", "YWWB4", "YWEB1", "YWEB2", "YWEB3", "YWEB4"],
				"bits"   : [[3, 3],  [3, 4],  [3, 5],  [3, 6],  [3, 7],  [4, 0],  [4, 1],  [4, 2]]
			},
			"Cliff A": {
				"node"   : "Sheffield",
				"buttons": ["C50E", "C51E", "C52E", "C53E", "C54E", "C50W", "C51W", "C52W", "C53W", "C54W"],
				"bits"   : [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [1, 0], [1, 1]]
			},
			"Cliff B": {
				"node"   : "Cliff",
				"buttons": ["C21E", "C40E", "C41E", "C42E", "C43E", "C44E", "C21W", "C40W", "C41W", "C42W", "C43W", "C44W"],
				"bits"   : [[0, 0], [0, 1], [0, 5], [0, 4], [0, 3], [0, 2], [1, 0], [1, 1], [0, 6], [0, 7], [1, 3], [1, 2]]
			}
		}		

	def EnableButtons(self, flag=True):
		self.bSessions.Enable(flag)
		self.bTrains.Enable(flag)
		self.bGetBits.Enable(flag)
		self.bSigLvrShow.Enable(flag)	
		if self.settings.rrserver.simulation:
			self.bOccupy.Enable(flag)
			self.bBreaker.Enable(flag)
			self.bClearAll.Enable(flag)
			self.bQuit.Enable(flag)
			self.bReopen.Enable(flag)
			self.bTurnoutPos.Enable(flag)
			self.bSetInputBit.Enable(flag)
			self.bMatrix.Enable(flag)	
			self.bSigLvr.Enable(flag)
			self.bScript.Enable(flag)
			
	def OnConnect(self, _):
		self.ConnectToServer()
			
	def OnOccupy(self, _):
		chx = self.chBlock.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.Request({"simulate": {"action": "occupy", "block": self.chBlock.GetString(chx), "state": 1 if self.cbOccupy.IsChecked() else 0}})
		
	def OnGetBits(self, _):
		dlg = GetBitsDlg(self, self.rrServer, Nodes)
		dlg.Show()
		
	def OnBreaker(self, _):
		chx = self.chBreaker.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.Request({"simulate": {"action": "breaker", "breaker": self.chBreaker.GetString(chx), "state": 0 if self.cbBreaker.IsChecked() else 1}})
		
	def OnClearBreakers(self, _):
		for brkrname in breakerNames.keys():
			self.Request({"simulate": {"action": "breaker", "breaker": brkrname, "state": 0}})
		
	def OnTurnoutPos(self, _):
		chx = self.chTurnout.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		self.Request({"simulate": {"action": "turnoutpos", "turnout": self.chTurnout.GetString(chx), "normal": 1 if self.cbNormal.IsChecked() else 0}})
		
	def OnRoute(self, _):
		chx = self.chRoutes.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		
		rtnm = self.chRoutes.GetString(chx)
		if rtnm not in self.routes:
			return 
		
		rinfo = self.routes[rtnm]

	def OnMatrix(self, _):
		chx = self.chMatrixArea.GetSelection()
		if chx == wx.NOT_FOUND:
			return 

		area = self.chMatrixArea.GetString(chx)
		if area not in self.matrixMap:
			return 
		
		try:
			blist1 = self.matrixMap[area]["entry"]
			bits1  = self.matrixMap[area]["entrybits"]
			blist2 = self.matrixMap[area]["exit"]
			bits2  = self.matrixMap[area]["exitbits"]
		except KeyError:
			try:
				blist1 = self.matrixMap[area]["buttons"]
				bits1  = self.matrixMap[area]["bits"]
				blist2 = None
				bits2  = None
			except KeyError:
				# error
				return
			
		dlg = ButtonChoiceDlg(self, blist1, blist2)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			buttons = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		vbytes = []
		vbits = []
		vals1 = []
		vals0 = []
		
		vbytes.append(bits1[buttons[0]][0])
		vbits.append(bits1[buttons[0]][1])
		vals1.append(1)
		vals0.append(0)
		if len(buttons) > 1:
			vbytes.append(bits2[buttons[1]][0])
			vbits.append(bits2[buttons[1]][1])
			vals1.append(1)
			vals0.append(0)

		addr = getNodeAddress(self.matrixMap[area]["node"])
		if addr is not None:		
			req = {"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals1}}
			self.Request(req)
			req = {"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals0, "delay": 10}}
			self.Request(req)
		
		
	def OnSigLvr(self, _):	
		chx = self.chSigLvr.GetSelection()
		if chx == wx.NOT_FOUND:
			return

		lvr = self.chSigLvr.GetString(chx)
		if lvr not in self.sigLevers:
			return 
				
		info = self.sigLevers[lvr].GetData()
		if info is None:
			return 

		if info["left"] is None:		
			vbytes = [info["right"][0]]
			vbits  = [info["right"][1]]	
			vals = [ 1 if self.cbRight.IsChecked() else 0]
		elif info["right"] is None:
			vbytes = [info["left"][0]]
			vbits  = [info["left"][1]]	
			vals = [ 1 if self.cbLeft.IsChecked() else 0]
		else:
			vbytes = [info["left"][0], info["right"][0]]
			vbits  = [info["left"][1], info["right"][1]]	
			vals = [ 1 if self.cbLeft.IsChecked() else 0, 1 if self.cbRight.IsChecked() else 0]
		
		addr = getNodeAddress(info["node"])
		if addr is not None:		
			req = {"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}}
			self.rrServer.SendRequest(req)
		
	def OnSigLvrShow(self, _):	
		if self.dlgSigLvrs is None:
			self.dlgSigLvrs = SigLeverShowDlg(self, self.CloseSigLvrShow)
			self.dlgSigLvrs.Show()
		else:
			self.dlgSigLvrs.Refresh()
			
	def CloseSigLvrShow(self):
		if self.dlgSigLvrs is None:
			return 
		
		self.dlgSigLvrs.Destroy()
		self.dlgSigLvrs = None
		
	def OnScript(self, _):
		dlg = wx.FileDialog(
			self, message="Select script file file",
			defaultDir=os.path.join(os.getcwd(), "monitor", "scripts"),
			defaultFile="",
			wildcard="Monitor Script File (*.scr)|*.scr",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		with open(path, "r") as jfp:
			try:
				script = json.load(jfp)
			except json.JSONDecodeError as e:
				dlg = wx.MessageDialog(self, str(e), 'JSON Decode Error', wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				script = []
			
		for c in script:
			cmd = list(c.keys())[0]
			parms = c[cmd]
			if cmd == "delay":
				try:
					secs = parms["sec"]
				except KeyError:
					secs = None
				try:
					msecs = parms["ms"]
				except KeyError:
					msecs = None
					
				if secs is None:
					if msecs is None:
						secs = 1
					else:
						secs = msecs / 1000.0
				
				time.sleep(secs)
			else:
				self.rrServer.SendRequest(c)

	def OnSetInputBit(self, _):
		dlg = SetInputBitsDlg(self, Nodes)
		dlg.Show()
			
	def OnTrains(self, _):
		if self.dlgTrains is None:
			self.dlgTrains = TrainsDlg(self, self.DlgTrainsExit, self.rrServer)
			self.dlgTrains.Show()

	def DlgTrainsExit(self):
		self.dlgTrains.Destroy()
		self.dlgTrains = None
				
	def OnSessions(self, _):
		if self.dlgSessions is None:
			self.dlgSessions = SessionsDlg(self, self.DlgSessionsExit, self.rrServer)
			self.dlgSessions.Show()

	def DlgSessionsExit(self):
		self.dlgSessions.Destroy()
		self.dlgSessions = None
		
	def OnReopen(self, _):
		self.rrServer.SendRequest({"reopen": {}})
		
	def OnQuit(self, _):
		self.rrServer.SendRequest({"quit": {}})
		self.connected = False
		self.EnableButtons(False)			
				
	def Initialize(self):
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.EnableButtons(False)	

		self.delayedRequests = DelayedRequests()				
		self.Bind(wx.EVT_TIMER, self.OnTicker)
		self.ticker = wx.Timer(self)
		self.ticker.Start(400)
		
	def OnTicker(self, _):
		self.delayedRequests.CheckForExpiry(self.Request)

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

		if self.settings.rrserver.simulation:			
			b = layout["blocks"]
			
			bl = [bn for bn in b.keys()]
			for bn in b.keys():
				if b[bn]["sbeast"] is not None:
					bl.append(b[bn]["sbeast"])
				if b[bn]["sbwest"] is not None:
					bl.append(b[bn]["sbwest"])

			self.blockList = sorted(bl, key=self.BuildBlockKey)
			self.chBlock.SetItems(self.blockList)
			self.chBlock.SetSelection(0)
	
			tolist = {"NSw13": 1, "NSw15": 1, "NSw17": 1, "PBSw17": 1, "RSw1": 1}
			leverlist = {}	
			r = layout["routes"]
			self.routes = r
			for rt in r.values():
				for tnm, st in rt["turnouts"]:
					tolist[tnm] = 1
				for signm in rt["signals"]:
					levers = re.findall('[A-Z]+[0-9]+', signm)
					if len(levers) == 1:
						node = levers[0][0]
						if node in [ "C", "N", "P", "Y" ]:  # cliff, nassau, port, yard
							leverlist[levers[0]] = 1
					
			self.turnoutList = sorted([t for t in tolist.keys()], key=self.BuildTurnoutKey)
			self.chTurnout.SetItems(self.turnoutList)
			self.chTurnout.SetSelection(0)
			
			llist = [l for l in leverlist.keys()]
			lvrs = {n: SigLever(n) for n in llist}
			self.sigLevers = {n: sl for n,sl in lvrs.items() if sl.IsValid()}
			self.leverList = sorted([l for l in self.sigLevers.keys()], key=self.BuildSignalLeverKey)
			
			self.chSigLvr.SetItems(self.leverList)
			self.chSigLvr.SetSelection(0)

		self.EnableButtons(self.connected)			
		return self.connected

	def BuildBlockKey(self, blk):
		z = re.match("([A-Za-z]+)([0-9]*)(\\.[EW])?", blk)
		if z is None:
			return blk

		if len(z.groups()) != 3:
			return blk

		base, nbr, suffix = z.groups()
		if nbr != "":
			nbr = "%03d" % int(nbr)

		if suffix is None:
			suffix = ".M"

		return base+nbr+suffix

	def BuildSignalLeverKey(self, slnm):
		z = re.match("([A-Za-z]+)([0-9]+)", slnm)
		if z is None or len(z.groups()) != 2:
			return slnm

		nm, nbr = z.groups()
		return "%s%03d" % (nm, int(nbr))

	def BuildTurnoutKey(self, tonm):
		z = re.match("([A-Za-z]+)([0-9]+)", tonm)
		if z is None or len(z.groups()) != 2:
			return tonm

		nm, nbr = z.groups()
		return "%s%03d" % (nm, int(nbr))

	def Request(self, req):
		if self.connected:
			command = list(req.keys())[0]			
			if "delay" in req[command] and req[command]["delay"] > 0:
				self.delayedRequests.Append(req)
			else:
				self.rrServer.SendRequest(req)
		else:
			dlg = wx.MessageDialog(self, "No connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			

	def OnClose(self, evt):
		try:
			self.ticker.Stop()
		except:
			pass
		
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

