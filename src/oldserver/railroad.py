import wx
import logging
import time

from oldserver.districts.hyde import Hyde
from oldserver.districts.yard import Yard
from oldserver.districts.latham import Latham
from oldserver.districts.dell import Dell
from oldserver.districts.shore import Shore
from oldserver.districts.krulish import Krulish
from oldserver.districts.nassau import Nassau
from oldserver.districts.bank import Bank
from oldserver.districts.cliveden import Cliveden
from oldserver.districts.cliff import Cliff
from oldserver.districts.port import Port

from oldserver.district import District


class Railroad(wx.Notebook):
	def __init__(self, frame, cbEvent, settings):
		wx.Notebook.__init__(self, frame, wx.ID_ANY, style=wx.BK_DEFAULT)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.pageChanged)
		self.frame = frame
		self.cbEvent = cbEvent
		self.settings = settings
		self.pendingEvents = []

		self.districtList = [
			[ "Yard", Yard ],
			[ "Latham", Latham ],
			[ "Dell", Dell ],
			[ "Shore", Shore ],
			[ "Krulish", Krulish ],
			[ "Nassau", Nassau ],
			[ "Bank", Bank ],
			[ "Cliveden", Cliveden ],
			[ "Cliff", Cliff ],
			[ "Port", Port ],
			[ "Hyde", Hyde ],
		]

		self.controlOptions = {
		}

		self.districts = {}
		self.outputs = {}
		self.inputs = {}
		self.osRoutes = {}
		self.switchLock = {}
		self.fleetedSignals = {}
		self.districtLock = {"NWSL": [0, 0, 0, 0], "NESL": [0, 0, 0]}
		self.enableSendIO = True

		for dname, dclass in self.districtList:
			logging.debug("Creating district %s" % dname)
			p = dclass(self, dname, self.settings)
			self.AddPage(p, dname)
			self.districts[dname] = p

		self.SetPageText(0, "* " + self.districtList[0][0] + " *")

	def Initialize(self):
		# TODO:  put all of these in an ini file
		self.SetControlOption("nassau", 0)
		self.SetControlOption("cliff", 0)
		self.SetControlOption("yard", 0)
		self.SetControlOption("signal4", 0)
		self.SetControlOption("bank.fleet", 0)
		self.SetControlOption("carlton.fleet", 0)
		self.SetControlOption("cliff.fleet", 0)
		self.SetControlOption("cliveden.fleet", 0)
		self.SetControlOption("foss.fleet", 0)
		self.SetControlOption("hyde.fleet", 0)
		self.SetControlOption("hydejct.fleet", 0)
		self.SetControlOption("krulish.fleet", 0)
		self.SetControlOption("latham.fleet", 0)
		self.SetControlOption("nassau.fleet", 0)
		self.SetControlOption("shore.fleet", 0)
		self.SetControlOption("valleyjct.fleet", 0)
		self.SetControlOption("yard.fleet", 0)
		
		self.SetControlOption("osslocks", 1)

		for _, dobj in self.districts.items():
			dobj.SendIO(False)
			dobj.DetermineSignalLevers()

		self.currentDistrict = self.districts["Yard"]
		self.currentDistrict.SendIO(self.settings.viewiobits and not self.settings.hide)
		
		self.GetSubBlockInfo()

	def EnableSendIO(self, flag):
		self.enableSendIO = flag
		self.currentDistrict.SendIO(flag)
				
	def SendIOEnabled(self):
		return self.enableSendIO

	def setBus(self, bus):
		self.rrBus = bus
		for _, dobj in self.districts.items():
			dobj.setBus(bus)

	def pageChanged(self, evt):
		opx = evt.GetOldSelection()
		if opx != wx.NOT_FOUND:
			self.SetPageText(opx, self.districtList[opx][0])
			odistrict = self.districts[self.districtList[opx][0]]
			odistrict.SendIO(False)
		px = evt.GetSelection()
		if px != wx.NOT_FOUND:
			self.SetPageText(px, "* " + self.districtList[px][0] + " *")
			district = self.districts[self.districtList[px][0]]
			district.SendIO(True)
			self.currentDistrict = district

	def ClearIO(self):
		self.frame.ClearIO()

	def ShowText(self, name, addr, otext, itext, line, lines):
		self.frame.ShowText(name, addr, otext, itext, line, lines)

	def AddOutput(self, output, district, otype):
		output.SetRailRoad(self)
		oname = output.GetName()
		if oname in self.outputs:
			logging.warning("Output (%s) duplicate definition" % oname)
			return

		self.outputs[oname] = [output, district, otype]

	def AddInput(self, iput, district, itype):
		iput.SetRailRoad(self)
		iname = iput.GetName()
		if iname in self.inputs:
			logging.warning("Input (%s) duplicate definitionb" % iname)
			return

		self.inputs[iname] = [iput, district, itype]

	def GetOutput(self, oname):
		try:
			return self.outputs[oname][0]
		except KeyError:
			logging.warning("No output found for name \"%s\"" % oname)
			return None

	def GetOutputInfo(self, oname):
		try:
			return self.outputs[oname]
		except KeyError:
			logging.warning("No output found for name \"%s\"" % oname)
			return None

	def GetInput(self, iname):
		try:
			return self.inputs[iname][0]
		except KeyError:
			logging.warning("No input found for name \"%s\"" % iname)
			return None

	def GetInputInfo(self, iname):
		try:
			return self.inputs[iname]
		except KeyError:
			logging.warning("No input found for name \"%s\"" % iname)
			return None

	def GetCurrentValues(self):
		for ip, _, _ in self.inputs.values():
			m = ip.GetEventMessage()
			if m is not None:
				yield m

		for op, _, _ in self.outputs.values():
			m = op.GetEventMessage()
			if m is not None:
				yield m

		for osblk, rtinfo in self.osRoutes.items():
			rt = rtinfo[0]
			ends = rtinfo[1]
			m = {"setroute": [{ "block": osblk, "route": str(rt)}]}
			if ends is not None:
				m["setroute"][0]["ends"] = ["-" if e is None else e for e in ends]
			yield m

		for signm, flag in self.fleetedSignals.items():
			m = {"fleet": [{ "name": signm, "value": flag}]}
			yield m

	def SetControlOption(self, name, value):
		self.controlOptions[name] = value

	def GetControlOption(self, name):
		try:
			return self.controlOptions[name]
		except IndexError:
			return 0

	def SetOSRoute(self, blknm, rtname, ends, signals):
		self.osRoutes[blknm] = [rtname, ends, signals]

	def PlaceTrain(self, blknm):
		if blknm not in self.inputs:
			logging.warning("No input defined for block %s" % blknm)
			return
		_, district, _ = self.inputs[blknm]
		district.PlaceTrain(blknm)

	def RemoveTrain(self, blknm):
		if blknm not in self.inputs:
			logging.warning("No input defined for block %s" % blknm)
			return
		_, district, _ = self.inputs[blknm]
		district.RemoveTrain(blknm)

	def SetAspect(self, signame, aspect):
		if signame not in self.outputs:
			logging.warning("No output defined for signal %s" % signame)
			return
		op, district, _ = self.outputs[signame]
		op.SetAspect(aspect)
		district.DetermineSignalLevers()
		district.RefreshOutput(signame)

	def SetSignalLock(self, signame, lock):
		if signame not in self.outputs:
			logging.warning("No output defined for signal %s" % signame)
			return
		op, district, _ = self.outputs[signame]
		op.SetLock(lock)
		district.RefreshOutput(signame)

	def SetSignalFleet(self, signame, flag):
		self.fleetedSignals[signame] = flag

	def SetBlockDirection(self, block, direction):
		if block not in self.inputs:
			logging.warning("No input defined for block %s" % block)
			return
		ip, _, _ = self.inputs[block]
		ip.SetDirection(direction)

	def SetBlockClear(self, block, clear):
		if block not in self.inputs:
			logging.warning("No input defined for block %s" % block)
			return
		ip, _, _ = self.inputs[block]
		ip.SetClear(clear)

	def SetIndicator(self, indname, state):
		if indname not in self.outputs:
			logging.warning("no output defined for indicator %s" % indname)
			return
		op, district, _ = self.outputs[indname]
		op.SetStatus(state != 0)
		district.UpdateIndicator(indname)

	def SetRelay(self, relayname, state):
		if relayname not in self.outputs:
			logging.warning("no output defined for relay %s" % relayname)
			return
		op, district, _ = self.outputs[relayname]
		op.SetStatus(state != 0)
		district.UpdateRelay(relayname)

	def SetHandSwitch(self, hsname, state):
		if hsname not in self.outputs:
			logging.warning("no output defined for handswitch %s" % hsname)
			return
		op, district, _ = self.outputs[hsname]
		op.SetStatus(state != 0)
		district.UpdateHandSwitch(hsname)

	def SetSwitchLock(self, toname, state):
		self.switchLock[toname] = state
		if toname not in self.outputs:
			logging.warning("no output defined for turnout %s" % toname)
			return
		op, district, _ = self.outputs[toname]
		op.SetLock(state)
		district.RefreshOutput(toname)

	def GetSwitchLock(self, toname):
		if toname in self.switchLock:
			return self.switchLock[toname]
		else:
			return False

	def SetDistrictLock(self, name, value):
		self.districtLock[name] = value

	def GetDistrictLock(self, name):
		if name in self.districtLock:
			return self.districtLock[name]

		return None

	def SetOutPulseTo(self, oname, state):
		if oname not in self.outputs:
			logging.warning("no pulsed output defined for %s" % oname)
			return
		op, district, _ = self.outputs[oname]
		op.SetOutPulseTo(state)
		district.RefreshOutput(oname)

	def SetOutPulseNXB(self, oname):
		if oname not in self.outputs:
			logging.warning("no pulsed output defined for %s" % oname)
			return
		op, district, _ = self.outputs[oname]
		op.SetOutPulseNXB()
		district.RefreshOutput(oname)

	def RefreshOutput(self, oname):
		if oname not in self.outputs:
			logging.warning("no output defined for %s" % oname)
			return
		district = self.outputs[oname][1]
		district.RefreshOutput(oname)

	def RefreshInput(self, iname):
		if iname in self.inputs:
			district, itype = self.inputs[iname][1:3]
			district.RefreshInput(iname, itype)

		else:
			logging.warning("No input defined for %s" % iname)
			return

	def xRefreshInput(self, iname):
		if iname not in self.inputs:
			logging.warning("No input defined for %s" % iname)
			return
		district, itype = self.inputs[iname][1:3]
		district.RefreshInput(iname, itype)

	def EvaluateNXButtons(self, bEntry, bExit):
		if bEntry not in self.outputs:
			logging.warning("No output defined for %s" % bEntry)
			return
		district = self.outputs[bEntry][1]
		district.EvaluateNXButtons(bEntry, bExit)

	def EvaluateNXButton(self, btn):
		if btn not in self.outputs:
			logging.warning("No output defined for %s" % btn)
			return
		district = self.outputs[btn][1]
		district.EvaluateNXButton(btn)

	def allIO(self):
		st = time.monotonic_ns()
		for _, d in self.districts.items():
			d.OutIn()

		self.ReleasePendingEvents()
		et = time.monotonic_ns()
		d = (et-st)/1000000
		#print("IO duration: %d-%d = %f" % (et, st, d))

	def RailroadEvent(self, event):
		self.pendingEvents.append(event)

	def ReleasePendingEvents(self):
		for event in self.pendingEvents:
			self.cbEvent(event)
		
		self.pendingEvents = []
		
	def GetBlockInfo(self):
		blocks = []
		for iput, _, itype in self.inputs.values():
			if itype == District.block:				
				blocks.append([iput.GetName(), 1 if iput.GetEast() else 0])
		return sorted(blocks)

	def GetSubBlockInfo(self):
		self.subblocks = {}
		for iput, _, itype in self.inputs.values():
			if itype == District.block:
				self.subblocks.update(iput.ToJson())
		return self.subblocks