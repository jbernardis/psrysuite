import json

class Schedule():
	def __init__(self):
		self.schedule  = []
		self.extras = []
					
		self.ox = 0
		
	def getSchedule(self):
		return self.schedule
	
	def getExtras(self):
		return self.extras
	
	def isExtraTrain(self, tid):
		return tid in self.extras
		
	def getTid(self, tx):
		if tx < 0 or tx >= len(self.order):
			return None
		
		return self.order[tx]
		
	def __len__(self):
		return len(self.order)

	def __iter__(self):
		self.ox = 0
		return self
	
	def __next__(self):
		if self.ox >= len(self.order):
			raise StopIteration
		
		rv = self.order[self.ox]
		self.ox += 1
		return rv
	
	def setNewSchedule(self, no):
		self.schedule  = [t for t in no]
	
	def setNewExtras(self, nex):
		self.extras  = [t for t in nex]
		
	def save(self, fn):
		j = {"schedule": self.schedule, "extras": self.extras}
		with open(fn, "w") as fp:
			json.dump(j, fp, indent=4, sort_keys=True)
		
	def load(self, fn):
		try:
			with open(fn, "r") as fp:
				j = json.load(fp)
		except:
			self.schedule = []
			self.extras = []
			return False
			
		self.schedule = [t for t in j["schedule"]]
		self.extras = [t for t in j["extras"]]
		return True

