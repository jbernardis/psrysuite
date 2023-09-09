from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING, RegAspects


class Bank (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)
		
	def PerformHandSwitchAction(self, hs):
		controlOpt = self.frame.rbCliffControl.GetSelection()
		if controlOpt == 0:  # cliff local control or limited to bank/cliveden (handled in those districts)
			msg = "Cliff control is local"
			self.frame.PopupEvent(msg)
			return

		District.PerformHandSwitchAction(self, hs)

	def PerformTurnoutAction(self, turnout, force=False):
		controlOpt = self.frame.rbCliffControl.GetSelection()
		if controlOpt == 0:  # bank local control
			self.frame.PopupEvent("Bank control is local")
			return

		District.PerformTurnoutAction(self, turnout, force=force)

	def PerformSignalAction(self, sig, callon=False):
		controlOpt = self.frame.rbCliffControl.GetSelection()
		if controlOpt == 0:  # bank local control
			self.frame.PopupEvent("Bank control is local")
			return

		District.PerformSignalAction(self, sig, callon=callon)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, ["CSw17", "CSw23"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["B20"] = Block(self, self.frame, "B20",
			[
				(self.tiles["horiznc"], self.screen,      (45, 13), False),
				(self.tiles["horiz"],   self.screen,      (46, 13), False),
				(self.tiles["horiznc"], self.screen,      (47, 13), False),
				(self.tiles["horiz"],   self.screen,      (48, 13), False),
				(self.tiles["horiznc"], self.screen,      (49, 13), False),
			], True)
		self.blocks["B20"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen,      (50, 13), False),
				(self.tiles["horiznc"], self.screen,      (51, 13), False),
				(self.tiles["eobright"],self.screen,      (52, 13), False),
			], True)
		self.blocks["B20"].AddTrainLoc(self.screen, (47, 13))

		self.blocks["B11"] = Block(self, self.frame, "B11",
			[
				(self.tiles["horiznc"], self.screen,      (61, 11), False),
				(self.tiles["horiz"],   self.screen,      (62, 11), False),
				(self.tiles["horiz"],   self.screen,      (64, 11), False),
				(self.tiles["horiznc"], self.screen,      (65, 11), False),
				(self.tiles["eobright"],self.screen,      (67, 11), False),
			], False)
		self.blocks["B11"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (58, 11), False),
				(self.tiles["horiznc"], self.screen,      (59, 11), False),
				(self.tiles["horiz"],   self.screen,      (60, 11), False),
			], False)
		self.blocks["B11"].AddTrainLoc(self.screen, (59, 11))

		self.blocks["B21"] = Block(self, self.frame, "B21",
			[
				(self.tiles["horiz"],   self.screen,      (60, 13), False),
				(self.tiles["horiznc"], self.screen,      (61, 13), False),
				(self.tiles["horiz"],   self.screen,      (62, 13), False),
				(self.tiles["horiz"],   self.screen,      (64, 13), False),
				(self.tiles["horiznc"], self.screen,      (65, 13), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen,      (66, 13), False),
				(self.tiles["eobright"],self.screen,      (67, 13), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (58, 13), False),
				(self.tiles["horiznc"], self.screen,      (59, 13), False),
			], False)
		self.blocks["B21"].AddTrainLoc(self.screen, (59, 13))

		self.blocks["BOSWW"] = OverSwitch(self, self.frame, "BOSWW",
			[
				(self.tiles["eobleft"],  self.screen,     (53, 11), False),
				(self.tiles["horiznc"],  self.screen,     (55, 11), False),
				(self.tiles["horiz"],    self.screen,     (56, 11), False),
				(self.tiles["eobright"], self.screen,     (57, 11), False),
				(self.tiles["diagright"],self.screen,     (55, 12), False),
				(self.tiles["eobright"], self.screen,     (57, 13), False),
			], False)

		self.blocks["BOSWE"] = OverSwitch(self, self.frame, "BOSWE",
			[
				(self.tiles["eobleft"],  self.screen,     (53, 13), False),
				(self.tiles["horiz"],    self.screen,     (54, 13), False),
				(self.tiles["horiznc"],  self.screen,     (55, 13), False),
				(self.tiles["eobright"], self.screen,     (57, 13), False),
			], False)

		self.blocks["BOSE"] = OverSwitch(self, self.frame, "BOSE",
			[
				(self.tiles["eobleft"],  self.screen,     (68, 11), False),
				(self.tiles["turnrightright"],self.screen,(69, 11), False),
				(self.tiles["diagright"],self.screen,     (70, 12), False),
				(self.tiles["eobleft"],  self.screen,     (68, 13), False),
				(self.tiles["horiz"],    self.screen,     (69, 13), False),
				(self.tiles["horiznc"],  self.screen,     (70, 13), False),
				(self.tiles["eobright"], self.screen,     (72, 13), False),
			], True)

		self.osBlocks["BOSWW"] = [ "B10", "B11", "B21" ]
		self.osBlocks["BOSWE"] = [ "B20", "B21", "B10" ]
		self.osBlocks["BOSE"] = [ "B11", "B21", "C13" ]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			[ "CSw17",  "torightleft",  ["BOSE"], (71, 13) ],
			[ "CSw19",  "torightright",  ["B21"], (63, 13) ],
			[ "CSw21a", "torightleft",   ["B11"], (66, 11) ],
			[ "CSw21b", "torightleft",   ["B11"], (63, 11) ],
			[ "CSw23",  "torightright",  ["BOSWW", "BOSWE"], (54, 11) ],
			[ "CSw23b", "torightleft",   ["BOSWW", "BOSWE"], (56, 13) ],
		]

		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		self.turnouts["CSw23"].SetPairedTurnout(self.turnouts["CSw23b"])

		self.turnouts["CSw19"].SetDisabled(True)
		self.turnouts["CSw21a"].SetDisabled(True)
		self.turnouts["CSw21b"].SetDisabled(True)

		return self.turnouts
		
	def DefineSignals(self):
		self.signals = {}

		sigList = [
			[ "C18LA",  RegAspects, True,    "right", (68, 12) ],
			[ "C18LB",  RegAspects, True,    "rightlong", (68, 14) ],
			[ "C18R",   RegAspects, False,   "leftlong", (72, 12) ],

			[ "C22L",   RegAspects, True,    "right", (53, 12) ],
			[ "C22R",   RegAspects, False,   "leftlong", (57, 10) ],

			[ "C24L",   RegAspects, True,    "rightlong", (53, 14) ],
			[ "C24R",   RegAspects, False,   "leftlong", (57, 12) ],
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.sigLeverMap = {
			"C18.lvr": [ "BOSE" ],
			"C22.lvr": [ "BOSWW" ],
			"C24.lvr": [ "BOSWW", "BOSWE" ],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		blockSbSigs = {
			# # which signals govern stopping sections, west and east
			"B11": ("C22R",  None),
			"B20": (None,    "C24L"),
			"B21": ("C24R",  "C18LB"),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)
			
		blockSigs = {
			# # which signals govern blocks, west and east - not needed for OS and stopping blocks
			"B11": ("C22R",  "C18LA"),
			"B20": ("N24L",  "C24L"),
			"B21": ("C24R",  "C18LB"),
		}

		for blknm, siglist in blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}

		block = self.blocks["BOSWW"]
		self.routes["BRtB10B11"] = Route(self.screen, block, "BRtB10B11", "B11", [ (53, 11), (54, 11), (55, 11), (56, 11), (57, 11) ], "B10", [RESTRICTING, MAIN], ["CSw23:N"], ["C22R", "C22L"])
		self.routes["BRtB10B21"] = Route(self.screen, block, "BRtB10B21", "B21", [ (53, 11), (54, 11), (55, 12), (56, 13), (57, 13) ], "B10", [RESTRICTING, DIVERGING], ["CSw23:R"], ["C24R", "C22L"])

		block=self.blocks["BOSWE"]
		self.routes["BRtB20B21"] = Route(self.screen, block, "BRtB20B21", "B21", [ (53, 13), (54, 13), (55, 13), (56, 13), (57, 13) ], "B20", [MAIN, RESTRICTING], ["CSw23:N"], ["C24R", "C24L"])

		block=self.blocks["BOSE"]
		self.routes["BRtB11C13"] = Route(self.screen, block, "BRtB11C13", "B11", [ (68, 11), (69, 11), (70, 12), (71, 13), (72, 13) ], "C13", [RESTRICTING, DIVERGING], ["CSw17:R"], ["C18LA", "C18R"])
		self.routes["BRtB21C13"] = Route(self.screen, block, "BRtB21C13", "B21", [ (68, 13), (69, 13), (70, 13), (71, 13), (72, 13) ], "C13", [MAIN, MAIN], ["CSw17:N"], ["C18LB", "C18R"])

		self.signals["C22L"].AddPossibleRoutes("BOSWW", [ "BRtB10B11", "BRtB10B21" ])
		self.signals["C22R"].AddPossibleRoutes("BOSWW", [ "BRtB10B11" ])

		self.signals["C24L"].AddPossibleRoutes("BOSWE", [ "BRtB20B21" ])
		self.signals["C24R"].AddPossibleRoutes("BOSWE", [ "BRtB20B21" ])
		self.signals["C24R"].AddPossibleRoutes("BOSWW", [ "BRtB10B21" ])

		self.signals["C18LA"].AddPossibleRoutes("BOSE", ["BRtB11C13"])
		self.signals["C18LB"].AddPossibleRoutes("BOSE", ["BRtB21C13"])
		self.signals["C18R"].AddPossibleRoutes("BOSE", ["BRtB11C13", "BRtB21C13"])

		self.osSignals["BOSWW"] = [ "C22L", "C22R", "C24R" ]
		self.osSignals["BOSWE"] = [ "C24L", "C24R" ]
		self.osSignals["BOSE"] = [ "C18LB", "C18LA", "C18R" ]

		return self.signals

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21b.hand", (63, 10), self.misctiles["handdown"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21b.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21a.hand", (66, 10), self.misctiles["handdown"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21a.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B21"], "CSw19.hand", (63, 14), self.misctiles["handup"])
		self.blocks["B21"].AddHandSwitch(hs)
		self.handswitches["CSw19.hand"] = hs

		return self.handswitches
	
	def DoBlockAction(self, blk, blockend, state):
		District.DoBlockAction(self, blk, blockend, state)
		blknm = blk.GetName()
		if blknm in [ "B20", "B21" ]:
			self.CheckBlockSignalsAdv("B20", "B21", "B20E", True)
			
	def DoSignalAction(self, sig, aspect, callon=False):
		District.DoSignalAction(self, sig, aspect, callon=callon)
		signame = sig.GetName()
		if signame in [ "C18R", "C22R", "C24R", "C22L", "C24L" ]:
			self.CheckBlockSignalsAdv("B20", "B21", "B20E", True)

