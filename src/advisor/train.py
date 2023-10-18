class Train:
	def __init__(self, parent, name, loco):
		self.parent = parent
		self.name = name
		self.loco = loco
		self.blocks = []
		self.atOrigin = True
		self.east = True

	def AddBlock(self, block):
		if block in self.blocks:
			return

		self.blocks.append(block)
		self.parent.TrainAddBlock(self.name, block)
		
	def IsAtOrigin(self):
		return self.atOrigin
	
	def SetAtOrigin(self, flag):
		self.atOrigin = flag
		
	def SetEast(self, flag):
		self.east = flag
		
	def GetBlocks(self):
		return self.blocks

	def DelBlock(self, block):
		if block in self.blocks:
			self.blocks.remove(block)
			self.parent.TrainRemoveBlock(self.name, block, self.blocks)
			
		if len(self.blocks) > 0:
			self.parent.TrainTailInBlock(self.name, self.blocks[0])

		return len(self.blocks)
