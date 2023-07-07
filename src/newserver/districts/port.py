import logging

from district import District
from constants import PORTA, PORTB, PARSONS
from node import Node

class Port(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		logging.info("creating district Port")
		self.rr = rr
		self.name = name
		self.released = False
		self.n25occ = None
		self.nodeAddresses = [ PORTA, PORTB, PARSONS]
		self.nodes = {
			PORTA:    Node(self, rr, PORTA,   9, settings),
			PORTB:    Node(self, rr, PORTB,   7, settings),
			PARSONS:  Node(self, rr, PARSONS, 4, settings)
		}

		self.PBE = False
		self.PBW = False
		self.PBXO = None
		self.clr10w = None
		self.clr50w = None
		self.clr11e = None
		self.clr21e = None
		self.clr40w = None
		self.clr32w = None
		self.clr42e = None

		# Port A - Southport
		addr = PORTA
		with self.nodes[PORTA] as n:
			self.rr.AddSignal("PA12R",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddSignal("PA10RA", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddSignal("PA12LA", self, n, addr, [(0, 4)])
			self.rr.AddSignal("PA10RB", self, n, addr, [(0, 5), (0, 6)])
			self.rr.AddSignal("PA8R",   self, n, addr, [(0, 7), (1, 0)])
			self.rr.AddSignal("PA12LB", self, n, addr, [(1, 1)])
			self.rr.AddSignal("PA6R",   self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddSignal("PA4RA",  self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddSignal("PA12LC", self, n, addr, [(1, 6)])
			self.rr.AddSignal("PA4RB",  self, n, addr, [(1, 7), (2, 0)])
			self.rr.AddSignal("PA8L",   self, n, addr, [(2, 1)])
			self.rr.AddSignal("PA6LA",  self, n, addr, [(2, 2)])
			self.rr.AddSignal("PA6LB",  self, n, addr, [(2, 3)])
			self.rr.AddSignal("PA6LC",  self, n, addr, [(2, 4)])
		
			self.rr.AddSignalLED("PA4",  self, n, addr, [(2, 7), (3, 0), (3, 1)])
			self.rr.AddSignalLED("PA6",  self, n, addr, [(3, 2), (3, 3), (3, 4)])
			self.rr.AddSignalLED("PA8",  self, n, addr, [(3, 5), (3, 6), (3, 7)])
			self.rr.AddSignalLED("PA10", self, n, addr, [(4, 0), (4, 1), (4, 2)])
			self.rr.AddSignalLED("PA12", self, n, addr, [(4, 3), (4, 4), (4, 5)])
			self.rr.AddSignalLED("PA32", self, n, addr, [(4, 6), (4, 7), (5, 0)])
			self.rr.AddSignalLED("PA34", self, n, addr, [(5, 1), (5, 2), (5, 3)])
		
			self.rr.AddBlockInd("P21", self, n, addr, [(5, 4)])
			self.rr.AddBlockInd("P40", self, n, addr, [(5, 5)])
			
			self.rr.AddBreakerInd("CBParsonsJct", self, n, addr, [(6, 1)])
			self.rr.AddBreakerInd("CBSouthport",  self, n, addr, [(6, 2)])
			self.rr.AddBreakerInd("CBLavinYard",  self, n, addr, [(6, 3)])
		
			self.rr.AddTurnoutLock("PASw1", self, n, addr, [(6, 4)])
			self.rr.AddTurnoutLock("PASw3", self, n, addr, [(6, 5)])
			self.rr.AddTurnoutLock("PASw5", self, n, addr, [(6, 6)])
			self.rr.AddTurnoutLock("PASw7", self, n, addr, [(6, 7)])
			self.rr.AddTurnoutLock("PASw9", self, n, addr, [(7, 0)])
			self.rr.AddTurnoutLock("PASw11", self, n, addr, [(7, 1)])
			self.rr.AddTurnoutLock("PASw15", self, n, addr, [(7, 2)])
			self.rr.AddTurnoutLock("PASw19", self, n, addr, [(7, 3)])
			self.rr.AddTurnoutLock("PASw21", self, n, addr, [(7, 4)])
			self.rr.AddTurnoutLock("PASw23", self, n, addr, [(7, 5)])
			self.rr.AddTurnoutLock("PASw31", self, n, addr, [(7, 6)])
			self.rr.AddTurnoutLock("PASw33", self, n, addr, [(7, 7)])
			self.rr.AddTurnoutLock("PASw35", self, n, addr, [(8, 0)])
			self.rr.AddTurnoutLock("PASw37", self, n, addr, [(8, 1)])
			
			self.rr.AddStopRelay("P10.srel", self, n, addr, [(8, 2)])
			self.rr.AddStopRelay("P40.srel", self, n, addr, [(8, 3)])
			self.rr.AddStopRelay("P31.srel", self, n, addr, [(8, 4)])

			# inputs
			self.rr.AddTurnoutPosition("PASw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PASw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PASw5",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PASw7",  self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("PASw9",  self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("PASw11", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnoutPosition("PASw13", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddTurnoutPosition("PASw15", self, n, addr, [(1, 6), (1, 7)])
			self.rr.AddTurnoutPosition("PASw17", self, n, addr, [(2, 0), (2, 1)])
			self.rr.AddTurnoutPosition("PASw19", self, n, addr, [(2, 2), (2, 3)])
			self.rr.AddTurnoutPosition("PASw21", self, n, addr, [(2, 4), (2, 5)])
			self.rr.AddTurnoutPosition("PASw23", self, n, addr, [(2, 6), (2, 7)])

			self.rr.AddBlock("P1",     self, n, addr, [(3, 0)])
			self.rr.AddBlock("P2",     self, n, addr, [(3, 1)])
			self.rr.AddBlock("P3",     self, n, addr, [(3, 2)])
			self.rr.AddBlock("P4",     self, n, addr, [(3, 3)])
			self.rr.AddBlock("P5",     self, n, addr, [(3, 4)])
			self.rr.AddBlock("P6",     self, n, addr, [(3, 5)])
			self.rr.AddBlock("P7",     self, n, addr, [(3, 6)])
			self.rr.AddBlock("POSSP1", self, n, addr, [(3, 7)])
			self.rr.AddBlock("POSSP2", self, n, addr, [(4, 0)])
			self.rr.AddBlock("POSSP3", self, n, addr, [(4, 1)])
			self.rr.AddBlock("POSSP4", self, n, addr, [(4, 2)])
			self.rr.AddBlock("POSSP5", self, n, addr, [(4, 3)])
			self.rr.AddBlock("P10",    self, n, addr, [(4, 4)])
			self.rr.AddBlock("P10.E",  self, n, addr, [(4, 5)])

			self.rr.AddSignalLever("PA4",  self, n, addr, [(4, 6), (4, 7), (5, 0)])
			self.rr.AddSignalLever("PA6",  self, n, addr, [(5, 1), (5, 2), (5, 3)])
			self.rr.AddSignalLever("PA8",  self, n, addr, [(5, 4), (5, 5), (5, 6)])			
			self.rr.AddSignalLever("PA10", self, n, addr, [(5, 7), (6, 0), (6, 1)])
			self.rr.AddSignalLever("PA12", self, n, addr, [(6, 2), (6, 3), (6, 4)])
			self.rr.AddSignalLever("PA32", self, n, addr, [(6, 5), (6, 6), (6, 7)])
			self.rr.AddSignalLever("PA34", self, n, addr, [(7, 0), (7, 1), (7, 2)])
	
		with self.nodes[PARSONS] as n:
			#outputs
			self.rr.AddSignal("PA34LB", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("PA32L",  self, n, addr, [(0, 3)])
			self.rr.AddSignal("PA34LA", self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("PA34RD", self, n, addr, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("PA34RC", self, n, addr, [(1, 2)])
			self.rr.AddSignal("PA32RA", self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignal("PA34RB", self, n, addr, [(1, 6)])
			self.rr.AddSignal("PA32RB", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignal("PA34RA", self, n, addr, [(2, 2)])

			self.rr.AddStopRelay("P20.srel", self, n, addr, [(2, 3)])
			self.rr.AddStopRelay("P30.srel", self, n, addr, [(2, 4)])
			self.rr.AddStopRelay("P50.srel", self, n, addr, [(2, 5)])
			self.rr.AddStopRelay("P11.srel", self, n, addr, [(2, 6)])

			# Inputs
			self.rr.AddTurnoutPosition("PASw27", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PASw29", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PASw31", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PASw33", self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("PASw35", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("PASw37", self, n, addr, [(1, 2), (1, 3)])
			
			self.rr.AddBlock("P20",    self, n, addr, [(1, 4)])
			self.rr.AddBlock("P20.E",  self, n, addr, [(1, 5)])
			self.rr.AddBlock("P30.W",  self, n, addr, [(1, 6)])
			self.rr.AddBlock("P30",    self, n, addr, [(1, 7)])				
			self.rr.AddBlock("P30.E",  self, n, addr, [(2, 0)])
			self.rr.AddBlock("POSPJ1", self, n, addr, [(2, 1)])
			self.rr.AddBlock("POSPJ2", self, n, addr, [(2, 2)])
			self.rr.AddBlock("P50.W",  self, n, addr, [(2, 3)])
			self.rr.AddBlock("P50",    self, n, addr, [(2, 4)])
			self.rr.AddBlock("P50.E",  self, n, addr, [(2, 5)])
			self.rr.AddBlock("P11.W",  self, n, addr, [(2, 6)])
			self.rr.AddBlock("P11",    self, n, addr, [(2, 7)])
			self.rr.AddBlock("P11.E",  self, n, addr, [(3, 0)])


		with self.nodes[PORTB] as n:
			#outputs
			self.rr.AddSignal("PB2R",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("PB4R",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("PB2L",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignal("PB4L",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignal("PB12L", self, n, addr, [(1, 4), (1, 5), (1, 6)])
			self.rr.AddSignal("PB14L", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignal("PB12R", self, n, addr, [(2, 2), (2, 3), (2, 4)])
			self.rr.AddSignal("PB14R", self, n, addr, [(2, 5), (2, 6), (2, 7)])

			self.rr.AddSignalLED("PB2",  self, n, addr, [(3, 0), (3, 1), (3, 2)])
			self.rr.AddSignalLED("PB4",  self, n, addr, [(3, 3), (3, 4), (3, 5)])

			self.rr.AddHandswitchInd("PBSw5",  self, n, addr, [(3, 6), (3, 7)])

			self.rr.AddSignalLED("PB12",  self, n, addr, [(4, 0), (4, 1), (4, 2)])
			self.rr.AddSignalLED("PB14",  self, n, addr, [(4, 3), (4, 4), (4, 5)])

			self.rr.AddHandswitchInd("PBSw15ab",  self, n, addr, [(4, 6), (4, 7)])
			
			self.rr.AddBlockInd("P30", self, n, addr, [(5, 0)])
			self.rr.AddBlockInd("P42", self, n, addr, [(5, 1)])
			
			self.rr.AddBreakerInd("CBSouthJct",  self, n, addr, [(5, 4)])
			self.rr.AddBreakerInd("CBCircusJct", self, n, addr, [(5, 5)])

			self.rr.AddTurnoutLock("PBSw1", self, n, addr, [(5, 6)])
			self.rr.AddTurnoutLock("PBSw3", self, n, addr, [(5, 7)])

			self.rr.AddHandswitchInd("PBSw5", self, n, addr, [(6, 0)])
			
			self.rr.AddTurnoutLock("PBSw11", self, n, addr, [(6, 1)])
			self.rr.AddTurnoutLock("PBSw13", self, n, addr, [(6, 2)])
	
			self.rr.AddHandswitchInd("PBSw15ab",  self, n, addr, [(6, 3)])
			
			self.rr.AddStopRelay("P32.srel", self, n, addr, [(6, 4)])
			self.rr.AddStopRelay("P41.srel", self, n, addr, [(6, 5)])
	
			# Inputs
			self.rr.AddTurnoutPosition("PBSw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PBSw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PBSw11", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PBSw13", self, n, addr, [(0, 6), (0, 7)])
	
			self.rr.AddHandswitch("PBSw5",   self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddHandswitch("PBSw15a", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddHandswitch("PBSw15b", self, n, addr, [(1, 4), (1, 5)])

			self.rr.AddBlock("P40",    self, n, addr, [(1, 6)])	
			self.rr.AddBlock("P40.E",  self, n, addr, [(1, 7)])	
			self.rr.AddBlock("POSSJ2", self, n, addr, [(2, 0)])	
			self.rr.AddBlock("POSSJ1", self, n, addr, [(2, 1)])	
			self.rr.AddBlock("P31.W",  self, n, addr, [(2, 2)])	
			self.rr.AddBlock("P31",    self, n, addr, [(2, 3)])	
			self.rr.AddBlock("P31.E",  self, n, addr, [(2, 4)])	
			self.rr.AddBlock("P32.W",  self, n, addr, [(2, 5)])	
			self.rr.AddBlock("P32",    self, n, addr, [(2, 6)])	
			self.rr.AddBlock("P32.E",  self, n, addr, [(2, 7)])	
			self.rr.AddBlock("POSCJ2", self, n, addr, [(3, 0)])	
			self.rr.AddBlock("POSCJ1", self, n, addr, [(3, 1)])	
			self.rr.AddBlock("P41.W",  self, n, addr, [(3, 2)])	
			self.rr.AddBlock("P41",    self, n, addr, [(3, 3)])	
			self.rr.AddBlock("P41.E",  self, n, addr, [(3, 4)])	
				
				
			self.rr.AddSignalLever("PB2",  self, n, addr, [(3, 5), (3, 6), (3, 7)])
			self.rr.AddSignalLever("PB4",  self, n, addr, [(4, 0), (4, 1), (4, 2)])
				
			self.rr.AddHandswitchUnlock("PBSw5",    self, n, addr, [(4, 3)])
				
			self.rr.AddSignalLever("PB12",  self, n, addr, [(4, 4), (4, 5), (4, 6)])
			self.rr.AddSignalLever("PB14",  self, n, addr, [(4, 7), (5, 0), (5, 1)])
				
			self.rr.AddHandswitchUnlock("PBSw15ab",    self, n, addr, [(5, 2)])


	def OutIn(self):
		rlReq = self.nodes[PORTA].GetInputBit(7, 3)
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks

		P40M = self.rr.GetBlock("P40").IsOccupied()
		P40E = self.rr.GetBlock("P40.E").IsOccupied()
		if P40M and not self.PBE:
			self.PBW = True
		if P40E and not self.PBW:
			self.PBE = True
		if not P40M and not P40E:
			self.PBE = self.PBW = False
		PBXO = (P40E and self.PBE) or (P40M and self.PBW)
		if PBXO != self.PBXO:
			self.PBXO = PBXO
			self.nodes[PORTB].SetOutputBit(6, 6, 1 if PBXO else 0)
		
		blk = self.rr.GetBlock("P10")
		clr10w = blk.IsCleared() and not blk.IstEast()
		if clr10w != self.clr10w:
			self.clr10w = clr10w
			self.nodes[PORTA].SetOutputBit(2, 5, 1 if clr10w else 0) # semaphore 
			self.nodes[PORTA].SetOutputBit(2, 6, 1 if clr10w else 0) # semaphore 
		
		blk = self.rr.GetBlock("P50")
		clr50w = blk.IsCleared() and not blk.IsEast()
		if clr50w != self.clr50w:
			self.clr50w = clr50w
			self.nodes[PORTA].SetOutputBit(5, 6, 1 if clr50w else 0) # yard signal
		
		blk = self.rr.GetBlock("P11")
		clr11e = blk.IsCleared() and blk.IsEast()
		if clr11e != self.clr11e:
			self.clr11e = clr11e
			self.nodes[PORTA].SetOutputBit(5, 7, 1 if clr11e else 0) # latham signals
		
		blk = self.rr.GetBlock("P21")
		clr21e = blk.IsCleared() and blk.IsEast()
		if clr21e != self.clr21e:
			self.clr21e = clr21e
			self.nodes[PORTA].SetOutputBit(6, 0, 1 if clr21e else 0) 
		
		blk = self.rr.GetBlock("P40")
		clr40w = blk.IsCleared() and not blk.IsEast()
		if clr40w != self.clr40w:
			self.clr40w = clr40w
			self.nodes[PORTA].SetOutputBit(8, 5, 1 if clr40w else 0) 
			self.nodes[PORTA].SetOutputBit(8, 6, 1 if clr40w else 0) 
			
		blk = self.rr.GetBlock("P32")
		clr32w = blk.IsCleared() and not blk.IsEast()
		if clr32w != self.clr32w:
			self.clr32w = clr32w
			self.nodes[PORTB].SetOutputBit(5, 2, 1 if clr32w else 0)
		
		blk = self.rr.GetBlock("P42")
		clr42e = blk.IsCleared() and blk.IsEast()
		if clr42e != self.clr42e:
			self.clr42e = clr42e
			self.nodes[PORTB].SetOutputBit(5, 3, 1 if clr42e else 0)
		
		#self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)
		
		District.OutIn(self)

	def SetHandswitch(self, hsname, state):
		print("Port evaluating handswitch %s at state %s" % (hsname, state))
		if hsname in ["PBSw15a", "PBSw15b"]:
			hsa = self.rr.GetHandswitch("PBSw15a")
			hsb = self.rr.GetHandswitch("PSw15b")
			locked = hsa.IsLocked() or hsb.IsLocked()
			print("%s or %s = %s" % (hsa.IsLocked(), hsb.IsLocked(), locked))
			
			hs = self.rr.GetHandswitch("PBSw15ab")
			if hs.Lock(locked):
				print("changes - updating indicators")
				hs.UpdateIndicators()

