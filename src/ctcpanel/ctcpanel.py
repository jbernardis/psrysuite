import wx
from siglever import SigLever, EVT_SIGNAL_LEVER
from turnoutlever import TurnoutLever, EVT_TURNOUT_LEVER


class CTCPanel(wx.Dialog):
	def __init__(self, parent, name, signals, turnouts, position):
		self.parent = parent
		self.titleString = name
		self.position = [x for x in position]
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "", style = wx.DIALOG_NO_PARENT | wx.STAY_ON_TOP, pos=position)
		self.panelName = name
		self.signals = signals
		self.turnouts = turnouts
		self.sigLeverMap = {}
		self.trnLeverMap = {}
		self.connected = False

		self.SetBackgroundColour(wx.Colour(0, 0, 0))

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(5)
		for sig in self.signals:
			sl = SigLever(self, sig["label"], sig["name"], self.panelName)
			hsz.Add(sl)
			self.sigLeverMap[sig["name"]] = sl
			sl.Bind(EVT_SIGNAL_LEVER, self.onSignalLever)

			hsz.AddSpacer(5)

		hsz2 = wx.BoxSizer(wx.HORIZONTAL)
		hsz2.AddSpacer(5)

		for sw in self.turnouts:
			tl = TurnoutLever(self, sw["label"], sw["name"], self.panelName)
			hsz2.Add(tl)
			self.trnLeverMap[sw["name"]] = tl
			tl.Bind(EVT_TURNOUT_LEVER, self.onTurnoutLever)

			hsz2.AddSpacer(5)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(5)
		vsz.Add(hsz)
		vsz.AddSpacer(5)
		vsz.Add(hsz2)
		vsz.AddSpacer(5)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.ShowTitle()

	def ShowTitle(self):
		ts = self.titleString

		if not self.connected:
			ts += " - NOT connected"

		self.SetTitle(ts)

	def SetConnected(self, flag=True):
		self.connected = flag
		self.ShowTitle()

	def IsConnected(self):
		return self.connected

	def SetHidden(self, flag):
		if flag:
			self.Hide()
		else:
			self.Show()

	def AssertPosition(self):
		self.SetPosition(self.position)

	def GetSignalLeverMap(self):
		return self.sigLeverMap

	def GetTurnoutLeverMap(self):
		return self.trnLeverMap

	def onSignalLever(self, evt):
		if not self.connected:
			return

		Level = evt.StopPropagation()
		evt.ResumePropagation(evt.StopPropagation()+1)
		evt.Skip()

	def onTurnoutLever(self, evt):
		if not self.connected:
			return

		Level = evt.StopPropagation()
		evt.ResumePropagation(evt.StopPropagation()+1)
		evt.Skip()
