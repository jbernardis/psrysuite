import wx
import logging
from rrobjects import BlockInput, SubBlockInput


class RadioDlg (wx.Dialog):
	def __init__(self, parent, title, choices, value):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.choices = [x for x in choices]
		self.rb = wx.RadioBox(self, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize,
					self.choices, 1, wx.RA_SPECIFY_COLS)
		try:
			ix = self.choices.index(value)
		except ValueError:
			ix = None

		if ix is not None:
			self.rb.SetSelection(ix)

		vsz.Add(self.rb, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
		vsz.AddSpacer(20)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(10)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(vsz)
		hsz.AddSpacer(10)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		self.EndModal(wx.ID_OK)

	def GetResults(self):
		return self.choices[self.rb.GetSelection()]

# district node addresses
YARD      = 0x11
KALE      = 0x12
EASTJCT   = 0x13
CORNELL   = 0x14
YARDSW    = 0x15
PARSONS   = 0x21
PORTA     = 0x22
PORTB     = 0x23
LATHAM    = 0x31
CARLTON   = 0x32
DELL      = 0x41
FOSS      = 0x42
HYDEJCT   = 0x51
HYDE      = 0x52
SHORE     = 0x61
KRULISH   = 0x71
NASSAUW   = 0x72
NASSAUE   = 0x73
NASSAUNX  = 0x74
BANK      = 0x81
CLIVEDEN  = 0x91
GREENMTN  = 0x92
CLIFF     = 0x93
SHEFFIELD = 0x95


def leverState(lvrL, _, lvrR):  # parameter 2 is callon lever - not yet used
	if lvrL == 1 and lvrR == 0:
		return "L"

	if lvrR == 1 and lvrL == 0:
		return "R"

	return "N"

def formatIText(ibuf, nibuf):
	s = []
	for i in range(nibuf):
		s.append("{0:08b}".format(int(ibuf[i].hex(), 16)))
	return " ".join(s)

def formatOText(obuf, nobuf):
	s = []
	for i in range(nobuf):
		s.append("{0:08b}".format(obuf[i]))
	return " ".join(s)


class District(wx.Panel):
	signal = 0
	turnout = 1
	indicator = 2
	relay = 3
	handswitch = 4
	route = 5
	block = 6
	breaker = 7
	nxbutton = 8
	slever = 9
	flever = 10
	hslever = 11
	toggle = 12
	typeLabels = [ "Signal", "Turnout", "Indicator", "Stop Relay", "Handswitch", "Route", "Block", "Breaker",
					"NX Button", "Signal Lever", "Fleet Lever", "HS Lever", "Toggle" ]

	def __init__(self, parent, name, settings):
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.routeMap = {}
		self.name = name
		self.rr = parent
		self.settings = settings
		self.outputMap = {}
		self.inputMap = {}
		self.sigLever = {}  # outbound representation of signal levers
		self.sendIO = False

		self.olist = wx.ListCtrl(self, wx.ID_ANY, pos=(0, 0), size=(260, 300), style=wx.LC_REPORT)
		self.olist.InsertColumn(0, "Output")
		self.olist.SetColumnWidth(0, 100)
		self.olist.InsertColumn(1, "Value", wx.LIST_FORMAT_CENTER)
		self.olist.SetColumnWidth(1, 50)
		self.olist.InsertColumn(2, "Type", wx.LIST_FORMAT_CENTER)
		self.olist.SetColumnWidth(2, 90)

		self.ilist = wx.ListCtrl(self, wx.ID_ANY, pos=(330, 0), size=(260, 300), style=wx.LC_REPORT)
		self.ilist.InsertColumn(0, "Input")
		self.ilist.SetColumnWidth(0, 100)
		self.ilist.InsertColumn(1, "Value", wx.LIST_FORMAT_CENTER)
		self.ilist.SetColumnWidth(1, 50)
		self.ilist.InsertColumn(2, "Type", wx.LIST_FORMAT_CENTER)
		self.ilist.SetColumnWidth(2, 90)

		if self.settings.simulation:
			self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.inputDClick, self.ilist)

	def SendIO(self, flag):
		self.sendIO = flag
		if not flag:
			self.rr.ClearIO()

	def inputDClick(self, evt):
		index = evt.Index
		logging.debug("Double click item %d" % index)
		if index == wx.NOT_FOUND:
			return

		iname = self.ilist.GetItemText(index, 0)
		itype = self.inputMap[iname][2]
		if itype == District.turnout:
			cval = self.ilist.GetItemText(index, 1)
			nval = "R" if cval == "N" else "N"
		elif itype == District.block:
			cval = int(self.ilist.GetItemText(index, 1).split(",")[0])
			nval = 1 - cval
		elif itype == District.slever:
			cval = self.ilist.GetItemText(index, 1)
			dlg = RadioDlg(self, "Signal Lever Position", ["L", "N", "R"], cval)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				nval = dlg.GetResults()
			dlg.Destroy()
			if rc != wx.ID_OK:
				return
		else:
			cval = int(self.ilist.GetItemText(index, 1))
			nval = 1 - cval
		
		# update the display with the new value
		self.ilist.SetItem(index, 1, "%s" % str(nval))
		ip = self.rr.GetInput(iname)
		if ip is None:
			logging.warning("Unable to identify input by name: %s" % iname)
			return

		# apply change to input objects and through there to the listeners
		if itype == District.route:
			ip.SetValue(nval)

		elif itype == District.block:
			ip.SetValue(nval)

		elif itype in [District.turnout, District.slever, District.flever, District.hslever, District.toggle]:
			ip.SetState(nval)

		elif itype == District.breaker:
			ip.SetValue(nval)

		else:
			logging.warning("No handling of input type %s(%s)" % (District.typeLabels[itype], itype))

	def PlaceTrain(self, blknm):
		try:
			ix, ip, itype = self.inputMap[blknm]
		except IndexError:
			return
		if itype != District.block:
			return

		self.ilist.SetItem(ix, 1, "1")
		ip.SetValue(1)

	def RemoveTrain(self, blknm):
		try:
			ix, ip, itype = self.inputMap[blknm]
		except IndexError:
			return
		if itype != District.block:
			return

		self.ilist.SetItem(ix, 1, "0")
		ip.SetValue(0)

	def AddOutputs(self, olist, oclass, otype, ix=0):
		for oname in olist:
			oc = oclass(oname, self)
			self.rr.AddOutput(oc, self, otype)
			self.olist.InsertItem(ix, oname)
			if otype == District.turnout:
				self.olist.SetItem(ix, 1, "0,U")
			elif otype == District.signal:
				self.olist.SetItem(ix, 1, "0,U")
			else:
				self.olist.SetItem(ix, 1, "0")
			self.olist.SetItem(ix, 2, District.typeLabels[otype])
			self.outputMap[oname] = (ix, oc, otype)
			ix += 1
		return ix

	def AddInputs(self, ilist, iclass, itype, ix=0):
		for iname in ilist:
			ic = iclass(iname, self)
			self.rr.AddInput(ic, self, itype)
			self.ilist.InsertItem(ix, iname)
			if itype == District.turnout:
				self.ilist.SetItem(ix, 1, "N")
			elif itype == District.slever:
				self.ilist.SetItem(ix, 1, "N")
			elif itype == District.block:
				self.ilist.SetItem(ix, 1, "0,N,E")
			else:
				self.ilist.SetItem(ix, 1, "0")
			self.ilist.SetItem(ix, 2, District.typeLabels[itype])
			self.inputMap[iname] = (ix, ic, itype)
			ix += 1
		return ix

	def AddSubBlocks(self, bname, sblist, ix):
		blkinp = BlockInput(bname, self)
		self.rr.AddInput(blkinp, self, District.block)
		ix = self.AddInputs(sblist, SubBlockInput, District.block, ix)
		for sbname in sblist:
			subinp = self.rr.GetInput(sbname)
			subinp.SetParent(blkinp)
		return ix

	def RefreshInput(self, iname, itype):
		try:
			ix, ic, dtype = self.inputMap[iname]
		except KeyError:
			logging.warning("Input for %s in district %s not found" % (iname, self.name))
			return
		
		if itype != dtype:
			logging.warning("Type mismatch refreshing input %s: %d != %d" % (iname, itype, dtype))
			return

		if itype == District.turnout:
			state = ic.GetState()
			self.ilist.SetItem(ix, 1, "%s" % state)

		if itype == District.block:
			east = ic.GetEast()
			clear = ic.GetClear()
			val = ic.GetValue()
			self.ilist.SetItem(ix, 1, "%d,%s,%s" % (val, "C" if clear else "N", "E" if east else "W"))
		else:
			logging.warning("Refresh input: no handling of type %s" % itype)

	def RefreshOutput(self, oname, otype=None):
		try:
			ix, oc, dtype = self.outputMap[oname]
		except KeyError:
			logging.warning("Output for %s in district %s not found" % (oname, self.name))
			return
		
		if otype is None:
			otype = dtype
		elif otype != dtype:
			logging.warning("Type mismatch refreshing output %s: %d != %d" % (oname, otype, dtype))
			return

		if otype == District.turnout:
			pulseval = oc.GetOutPulseValue()
			state = oc.GetLock()
			self.olist.SetItem(ix, 1, "%d,%s" % (pulseval, "L" if state != 0 else "U"))
		elif otype == District.signal:
			aspect = oc.GetAspect()
			lock = oc.IsLocked() == 1
			self.olist.SetItem(ix, 1, "%d,%s" % (aspect, "L" if lock else "U"))
		elif otype == District.nxbutton:
			pulseval = oc.GetOutPulseValue()
			self.olist.SetItem(ix, 1, "%d" % pulseval)
		else:
			logging.warning("Refresh output: no handling of type %s" % otype)

	def MapRouteToTurnouts(self, rname):
		try:
			tolist = self.routeMap[rname]
		except KeyError:
			logging.warning("MapRouteToTurnouts: Unknown route name: %s" % rname)
			return False

		for toname, tostate in tolist:
			ip = self.rr.GetInput(toname)
			if ip is None:
				logging.warning("Unable to determine turnout input from name: %s" % toname)
			else:
				ip.SetState(tostate)
		return True

	def EvaluateNXButtons(self, bEntry, bExit):
		pass

	def EvaluateNXButton(self, btn):
		pass

	def SetTurnoutPulseLen(self, to, pl):
		if to not in self.outputMap:
			logging.warning("Turnout %s not found - unable to change pulse length" % to)
			return False

		oc = self.outputMap[to][1]
		oc.SetPulseLen(pl)

	def SetNXButtonPulseLen(self, nxb, pl):
		if nxb not in self.outputMap:
			logging.warning("NX Button %s not found - unable to change pulse length" % nxb)
			return False

		oc = self.outputMap[nxb][1]
		oc.SetPulseLen(pl)

	def UpdateSignal(self, signame):
		try:
			ix, oc = self.outputMap[signame][0:2]
		except KeyError:
			logging.warning("Output for signal %s in district %s not found" % (signame, self.name))
			return
		
		aspect = oc.GetAspect()
		self.olist.SetItem(ix, 1, "%d" % aspect)

	def DetermineSignalLevers(self):
		pass

	def DetermineSignalLever(self, lsigs, rsigs):
		lval = 0
		for sig in lsigs:
			oc = self.rr.GetOutput(sig)
			if oc:
				lval += oc.GetAspect()

		rval = 0
		for sig in rsigs:
			oc = self.rr.GetOutput(sig)
			if oc:
				rval += oc.GetAspect()

		if rval == 0 and lval == 0:
			return 'N'

		if rval == 0:
			return "L"

		if lval == 0:
			return 'R'

		# both non-zero - shouldn't happen, bue set to N
		return 'N'

	def UpdateIndicator(self, indname):
		try:
			ix, oc = self.outputMap[indname][0:2]
		except KeyError:
			logging.warning("Output for indicator %s in district %s not found" % (indname, self.name))
			return
		
		state = oc.GetStatus()
		self.olist.SetItem(ix, 1, "%d" % state)

	def UpdateRelay(self, relayname):
		try:
			ix, oc = self.outputMap[relayname][0:2]
		except KeyError:
			logging.warning("Output for relay %s in district %s not found" % (relayname, self.name))
			return
		
		state = oc.GetStatus()
		self.olist.SetItem(ix, 1, "%d" % state)

	def UpdateHandSwitch(self, hsname):
		try:
			ix, oc = self.outputMap[hsname][0:2]
		except KeyError:
			logging.warning("Output for handswitch %s in district %s not found" % (hsname, self.name))
			return
		
		state = oc.GetStatus()
		self.olist.SetItem(ix, 1, "%d" % state)

	def RailroadEvent(self, cmd):
		self.rr.RailroadEvent(cmd)
