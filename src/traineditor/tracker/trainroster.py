import json
import copy

class TrainRoster:
	def __init__(self, fn):
		self.filename = fn
		with open(fn, "r") as fp:	
			self.trains = json.load(fp)
			
		for tid in self.trains:
			trn = self.trains[tid]
			if "cutoff" not in trn:
				trn["cutoff"] = False
			trn["block"] = None
			trn["loco"] = trn["normalloco"]

	def __iter__(self):
		self.order = sorted(self.trains.keys())
		self._tx = 0
		return self
		
	def __next__(self):
		if self._tx >= len(self.order):
			raise StopIteration
		
		rv = self.order[self._tx]
		self._tx += 1
		return rv
				
	def getTrainList(self):
		return list(self.trains.keys())
	
	def getTrain(self, tid):
		if not tid in self.trains:
			return None
		
		return self.trains[tid]
	
	def getTrainByLoco(self, loco):
		for tid in self.trains:
			if loco == self.trains[tid]["loco"]:
				return tid
			
		return None
	
	def save(self):
		newJson = copy.deepcopy(self.trains)
		for tid in newJson:
			trn = newJson[tid]
			trn["loco"] = None
			trn["block"] = None

		with open(self.filename, "w") as fp:
			json.dump(newJson, fp, indent=4, sort_keys=True)
