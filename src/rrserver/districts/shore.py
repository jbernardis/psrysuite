import logging

from rrserver.district import District
from rrserver.constants import SHORE, HYDEJCT
from rrserver.node import Node


class Shore(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
			
		self.S1E = self.S1W = False
		self.S2E = self.S2W = False
		self.SXG = None
		self.BX = None
		self.F10H = self.F10D = None

		self.rr = rr
		self.name = name
		self.released = False
		self.control = 0
		self.nodeAddresses = [ SHORE, HYDEJCT ]
		self.nodes = {
			SHORE:   Node(self, rr, SHORE,   7, settings),
			HYDEJCT: Node(self, rr, HYDEJCT, 3, settings)
		}

		with self.nodes[SHORE] as n:
			#outputs
			self.rr.AddSignal("S4R",   self, n, SHORE, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("S12R",  self, n, SHORE, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("S4LA",  self, n, SHORE, [(0, 6)])
			self.rr.AddSignal("S4LB",  self, n, SHORE, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("S4LC",  self, n, SHORE, [(1, 2), (1, 3), (1, 4)])
			self.rr.AddSignal("S12LA", self, n, SHORE, [(1, 5), (1, 6), (1, 7)])
			self.rr.AddSignal("S12LB", self, n, SHORE, [(2, 0)])
			self.rr.AddSignal("S12LC", self, n, SHORE, [(2, 1), (2, 2), (2, 3)])

			self.rr.AddSignal("F10H",  self, n, SHORE, [(2, 4)])  # Branch signals
			self.rr.AddSignal("F10D",  self, n, SHORE, [(2, 5)])
			self.rr.AddSignal("S8R",   self, n, SHORE, [(2, 6)])
			self.rr.AddSignal("S8L",   self, n, SHORE, [(2, 7)])

			# bortell crossing animation being managed by local circuit 
			# bits 3:0 and 3:1 are no loinger used
			self.rr.AddBlockInd("S10", self, n, SHORE, [(3, 2)])
			self.rr.AddBlockInd("H20", self, n, SHORE, [(3, 3)])
			self.rr.AddBlockInd("S21", self, n, SHORE, [(3, 4)])
			self.rr.AddBlockInd("P32", self, n, SHORE, [(3, 5)])
			
			self.rr.AddBreakerInd("CBShore", self, n, SHORE, [(3, 6)])
			self.rr.AddBreakerInd("CBHarpersFerry", self, n, SHORE, [(3, 7)])

			self.rr.AddHandswitchInd("SSw1", self, n, SHORE, [(4, 0)])
			
			self.rr.AddTurnout("SSw3",  self, n, SHORE, [(4, 1), (4, 2)])
			self.rr.AddTurnout("SSw5",  self, n, SHORE, [(4, 3), (4, 4)])
			self.rr.AddTurnout("SSw7",  self, n, SHORE, [(4, 5), (4, 6)])
			self.rr.AddTurnout("SSw9",  self, n, SHORE, [(4, 7), (5, 0)])
			self.rr.AddTurnout("SSw11", self, n, SHORE, [(5, 1), (5, 2)])
			self.rr.AddTurnout("SSw13", self, n, SHORE, [(5, 3), (5, 4)])
			self.rr.AddOutputDevice("BX", self, n, SHORE, [(5, 5)]) # diamopnd crossing power relay

			self.rr.AddStopRelay("S20.srel", self, n, SHORE, [(5, 6)])
			self.rr.AddStopRelay("S11.srel", self, n, SHORE, [(5, 7)])
			self.rr.AddStopRelay("H30.srel", self, n, SHORE, [(6, 0)])
			self.rr.AddStopRelay("H10.srel", self, n, SHORE, [(6, 1)])
			self.rr.AddStopRelay("F10.srel", self, n, SHORE, [(6, 2)])
			self.rr.AddStopRelay("F11.srel", self, n, SHORE, [(6, 3)])

			self.rr.AddHandswitchInd("CSw15", self, n, SHORE, [(6, 4)])
			self.rr.AddOutputDevice("SXG", self, n, SHORE, [(6, 5)]) # bortell crossing gate

			#inputs	
			self.rr.AddHandswitch("SSw1",  self, n, SHORE, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("SSw3",  self, n, SHORE, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("SSw5",  self, n, SHORE, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("SSw7",  self, n, SHORE, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("SSw9",  self, n, SHORE, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("SSw11", self, n, SHORE, [(1, 2), (1, 3)])
			self.rr.AddTurnoutPosition("SSw13", self, n, SHORE, [(1, 4), (1, 5)])
	
			sbw = self.rr.AddBlock("S20.W",  self, n, SHORE, [(1, 6)]) 
			sba = self.rr.AddBlock("S20A",   self, n, SHORE, [(1, 7)]) 
			sbc = self.rr.AddBlock("S20C",   self, n, SHORE, [(2, 0)]) # C and B are wired backwards
			sbb = self.rr.AddBlock("S20B",   self, n, SHORE, [(2, 1)]) 
			sbe = self.rr.AddBlock("S20.E",  self, n, SHORE, [(2, 2)]) 
			b = self.rr.AddBlock("S20",  self, n, SHORE, []) 
			b.AddStoppingBlocks([sbe, sbw])
			b.AddSubBlocks([sba, sbb, sbc])
			
			self.rr.AddBlock("SOSW",   self, n, SHORE, [(2, 3)]) 
			self.rr.AddBlock("SOSE",   self, n, SHORE, [(2, 4)]) 
			sbw = self.rr.AddBlock("S11.W",  self, n, SHORE, [(2, 5)]) 
			sba = self.rr.AddBlock("S11A",  self, n, SHORE, [(4, 4)]) 
			sbb = self.rr.AddBlock("S11B",   self, n, SHORE, [(2, 6)]) 
			sbe = self.rr.AddBlock("S11.E",  self, n, SHORE, [(2, 7)]) 
			b = self.rr.AddBlock("S11",    self, n, SHORE, [])  # virtual definition for S11
			b.AddStoppingBlocks([sbe, sbw])
			b.AddSubBlocks([sba, sbb])
			
			sbw = self.rr.AddBlock("H30.W",  self, n, SHORE, [(3, 0)]) 
			sba = self.rr.AddBlock("H30A",   self, n, SHORE, [(4, 5)]) 
			sbb = self.rr.AddBlock("H30B",   self, n, SHORE, [(3, 1)]) 
			b = self.rr.AddBlock("H30",    self, n, SHORE, []) 
			b.AddStoppingBlocks([sbw])
			b.AddSubBlocks([sba, sbb])
						
			sbw = self.rr.AddBlock("H10.W",  self, n, SHORE, [(3, 2)]) 
			sba = self.rr.AddBlock("H10A",   self, n, SHORE, [(4, 6)]) 
			sbb = self.rr.AddBlock("H10B",   self, n, SHORE, [(3, 3)]) 
			b = self.rr.AddBlock("H10",    self, n, SHORE, [])
			b.AddStoppingBlocks([sbw])
			b.AddSubBlocks([sba, sbb])

			self.rr.AddBlock("F10",    self, n, SHORE, [(3, 4)]) 
			self.rr.AddBlock("F10.E",  self, n, SHORE, [(3, 5)]) 
			self.rr.AddBlock("SOSHF",  self, n, SHORE, [(3, 6)]) 
			self.rr.AddBlock("F11.W",  self, n, SHORE, [(3, 7)]) 
			self.rr.AddBlock("F11",    self, n, SHORE, [(4, 0)]) 
			# 		SXON  = SIn[4].bit.b1;	//Crossing gate off normal - no londer needed

			self.rr.AddHandswitch("CSw15", self, n, SHORE, [(4, 2), (4, 3)])

			

		with self.nodes[HYDEJCT] as n:
			#outputs
			self.rr.AddSignal("S16R",  self, n, HYDEJCT, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("S18R",  self, n, HYDEJCT, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("S20R",  self, n, HYDEJCT, [(0, 6)])
			self.rr.AddSignal("S16L",  self, n, HYDEJCT, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("S18LB", self, n, HYDEJCT, [(1, 2)])
			self.rr.AddSignal("S18LA", self, n, HYDEJCT, [(1, 3)])
			self.rr.AddSignal("S20L",  self, n, HYDEJCT, [(1, 4), (1, 5), (1, 6)])
			
			self.rr.AddTurnout("SSw15", self, n, HYDEJCT, [(1, 7), (2, 0)])
			self.rr.AddTurnout("SSw17", self, n, HYDEJCT, [(2, 1), (2, 2)])
			self.rr.AddTurnout("SSw19", self, n, HYDEJCT, [(2, 3), (2, 4)])

			self.rr.AddStopRelay("H20.srel", self, n, HYDEJCT, [(2, 5)])
			self.rr.AddStopRelay("P42.srel", self, n, HYDEJCT, [(2, 6)])
			self.rr.AddStopRelay("H11.srel", self, n, HYDEJCT, [(2, 7)])
			
			# inputs
			self.rr.AddTurnoutPosition("SSw15", self, n, HYDEJCT, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("SSw17", self, n, HYDEJCT, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("SSw19", self, n, HYDEJCT, [(0, 4), (0, 5)])

			b = self.rr.AddBlock("H20",    self, n, HYDEJCT, [(0, 6)]) 
			sbe = self.rr.AddBlock("H20.E",  self, n, HYDEJCT, [(0, 7)]) 
			b.AddStoppingBlocks([sbe])
			
			self.rr.AddBlock("P42.W",  self, n, HYDEJCT, [(1, 0)]) 
			self.rr.AddBlock("P42",    self, n, HYDEJCT, [(1, 1)]) 
			self.rr.AddBlock("P42.E",  self, n, HYDEJCT, [(1, 2)]) 
			self.rr.AddBlock("SOSHJW", self, n, HYDEJCT, [(1, 3)]) 
			self.rr.AddBlock("SOSHJM", self, n, HYDEJCT, [(1, 4)]) 
			self.rr.AddBlock("SOSHJE", self, n, HYDEJCT, [(1, 5)]) 
			self.rr.AddBlock("H11.W",  self, n, HYDEJCT, [(1, 6)]) 
			self.rr.AddBlock("H11",    self, n, HYDEJCT, [(1, 7)]) 
			


		
	def OutIn(self):
		# determine whether or not the bortell gate should be activated
		S10B = self.rr.GetBlock("S10B").IsOccupied()
		S10C = self.rr.GetBlock("S10C").IsOccupied()
		S20B = self.rr.GetBlock("S20B").IsOccupied()
		S20C = self.rr.GetBlock("S20C").IsOccupied()
		if S10B and  not self.S1W:
			self.S1E = True
		if S10C and not self.S1E:
			self.S1W = True
		if not S10B and not S10C:
			self.S1E = self.S1W = False
		if S20B and not self.S2W:
			self.S2E = True
		if S20C and not self.S2E:
			self.S2W = True
		if not S20B and not S20C:
			self.S2E = self.S2W = False
		
		SXG = (self.S1E and S10B) or (self.S1W and S10C) or (self.S2E and S20B) or (self.S2W and S20C)
		if self.SXG != SXG:
			self.SXG = SXG
			self.rr.SetODevice("SXG", self.SXG)

		# determine if we need to power the harper's ferry crossing diamond		
		asp = self.rr.GetSignal("S8R").Aspect()
		BX = asp		
		asp = self.rr.GetSignal("S8L").Aspect()
		BX += asp
		if self.BX != BX:
			self.BX = BX
			self.rr.SetODevice("BX", self.BX)

		# determine how we need to set the branch signals		
		asp8l = self.rr.GetSignal("S8L").Aspect()
		asp8r = self.rr.GetSignal("S8R").Aspect()
		f10occ = self.rr.GetBlock("F10").IsOccupied()
		F10H = asp8l == 0 and f10occ == 0
		F10D = F10H and (asp8r != 0)
		
		if F10H != self.F10H:
			self.F10H = F10H
			self.rr.SetAspect("F10H", 1 if F10H else 0)
		
		if F10D != self.F10D:
			self.F10D = F10D
			self.rr.SetAspect("F10D", 1 if F10D else 0)
		
		District.OutIn(self)

