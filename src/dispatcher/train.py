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
		self.arReleased = False
		self.blocks = {}

	def tstring(self):
		return "%s/%s (%s)" % (self.name, self.loco, str(self.blocks))

	def SetName(self, name):
		self.name = name
		
	def SetARReleased(self, flag):
		self.arReleased = flag
		
	def IsARReleased(self):
		return self.arReleased
		
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
		
	def IsContiguous(self):
		bnames = list(self.blocks.keys())
		countBlocks = len(bnames)
		if countBlocks <= 1:
			# only occupying 1 block - contiguous by default
			return True
		
		count1 = 0
		count2 = 0
		# for each block the train is in, count how many blocks adjacent to that block contain the same train
		for blk in self.blocks.values():
			adje, adjw = blk.GetAdjacentBlocks()
			adjc = 0
			for adj in adje, adjw:
				if adj is None:
					continue
				if adj.GetName() in bnames:
					adjc += 1

			# the count is either 1 (for the blocks at the beginning and the end of the train)
			# or two for all of the blocks in between					
			if adjc == 1:
				count1 += 1
			elif adjc == 2:
				count2 += 1

		# so when we reach here, there MUST be 2 blocks whose adjacent count is 1 - the first and last blocks
		# there must also be countBlocks-2 blocks whose count is 2 - this is all the blocks mid train						
		if count1 != 2 or count2 != countBlocks-2:
			return False
		
		return True
			

	def IsInBlock(self, blk):
		bn = blk.GetName()
		return bn in self.blocks

	def IsInNoBlocks(self):
		return len(self.blocks) == 0
