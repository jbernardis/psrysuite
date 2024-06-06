import wx
import wx.lib.newevent
import json
import re
import os

from ctcmanager.ctcpanel import CTCPanel


class CTCManager:
	def __init__(self, frame, settings, diagrams):
		self.settings = settings
		self.frame = frame
		self.visible = False

		try:
			with open(os.path.join(os.getcwd(), "data", "ctc.json"), "r") as jfp:
				self.ctcdata = json.load(jfp)
		except FileNotFoundError:
			print("unable to open CTC panel data file ctc.json")
			exit(1)

		self.ctcPanels = {}
		self.sigLeverMap = {}
		self.turnoutLeverMap = {}

		# if self.settings.display.pages == 1:
		# 	for pname in self.ctcdata["order"]:
		# 		if self.ctcdata[pname]["screen"] == "LaKr":
		# 			self.ctcdata[pname]["position"][0] += 2560
		# 		elif self.ctcdata[pname]["screen"] == "NaCl":
		# 			self.ctcdata[pname]["position"][0] += 5120

		for pname in self.ctcdata["order"]:
			screen = self.ctcdata[pname]["screen"]
			offset = diagrams[screen].offset
			ctc = CTCPanel(frame, pname, self.ctcdata[pname]["signals"], self.ctcdata[pname]["turnouts"], screen, offset, self.ctcdata[pname]["position"])
			self.sigLeverMap.update(ctc.GetSignalLeverMap())
			self.turnoutLeverMap.update(ctc.GetTurnoutLeverMap())
			self.ctcPanels[pname] = ctc

	def SetVisible(self, flag):
		self.visible = flag

	def GetBitmaps(self):
		for ctc in self.ctcPanels.values():
			for bmp in ctc.GetBitmaps():
				yield bmp

	def GetLabels(self):
		for ctc in self.ctcPanels.values():
			for lbl in ctc.GetLabels():
				yield lbl

	def onSignalLever(self, evt):
		self.frame.Request({'siglever': {'name': evt.name, 'state': evt.position, 'callon': 0, "silent": 0, 'source': 'ctc'}})

	def onTurnoutLever(self, evt):
		self.frame.Request({'turnoutlever': {'name': evt.name, 'state': evt.position, 'force': 0, 'source': 'ctc'}})

	def SetScreen(self, scrName):
		self.AdjustForScreen(scrName)

	def ResetScreen(self, scrName):
		self.AdjustPosition(scrName)

	def AdjustForScreen(self, scrName):
		for cn in self.ctcdata["order"]:
			m = scrName == self.ctcdata[cn]["screen"]
			self.ctcPanels[cn].SetHidden(not m)

	def CheckHotSpots(self, scrName, x, y):
		if not self.visible:
			return
		self.frame.PopupEvent("hot spots at %s %d %d" % (scrName, x, y))
		for cn in self.ctcdata["order"]:
			if scrName is None or scrName == self.ctcdata[cn]["screen"]:
				self.ctcPanels[cn].CheckHotSpots(x, y)

	def AdjustPosition(self, scrName):
		for cn in self.ctcdata["order"]:
			self.ctcPanels[cn].AssertPosition()

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

