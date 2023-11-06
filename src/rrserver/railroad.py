import logging
import re
import sys

from rrserver.districts.yard import Yard
from rrserver.districts.latham import Latham
from rrserver.districts.dell import Dell
from rrserver.districts.shore import Shore
from rrserver.districts.krulish import Krulish
from rrserver.districts.nassau import Nassau
from rrserver.districts.bank import Bank
from rrserver.districts.cliveden import Cliveden
from rrserver.districts.cliff import Cliff
from rrserver.districts.hyde import Hyde
from rrserver.districts.port import Port

from rrserver.constants import INPUT_BLOCK, INPUT_TURNOUTPOS, INPUT_BREAKER, INPUT_SIGNALLEVER,\
	INPUT_HANDSWITCH, INPUT_ROUTEIN

from rrserver.rrobjects import Block, StopRelay, Signal, SignalLever, RouteIn, Turnout,\
			OutNXButton, Handswitch, Breaker, Indicator, ODevice, Lock

class Railroad():
	def __init__(self, parent, cbEvent, settings):
		self.cbEvent = cbEvent
		self.settings = settings
		self.districts = {}
		self.nodes = {}

		self.districtList = [
			[ Yard, "Yard" ],
   			[ Latham, "Latham" ],
   			[ Dell, "Dell" ],
   			[ Shore, "Shore" ],
   			[ Krulish, "Krulish" ],
   			[ Nassau, "Nassau" ],
   			[ Bank, "Bank" ],
   			[ Cliveden, "Cliveden" ],
   			[ Cliff, "Cliff" ],
   			[ Hyde, "Hyde" ],
   			[ Port, "Port" ],
		]
		
		self.controlOptions = {}
		self.signals = {}
		self.signalLevers = {}
		self.blocks = {}
		self.turnouts = {}
		self.handswitches = {}
		self.breakers = {}
		self.stopRelays = {}
		self.outNxButtons = {}
		self.routesIn = {}
		self.osRoutes = {}
		self.indicators = {}
		self.odevices = {}
		self.locks = {}
		self.pendingDetectionLoss = PendingDetectionLoss(self)
		self.reSigName = re.compile("([A-Z][0-9]*)([A-Z])")
		
		self.pulsedOutputs = {} 
		self.topulselen = self.settings.topulselen
		self.topulsect = self.settings.topulsect
		self.nxbpulselen = self.settings.nxbpulselen
		self.nxbpulsect = self.settings.nxbpulsect
		
		
		self.fleetedSignals = {}
		self.districtLock = {"NWSL": [0, 0, 0, 0], "NESL": [0, 0, 0]}
		self.enableSendIO = True
		
		self.addrList = []

		self.subBlocks = {
			"D11": [ "D11A", "D11B" ],
			"D21": [ "D21A", "D21B" ],
			"H10": [ "H10A", "H10B" ],
			"H30": [ "H30A", "H30B" ],
			"S10": [ "S10A", "S10B", "S10C" ],
			"S11": [ "S11A", "S11B" ],
			"S20": [ "S20A", "S20B", "S20C" ],
			"R10": [ "R10A", "R10B", "R10C" ],
		}		

		for dclass, name in self.districtList:
			logging.info("Creating District %s" % name)
			self.districts[name] = dclass(self, name, self.settings)
			self.nodes[name] = self.districts[name].GetNodes()
			self.addrList.extend([[addr, self.districts[name], node] for addr, node, in self.districts[name].GetNodes().items()])
			
	def GetSubBlockInfo(self):
		return self.subBlocks
	
	def GetBlockInfo(self):
		blks = []
		for blknm, blk in self.blocks.items():
			if blk.District() is not None:
				blks.append([blknm, 1 if blk.IsEast() else 0])
		return sorted(blks)

			
	def dump(self):
		logging.info("================================SIGNALS")
		for s in self.signals.values():
			s.dump()

		logging.info("================================BLOCKS")
		for b in self.blocks.values():
			b.dump()

		logging.info("==============================TURNOUTS")
		for t in self.turnouts.values():
			t.dump()

		logging.info("==============================BREAKERS")
		for b in self.breakers.values():
			b.dump()
			
	def Initialize(self):	
		for d in self.districts.values():
			d.Initialize()
			
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
		
		#self.dump()

		return True
			
	def OccupyBlock(self, blknm, state):
		'''
		this method is solely for simulation - to set a block as occupied or not
		'''
		try:
			blist = [ self.blocks[blknm] ]
		except KeyError:
			try:
				blist = [self.GetBlock(x) for x in self.subBlocks[blknm]]
			except KeyError:
				logging.warning("Ignoring occupy command - unknown block name: %s" % blknm)
				return

		for blk in blist:
			if len(blk.Bits()) > 0:
				vbyte, vbit = blk.Bits()[0]
				blk.node.SetInputBit(vbyte, vbit, 1 if state != 0 else 0)
			else:
				'''
				block has sub blocks - occupy all of them as per state
				'''
				sbl = blk.SubBlocks()
				for sb in sbl:
					if len(sb.Bits()) > 0:
						vbyte, vbit = sb.Bits()[0]
						sb.node.SetInputBit(vbyte, vbit, 1 if state != 0 else 0)
		
	def SetTurnoutPos(self, tonm, normal):
		'''
		this method is for simulation - to set a turnout to normal or reverse position - this is also used for handswitches
		'''
		try:
			tout = self.turnouts[tonm]
		except KeyError:
			try:
				tout = self.handswitches[tonm]

			except KeyError:			
				logging.warning("Ignoring turnoutpos command - unknown turnoutname: %s" % tonm)
				return
	
		pos = tout.Position()
		if pos is None:
			logging.warning("Turnout definition does not have position - ignoring turnoutpos command")
			return 
		
		bits, district, node, addr = pos
		node.SetInputBit(bits[0][0], bits[0][1], 1 if normal else 0)
		node.SetInputBit(bits[1][0], bits[1][1], 0 if normal else 1)
			
	def SetBreaker(self, brkrnm, state):
		'''
		this method is solely for simulation - to set a breaker as on or not
		'''
		try:
			brkr = self.breakers[brkrnm]
		except KeyError:
			logging.warning("Ignoring breaker command - unknown breaker name: %s" % brkrnm)
			return
		
		try:
			vbyte, vbit = brkr.Bits()[0]
		except IndexError:
			logging.warning("Breaker definition incomplete - ignoring breaker command")
			return 

		brkr.node.SetInputBit(vbyte, vbit, 1 if state == 0 else 0)
		
	def SetInputBit(self, distName, vbyte, vbit, val):
		pass

	def SetIndicator(self, indname, state):
		'''
		turn an indicator on/off
		'''
		try:
			ind = self.indicators[indname]
		except KeyError:
			logging.warning("Ignoring indicator command - unknown indicator: %s" % indname)
			return
		
		if state == ind.IsOn():
			return False
	
		ind.SetOn(state)	
		bits = ind.Bits()
		if len(bits) > 0:
			vbyte, vbit = bits[0]
			ind.node.SetOutputBit(vbyte, vbit, 1 if state else 0)
		return True

	def SetODevice(self, odname, state):
		'''
		turn an output device on/off
		'''
		try:
			od = self.odevices[odname]
		except KeyError:
			logging.warning("Ignoring output device command - unknown output device: %s" % odname)
			return
		
		vbyte, vbit = od.Bits()[0]
		od.node.SetOutputBit(vbyte, vbit, 1 if state != 0 else 0)

	def SetRelay(self, relayname, state):
		'''
		turn a stopping relay on/off
		'''
		try:
			r = self.stopRelays[relayname]
		except KeyError:
			logging.warning("Ignoring stoprelay command - unknown relay: %s" % relayname)
			return

		bits = r.Bits()
		if len(bits) > 0:		
			vbyte, vbit = bits[0]
			r.node.SetOutputBit(vbyte, vbit, 1 if state != 0 else 0)
		
	def GetRouteIn(self, rtnm):
		try:
			return self.routesIn[rtnm]
		except KeyError:
			return None
		
	def GetBreaker(self, brknm):
		try:
			return self.breakers[brknm]
		except KeyError:
			return None
			
	def SetRouteIn(self, rtnm):
		'''
		this method is solely for simulation - to set the current inbound route
		'''
		try:
			rt = self.routesIn[rtnm]
		except KeyError:
			logging.warning("Ignoring route in command - unknown route name: %s" % rtnm)
			return
		
		offRts = rt.district.SelectRouteIn(rt)
		if offRts is None:
			return 

		for rtenm in offRts:
			rte = self.routesIn[rtenm]
			bt = rte.Bits()
			rte.node.SetInputBit(bt[0][0], bt[0][1], 0)
			
		bt = rt.Bits()
		rt.node.SetInputBit(bt[0][0], bt[0][1], 1)
		
	def ClearAllRoutes(self, rtList):
		for rtenm in rtList:
			rte = self.routesIn[rtenm]
			bt = rte.Bits()
			rte.node.SetInputBit(bt[0][0], bt[0][1], 0)

	def SetOutPulseTo(self, toname, state):
		try:
			turnout = self.turnouts[toname]
		except KeyError:
			logging.warning("Attempt to change state on unknown turnout: %s" % toname)
			return		
			
		Nval = 0 if state == "R" else 1
		Rval = 1 if state == "R" else 0

		bits = turnout.Bits()
		if len(bits) > 0:
			try:
				Nbyte, Nbit = bits[0]
			except IndexError:
				logging.error("index error on turnout %s" % toname)
				return
			
			Rbyte, Rbit = bits[1]
			pbyte = Nbyte if Nval == 1 else Rbyte
			pbit =  Nbit  if Nval == 1 else Rbit
				
			self.pulsedOutputs[toname] = PulseCounter(pbyte, pbit, self.topulsect, self.topulselen, turnout.node)
			
			turnout.node.SetOutputBit(Nbyte, Nbit, Nval)
			turnout.node.SetOutputBit(Rbyte, Rbit, Rval)
		
		if self.settings.simulation:
			'''
			if simulation, set the corresponding input bits to show switch position change
			if there is no position information, defer to the district logic
			'''
			pos = turnout.Position()
			if pos is None:
				turnout.SetNormal(state == "N")
				turnout.district.CheckTurnoutPosition(turnout)
			else:
				bits, district, node, addr = pos
				node.SetInputBit(bits[0][0], bits[0][1], Nval)
				node.SetInputBit(bits[1][0], bits[1][1], Rval)
			
	def SetOutPulseNXB(self, bname):
		try:
			btn = self.outNxButtons[bname]
		except KeyError:
			logging.warning("Attempt to change state on unknown button: %s" % bname)
			return

		bits = btn.Bits()
		Bbyte, Bbit = bits[0]
			
		self.pulsedOutputs[bname] = PulseCounter(Bbyte, Bbit, self.nxbpulsect, self.nxbpulselen, btn.node)
		
		btn.node.SetOutputBit(Bbyte, Bbit, 1)
		if self.settings.simulation:
			'''
			let the district code determine the course of action to simulate the route
			'''
			btn.district.PressButton(btn)

	def SetLock(self, lname, state):
		try:
			lk = self.locks[lname]
		except KeyError:
			logging.warning("Attempt to change lock state on unknown lock: %s" % lname)
			return False
			
		if lk.SetOn(state):
			bits = lk.Bits()
			lk.node.SetOutputBit(bits[0][0], bits[0][1], 1 if state else 0)
			return True
			
		return False

	def SetTurnoutLock(self, toname, state):
		try:
			tout = self.turnouts[toname]
		except KeyError:
			# logging.warning("Attempt to change lock state on unknown turnout: %s" % toname)
			# this is normal for the B half of all crossover pairings
			return

		release = tout.district.Released(tout)			
		if tout.Lock(state == 1):
			tout.UpdateLockBits(release=release)
			self.RailroadEvent(tout.GetEventMessage(lock=True))
		
	def SetAspect(self, signame, aspect, callon=False):
		try:
			sig = self.signals[signame]
		except KeyError:
			logging.warning("Ignoring set aspect - unknown signal name: %s" % signame)
			return
		
		aspect = sig.district.VerifyAspect(signame, aspect)	
		if not sig.SetAspect(aspect):
			return 
		
		bits = sig.Bits()
		lb = len(bits)
		if lb == 0:	
			sig.district.SetAspect(sig, aspect)
		else:
			if lb == 1:
				vals = [1 if aspect != 0 else 0] 
			elif lb == 2:
				vals = [aspect & 0x02, aspect & 0x01] 
			elif lb == 3:
				vals = [aspect & 0x04, aspect & 0x02, aspect & 0x01] 
			else:
				logging.warning("Unknown bits length for signal %s: %d" % (sig.Name(), len(bits)))
				return

			for (vbyte, vbit), val in zip(bits, vals):
				sig.node.SetOutputBit(vbyte, vbit, 1 if val != 0 else 0)

		sig.UpdateIndicators() # make sure all indicators reflect this change
		self.UpdateSignalLeverLEDs(sig, aspect, callon)
		self.RailroadEvent(sig.GetEventMessage(callon=callon))
		
	def UpdateSignalLeverLEDs(self, sig, aspect, callon):
		r = self.reSigName.findall(sig.Name())
		if len(r) != 1 or len(r[0]) != 2:
			return 
		
		try:
			sl = self.signalLevers[r[0][0]]
		except KeyError:
			return

		if aspect == 0:
			lbit = 0
			rbit = 0
		elif r[0][1] == "L":
			lbit = 1
			rbit = 0
		elif r[0][1] == "R":
			lbit = 0
			rbit = 1
		else:
			lbit = 0
			rbit = 0
					
		sl.SetLeverState(rbit, 1 if callon else 0, lbit)
		sl.UpdateLed()
		
	def SetSignalLock(self, signame, lock):
		try:
			sig = self.signals[signame]
		except KeyError:
			logging.warning("Ignoring set signal lock - unknown signal name: %s" % signame)
			return
		
		b = sig.LockBits()
		if len(b) > 0:
			for vbyte, vbit in b:
				sig.node.SetOutputBit(vbyte, vbit, lock)
		
		if sig.Lock(lock):
			self.RailroadEvent(sig.GetEventMessage(lock=True))
			
	def SetHandswitch(self, hsname, state):
		hsnameKey = hsname.split(".")[0] # strip off the ".hand suffix

		try:
			hs = self.handswitches[hsnameKey]
		except KeyError:
			logging.warning("Ignoring set handswitch- unknown switch name: %s" % hsname)
			return
		
		if hs.Lock(state == 1):
			self.RailroadEvent(hs.GetEventMessage(lock=True))
			if not hs.UpdateIndicators():
				hs.District().SetHandswitch(hsnameKey, state)

	def SetSignalFleet(self, signame, flag):
		self.fleetedSignals[signame] = flag

	def SetOSRoute(self, blknm, rtname, ends, signals):
		self.osRoutes[blknm] = [rtname, ends, signals]
		
	def SetControlOption(self, name, value):
		self.controlOptions[name] = value
		if name == "osslocks":
			self.osslocks = value == 1

	def GetControlOption(self, name):
		try:
			return self.controlOptions[name]
		except IndexError:
			return 0
		
	def SetBlockDirection(self, blknm, direction):
		if blknm == "S11":
			print("Set Block Direction S11: %s" % direction, file=sys.stderr, flush=True)
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block direction - unknown block: %s" % blknm)
			return 
		
		if blk.SetDirection(direction == "E"):
			self.RailroadEvent(blk.GetEventMessage(direction=True))

	def SetBlockClear(self, blknm, clear):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block clear - unknown block: %s" % blknm)
			return 
		
		if blk.SetCleared(clear):
			self.RailroadEvent(blk.GetEventMessage(clear=True))
		
	def SetDistrictLock(self, name, value):
		self.districtLock[name] = value
		
		
		
		
		

	def AddBlock(self, name, district, node, address, bits):
		try:
			b = self.blocks[name]
				
		except KeyError:
			# this is the normal scenario
			b = None
			
		if b is None:
			b = Block(name, district, node, address)
		else:
			if b.IsNullBlock():
				b.SetBlockAddress(district, node, address)
			else:
				logging.warning("Potential duplicate block: %s" % name)
				
		b.SetBits(bits)
		self.blocks[name] = b
		if len(bits) > 0:
			node.AddInputToMap(bits[0], [b])
		return b
					
	def AddBlockInd(self, name, district, node, address, bits):
		try:
			b = self.blocks[name]
		except KeyError:
			b = Block(name, None, None, None)
			self.blocks[name] = b
			
		b.AddIndicator(district, node, address, bits)
		return b

	def AddIndicator(self, name, district, node, address, bits):
		if name in self.indicators:
			logging.warning("Duplicate definition for indicator %s" % name)
			return self.indicators[name]
			
		i = Indicator(name, district, node, address)
		i.SetBits(bits)
		self.indicators[name] = i
		return i

	def AddOutputDevice(self, name, district, node, address, bits):
		if name in self.odevices:
			logging.warning("Duplicate definition for output device %s" % name)
			return self.odevices[name]
			
		i = ODevice(name, district, node, address)
		i.SetBits(bits)
		self.odevices[name] = i
		return i

	def AddLock(self, name, district, node, address, bits):
		if name in self.locks:
			logging.warning("Duplicate definition for lock%s" % name)
			return self.odevices[name]
			
		i = Lock(name, district, node, address)
		i.SetBits(bits)
		self.locks[name] = i
		return i

	def AddStopRelay(self, name, district, node, address, bits):
		if name in self.stopRelays:
			logging.warning("Duplicate definition for stopping relay %s" % name)
			return self.stopRelays[name]
			
		r = StopRelay(name, district, node, address)
		r.SetBits(bits)
		self.stopRelays[name] = r
		return r
	
	def AddSignal(self, name, district, node, address, bits):
		try:
			s = self.signals[name]
				
		except KeyError:
			# this is the normal scenario
			s = None
			
		if s is None:
			s = Signal(name, district, node, address)
		else:
			if s.IsNullSignal():
				s.SetSignalAddress(district, node, address)
			else:
				logging.warning("Potential duplicate signal: %s" % name)
				
		s.SetBits(bits)
		self.signals[name] = s
		return s

	def AddSignalInd(self, name, district, node, address, bits):
		try:
			s = self.signals[name]
		except KeyError:
			s = Signal(name, None, None, None)
			self.signals[name] = s
				
		s.AddIndicator(district, node, address, bits)
		return s

	def AddSignalLever(self, name, district, node, address, bits):
		try:
			s = self.signalLevers[name]
				
		except KeyError:
			# this is the normal scenario
			s = None
			
		if s is None:
			s = SignalLever(name, district, node, address)
		else:
			if s.IsNullLever():
				s.SetLeverAddress(district, node, address)
			else:
				logging.warning("Potential duplicate signal lever: %s" % name)
				
		s.SetBits(bits)
		self.signalLevers[name] = s
		if bits[0] is not None:
			node.AddInputToMap(bits[0], [s, 'R'])
		if bits[1] is not None:
			node.AddInputToMap(bits[1], [s, 'C'])
		if bits[2] is not None:
			node.AddInputToMap(bits[2], [s, 'L'])
		return s

	def AddSignalLED(self, name, district, node, address, bits):
		try:
			s = self.signalLevers[name]
		except KeyError:
			s = SignalLever(name, None, None, None)
			self.signalLevers[name] = s
				
		s.SetLed(bits, district, node, address)
		return s
		
	def AddTurnout(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
				
		except KeyError:
			# this is the normal scenario
			t = None
			
		if t is None:
			t = Turnout(name, district, node, address)
		else:
			if t.IsNullTurnout():
				t.SetTurnoutAddress(district, node, address)
			else:
				logging.warning("Potential duplicate turnout: %s" % name)
				
		t.SetBits(bits)
		self.turnouts[name] = t
		return t

	def AddTurnoutPosition(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetPosition(bits, district, node, address)
		node.AddInputToMap(bits[0], [t, 'N'])
		node.AddInputToMap(bits[1], [t, 'R'])
		return t

	def AddTurnoutLock(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLockBits(bits, district, node, address)
		return t

	def AddTurnoutLever(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLever(bits, district, node, address)
		return t

	def AddTurnoutLED(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLed(bits, district, node, address)
		return t
		
					
	def AddOutNXButton(self, name, district, node, address, bits):
		if name in self.outNxButtons:
			logging.warning("Duplicate definition for Out NX Button %s" % name)
			return self.outNxButtons[name]

		b = OutNXButton(name, district, node, address)
		self.outNxButtons[name] = b			
		b.SetBits(bits)
		return b
	
	def AddHandswitch(self, name, district, node, address, bits):
		try:
			t = self.handswitches[name]
				
		except KeyError:
			# this is the normal scenario
			t = None
			
		if t is None:
			t = Handswitch(name, district, node, address)
		else:
			if t.IsNullHandswitch():
				t.SetHandswitchAddress(district, node, address)
			else:
				logging.warning("Potential duplicate handset: %s" % name)

		self.handswitches[name] = t		
		t.SetBits(bits)
		node.AddInputToMap(bits[0], [t, 'N'])
		node.AddInputToMap(bits[1], [t, 'R'])
		return t
					
	def AddHandswitchInd(self, name, district, node, address, bits, inverted=False):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
			self.handswitches[name] = s
			
		s.AddIndicator(district, node, address, bits, inverted)
		return s
					
	def AddHandswitchReverseInd(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
			self.handswitches[name] = s
			
		s.AddReverseIndicator(district, node, address, bits)
		return s
					
	def AddHandswitchUnlock(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
			self.handswitches[name] = s
			
		s.AddUnlock(district, node, address, bits)
		node.AddInputToMap(bits[0], [s, 'L'])
		return s
					
	def AddRouteIn(self, name, district, node, address, bits):
		if name in self.routesIn:
			logging.warning("Duplicate definition for Route In %s" % name)
			return self.routesIn[name]

		b = RouteIn(name, district, node, address)
		self.routesIn[name] = b		
		b.SetBits(bits)
		node.AddInputToMap(bits[0], [b])
		
		return b

	def AddBreaker(self, name, district, node, address, bits):
		try:
			b = self.breakers[name]
				
		except KeyError:
			# this is the normal scenario
			b = None
			
		if b is None:
			b = Breaker(name, district, node, address)
		else:
			if b.IsNullBreaker():
				b.SetBreakerAddress(district, node, address)
			else:
				logging.warning("Potential duplicate breaker: %s" % name)
				
		b.SetBits(bits)
		self.breakers[name] = b
		if len(bits) > 0:
			node.AddInputToMap(bits[0], [b])
			
		return b
					
	def AddBreakerInd(self, name, district, node, address, bits):
		try:
			b = self.breakers[name]
		except KeyError:
			b = Breaker(name, None, None, None)
			self.breakers[name] = b
			
		b.AddIndicator(district, node, address, bits)
		return b
	
	def setBus(self, bus):
		self.rrBus = bus
		for _, dobj in self.districts.items():
			dobj.setBus(bus)

	def GetCurrentValues(self):
		'''
		set turnouts/routes/blocks BEFORE signals
		'''					
		for l in [self.turnouts, self.blocks, self.signals, self.signalLevers, self.stopRelays]:
			for s in l.values():
				ml = s.GetEventMessages()
				for m in ml:
					if m is not None:
						yield m
					
		for s in self.breakers.values():
			if not s.HasProxy(): # skip breakers that use a proxy
				m = s.GetEventMessage()
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

	def PlaceTrain(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("Skipping train placement for block %s: unknown block" % blknm)
			return

		if blk.SetOccupied(True):
			self.RailroadEvent(blk.GetEventMessage())


	def RemoveTrain(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("Skipping remove train for block %s: unknown block" % blknm)
			return

		if blk.SetOccupied(False):
			self.RailroadEvent(blk.GetEventMessage())









	def GetSwitchLock(self, toname):  # only used by port - reserve judgement until then
		if toname in self.switchLock:
			return self.switchLock[toname]
		else:
			return False

	def GetDistrictLock(self, name):  # only used in nassau - reserve judgement til then
		if name in self.districtLock:
			return self.districtLock[name]

		return None

	def GetBlock(self, blknm):
		try:
			return self.blocks[blknm]
		except KeyError:
			return None

	def GetStopRelay(self, blknm):
		try:
			return self.stopRelays[blknm]
		except KeyError:
			return None

	def GetTurnout(self, tonm):
		try:
			return self.turnouts[tonm]
		except KeyError:
			return None

	def GetHandswitch(self, hsnm):
		try:
			return self.handswitches[hsnm]
		except KeyError:
			return None

	def GetIndicator(self, indnm):
		try:
			return self.indicators[indnm]
		except KeyError:
			return None

	def GetSignal(self, signm):
		try:
			return self.signals[signm]
		except KeyError:
			return None

	def GetOutputDevice(self, onm):
		try:
			return self.odevices[onm]
		except KeyError:
			return None
			
	def GetNodeBits(self, addr):
		'''
		this routine handles the getbits command from HTTP server
		'''
		for dnodes in self.nodes.values():
			if addr in dnodes:
				return dnodes[addr].GetAllBits()
			
		return 0, [], []

	def SetInputBitByAddr(self, addr, vbytes, vbits, vals):
		'''
		this routine handles the setinbit command from HTTP server
		'''
		for dnodes in self.nodes.values():
			if addr in dnodes:
				for i in range(len(vbytes)):
					dnodes[addr].SetInputBit(vbytes[i], vbits[i], 1 if vals[i] != 0 else 0)

	def OutIn(self):
		delList = []
		for toname, ctr in self.pulsedOutputs.items():
			if not ctr.tally():
				delList.append(toname)
				
		for toname in delList:
			del self.pulsedOutputs[toname]	
			
		self.pendingDetectionLoss.NextCycle()			
		
		for district in self.districts.values():
			district.OutIn()
					
		self.ExamineInputs()
		
	def UpdateDistrictTurnoutLocksByNode(self, districtName, released, addressList):
		for t in self.turnouts.values():
			if t.district is None:
				continue
			
			if t.district.Name() == districtName and t.address in addressList:
				t.UpdateLockBits(released)
		
	def UpdateDistrictTurnoutLocks(self, districtName, released):
		for t in self.turnouts.values():
			if t.district is None:
				continue
			
			if t.district.Name() == districtName:
				t.UpdateLockBits(released)
		
	def ExamineInputs(self):
		for addr, district, node in self.addrList:
			skiplist, resumelist = district.GetControlOption()
			changedBits = node.GetChangedInputs()
			for node, vbyte, vbit, objparms, newval in changedBits:
				obj = objparms[0]
				objType = obj.InputType()
				objName = obj.Name()

				if objType == INPUT_BLOCK:
					# if block has changed to occupied
					if newval != 0:
						# remove any pending detectio loss
						self.pendingDetectionLoss.Remove(objName)
						# and process the detection gain
						if obj.SetOccupied(True):
							self.RailroadEvent(obj.GetEventMessage())
							obj.UpdateIndicators()
					
					# otherwise, this is a detection loss - add it to pending, but only if we are currently occupied
					else:
						if obj.IsOccupied():
							self.pendingDetectionLoss.Add(objName, obj)
						else:
							if obj.SetOccupied(False):
								self.RailroadEvent(obj.GetEventMessage())
								obj.UpdateIndicators()

			
				elif objType == INPUT_TURNOUTPOS:
					pos = obj.Position()
					if pos:
						bits, district, node, address = pos
						nflag = node.GetInputBit(bits[0][0], bits[0][1])
						rflag = node.GetInputBit(bits[1][0], bits[1][1])
						'''
						the switch itself is telling us what position it is it.  This
						must be forced on all display programs
						'''
						if obj.IsNormal():
							if nflag == 0 and rflag == 1:
								if obj.SetNormal(False):
									self.RailroadEvent(obj.GetEventMessage(force=True))
									obj.UpdateLed()
						else:
							if nflag == 1 and rflag == 0:
								if obj.SetNormal(True):
									self.RailroadEvent(obj.GetEventMessage(force=True))
									obj.UpdateLed()
								
					if obj.HasLever():
						bt = obj.Bits()
						if len(bt) > 0:
							nbit, rbit = node.GetInputBits(bt)
							if obj.SetLeverState('R' if nbit == 0 else 'N'):
								obj.district.TurnoutLeverChange(obj)
						
				elif objType == INPUT_BREAKER:
					if obj.SetStatus(newval == 1):
						if obj.HasProxy():
							# use the proxy to show updated breaker status
							obj.district.ShowBreakerState(obj)
						else:
							obj.UpdateIndicators()
							self.RailroadEvent(obj.GetEventMessage())
	
				elif objType == INPUT_SIGNALLEVER:
					if obj.Name() not in skiplist: # bypass levers that are skipped because of control option
						bt = obj.Bits()
						if len(bt) > 0:
							rbit, cbit, lbit = node.GetInputBits(bt)
							if obj.SetLeverState(rbit, cbit, lbit):
								self.RailroadEvent(obj.GetEventMessage())
								obj.UpdateLed()

				elif objType == INPUT_HANDSWITCH:
					dataType = objparms[1]
					if dataType == "L":
						objnm = obj.Name()
						if objnm in [ "CSw21ab", "PBSw15ab" ]:
							if objnm not in skiplist:
								if obj.Lock(newval != 0):
									obj.UpdateIndicators()
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									district.SetHandswitchIn(obj, newval)
						else:
							if objnm not in skiplist:
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									uflag = node.GetInputBit(bits[0][0], bits[0][1])
									if obj.Lock(uflag != 0):
										self.RailroadEvent(obj.GetEventMessage(lock=True))
										obj.UpdateIndicators()
					
					else:
						pos = obj.Position()
						if pos:
							district, node, address, bits = pos
							nflag = node.GetInputBit(bits[0][0], bits[0][1])
							rflag = node.GetInputBit(bits[1][0], bits[1][1])
							if obj.IsNormal():
								if nflag == 0 and rflag == 1:
									if obj.SetNormal(False):
										self.RailroadEvent(obj.GetEventMessage())
							else:
								if nflag == 1 and rflag == 0:
									if obj.SetNormal(True):
										self.RailroadEvent(obj.GetEventMessage())
		
				elif objType == INPUT_ROUTEIN:
					bt = obj.Bits()
					if len(bt) > 0:
						stat = node.GetInputBit(bt[0][0], bt[0][1])
						obj.district.RouteIn(obj, stat)
						
			'''
			The resume list is a list of objects - signal levers, or handswitch unlocks - that have been ignored because of the
			control setting for this district, but now need to be considered because the control value has changed.  We need to 
			react to the current value of these objects as if they were just now set to their current value
			'''
			for o in resumelist:
				try:
					obj = self.signalLevers[o]
				except KeyError:
					try:
						obj = self.handswitches[o]
					except KeyError:
						logging.error("Unknown object name: %s in resume list" % o)
						
					else:
						unlock = obj.GetUnlock()
						if unlock:
							district, node, addr, bits = unlock
							uflag = node.GetInputBit(bits[0][0], bits[0][1])
							if obj.Lock(uflag == 1):
								self.RailroadEvent(obj.GetEventMessage(lock=True))
						
				else:
					bt = obj.Bits()
					if len(bt) > 0:
						rbit, cbit, lbit = obj.node.GetInputBits(bt)
						if obj.SetLeverState(rbit, cbit, lbit):
							self.RailroadEvent(obj.GetEventMessage())
							obj.UpdateLed()
			

	def RailroadEvent(self, event):
		self.cbEvent(event)

class PendingDetectionLoss:
	def __init__(self, railroad):
		self.pendingDetectionLoss = {}
		self.railroad = railroad
		self.pendingDetectionLossCycles = railroad.settings.pendingdetectionlosscycles
				
	def Add(self, block, obj):
		self.pendingDetectionLoss[block] = [obj, self.pendingDetectionLossCycles]
		
	def Remove(self, block):
		try:
			del self.pendingDetectionLoss[block]
		except:
			return False
		
		return True
		
	def NextCycle(self):
		removeBlock = []
		for blkName in self.pendingDetectionLoss:
			self.pendingDetectionLoss[blkName][1] -= 1
			if self.pendingDetectionLoss[blkName][1] <= 0:
				# it's time to believe - process the detection loss and remove from this list
				obj = self.pendingDetectionLoss[blkName][0]
				if obj.SetOccupied(False):
					self.railroad.RailroadEvent(obj.GetEventMessage())
					obj.UpdateIndicators()
					
				removeBlock.append(blkName)
			
		for blkName in removeBlock:
			del(self.pendingDetectionLoss[blkName])
		
class PulseCounter:
	def __init__(self, vbyte, vbit, pct, plen, node):
		self.vbyte = vbyte
		self.vbit = vbit
		self.count = pct
		self.length = plen
		self.resetLength = plen
		self.node = node
		
	def tally(self):
		if self.length == 0:
			self.count -= 1
			if self.count == 0:
				return False
				
			self.length = self.resetLength
			sendBit = 1
		else:
			self.length -= 1
			sendBit = 0 if self.length == 0 else 1

		self.node.SetOutputBit(self.vbyte, self.vbit, sendBit)
		return True
