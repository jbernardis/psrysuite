import logging

from district import District
from constants import YARD, KALE, EASTJCT, CORNELL, YARDSW
from node import Node

class Yard(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		logging.info("creating district Yard")
		self.rr = rr
		self.name = name
		self.released = False
		self.control = 0
		self.nodeAddresses = [ CORNELL, EASTJCT, KALE, YARD, YARDSW ]
		self.nodes = {
			CORNELL: Node(self, rr, CORNELL, 2, settings),
			EASTJCT: Node(self, rr, EASTJCT, 2, settings),
			KALE:    Node(self, rr, KALE,    4, settings),
			YARD:    Node(self, rr, YARD,    6, settings),
			YARDSW:  Node(self, rr, YARDSW,  5, settings)
		}
		
		# cornell node
		addr = CORNELL
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y4L",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("Y2L",  self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y2R",  self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("Y4RA", self, n, addr, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("Y4RB", self, n, addr, [(1, 2)])
			
			self.rr.AddStopRelay("Y21.srel", self, n, addr, [(1, 3)])
			self.rr.AddStopRelay("L10.srel", self, n, addr, [(1, 4)])
		
			# inputs
			self.rr.AddTurnoutPosition("YSw1", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw3", self, n, addr, [(0, 2), (0, 3)])
			
			self.rr.AddBlock("Y21.W",   self, n, addr, [(0, 4)])
			self.rr.AddBlock("Y21",     self, n, addr, [(0, 5)])
			self.rr.AddBlock("Y21.E",   self, n, addr, [(0, 6)])
			self.rr.AddBlock("YOSCJW",  self, n, addr, [(0, 7)]) #  CJOS1	
			self.rr.AddBlock("YOSCJE",  self, n, addr, [(1, 0)]) #  CJOS2
			self.rr.AddBlock("L10.W",   self, n, addr, [(1, 1)])
			self.rr.AddBlock("L10",     self, n, addr, [(1, 2)])
		
		
		# eastend jct node
		addr = EASTJCT
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y10L", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("Y8LA", self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y8LB", self, n, addr, [(0, 4)])
			self.rr.AddSignal("Y8LC", self, n, addr, [(0, 5)])
			self.rr.AddSignal("Y8R",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignal("Y10R", self, n, addr, [(1, 1)])
			
			self.rr.AddStopRelay("Y20.srel", self, n, addr, [(1, 2)])
			self.rr.AddStopRelay("Y11.srel", self, n, addr, [(1, 3)])
		
		
			# inputs
			self.rr.AddTurnoutPosition("YSw7",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw9",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("YSw11", self, n, addr, [(0, 4), (0, 5)])

			self.rr.AddBlock("Y20",    self, n, addr, [(0, 6)])
			self.rr.AddBlock("Y20.E",  self, n, addr, [(0, 7)])
			self.rr.AddBlock("YOSEJW", self, n, addr, [(1, 0)]) #  KJOS1
			self.rr.AddBlock("YOSEJE", self, n, addr, [(1, 1)]) #  KJOS2
			self.rr.AddBlock("Y11.W" , self, n, addr, [(1, 2)])
			self.rr.AddBlock("Y11",    self, n, addr, [(1, 3)])

		# kale node
		addr = KALE
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y22L",  self, n, addr, [(0, 0)])
			self.rr.AddSignal("Y26LA", self, n, addr, [(0, 1)])
			self.rr.AddSignal("Y26LB", self, n, addr, [(0, 2)])
			self.rr.AddSignal("Y26LC", self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y24LA", self, n, addr, [(0, 4)])
			self.rr.AddSignal("Y24LB", self, n, addr, [(0, 5)])
			
			self.rr.AddSignal("Y20H",  self, n, addr, [(0, 6)])  # these are the 2 bits to be used for roger's new signal bridge
			self.rr.AddSignal("Y20D",  self, n, addr, [(0, 7)])

			self.rr.AddSignal("Y26R", self, n, addr, [(1, 0)])
			self.rr.AddSignal("Y22R", self, n, addr, [(1, 1), (1, 2)]) # 
											# 1,1 = 1 if asp == 0b101 else 0)  # Approach
											# 1,2 = 1 if asp == 0b001 else 0)  # Restricting

			# inputs
			self.rr.AddTurnoutPosition("YSw17", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw19", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("YSw21", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("YSw23", self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("YSw25", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("YSw27", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnoutPosition("YSw29", self, n, addr, [(1, 4), (1, 5)])
						
			self.rr.AddBlock("Y30",    self, n, addr, [(1, 6)])
			self.rr.AddBlock("YOSKL4", self, n, addr, [(1, 7)]) #KAOS1
			self.rr.AddBlock("Y53",    self, n, addr, [(2, 0)])
			self.rr.AddBlock("Y52",    self, n, addr, [(2, 1)])
			self.rr.AddBlock("Y51",    self, n, addr, [(2, 2)])
			self.rr.AddBlock("Y50",    self, n, addr, [(2, 3)])
			self.rr.AddBlock("YOSKL2", self, n, addr, [(2, 4)]) #KAOS3
			self.rr.AddBlock("YOSKL1", self, n, addr, [(2, 5)]) #KAOS4
			self.rr.AddBlock("YOSKL3", self, n, addr, [(2, 6)]) #KAOS2
			self.rr.AddBlock("Y10",    self, n, addr, [(2, 7)])
		
		# engine yard	
		addr = YARD
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignalLED("Y2",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignalLED("Y4",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignalLED("Y8",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignalLED("Y10", self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignalLED("Y22", self, n, addr, [(1, 4), (1, 5), (1, 6)])
			self.rr.AddSignalLED("Y24", self, n, addr, [(1, 7), (2, 0), None])
			self.rr.AddSignalLED("Y26", self, n, addr, [(2, 1), (2, 2), (2, 3)])
			self.rr.AddSignalLED("Y34", self, n, addr, [(2, 4), (2, 5), (2, 6)])
			
			self.rr.AddSignal("Y34RA", self, n, addr, [(2, 7)])
			self.rr.AddSignal("Y34RB", self, n, addr, [(3, 0)])
			self.rr.AddSignal("Y34L",  self, n, addr, [(3, 1), (3, 2), (3, 3)])
						
			self.rr.AddBreakerInd("CBKale",       self, n, addr, [(3, 4)])
			self.rr.AddBreakerInd("CBEastEndJct", self, n, addr, [(3, 5)])
			self.rr.AddBreakerInd("CBCornellJct", self, n, addr, [(3, 6)])
			self.rr.AddBreakerInd("CBEngineYard", self, n, addr, [(3, 7)])
			self.rr.AddBreakerInd("CBWaterman",   self, n, addr, [(4, 0)])
			
			self.rr.AddBlockInd("L20", self, n, addr, [(4, 1)])
			self.rr.AddBlockInd("P50", self, n, addr, [(4, 2)])
						
			self.rr.AddTurnoutLock("YSw1",  self, n, addr, [(4, 3)])
			self.rr.AddTurnoutLock("YSw3",  self, n, addr, [(4, 4)])
			self.rr.AddTurnoutLock("YSw7",  self, n, addr, [(4, 5)])
			self.rr.AddTurnoutLock("YSw9",  self, n, addr, [(4, 6)])
			self.rr.AddTurnoutLock("YSw17", self, n, addr, [(4, 7)])			
			self.rr.AddTurnoutLock("YSw19", self, n, addr, [(5, 0)])
			self.rr.AddTurnoutLock("YSw21", self, n, addr, [(5, 1)])
			self.rr.AddTurnoutLock("YSw23", self, n, addr, [(5, 2)])
			self.rr.AddTurnoutLock("YSw25", self, n, addr, [(5, 3)])
			self.rr.AddTurnoutLock("YSw29", self, n, addr, [(5, 4)])
			self.rr.AddTurnoutLock("YSw33", self, n, addr, [(5, 5)])
			
			# inputs	
			self.rr.AddTurnoutPosition("YSw33", self, n, addr, [(0, 0), (0, 1)])		
			self.rr.AddSignalLever("Y2",  self, n, addr, [(0, 2), (0, 3), (0, 4)])
			self.rr.AddSignalLever("Y4",  self, n, addr, [(0, 5), (0, 6), (0, 7)])
			self.rr.AddSignalLever("Y8",  self, n, addr, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignalLever("Y10", self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignalLever("Y22", self, n, addr, [(1, 6), (1, 7), (2, 0)])
			self.rr.AddSignalLever("Y24", self, n, addr, [(2, 1), (2, 2), None])
			self.rr.AddSignalLever("Y26", self, n, addr, [(2, 3), (2, 4), (2, 5)])
			self.rr.AddSignalLever("Y34", self, n, addr, [(2, 6), (2, 7), (3, 0)])
			
			self.rr.AddRouteIn("Y81W",  self, n, addr, [(3, 3)])
			self.rr.AddRouteIn("Y82W",  self, n, addr, [(3, 4)])
			self.rr.AddRouteIn("Y83W",  self, n, addr, [(3, 5)])
			self.rr.AddRouteIn("Y84W",  self, n, addr, [(3, 6)])
			self.rr.AddRouteIn("Y81E",  self, n, addr, [(3, 7)])
			self.rr.AddRouteIn("Y82E",  self, n, addr, [(4, 0)])
			self.rr.AddRouteIn("Y83E",  self, n, addr, [(4, 1)])
			self.rr.AddRouteIn("Y84E",  self, n, addr, [(4, 2)])
			
			self.rr.AddBlock("Y70",    self, n, addr, [(4, 3)])  # waterman detectiuon
			self.rr.AddBlock("YOSWYW", self, n, addr, [(4, 4)]) #  WOS1
			# bit 5 is bad
			self.rr.AddBlock("Y82",    self, n, addr, [(4, 6)])
			self.rr.AddBlock("Y83",    self, n, addr, [(4, 7)])
			self.rr.AddBlock("Y84",    self, n, addr, [(5, 0)])
			self.rr.AddBlock("YOSWYE", self, n, addr, [(5, 1)]) #  WOS2
			self.rr.AddBlock("Y87",    self, n, addr, [(5, 2)])
			self.rr.AddBlock("Y81",    self, n, addr, [(5, 3)])
			
			# virtual signals - these do not physically exist and are given no bit positione
			self.rr.AddSignal("Y40L",  self, n, addr, [])
			self.rr.AddSignal("Y40RA", self, n, addr, [])
			self.rr.AddSignal("Y40RB", self, n, addr, [])
			self.rr.AddSignal("Y40RC", self, n, addr, [])
			self.rr.AddSignal("Y40RD", self, n, addr, [])
			self.rr.AddSignal("Y42R",  self, n, addr, [])
			self.rr.AddSignal("Y42LA", self, n, addr, [])
			self.rr.AddSignal("Y42LB", self, n, addr, [])
			self.rr.AddSignal("Y42LC", self, n, addr, [])
			self.rr.AddSignal("Y42LD", self, n, addr, [])

		addr = YARDSW			
		with self.nodes[addr] as n:
			#outputs
			self.rr.AddTurnout("YSw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnout("YSw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnout("YSw7",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnout("YSw9",  self, n, addr, [(0, 6), (0, 7)])		
			self.rr.AddTurnout("YSw11", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnout("YSw17", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnout("YSw19", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddTurnout("YSw21", self, n, addr, [(1, 6), (1, 7)])		
			self.rr.AddTurnout("YSw23", self, n, addr, [(2, 0), (2, 1)])
			self.rr.AddTurnout("YSw25", self, n, addr, [(2, 2), (2, 3)])
			self.rr.AddTurnout("YSw27", self, n, addr, [(2, 4), (2, 5)])
			self.rr.AddTurnout("YSw29", self, n, addr, [(2, 6), (2, 7)])			
			self.rr.AddTurnout("YSw33", self, n, addr, [(3, 0), (3, 1)])
			
			self.rr.AddOutNXButton("YWWB1", self, n, addr, [(4, 0)])
			self.rr.AddOutNXButton("YWWB2", self, n, addr, [(4, 1)])
			self.rr.AddOutNXButton("YWWB3", self, n, addr, [(4, 2)])
			self.rr.AddOutNXButton("YWWB4", self, n, addr, [(4, 3)])
			self.rr.AddOutNXButton("YWEB1", self, n, addr, [(4, 4)])
			self.rr.AddOutNXButton("YWEB2", self, n, addr, [(4, 5)])
			self.rr.AddOutNXButton("YWEB3", self, n, addr, [(4, 6)])
			self.rr.AddOutNXButton("YWEB4", self, n, addr, [(4, 7)])
			# no inputs
			

		self.buttonMap = {
			"YWEB1": "Y81E", "YWEB2": "Y82E", "YWEB3": "Y83E", "YWEB4": "Y84E",
			"YWWB1": "Y81W", "YWWB2": 'Y82W', "YWWB3": 'Y83W', "YWWB4": "Y84W"
		}
		self.routes = {
			"east": ["Y81E", "Y82E", "Y83E", "Y84E"],
			"west": ["Y81W", "Y82W", "Y83W", "Y84W"]
		}
		self.currentRoute = {"east": None, "west": None}

		self.routeMap = {
				"Y81W": [ ["YSw113", "N"], ["YSw115","N"], ["YSw116", "N"] ], 
				"Y82W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "R"] ],
				"Y83W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "N"] ],
				"Y84W": [ ["YSw113", "R"], ["YSw115","N"], ["YSw116", "N"] ],
				"Y81E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "N"] ], 
				"Y82E": [ ["YSw131", "R"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y83E": [ ["YSw131", "N"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y84E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "R"] ],
		}





	def DetermineSignalLevers(self):
		self.sigLever["Y2"] = self.DetermineSignalLever(["Y2L"], ["Y2R"])
		self.sigLever["Y4"] = self.DetermineSignalLever(["Y4LA", "Y4LB"], ["Y4R"])
		self.sigLever["Y8"] = self.DetermineSignalLever(["Y8L"], ["Y8RA", "Y8RB", "Y8RC"])
		self.sigLever["Y10"] = self.DetermineSignalLever(["Y10L"], ["Y10R"])
		self.sigLever["Y22"] = self.DetermineSignalLever(["Y22L"], ["Y22R"])
		self.sigLever["Y24"] = self.DetermineSignalLever([], ["Y24RA", "Y24RB"])
		self.sigLever["Y26"] = self.DetermineSignalLever(["Y26L"], ["Y26RA", "Y26RB", "Y26RC"])
		self.sigLever["Y34"] = self.DetermineSignalLever(["Y34LA", "Y34LB"], ["Y34R"])
		
		
		
		

	def PressButton(self, btn):
		try:
			rtnm = self.buttonMap[btn.name]
		except KeyError:
			logging.warning("Unknown button pressed: %s" % btn.name)
			return None
		
		rtl = self.routes["east"] if rtnm in self.routes["east"] else self.routes["west"] if rtnm in self.routes["west"] else None
		if rtl is None:
			return None

		for rnm in rtl:		
			rt = self.rr.GetRouteIn(rnm)
			if rt is None:
				continue
			
			bt = rt.Bits()
			rt.node.SetInputBit(bt[0][0], bt[0][1], 0)
		
		rt = self.rr.GetRouteIn(rtnm)
		if rt is None:
			return None
		
		bt = rt.Bits()
		rt.node.SetInputBit(bt[0][0], bt[0][1], 1)
		
	
	def SelectRouteIn(self, rt):
		rtl = self.routes["east"] if rt.name in self.routes["east"] else self.routes["west"] if rt.name in self.routes["west"] else None
		if rtl is None:
			return None
		
		offRtList = [x for x in rtl if x != rt.name]
		return offRtList
		
	def RouteIn(self, rt, stat):
		group = "east" if rt.name in self.routes["east"] else "west" if rt.name in self.routes["west"] else None
		if group is None:
			return 
		
		if stat == 1:
			if rt.name == self.currentRoute[group]:
				return 
			
			self.currentRoute[group] = rt.name
			resp = {"turnout": [{"name": x[0], "state": x[1]} for x in self.routeMap[rt.name]] }
			self.rr.RailroadEvent(resp)
			
		else:
			if rt.name == self.currentRoute[group]:
				self.currentRoute[group] = None

	def Released(self):
		return self.released
		
	def OutIn(self):
		self.lastControl = self.control
		self.control = self.rr.GetControlOption("yard")  # 0 => Yard, 1 => Dispatcher
		if self.control == 0: #yard local control allows the panel release button
			rlReq = self.nodes[YARD].GetInputBit(3, 1)
			if rlReq is None:
				rlReq = 0
		else:
			rlReq = 0
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks
		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)

		optFleet = self.rr.GetControlOption("yard.fleet")  # 0 => no fleeting, 1 => fleeting

		District.OutIn(self)
		
	def GetControlOption(self):
		if self.control == 1:  # dispatcher control
			skiplist = ["Y2", "Y4", "Y8", "Y10", "Y22", "Y24", "Y26", "Y34"]
			resumelist = []
						
		else:  # assume local control
			skiplist = []
			if self.lastControl == 1:
				resumelist = ["Y2", "Y4", "Y8", "Y10", "Y22", "Y24", "Y26", "Y34"]
			else:
				resumelist = []
				
		return skiplist, resumelist
