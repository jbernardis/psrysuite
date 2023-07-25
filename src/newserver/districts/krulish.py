import logging

from district import District
from constants import  KRULISH
from node import Node

class Krulish(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		logging.info("creating district Krulish")
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ KRULISH ]
		self.nodes = {
			KRULISH:   Node(self, rr, KRULISH,   3, settings)
		}

		addr = KRULISH
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("K8R",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("K4R",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("K2R",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignal("K2L",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignal("K8LA", self, n, addr, [(1, 4)])
			self.rr.AddSignal("K8LB", self, n, addr, [(1, 5), (1, 6), (1, 7)])

			# bits 2:0 thru 2:3 are unused
			self.rr.AddBreakerInd("CBKrulishYd", self, n, addr, [(2, 4)])

			self.rr.AddStopRelay("N10.srel", self, n, addr, [(2, 5)])
			self.rr.AddStopRelay("N20.srel", self, n, addr, [(2, 6)])
			self.rr.AddStopRelay("N11.srel", self, n, addr, [(2, 7)])

			# inputs	
			self.rr.AddTurnoutPosition("KSw1", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("KSw3", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("KSw5", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("KSw7", self, n, addr, [(0, 6), (0, 7)])
	
			# bits 1:0 and 1:1 are unused
			self.rr.AddBlock("N10.W",  self, n, addr, [(1, 2)])
			self.rr.AddBlock("N10",    self, n, addr, [(1, 3)])
			self.rr.AddBlock("N10.E",  self, n, addr, [(1, 4)])
			self.rr.AddBlock("N20.W",  self, n, addr, [(1, 5)])
			self.rr.AddBlock("N20",    self, n, addr, [(1, 6)])
			self.rr.AddBlock("N20.E",  self, n, addr, [(1, 7)])
			self.rr.AddBlock("KOSW",   self, n, addr, [(2, 0)])
			self.rr.AddBlock("KOSM",   self, n, addr, [(2, 1)])
			self.rr.AddBlock("KOSE",   self, n, addr, [(2, 2)])
			self.rr.AddBlock("N11.W",  self, n, addr, [(2, 3)])
			self.rr.AddBlock("N11",    self, n, addr, [(2, 4)])
			self.rr.AddBlock("N11.E",  self, n, addr, [(2, 5)])

