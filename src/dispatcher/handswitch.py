class HandSwitch:
	def __init__(self, district, screen, frame, block, name, pos, tiles):
		self.district = district
		self.screen = screen
		self.frame = frame
		self.block = block
		self.name = name
		self.tiles = tiles
		self.pos = pos
		self.locked = False
		self.possibleRoutes = {}

	def GetDistrict(self):
		return self.district

	def GetScreen(self):
		return self.screen

	def GetBlock(self):
		return self.block

	def IsBlockBusy(self):
		return self.block.IsBusy()

	def IsBlockCleared(self):
		return self.block.IsCleared()

	def GetName(self):
		return self.name

	def GetPos(self):
		return self.pos

	def GetValue(self):
		return self.locked

	def SetValue(self, val, refresh=False):
		self.locked = val
		if refresh:
			self.Draw()

	def Draw(self):
		bmp = self.tiles.getBmp("", "locked" if self.locked else "unlocked")
		self.frame.DrawTile(self.screen, self.pos, bmp) 


