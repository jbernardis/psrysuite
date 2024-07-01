import logging
import json
from tracker import engineers

class TrainList:
	def __init__(self, parent):
		self.parent = parent
		self.trains = {}

	def SetAtc(self, train, atcflag):
		if train not in self.trains:
			return 
		
		self.trains[train]["atc"] = atcflag

	def Update(self, train, loco, blocks, east, action):
		if len(blocks) == 0:
			return

		if train is None:
			# search for and remove the block from the table
			dellist = []
			for tr in self.trains:
				for b in blocks:
					if b in self.trains[tr]["blocks"]:
						self.trains[tr]["blocks"].remove(b)
						if len(self.trains[tr]["blocks"]) == 0:
							dellist.append(tr)

			for tr in dellist:
				del(self.trains[tr])

		else:
			if train in self.trains:
				if action == "replace":
					self.trains[train]["blocks"] = [b for b in blocks]
				else:
					for b in blocks:
						if b not in self.trains[train]["blocks"]:
							if action == "front":
								self.trains[train]["blocks"].append(b)
							else:
								self.trains[train]["blocks"] = [b] + self.trains[train]["blocks"]
				if loco:
					self.trains[train]["loco"] = loco
				self.trains[train]["east"] = east
			else:
				self.trains[train] = {"blocks": [b for b in blocks], "blockorder": [b for b in blocks], "loco": loco, "atc": False, "signal": None, "aspect": 0, "east": east}

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
				
	def UpdateEngineer(self, train, engineer):
		if train not in self.trains:
			return 
		
		self.trains[train]["engineer"] = engineer

	def UpdateTrainBlockOrder(self, train, blocks):
		if train not in self.trains:
			return

		self.trains[train]["blockorder"] = [b for b in blocks]

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

	def SetEast(self, name,east):
		if east is not None:
			self.trains[name]["east"] = east
	
	def GetTrainList(self):
		return self.trains

	def GetSetTrainCmds(self, train=None, nameonly=False):
		nameflag = "1" if nameonly else "0"
		for tr, trinfo in self.trains.items():
			if train is None or train == tr:
				loco = trinfo["loco"]
				blocks = trinfo["blockorder"]
				if len(blocks) == 0:
					frontblock = None
				else:
					frontblock = blocks[-1]
				atc = trinfo["atc"]
				signal = trinfo["signal"]
				aspect = "%d" % trinfo["aspect"]
				east = trinfo["east"]
				yield ({"settrain": {"blocks": blocks, "name": tr, "loco": loco, "atc": atc, "east": east, "nameonly": nameflag}})
				yield({"trainsignal": {"train": tr, "block": frontblock, "signal": signal, "aspect": aspect}})

				try:
					eng = trinfo["engineer"]
				except KeyError:
					eng = None
					
				p = {"train": tr, "reassign": 0}
				if eng is not None:
					p["engineer"] = eng
				
				yield({"assigntrain": [p]})
				
				
