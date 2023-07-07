import logging

from district import District
from constants import  DELL, FOSS
from node import Node

class Dell(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		logging.info("creating district Latham")
		
		self.DXO = None
		self.RXO = None
		
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ DELL, FOSS ]
		self.nodes = {
			DELL:  Node(self, rr, DELL,  5, settings),
			FOSS:  Node(self, rr, FOSS,  3, settings)
		}

		with self.nodes[DELL] as n:
			# outputs
			self.rr.AddSignal("D4RA", self, n, DELL, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("D4RB", self, n, DELL, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("D6RA", self, n, DELL, [(0, 6)])
			self.rr.AddSignal("D6RB", self, n, DELL, [(0, 7)])
	
			self.rr.AddSignal("D4L",  self, n, DELL, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignal("D6L",  self, n, DELL, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddOutputDevice("DXO", self, n, DELL, [(1, 6)]) # laport crossing signal/gate
			self.rr.AddBlockInd("H13", self, n, DELL, [(1, 7)])
	
			self.rr.AddBlockInd("D10", self, n, DELL, [(2, 0)])
			self.rr.AddBlockInd("S20", self, n, DELL, [(2, 1)])
			self.rr.AddHandswitchInd("DSw9", self, n, DELL, [(2, 2)])
			self.rr.AddTurnout("DSw1", self, n, DELL, [(2, 3), (2, 4)])
			self.rr.AddTurnout("DSw3", self, n, DELL, [(2, 5), (2, 6)])
			self.rr.AddTurnout("DSw5", self, n, DELL, [(2, 7), (3, 0)])

			self.rr.AddTurnout("DSw7",  self, n, DELL, [(3, 1), (3, 2)])
			self.rr.AddTurnout("DSw11", self, n, DELL, [(3, 3), (3, 4)])
			self.rr.AddStopRelay("D20.srel", self, n, DELL, [(3, 5)])
			self.rr.AddStopRelay("H23.srel", self, n, DELL, [(3, 6)])
			self.rr.AddStopRelay("D11.srel", self, n, DELL, [(3, 7)])

			# inputs	
			self.rr.AddTurnoutPosition("DSw1", self, n, DELL, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("DSw3", self, n, DELL, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("DSw5", self, n, DELL, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("DSw7", self, n, DELL, [(0, 6), (0, 7)])

			self.rr.AddHandswitch("DSw9", self, n, DELL, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("DSw11", self, n, DELL, [(1, 2), (1, 3)])
			self.rr.AddBlock("D20",      self, n, DELL, [(1, 4)]) 
			self.rr.AddBlock("D20.E",    self, n, DELL, [(1, 5)]) 
			self.rr.AddBlock("H23",      self, n, DELL, [(1, 6)]) 
			self.rr.AddBlock("H23.E",    self, n, DELL, [(1, 7)]) 

			self.rr.AddBlock("DOSVJW",   self, n, DELL, [(2, 0)]) 
			self.rr.AddBlock("DOSVJE",   self, n, DELL, [(2, 1)]) 
			self.rr.AddBlock("D11.W",    self, n, DELL, [(2, 2)]) 
			self.rr.AddBlock("D11A",     self, n, DELL, [(2, 3)]) 
			self.rr.AddBlock("D11B",     self, n, DELL, [(2, 4)]) 
			self.rr.AddBlock("D11.E",    self, n, DELL, [(2, 5)]) 
			
			self.rr.GetBlock("D11A").SetMainBlock("D11")
			self.rr.GetBlock("D11B").SetMainBlock("D11")

		with self.nodes[FOSS] as n:
			# outputs
			self.rr.AddSignal("D10R", self, n, FOSS, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("D12R", self, n, FOSS, [(0, 3), (0, 4), (0, 5)])
	
			self.rr.AddSignal("D10L", self, n, FOSS, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignal("D12L", self, n, FOSS, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddStopRelay("D21.srel", self, n, FOSS, [(1, 6)])
			self.rr.AddStopRelay("S10.srel", self, n, FOSS, [(1, 7)])
	
			# bit 2:0 is bad
			self.rr.AddStopRelay("R10.srel", self, n, FOSS, [(2, 1)])
			self.rr.AddOutputDevice("RXO", self, n, FOSS, [(2, 2)]) # rocky hill crossing gate/signal
			self.rr.AddSignal("R10W", self, n, FOSS, [(2, 3), (2, 4), (2, 5)])

			#inputs	
			self.rr.AddBlock("D21.W",     self, n, DELL, [(0, 0)]) 
			self.rr.AddBlock("D21A",      self, n, DELL, [(0, 1)]) 
			self.rr.AddBlock("D21B",      self, n, DELL, [(0, 2)]) 
			self.rr.AddBlock("D21.E",     self, n, DELL, [(0, 3)]) 
			self.rr.AddBlock("DOSFOW",    self, n, DELL, [(0, 4)]) 
			self.rr.AddBlock("DOSFOE",    self, n, DELL, [(0, 5)]) 
			self.rr.AddBlock("S10.W",     self, n, DELL, [(0, 6)]) 
			self.rr.AddBlock("S10A",      self, n, DELL, [(0, 7)]) 

			self.rr.AddBlock("S10B",      self, n, DELL, [(1, 0)]) 
			self.rr.AddBlock("S10C",      self, n, DELL, [(1, 1)]) 
			self.rr.AddBlock("S10.E",     self, n, DELL, [(1, 2)]) 
			self.rr.AddBlock("R10.W",     self, n, DELL, [(1, 3)]) 
			self.rr.AddBlock("R10A",      self, n, DELL, [(1, 4)]) 
			self.rr.AddBlock("R10B",      self, n, DELL, [(1, 5)]) 
			self.rr.AddBlock("R10C",      self, n, DELL, [(1, 6)]) 
			self.rr.AddBlock("R11",       self, n, DELL, [(1, 7)]) 
			
			self.rr.AddBlock("R12",       self, n, DELL, [(2, 0)]) 
			
			self.rr.GetBlock("D21A").SetMainBlock("D21")
			self.rr.GetBlock("D21B").SetMainBlock("D21")
			
			self.rr.GetBlock("S10A").SetMainBlock("S10")
			self.rr.GetBlock("S10B").SetMainBlock("S10")
			self.rr.GetBlock("S10C").SetMainBlock("S10")
			
			self.rr.GetBlock("R10A").SetMainBlock("R10")
			self.rr.GetBlock("R10B").SetMainBlock("R10")
			self.rr.GetBlock("R10C").SetMainBlock("R10")

		
	def OutIn(self):
		# determine the state of the crossing gate at laporte
		dos1 = self.rr.GetBlock("DOSVJW").IsOccupied()
		d11w = self.rr.GetBlock("D11.W").IsOccupied()
		d11a = self.rr.GetBlock("D11A").IsOccupied()
		if dos1 and not self.D1W:
			self.D1E = True
		if (d11w or d11a) and not self.D1E:
			self.D1W = True
		if not dos1 and not (d11w or d11a):
			self.D1E = self.D1W = False
		
		dos2 = self.rr.GetBlock("DOSVJE").IsOccupied()
		d21w = self.rr.GetBlock("D21.W").IsOccupied()
		d21a = self.rr.GetBlock("D21A").IsOccupied()
		if dos2 and not self.D2W:
			self.D2E = True
		if (d21w or d21a) and not self.D2E:
			self.D2W = True
		if not dos2 and not (d21w or d21a):
			self.D2E = self.D2W = False
		
		DXO = (self.D1E and dos1) or (self.D1W and (d11w or d11a)) or (self.D2E and dos2) or (self.D2W and (d21w or d21a))
		if DXO != self.DXO:
			self.DXO = DXO
			self.rr.SetODevice("DXO", self.DXO)
				
		# determine the state of the crossing gate at rocky hill
		r10b = self.rr.GetBlock("R10B").IsOccupied()
		r10c = self.rr.GetBlock("R10C").IsOccupied()
		if r10b and not self.RXW:
			self.RXE = True
		if r10c and not self.RXE:
			self.RXW = True
		if not r10b and not r10c:
			self.RXE = self.RXW = False
		
		RXO = (r10b and self.RXE) or (r10c and self.RXW)
		if RXO != self.RXO:
			self.RXO = RXO
			self.rr.SetODevice("RXO", self.RXO)

		District.OutIn(self)
