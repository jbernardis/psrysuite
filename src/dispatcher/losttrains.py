
class LostTrains:
	def __init__(self):
		self.trains = {}
		
	def Add(self, train, loco, engineer, block):
		if train.startswith("??"):
			return False
		
		self.trains[train] = (loco, engineer, block)
		return True
		
	def Remove(self, train):
		try:
			del(self.trains[train])
		except KeyError:
			return False
			
		return True
	
	def GetList(self):
		return [(train, info[0], info[1], info[2]) for train, info in self.trains.items()]
	
	def Count(self):
		return len(self.trains)