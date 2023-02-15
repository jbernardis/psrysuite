class Train:
	tx = 0
	def __init__(self, name=None):
		self.index = Train.tx
		Train.tx += 1
		if name:
			self.name = name
		else:
			self.name = "??%d" % self.index
		self.loco = "??"
		self.atc = False
		self.blocks = {}

	def tstring(self):
		return "%s/%s (%s)" % (self.name, self.loco, str(self.blocks))

	def SetName(self, name):
		self.name = name
		
	def SetATC(self, flag=True):
		self.atc = flag
		
	def IsOnATC(self):
		return self.atc

	def SetLoco(self, loco):
		self.loco = loco

	def GetName(self):
		return self.name

	def GetLoco(self):
		return self.loco

	def GetBlockNameList(self):
		return list(self.blocks.keys())

	def GetBlockList(self):
		return self.blocks

	def GetNameAndLoco(self):
		return self.name, self.loco

	def GetIDString(self):
		a = "A-" if self.atc else ""
		n = self.name if self.name else "??"
		l = self.loco if self.loco else "??"
		return a+n+"/"+l

	def Draw(self):
		for blk in self.blocks.values():
			blk.DrawTrain()

	def AddToBlock(self, blk):
		bn = blk.GetName()
		if bn in self.blocks:
			return

		self.blocks[bn] = blk

	def RemoveFromBlock(self, blk):
		bn = blk.GetName()
		if bn not in self.blocks:
			return

		del self.blocks[bn]

	def IsInBlock(self, blk):
		bn = blk.GetName()
		return bn in self.blocks

	def IsInNoBlocks(self):
		return len(self.blocks) == 0
