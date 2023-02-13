import wx
import wx.lib.newevent

import os
import json

from atc.settings import Settings


from atc.listener import Listener
from atc.rrserver import RRServer

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

		self.title = "PSRY Automatic Train Control"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh")
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		vsz.AddSpacer(20)

		hsz.AddSpacer(20)
		hsz.Add(self.bSubscribe)
		hsz.AddSpacer(20)
		hsz.Add(self.bRefresh)
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

		print("finished initialize")

	def enableButtons(self):
		pass
	
	def ClearDataStructures(self):
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}

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
		self.rrServer.SendRequest({"refresh": {"SID": self.sessionid}})

	def SignalAspect(self, signal):
		try:
			return self.signals[signal]
		except KeyError:
			print("signal %s unknown" % signal)
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
			print("Unable to parse (%s)" % data)
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

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					if block in self.blocks:
						self.blocks[block][0] = state
					else:
						self.blocks[block] = [ state, 'E']

			elif cmd == "blockdir":
				for p in parms:
					block = p["block"]
					direction = p["dir"]
					if block in self.blocks:
						self.blocks[block][1] = direction
					else:
						self.blocks[block] = [ 0, direction]
					
			elif cmd == "signal":
				for p in parms:
					sigName = p["name"]
					aspect = p["aspect"]
					self.signals[sigName] = aspect

			elif cmd == "setroute":
				for p in parms:
					blknm = p["block"]
					rte = p["route"]
					try:
						ends = p["ends"]
					except KeyError:
						ends = None
					self.routes[blknm] = [rte, ends]
											
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
				self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "ATC"}})

			elif cmd == "end":
				if parms["type"] == "layout":
					self.rrServer.SendRequest({"refresh": {"SID": self.sessionid, "type": "trains"}})
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

