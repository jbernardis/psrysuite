from constants import STOP


class Signal:
	def __init__(self, district, screen, frame, name, aspecttype, east, pos, tiles):
		self.district = district
		self.screen = screen
		self.frame = frame
		self.disabled = False
		self.name = name
		self.tiles = tiles
		self.pos = pos
		self.aspect = STOP
		self.aspectType = aspecttype
		self.east = east
		self.possibleRoutes = {}
		self.guardBlock = None # block that the signal is guarding exit from
		self.fleetEnabled = False
		self.lastAspect = 0
		self.locked = False
		self.lockedBy = []

	def SetDisabled(self, flag=True):
		self.disabled = flag

	def IsDisabled(self):
		return self.disabled

	def IsLocked(self):
		return self.locked

	def EnableFleeting(self, flag=None):
		if flag is None:
			self.fleetEnabled = not self.fleetEnabled
		else:
			self.fleetEnabled = flag
		# self.frame.Popup("Fleet %s for signal %s" % ("enabled" if self.fleetEnabled else "disabled", self.name))
		self.Draw()

	def IsFleeted(self):
		return self.fleetEnabled

	def AddPossibleRoutes(self, blk, rtList):
		self.possibleRoutes[blk] = rtList

	def IsPossibleRoute(self, blknm, rname):
		if blknm not in self.possibleRoutes:
			return False

		return rname in self.possibleRoutes[blknm]
		
	def GetDistrict(self):
		return self.district

	def GetScreen(self):
		return self.screen

	def GetName(self):
		return self.name

	def GetAspectType(self):
		return self.aspectType

	def GetPos(self):
		return self.pos

	def GetEast(self):
		return self.east

	def Draw(self):
		bmp = self.tiles.getBmp(self)
		self.frame.DrawTile(self.screen, self.pos, bmp) 

	def GetAspect(self):
		return self.aspect

	def SetLock(self, lockedby, flag=True):
		if flag:
			self.locked = True
			if lockedby in self.lockedBy:
				# already locked by this signal
				return
			self.lockedBy.append(lockedby)
			if len(self.lockedBy) == 1:
				self.frame.Request({"signallock": { "name": self.name, "status": 1}})
		else:
			if lockedby not in self.lockedBy:
				# this signal hasn't locked by this locker, so it can't unlock it
				return
			self.lockedBy.remove(lockedby)
			if len(self.lockedBy) == 0:
				self.locked = False
				self.frame.Request({"signallock": { "name": self.name, "status": 0}})

	def ClearLocks(self):
		print("clearing locks for signal %s" % self.name)
		self.lockedBy = []
		self.locked = False
		self.frame.Request({"signallock": { "name": self.name, "status": 0}})

	def SetAspect(self, aspect, refresh = False):
		if self.aspect == aspect:
			return False
		
		self.aspect = aspect
		if aspect != 0:
			self.lastAspect = aspect

		if refresh:
			self.Draw()

		if self.guardBlock is not None:
			self.guardBlock.EvaluateStoppingSections()
		return True

	def SetFleetPending(self, flag, blk):
		if not self.fleetEnabled:
			return

		if not flag:
			self.frame.DelPendingFleet(blk)
		else:
			self.frame.AddPendingFleet(blk, self)

	def DoFleeting(self):
		self.frame.Request({"signal": { "name": self.GetName(), "aspect": self.lastAspect }})

	def SetGuardBlock(self, blk):
		self.guardBlock = blk

	def GetGuardBlock(self):
		return self.guardBlock

