import logging
import json

class TrainList:
	def __init__(self, parent):
		self.parent = parent
		self.trains = {}

	def SetAtc(self, train, atcflag):
		if train not in self.trains:
			return 
		
		self.trains[train]["atc"] = atcflag

	def Update(self, train, loco, block, east):
		logging.debug("train list update %s %s %s east=%s" % (train, loco, block, east))
		if block is None:
			return

		if train is None:
			# search for and remove the block from the table
			dellist = []
			for tr in self.trains:
				if block in self.trains[tr]["blocks"]:
					logging.debug("deleting block %s from train %s" % (block, tr))
					self.trains[tr]["blocks"].remove(block)
					logging.debug("new block list = %s" % str(self.trains[tr]["blocks"]))
					if len(self.trains[tr]["blocks"]) == 0:
						dellist.append(tr)
						logging.debug("adding train %s to the dellist" % tr)

			for tr in dellist:
				del(self.trains[tr])
				logging.debug("removing train %s from the trainlist " % tr)

		else:
			if train in self.trains:
				if block not in self.trains[train]["blocks"]:
					self.trains[train]["blocks"].append(block)
				if loco:
					self.trains[train]["loco"] = loco
				self.trains[train]["east"] = east
			else:
				self.trains[train] = {"blocks": [block], "loco": loco, "atc": False, "signal": None, "aspect": 0, "east": east}
				
	def Dump(self):
		print("==========================start of trains dump")
		for trid in self.trains:
			print("%s: %s" % (trid, json.dumps(self.trains[trid])))
		print("==========================end of trains dump", flush=True)
				
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
	
	def GetTrainInfo(self, trid):
		if trid in self.trains:
			return self.trains[trid]
		
		return None

	def GetLocoForTrain(self, trn):
		for tr, trinfo in self.trains.items():
			if tr == trn:
				return trinfo["loco"]

		return None

	def RenameTrain(self, oname, nname, oloco, nloco, east):
		if oname == nname and oloco == nloco:
			if east is not None:
				self.trains[oname]["east"] = east
				return True
			else:
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
			
		if east is not None:
			self.trains[nname]["east"] = east

		return True
	
	def GetTrainList(self):
		return self.trains

	def GetSetTrainCmds(self, train=None, nameonly=False):
		nameflag = "1" if nameonly else "0"
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
				east = None if nameonly else trinfo["east"]
				logging.debug("trinfo = %s" % str(trinfo))
				clist = []
				for b in blocks:
					clist.append({"block": b, "name": tr, "loco": loco, "atc": atc, "east": east, "nameonly": nameflag})
				yield({"settrain": clist})
				yield({"trainsignal": {"train": tr, "block": frontblock, "signal": signal, "aspect": aspect}})
				
				
