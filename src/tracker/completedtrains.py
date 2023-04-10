class CompletedTrains:
	def __init__(self):
		self.completedTrains = {}
		self.entryOrder = []
		
	def clear(self):
		self.completedTrains = {}
		self.entryOrder = []
		
	def append(self, tid, engineer, loco):
		self.completedTrains[tid] = [engineer, loco]
		self.entryOrder.append(tid)
		
	def getTrain(self, tx):
		if tx < 0 or tx >= len(self.entryOrder):
			return None
		
		tid = self.entryOrder[tx]
		eng, loco = self.completedTrains[tid]
		if loco is None:
			loco = ""
		return tid, eng, loco
	
	def getTrainList(self):
		return self.entryOrder
	
	def count(self):
		return len(self.entryOrder)
		
	def __contains__(self, tid):
		return tid in self.completedTrains.keys()

	def __iter__(self):
		self.order = sorted(self.completedTrains.keys())
		self._tx = 0
		return self
		
	def __next__(self):
		if self._tx >= len(self.order):
			raise StopIteration
		
		tr = self.order[self._tx]
		self._tx += 1
		return tr, self.completedTrains[tr]
