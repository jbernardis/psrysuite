import logging

from district import District
from constants import  CLIFF, GREENMTN, SHEFFIELD
from node import Node


class Cliff(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		logging.info("creating district Cliff")
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ GREENMTN, CLIFF, SHEFFIELD ]
		
		self.nodes = {
			GREENMTN:   Node(self, rr, GREENMTN,  3, settings),
			CLIFF:      Node(self, rr, CLIFF,     8, settings),
			SHEFFIELD:  Node(self, rr, SHEFFIELD, 4, settings)
		}
		self.S11AB = None
		self.entryButton = None
		self.currentCoachRoute = None
		self.optFleet = None
		self.released = False
		
		self.revCSw21a = None
		self.revCSw21b = None
		self.revCSw19  = None
		self.revCSw15  = None
		self.revCSw11  = None
		
		self.revIndicators = [ "CSw21a", "CSw21b", "CSw19", "CSw15", "CSw11" ]
		self.norm = { ind: None for ind in self.revIndicators }

		addr = GREENMTN
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("C2LB", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("C2LD", self, n, addr, [(0, 3)])
			self.rr.AddSignal("C2R",  self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("C2LA", self, n, addr, [(0, 7), (1, 0)])
			self.rr.AddSignal("C2LC", self, n, addr, [(1, 1)])
			self.rr.AddSignal("C4RA", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddSignal("C4RB", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddSignal("C4RC", self, n, addr, [(1, 6), (1, 6), (2, 0)])
			self.rr.AddSignal("C4RD", self, n, addr, [(2, 1)])
			self.rr.AddSignal("C4L",  self, n, addr, [(2, 2), (2, 3), (2, 4)])

			self.rr.AddHandswitchInd("CSw3", self, n, addr, [(2, 5)])
			
			# virtual turnouts - these are managed by the CLIFF panel - no output bits
			self.rr.AddTurnout("CSw31", self, n, addr, [])
			self.rr.AddTurnout("CSw33", self, n, addr, [])
			self.rr.AddTurnout("CSw35", self, n, addr, [])
			self.rr.AddTurnout("CSw37", self, n, addr, [])
			self.rr.AddTurnout("CSw39", self, n, addr, [])
			self.rr.AddTurnout("CSw41", self, n, addr, [])

			# inpits
			self.rr.AddRouteIn("CC30E", self, n, addr, [(0, 0)])	
			self.rr.AddRouteIn("CC10E", self, n, addr, [(0, 1)])	
			self.rr.AddRouteIn("CG10E", self, n, addr, [(0, 2)])	
			self.rr.AddRouteIn("CG12E", self, n, addr, [(0, 3)])	
			self.rr.AddRouteIn("CC31W", self, n, addr, [(0, 4)])	
			self.rr.AddRouteIn("CC30W", self, n, addr, [(0, 5)])	
			self.rr.AddRouteIn("CC10W", self, n, addr, [(0, 6)])	
			self.rr.AddRouteIn("CG21W", self, n, addr, [(0, 7)])	
			
			self.rr.AddHandswitch("CSw3", self, n, addr, [(1, 0), (1, 1)])

			self.rr.AddBlock("C11", self, n, addr, [(1, 2)])
			self.rr.AddBlock("COSGMW", self, n, addr, [(1, 3)])
			self.rr.AddBlock("C10", self, n, addr, [(1, 4)])
			self.rr.AddBlock("C30", self, n, addr, [(1, 5)])
			self.rr.AddBlock("C31", self, n, addr, [(1, 6)])
			self.rr.AddBlock("COSGME", self, n, addr, [(1, 7)])
			self.rr.AddBlock("C20", self, n, addr, [(2, 0)])

		addr = CLIFF
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignalLED("C2",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignalLED("C4",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignalLED("C6",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignalLED("C8",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignalLED("C10", self, n, addr, [(1, 4), (1, 5), (1, 6)])
			self.rr.AddSignalLED("C12", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignalLED("C14", self, n, addr, [(2, 2), (2, 3), (2, 4)])
			self.rr.AddSignalLED("C18", self, n, addr, [(2, 7), (3, 0), (3, 1)])
			self.rr.AddSignalLED("C22", self, n, addr, [(3, 2), (3, 3), (3, 4)])
			self.rr.AddSignalLED("C24", self, n, addr, [(3, 5), (3, 6), (3, 7)])

			self.rr.AddHandswitchInd("CSw3",  self, n, addr, [(4, 0), (4, 1)])
			self.rr.AddHandswitchInd("CSw11", self, n, addr, [(4, 2), (4, 3)])
			self.rr.AddHandswitchInd("CSw15", self, n, addr, [(4, 4), (4, 5)])
			self.rr.AddHandswitchInd("CSw19", self, n, addr, [(4, 6), (4, 7)])
			self.rr.AddHandswitchInd("CSw21ab", self, n, addr, [(5, 0), (5, 1)])
			
			self.rr.AddBlockInd("B10", self, n, addr, [(5, 2)])
			
			self.rr.AddBreakerInd("CBGreenMtn",        self, n, addr, [(5, 3)]) # combines GreenMtnStn and GreenMtnYd
			self.rr.AddBreakerInd("CBSheffield",       self, n, addr, [(5, 4)]) # combines SheffieldA and SheffieldB
			self.rr.AddBreakerInd("CBCliveden",        self, n, addr, [(5, 5)])
			self.rr.AddBreakerInd("CBReverserC22C23",  self, n, addr, [(5, 6)])
			self.rr.AddBreakerInd("CBBank",            self, n, addr, [(5, 7)])
			
			self.rr.AddTurnoutLock("CSw31", self, n, addr, [(6, 0)])
			self.rr.AddTurnoutLock("CSw41", self, n, addr, [(6, 1)])
			self.rr.AddTurnoutLock("CSw43", self, n, addr, [(6, 2)])
			self.rr.AddTurnoutLock("CSw61", self, n, addr, [(6, 3)])
			self.rr.AddTurnoutLock("CSw9",  self, n, addr, [(6, 4)])
			self.rr.AddTurnoutLock("CSw13", self, n, addr, [(6, 5)])
			self.rr.AddTurnoutLock("CSw17", self, n, addr, [(6, 6)])
			self.rr.AddTurnoutLock("CSw23", self, n, addr, [(6, 7)])
			
			self.rr.AddIndicator("CSw21a", self, n, addr, [(7, 0)])
			self.rr.AddIndicator("CSw21b", self, n, addr, [(7, 1)])
			self.rr.AddIndicator("CSw19",  self, n, addr, [(7, 2)])
			self.rr.AddIndicator("CSw15",  self, n, addr, [(7, 3)])
			self.rr.AddIndicator("CSw11",  self, n, addr, [(7, 4)])

			# Inputs
			self.rr.AddRouteIn("CC21E",  self, n, addr, [(0, 0)])
			self.rr.AddRouteIn("CC40E",  self, n, addr, [(0, 1)])
			self.rr.AddRouteIn("CC44E",  self, n, addr, [(0, 2)])
			self.rr.AddRouteIn("CC43E",  self, n, addr, [(0, 3)])
			self.rr.AddRouteIn("CC42E",  self, n, addr, [(0, 4)])
			self.rr.AddRouteIn("CC41E",  self, n, addr, [(0, 5)])
			self.rr.AddRouteIn("CC41W",  self, n, addr, [(0, 6)])
			self.rr.AddRouteIn("CC42W",  self, n, addr, [(0, 7)])			
			self.rr.AddRouteIn("CC21W",  self, n, addr, [(1, 0)])
			self.rr.AddRouteIn("CC40W",  self, n, addr, [(1, 1)])
			self.rr.AddRouteIn("CC44W",  self, n, addr, [(1, 2)])
			self.rr.AddRouteIn("CC43W",  self, n, addr, [(1, 3)])
			self.rr.AddRouteIn("COSSHE", self, n, addr, [(1, 4)])
			self.rr.AddRouteIn("C21",    self, n, addr, [(1, 5)])
			self.rr.AddRouteIn("C40",    self, n, addr, [(1, 6)])
			self.rr.AddRouteIn("C41",    self, n, addr, [(1, 7)])
			self.rr.AddRouteIn("C42",    self, n, addr, [(2, 0)])
			self.rr.AddRouteIn("C43",    self, n, addr, [(2, 1)])
			self.rr.AddRouteIn("C44",    self, n, addr, [(2, 2)])
			self.rr.AddRouteIn("COSSHW", self, n, addr, [(2, 3)])
			
			self.rr.AddSignalLever("C2",  self, n, addr, [(2, 4), (2, 5), (2, 6)])
			self.rr.AddSignalLever("C4",  self, n, addr, [(2, 7), (3, 0), (3, 1)])
			self.rr.AddSignalLever("C6",  self, n, addr, [(3, 2), (3, 3), (3, 4)])
			self.rr.AddSignalLever("C8",  self, n, addr, [(3, 5), (3, 6), (3, 7)])
			self.rr.AddSignalLever("C10", self, n, addr, [(4, 0), (4, 1), (4, 2)])
			self.rr.AddSignalLever("C12", self, n, addr, [(4, 3), (4, 4), (4, 5)])
			self.rr.AddSignalLever("C14", self, n, addr, [(4, 6), (4, 7), (5, 0)])
			self.rr.AddSignalLever("C18", self, n, addr, [(5, 2), (5, 3), (5, 4)])
			self.rr.AddSignalLever("C22", self, n, addr, [(5, 5), (5, 6), (5, 7)])
			self.rr.AddSignalLever("C24", self, n, addr, [(6, 0), (6, 1), (6, 2)])
			
			self.rr.AddHandswitchUnlock("CSw3",    self, n, addr, [(6, 4)])
			self.rr.AddHandswitchUnlock("CSw11",   self, n, addr, [(6, 5)])
			self.rr.AddHandswitchUnlock("CSw15",   self, n, addr, [(6, 6)])
			self.rr.AddHandswitchUnlock("CSw19",   self, n, addr, [(6, 7)])
			self.rr.AddHandswitchUnlock("CSw21ab", self, n, addr, [(7, 0)])

		addr = SHEFFIELD
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddOutNXButton("CC54E", self, n, addr, [(0, 0)])
			self.rr.AddOutNXButton("CC53E", self, n, addr, [(0, 1)])
			self.rr.AddOutNXButton("CC52E", self, n, addr, [(0, 2)])
			self.rr.AddOutNXButton("CC51E", self, n, addr, [(0, 3)])
			self.rr.AddOutNXButton("CC50E", self, n, addr, [(0, 4)])
			self.rr.AddOutNXButton("CC21E", self, n, addr, [(0, 5)])
			self.rr.AddOutNXButton("CC40E", self, n, addr, [(0, 6)])
			self.rr.AddOutNXButton("CC41E", self, n, addr, [(0, 7)])
			self.rr.AddOutNXButton("CC42E", self, n, addr, [(1, 0)])
			self.rr.AddOutNXButton("CC43E", self, n, addr, [(1, 1)])
			self.rr.AddOutNXButton("CC44E", self, n, addr, [(1, 2)])
			self.rr.AddOutNXButton("CC54W", self, n, addr, [(1, 3)])
			self.rr.AddOutNXButton("CC53W", self, n, addr, [(1, 4)])
			self.rr.AddOutNXButton("CC52W", self, n, addr, [(1, 5)])
			self.rr.AddOutNXButton("CC51W", self, n, addr, [(1, 6)])
			self.rr.AddOutNXButton("CC50W", self, n, addr, [(1, 7)])
			self.rr.AddOutNXButton("CC21W", self, n, addr, [(2, 0)])
			self.rr.AddOutNXButton("CC40W", self, n, addr, [(2, 1)])
			self.rr.AddOutNXButton("CC41W", self, n, addr, [(2, 2)])
			self.rr.AddOutNXButton("CC42W", self, n, addr, [(2, 3)])
			self.rr.AddOutNXButton("CC43W", self, n, addr, [(2, 4)])
			self.rr.AddOutNXButton("CC44W", self, n, addr, [(2, 5)])
			self.rr.AddOutNXButton("CC30E", self, n, addr, [(2, 6)])
			self.rr.AddOutNXButton("CC10E", self, n, addr, [(2, 7)])			
			self.rr.AddOutNXButton("CG10E", self, n, addr, [(3, 0)])
			self.rr.AddOutNXButton("CG12E", self, n, addr, [(3, 1)])
			self.rr.AddOutNXButton("CC30W", self, n, addr, [(3, 2)])
			self.rr.AddOutNXButton("CC31W", self, n, addr, [(3, 3)])
			self.rr.AddOutNXButton("CC10W", self, n, addr, [(3, 4)])
			self.rr.AddOutNXButton("CG21W", self, n, addr, [(3, 5)])
			
			# virtual signals - these do not physically exist so no output bits
			self.rr.AddSignal("C6R", self, n, addr, [])
			self.rr.AddSignal("C6LA", self, n, addr, [])
			self.rr.AddSignal("C6LB", self, n, addr, [])
			self.rr.AddSignal("C6LC", self, n, addr, [])
			self.rr.AddSignal("C6LD", self, n, addr, [])
			self.rr.AddSignal("C6LE", self, n, addr, [])
			self.rr.AddSignal("C6LF", self, n, addr, [])
			self.rr.AddSignal("C6LG", self, n, addr, [])
			self.rr.AddSignal("C6LH", self, n, addr, [])
			self.rr.AddSignal("C6LJ", self, n, addr, [])
			self.rr.AddSignal("C6LK", self, n, addr, [])
			self.rr.AddSignal("C6LL", self, n, addr, [])
			self.rr.AddSignal("C8L", self, n, addr, [])
			self.rr.AddSignal("C8RA", self, n, addr, [])
			self.rr.AddSignal("C8RB", self, n, addr, [])
			self.rr.AddSignal("C8RC", self, n, addr, [])
			self.rr.AddSignal("C8RD", self, n, addr, [])
			self.rr.AddSignal("C8RE", self, n, addr, [])
			self.rr.AddSignal("C8RF", self, n, addr, [])
			self.rr.AddSignal("C8RG", self, n, addr, [])
			self.rr.AddSignal("C8RH", self, n, addr, [])
			self.rr.AddSignal("C8RJ", self, n, addr, [])
			self.rr.AddSignal("C8RK", self, n, addr, [])
			self.rr.AddSignal("C8RL", self, n, addr, [])
		
			# virtual turnouts - these are managed by the CLIFF panel - no output bits
			self.rr.AddTurnout("CSw43", self, n, addr, [])
			self.rr.AddTurnout("CSw45", self, n, addr, [])
			self.rr.AddTurnout("CSw47", self, n, addr, [])
			self.rr.AddTurnout("CSw49", self, n, addr, [])
			self.rr.AddTurnout("CSw51", self, n, addr, [])
			self.rr.AddTurnout("CSw53", self, n, addr, [])
			self.rr.AddTurnout("CSw55", self, n, addr, [])
			self.rr.AddTurnout("CSw57", self, n, addr, [])
			self.rr.AddTurnout("CSw59", self, n, addr, [])
			self.rr.AddTurnout("CSw61", self, n, addr, [])
			self.rr.AddTurnout("CSw63", self, n, addr, [])
			self.rr.AddTurnout("CSw65", self, n, addr, [])
			self.rr.AddTurnout("CSw67", self, n, addr, [])
			self.rr.AddTurnout("CSw69", self, n, addr, [])
			self.rr.AddTurnout("CSw71", self, n, addr, [])
			self.rr.AddTurnout("CSw73", self, n, addr, [])
			self.rr.AddTurnout("CSw75", self, n, addr, [])
			self.rr.AddTurnout("CSw77", self, n, addr, [])
			self.rr.AddTurnout("CSw79", self, n, addr, [])
			self.rr.AddTurnout("CSw81", self, n, addr, [])

			# inputs
			self.rr.AddRouteIn("CC50E", self, n, addr, [(0, 0)])
			self.rr.AddRouteIn("CC51E", self, n, addr, [(0, 1)])
			self.rr.AddRouteIn("CC52E", self, n, addr, [(0, 2)])
			self.rr.AddRouteIn("CC53E", self, n, addr, [(0, 3)])
			self.rr.AddRouteIn("CC54E", self, n, addr, [(0, 4)])
			self.rr.AddRouteIn("CC50W", self, n, addr, [(0, 5)])
			self.rr.AddRouteIn("CC51W", self, n, addr, [(0, 6)])
			self.rr.AddRouteIn("CC52W", self, n, addr, [(0, 7)])		
			self.rr.AddRouteIn("CC53W", self, n, addr, [(1, 0)])
			self.rr.AddRouteIn("CC54W", self, n, addr, [(1, 1)])
			
			self.rr.AddBlock("C50", self, n, addr, [(1, 2)])
			self.rr.AddBlock("C51", self, n, addr, [(1, 3)])
			self.rr.AddBlock("C52", self, n, addr, [(1, 4)])
			self.rr.AddBlock("C53", self, n, addr, [(1, 5)])
			self.rr.AddBlock("C54", self, n, addr, [(1, 6)])

		self.routeMap = {
			"CG21W":  [ ["CSw41", "R"] ],
			"CC10W":  [ ["CSw41", "N"], ["CSw39", "N"] ],
			"CC30W":  [ ["CSw41", "N"], ["CSw39", "R"], ["CSw37", "R"] ],
			"CC31W":  [ ["CSw41", "N"], ["CSw39", "R"], ["CSw37", "N"] ],

			"CG12E":  [ ["CSw31", "R"], ["CSw35", "N"] ],
			"CG10E":  [ ["CSw31", "R"], ["CSw35", "R"] ],
			"CC10E":  [ ["CSw31", "N"], ["CSw33", "N"] ],
			"CC30E":  [ ["CSw31", "N"], ["CSw33", "R"] ],

			"CC44E":  [ ["CSw43", "N"], ["CSw45", "N"], ["CSw49", "N"] ],
			"CC43E":  [ ["CSw43", "N"], ["CSw45", "R"], ["CSw49", "R"] ],			
			"CC42E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw51", "N"] ],			
			"CC41E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "R"], ["CSw51", "R"] ],
			"CC40E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "N"] ],			
			"CC21E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "R"] ],
			"CC50E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "N"], ["CSw65", "R"] ],
			"CC51E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "R"], ["CSw69", "N"] ],
			"CC52E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "R"], ["CSw69", "R"] ],
			"CC53E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "N"], ["CSw71", "R"] ],
			"CC54E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "N"], ["CSw71", "N"] ],

			"CC44W":  [ ["CSw57", "N"], ["CSw53", "R"], ["CSw55", "R"], ["CSw59", "N"], ["CSw61", "R"] ],
			"CC43W":  [ ["CSw57", "R"], ["CSw53", "N"], ["CSw55", "R"], ["CSw59", "N"], ["CSw61", "R"] ],
			"CC42W":  [ ["CSw53", "R"], ["CSw55", "N"], ["CSw59", "R"], ["CSw61", "R"] ],
			"CC41W":  [ ["CSw53", "N"], ["CSw55", "N"], ["CSw59", "R"], ["CSw61", "R"] ],
			"CC40W":  [ ["CSw55", "R"], ["CSw61", "N"] ],
			"CC21W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "R"], ["CSw73", "N"] ],
			"CC50W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "R"] ],
			"CC51W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"], ["CSw79", "N"] ],
			"CC52W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"], ["CSw79", "R"] ],
			"CC53W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"], ["CSw79", "N"], ["CSw81", "R"] ],
			"CC54W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"], ["CSw79", "R"], ["CSw81", "N"] ],			
		}
		
		self.routeGroups = [
			["CG21W", "CC10W", "CC30W", "CC31W"],
			["CG12E", "CG10E", "CC10E", "CC30E"],
			["CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W"],
			["CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E"]
		]

		nxButtons = [
			"CG21W", "CC10W", "CC30W", "CC31W",
			"CG12E", "CG10E", "CC10E", "CC30E",
			"CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E",
			"CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W",
		]


	def PressButton(self, btn):
		print("cliff - press button %s" % btn.Name())
		self.rr.SetRouteIn(btn.Name())
		
	def SelectRouteIn(self, rt):
		rtnm = rt.Name()
		print("Select route in: %s" % rtnm)
		
		for gp in self.routeGroups:
			if rtnm in gp:
				print(str([x for x in gp if x != rtnm]))
				return [x for x in gp if x != rtnm]
			
		return None
			
	def RouteIn(self, rt, stat):
		rtNm = rt.Name()
		print("Cliff Route IN: %s %d" % (rtNm, stat))
		if stat == 0:
			return 
		
		try:
			tolist = self.routeMap[rtNm]
		except KeyError:
			return 
		
		resp = {"turnout": [{"name": x[0], "state": x[1]} for x in tolist] }
		print(str(resp))
		self.rr.RailroadEvent(resp)

	def EvaluateNXButton(self, btn):
		if btn not in self.routeMap:
			return

		tolist = self.routeMap[btn]

		for toName, status in tolist:
			self.rr.GetInput(toName).SetState(status)
			
	def CheckTurnoutPosition(self, tout):
		self.rr.RailroadEvent({"turnout": [{"name": tout.Name(), "state": "N" if tout.IsNormal() else "R"}]})

	def DetermineSignalLevers(self):
		self.sigLever["C2"] = self.DetermineSignalLever(["C2L"], ["C2RA", "C2RB", "C2RC", "C2RD"])  # signal indicators
		self.sigLever["C4"] = self.DetermineSignalLever(["C4LA", "C4LB", "C4LC", "C4LD"], ["C4R"])
		self.sigLever["C6"] = self.DetermineSignalLever(["C6L"], ["C6RA", "C6RB", "C6RC", "C6RD", "C6RE", "C6RF", "C6RG", "C6RH", "C6GJ", "C6RK", "C6RL"])
		self.sigLever["C8"] = self.DetermineSignalLever(["C8LA", "C8LB", "C8LC", "C8LD", "C8LE", "C8LF", "C8LG", "C8LH", "C8LJ", "C8LK", "C8LL"], ["C8R"])
		self.sigLever["C10"] = self.DetermineSignalLever(["C10L"], ["C10R"])
		self.sigLever["C12"] = self.DetermineSignalLever(["C12L"], ["C12R"])
		self.sigLever["C14"] = self.DetermineSignalLever(["C14LA", "C14LB"], ["C14R"])
		self.sigLever["C18"] = self.DetermineSignalLever(["C18L"], ["C18RA", "C18RB"])
		self.sigLever["C22"] = self.DetermineSignalLever(["C22L"], ["C22R"])
		self.sigLever["C24"] = self.DetermineSignalLever(["C24L"], ["C24R"])






	def OutIn(self):
		self.control = self.rr.GetControlOption("cliff")  # 0 => Cliff, 1 => Dispatcher bank/cliveden, 2 => Dispatcher All
		if self.control == 0: 
			optFleet = self.nodes[CLIFF].GetInputBit(5, 1)
		else:
			optBankFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
			optClivedenFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
			optFleet = self.rr.GetControlOption("cliff.fleet")  # 0 => no fleeting, 1 => fleeting
			
		if optFleet != self.optFleet:
			self.optFleet = optFleet
			self.nodes[CLIFF].SetOutputBit(2, 5, optFleet)   # fleet indicator
			self.nodes[CLIFF].SetOutputBit(2, 6, 1-optFleet)   # fleet indicator

		rlReq = self.nodes[CLIFF].GetInputBit(6, 3)
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks

		# see if any of the reverse indicators need to be updated
		for tout in self.revIndicators:	
			norm = self.rr.GetHandswitch(tout).IsNormal()
			if norm != self.norm[tout]:
				self.norm[tout] = norm
				ind = self.rr.GetIndicator(tout)
				bits = ind.Bits()
				if bits is None or len(bits) < 1:
					print("no bits")
					continue
				print("setting CLIFF output bit %d:%d to %s" % (bits[0][0], bits[0][1], 0 if norm else 1))
				self.nodes[CLIFF].SetOutputBit(bits[0][0], bits[0][1], 0 if norm else 1)
			
		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)
		
		District.OutIn(self)
		
	def Released(self):
		return self.released

	def GetControlOptions(self):
		if self.control == 2: # Dispatcher ALL
			return ["C2", "C4", "c6", "C8", "C10", "C12", "C14", "C18", "C22", "C24",
					"CSw3", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b"]
		elif self.control == 1: # dispatcher runs bank/cliveden
			return ["C2", "C4", "c6", "C8"]
		else:
			return []
