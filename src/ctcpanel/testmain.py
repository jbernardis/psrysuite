import wx
import wx.lib.newevent
import requests
import json
import re
import os, sys
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from ctcpanel import CTCPanel
from turnoutlever import EVT_TURNOUT_LEVER
from siglever import EVT_SIGNAL_LEVER

from dispatcher.settings import Settings
from dispatcher.listener import Listener

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent()
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent()

ignoredCommands = []


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE)
		self.SetBackgroundColour(wx.Colour(64, 64, 64))
		self.settings = Settings()
		self.listener = None
		self.sessionid = None
		self.subscribed = False

		self.Bind(wx.EVT_CLOSE, self.onClose)

		try:
			with open(os.path.join(os.getcwd(), "data", "ctc.json"), "r") as jfp:
				self.ctcdata = json.load(jfp)
		except FileNotFoundError:
			print("unable to open CTC panel data file ctc.json")
			exit(1)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.ctcPanels = {}
		self.sigLeverMap = {}
		self.turnoutLeverMap = {}

		if self.settings.display.pages == 1:
			for pname in self.ctcdata["order"]:
				if self.ctcdata[pname]["screen"] == "LaKr":
					self.ctcdata[pname]["position"][0] += 2560
				elif self.ctcdata[pname]["screen"] == "NaCl":
					self.ctcdata[pname]["position"][0] += 5120

		for pname in self.ctcdata["order"]:
			ctc = CTCPanel(self, pname, self.ctcdata[pname]["signals"], self.ctcdata[pname]["turnouts"], self.ctcdata[pname]["position"])
			self.sigLeverMap.update(ctc.GetSignalLeverMap())
			self.turnoutLeverMap.update(ctc.GetTurnoutLeverMap())
			ctc.Show()
			ctc.Bind(EVT_TURNOUT_LEVER, self.onTurnoutLever)
			ctc.Bind(EVT_SIGNAL_LEVER,  self.onSignalLever)
			self.ctcPanels[pname] = ctc

		hsz.AddSpacer(20)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		self.bConnect = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnConnect, self.bConnect)
		vsz.Add(self.bConnect)
		vsz.AddSpacer(10)
		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.CreateDispatchTable()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		if self.settings.display.pages == 3:
			self.AdjustForScreen("LaKr")

	def raiseDisconnectEvent(self):  # thread context
		evt = DisconnectEvent()
		try:
			wx.PostEvent(self, evt)
		except RuntimeError:
			print(
				"Runtime error caught while trying to post disconnect event - not a problem if this is during shutdown")

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.bConnect.SetLabel("Connect")
		for c in self.ctcPanels.values():
			c.SetConnected(False)

		self.Show()
		self.ShowTitle()

		dlg = wx.MessageDialog(self, "The railroad server connection has gone down.",
							   "Server Connection Error",
							   wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()

	def ShowTitle(self):
		self.SetTitle("CTC Control Panel - %s" % ("NOT connected" if not self.subscribed else "connected" if self.sessionid is None else ("Session ID %d" % self.sessionid)))

	def onSignalLever(self, evt):
		print("main signal %s for lever %s panel %s" % (evt.position, evt.name, evt.panel))
		self.rrServer.SendRequest({'siglever': {'name': evt.name, 'state': evt.position, 'callon': 0, "silent": 0}})

	def onTurnoutLever(self, evt):
		print("main turnout %s for lever %s panel %s" % (evt.position, evt.name, evt.panel))
		self.rrServer.SendRequest({'turnoutlever': {'name': evt.name, 'state': evt.position, 'force': 0}})

	def raiseDeliveryEvent(self, data):  # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			print("Unable to parse (%s)" % data)
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def CreateDispatchTable(self):
		self.dispatch = {
			"signal": self.DoCmdSignal,
			"signallock": self.DoCmdSignalLock,
			"turnout": self.DoCmdTurnout,
			"turnoutlock": self.DoCmdTurnoutLock,

			"sessionID": self.DoCmdSessionID,
			"ctccmd": self.DoCmdCTC,
			# "end": self.DoCmdEnd,
		}

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd not in ignoredCommands:
				try:
					handler = self.dispatch[cmd]
				except KeyError:
					print("Unknown command: %s" % cmd)

				else:
					print("Inbound command: %s: %s" % (cmd, parms))
					handler(parms)

	def DoCmdCTC(self, parms):
		print("DoCmdCTC: %s" % str(parms))
		try:
			action = parms["action"][0]
		except KeyError:
			action = None

		if action is None:
			print("ignoring unknown ctc command: %s" % p)

		elif action == "setscreen":
			scrName = parms["screen"][0]
			self.AdjustForScreen(scrName)

		elif action == "resetscreen":
			scrName = parms["screen"][0]
			self.AdjustPosition(scrName)

	def AdjustForScreen(self, scrName):
		for cn in self.ctcdata["order"]:
			m = scrName == self.ctcdata[cn]["screen"]
			self.ctcPanels[cn].SetHidden(not m)

	def AdjustPosition(self, scrName):
		for cn in self.ctcdata["order"]:
			self.ctcPanels[cn].AssertPosition()

	def DoCmdSessionID(self, parms):
		self.sessionid = int(parms)
		print("connected to railroad server with session ID %d" % self.sessionid)
		self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "CTCPANEL"}})
		self.rrServer.SendRequest({"refresh": {"SID": self.sessionid}})
		self.ShowTitle()

	def DoCmdSignal(self, parms):
		for p in parms:
			signm = p["name"]
			aspect = int(p["aspect"])
			z = re.match("([A-Za-z]+)([0-9]+)([A-Z])", signm)
			if z is None or len(z.groups()) != 3:
				print("Unable to determine lever name from signal name %s" % signm)
				return

			nm, nbr, lr = z.groups()
			lvrID = "%s%d.lvr" % (nm, int(nbr))
			try:
				self.sigLeverMap[lvrID].SetSignalAspect(aspect, lr)
			except KeyError:
				pass

	def DoCmdSignalLock(self, parms):
		for p in parms:
			print("signal lock %s" % str(p))

	def DoCmdTurnout(self, parms):
		for p in parms:
			tonm = p["name"]
			state = p["state"]
			try:
				tl = self.turnoutLeverMap[tonm]
			except KeyError:
				tl = None

			if tl:
				tl.SetTurnoutState(state)

	def DoCmdTurnoutLock(self, parms):
		for p in parms:
			print("turnout lock: %s" % str(p))
			tonm = p["name"]
			try:
				state = int(p["state"])
			except (KeyError, ValueError):
				state = 0

			try:
				tl = self.turnoutLeverMap[tonm]
			except KeyError:
				tl = None

			if tl:
				tl.Enable(state == 0)

	def onClose(self, _):
		self.Destroy()

	def OnConnect(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bConnect.SetLabel("Connect")
			for c in self.ctcPanels.values():
				c.SetConnected(False)
			self.Show()

		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				print("Unable to establish connection with server")
				self.listener = None

				dlg = wx.MessageDialog(self, 'Unable to connect to server', 'Unable to Connect', wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				return

			self.listener.start()
			self.subscribed = True
			self.bConnect.SetLabel("Disconnect")
			for c in self.ctcPanels.values():
				c.SetConnected(True)

			self.Hide()

		self.ShowTitle()


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
			# print("HTTP Error %d" % r.status_code)
			return None

		return r.json()


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()