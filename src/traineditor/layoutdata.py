import pprint

import os
import json

class LayoutData:
	def __init__(self, ddir):
		with open(os.path.join(ddir, "layout.json"), "r") as jfp:
			self.layout = json.load(jfp)

		self.routes = self.layout["routes"]
		self.subblocks = self.layout["subblocks"]

		self.block2route = {}
		self.osblocks = []
		self.blocks = []

		self.blockdir = {b: d["east"] for b, d in self.layout["blocks"].items()}
		self.stopblocks = {b: [d["sbeast"], d["sbwest"]] for b, d in self.layout["blocks"].items()}
		for r in self.routes:
			for b in self.routes[r]["ends"]:
				if b not in self.blocks and b is not None:
					self.blocks.append(b)
				if b in self.block2route:
					self.block2route[b].append(r)
				else:
					self.block2route[b] = [r]
			oswitch = self.routes[r]["os"]
			if oswitch not in self.osblocks and oswitch is not None:
				self.osblocks.append(oswitch)
			if oswitch in self.block2route:
				self.block2route[oswitch].append(r)
			else:
				self.block2route[oswitch] = [r]

		self.osblocks = sorted(self.osblocks)
		self.blocks = sorted([x for x in self.blocks if x not in self.osblocks])

	def GetRoutesForBlock(self, blknm):
		try:
			return self.block2route[blknm]
		except KeyError:
			return None

	def GetRouteEnds(self, rname):
		return self.routes[rname]["ends"]

	def GetRouteSignals(self, rname):
		return self.routes[rname]["signals"]

	def GetRouteOS(self, rname):
		return self.routes[rname]["os"]

	def GetBlocks(self):
		return self.blocks

	def IsBlockEast(self, blknm):
		try:
			return self.blockdir[blknm] == 1
		except KeyError:
			return None

	def GetSubBlocks(self, blk):
		try:
			return self.subblocks[blk]
		except KeyError:
			return []

	def GetStopBlocks(self, blk):
		try:
			return self.stopblocks[blk]
		except KeyError:
			return [None, None]

	def Dump(self):
		#pprint.pprint(self.block2route)
		#print("====================")
		print(str(self.blocks))
		#print(str(self.osblocks))
		#print(str(self.subblocks))
		pprint.pprint(self.routes)
		#pprint.pprint(self.blockdir)
		pprint.pprint(self.layout["blocks"])
		print(str(self.stopblocks))
		print("============================")

