class Train:
	def __init__(self, parent, name, loco):
		self.parent = parent
		self.name = name
		self.loco = loco
		self.blocks = []
		self.governingSignal = {"signal": None, "os": None, "route": None}
		

	def AddBlock(self, block):
		if block in self.blocks:
			return

		self.blocks.append(block)
		self.parent.TrainAddBlock(self.name, block)
		
	def GetBlocks(self):
		return self.blocks
	
	def GetFirstBlock(self):
		if len(self.blocks) == 0:
			return None
		return self.blocks[0]
	
	def GetGoverningSignal(self):
		return self.governingSignal
	
	def SetGoverningSignal(self, sig):
		print("setting governing signal for train %s to %s" % (self.name, str(sig)))
		self.governingSignal = sig
	

	def DelBlock(self, block):
		if block in self.blocks:
			self.blocks.remove(block)
			self.parent.TrainRemoveBlock(self.name, block, self.blocks)
			
		if len(self.blocks) > 0:
			self.parent.TrainTailInBlock(self.name, self.blocks[0])

		return len(self.blocks)
