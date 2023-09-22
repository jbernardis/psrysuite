import logging

class TrainList:
	def __init__(self, parent):
		self.parent = parent
		self.trains = {}
		self.count = 0

	def SetAtc(self, train, atcflag):
		if train not in self.trains:
			return 
		
		self.trains[train]["atc"] = atcflag

	def Update(self, train, loco, block):
		if block is None:
			return

		if train is None:
			# search for and remove the block from the table
			dellist = []
			for tr in self.trains:
				if block in self.trains[tr]["blocks"]:
					self.trains[tr]["blocks"].remove(block)
					if len(self.trains[tr]["blocks"]) == 0:
						dellist.append(tr)

			for tr in dellist:
				del(self.trains[tr])

		else:
			if train in self.trains:
				if block not in self.trains[train]["blocks"]:
					self.trains[train]["blocks"].append(block)
				if loco:
					self.trains[train]["loco"] = loco
			else:
				self.trains[train] = {"blocks": [block], "loco": loco, "atc": False, "signal": None, "aspect": 0}
				
	def UpdateSignal(self, train, signal, aspect):
		if train not in self.trains:
			return 
		
		self.trains[train]["signal"] = signal
		self.trains[train]["aspect"] = int(aspect)
		

	def FindTrainInBlock(self, block):
		for tr, trinfo in self.trains.items():
			if block in trinfo["blocks"]:
				return tr, trinfo["loco"]

		return None, None

	def FindTrain(self, trn):
		for tr, trinfo in self.trains.items():
			if tr == trn:
				return trinfo["loco"]

		return None

	def RenameTrain(self, oname, nname, oloco, nloco):
		if oname == nname and oloco == nloco:
			return False
			
		if oname != nname:
			if oname not in self.trains:
				# we can't do anything if we can't find the original record
				return False

			if nname in self.trains:
				# in this case, we retain the old information, but merge the block lists
				for b in self.trains[oname]["blocks"]:
					if b not in self.trains[nname]["blocks"]:
						self.trains[nname]["blocks"].append(b)
			else:
				self.trains[nname] = self.trains[oname]

			del(self.trains[oname])

		if nloco is not None:
			self.trains[nname]["loco"] = nloco

		return True
	
	def GetTrainList(self):
		print("train list")
		for tr, trinfo in self.trains.items():
			print("Train %s: %s %s %s %s" % (tr, trinfo["loco"], str(trinfo["blocks"]), trinfo["signal"], trinfo["aspect"]))
		print("=======================================", flush=True)
		return self.trains

	def GetSetTrainCmds(self, train=None):
		for tr, trinfo in self.trains.items():
			if train is None or train == tr:
				loco = trinfo["loco"]
				blocks = trinfo["blocks"]
				if len(blocks) == 0:
					frontblock = None
				else:
					frontblock = blocks[-1]
				atc = trinfo["atc"]
				signal = trinfo["signal"]
				aspect = "%d" % trinfo["aspect"]
				clist = []
				for b in blocks:
					clist.append({"block": b, "name": tr, "loco": loco, "atc": atc})
				yield({"settrain": clist})
				yield({"trainsignal": {"train": tr, "block": frontblock, "signal": signal, "aspect": aspect}})
				
				
