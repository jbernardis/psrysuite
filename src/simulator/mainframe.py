import wx
import wx.lib.newevent

import os
import json

from simulator.settings import Settings


from simulator.listener import Listener
from simulator.rrserver import RRServer
from simulator.script import Script
from simulator.scrlist import ScriptListCtrl
from simulator.trainparmdlg import TrainParmDlg

from simulator.train import Trains

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 


class MainFrame(wx.Frame):
	def __init__(self, cmdFolder):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.sessionid = None
		self.subscribed = False
		self.settings = Settings()
		self.scripts = {}
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.pausedScripts = []
		self.listener = None
		self.ticker = None
		self.rrServer = None
		self.selectedScripts = []
		self.startable = []
		self.stoppable = []

		self.title = "PSRY Simulator"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh")
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		self.bStart = wx.Button(self, wx.ID_ANY, "Start")
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.bStart)
		self.bStart.Enable(False)

		self.bStop = wx.Button(self, wx.ID_ANY, "Stop")
		self.Bind(wx.EVT_BUTTON, self.OnStop, self.bStop)
		self.bStop.Enable(False)

		self.bClear = wx.Button(self, wx.ID_ANY, "Clear")
		self.Bind(wx.EVT_BUTTON, self.OnClear, self.bClear)
		self.bClear.Enable(False)

		self.bSelectAll = wx.Button(self, wx.ID_ANY, "All")
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.bSelectAll)

		self.bSelectNone = wx.Button(self, wx.ID_ANY, "None")
		self.Bind(wx.EVT_BUTTON, self.OnSelectNone, self.bSelectNone)

		vsz.AddSpacer(20)

		hsz.AddSpacer(20)
		hsz.Add(self.bSubscribe)
		hsz.AddSpacer(20)
		hsz.Add(self.bRefresh)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.scriptList = ScriptListCtrl(self, os.path.join(cmdFolder, "simulator"))
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		btnsz = wx.BoxSizer(wx.VERTICAL)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bSelectAll)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bSelectNone)
		btnsz.AddSpacer(50)
		btnsz.Add(self.bStart)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bStop)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bClear)
		btnsz.AddSpacer(20)
		hsz.Add(btnsz)
		hsz.AddSpacer(10)
		hsz.Add(self.scriptList)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def Initialize(self):
		self.listener = None
		self.ShowTitle()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.ClearDataStructures()

		with open(os.path.join(os.getcwd(), "data", "simscripts.json"), "r") as jfp:
			scripts = json.load(jfp)

		for scr in scripts:
			s = Script(self, scripts[scr], scr, self.cbComplete)
			self.scripts[scr] = s
			self.scriptList.AddScript(s)
			
		self.trains = Trains(os.path.join(os.getcwd(), "data"))

	def reportSelection(self):
		selectedScripts = self.scriptList.GetChecked()
		self.startable = [scr for scr in selectedScripts if not self.scripts[scr].IsRunning()]
		self.stoppable = [scr for scr in selectedScripts if self.scripts[scr].IsRunning()]
		self.enableButtons()

	def enableButtons(self):
		haveStartable = len(self.startable) > 0 and self.subscribed
		self.bStart.Enable(haveStartable)
		self.bClear.Enable(haveStartable)
		self.bStop.Enable(len(self.stoppable) > 0 and self.subscribed)

	def ClearDataStructures(self):
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.pausedScripts = []

	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			self.enableButtons()
			self.ClearDataStructures()
		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				print("Unable to establish connection with server")
				self.listener = None
				return

			self.listener.start()
			self.subscribed = True
			self.bSubscribe.SetLabel("Disconnect")
			self.bRefresh.Enable(True)
			self.enableButtons()

		self.ShowTitle()

	def OnRefresh(self, _):
		self.Request({"refresh": {"SID": self.sessionid}})

	def OnSelectAll(self, _):
		self.scriptList.SelectAll()

	def OnSelectNone(self, _):
		self.scriptList.SelectNone()

	def OnStart(self, _):
		trainParams = {}
		for scr in self.startable:
			tr = self.trains.GetTrainById(scr)
			loco = tr.GetNormalLoco()
			if loco is None:
				loco = "0"
			script = self.scripts[scr]
			tm = script.GetTimeMultiple()
			trainParams[scr] = [scr, loco, tm]
			
		dlg = TrainParmDlg(self, trainParams)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			rv = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
			
		for scr in self.startable:
			p = trainParams[scr]
			script.SetLoco(p[1])
			script.SetTimeMultiple(p[2])
			script = self.scripts[scr]
			script.Execute()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def OnStop(self, _):
		for scr in self.stoppable:
			self.scripts[scr].Stop()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def OnClear(self, _):
		for scr in self.startable:
			self.scripts[scr].RemoveTrain()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def cbComplete(self, scrName):
			self.Request({"traincomplete": {"train": scrName}})
	
	def PauseScript(self, script):
		self.pausedScripts.append(script)

	def CheckResumeScripts(self):
		delList = []
		resumeList = []
		for i in range(len(self.pausedScripts)):
			scr = self.pausedScripts[i]
			if not scr.CheckPause():
				delList.append(i)
				resumeList.append(scr)

		for i in delList:
			del(self.pausedScripts[i])

		for scr in resumeList:
			scr.Resume()

	def SignalAspect(self, signal):
		try:
			return self.signals[signal]
		except KeyError:
			# signal %s unknown
			return False

	def BlockOccupied(self, block):
		blist = block.split(",")
		for b in blist:
			if self.blocks[b][0] != 0:
				return True
		return False

	def NotOSRoute(self, OS, rte):
		route = self.routes[OS][0]
		if rte != route:
			return True
		return False

	def raiseDeliveryEvent(self, data):  # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			#print("Dispatch: %s: %s" % (cmd, parms))
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					self.turnouts[turnout] = state
				self.CheckResumeScripts()

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					if block in self.blocks:
						self.blocks[block][0] = state
					else:
						self.blocks[block] = [ state, 'E']
				self.CheckResumeScripts()

			elif cmd == "blockdir":
				for p in parms:
					block = p["block"]
					direction = p["dir"]
					if block in self.blocks:
						self.blocks[block][1] = direction
					else:
						self.blocks[block] = [ 0, direction]
				self.CheckResumeScripts()
					
			elif cmd == "signal":
				for p in parms:
					sigName = p["name"]
					aspect = p["aspect"]
					self.signals[sigName] = aspect
				self.CheckResumeScripts()

			elif cmd == "setroute":
				for p in parms:
					blknm = p["block"]
					rte = p["route"]
					try:
						ends = p["ends"]
					except KeyError:
						ends = None
					self.routes[blknm] = [rte, ends]
				self.CheckResumeScripts()
											
			elif cmd == "handswitch":
				for p in parms:
					hsName = p["name"]
					state = p["state"]
						
			elif cmd == "indicator":
				for p in parms:
					iName = p["name"]
					value = int(p["value"])

			elif cmd == "breaker":
				for p in parms:
					name = p["name"]
					val = p["value"]

			elif cmd == "settrain":
				for p in parms:
					block = p["block"]
					name = p["name"]
					loco = p["loco"]

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				self.Request({"identify": {"SID": self.sessionid, "function": "SIM"}})
				self.Request({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				if parms["type"] == "layout":
					self.Request({"refresh": {"SID": self.sessionid, "type": "trains"}})
				elif parms["type"] == "trains":
					pass

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def Request(self, req):
		if self.subscribed:
			# print("Outgoing request: %s" % json.dumps(req))
			self.rrServer.SendRequest(req)

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.sessionid = None
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		self.ClearDataStructures()
		self.ShowTitle()

	def OnClose(self, evt):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		self.Destroy()

