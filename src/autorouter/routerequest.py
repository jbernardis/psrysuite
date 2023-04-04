class RouteRequest:
	def __init__(self, train, route, entryblk):
		self.train = train
		self.route = route
		self.entryblk = entryblk

	def GetName(self):
		return self.route.GetName()

	def GetOS(self):
		return self.route.GetOS()

	def GetTrain(self):
		return self.train

	def GetEntryBlock(self):
		return self.entryblk
	
	def tostring(self):
		return "%s: OS:%s Train:%s  EBlk:%s" % (self.GetName(), self.GetOS(), self.GetTrain(), self.GetEntryBlock())

	def Print(self):
		print("Route Request: Trn:%s Rte:%s OS:%s Blk:%s" % (self.train, self.route.GetName(), self.route.GetOS(), self.entryblk))
		self.route.Print()