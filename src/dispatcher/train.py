import logging
	
ST_FWD    = "f"
ST_FWD128 = "F"
ST_REV    = "r"
ST_REV128 = "R"
ST_STOP   = "s"
ST_ESTOP  = "e"
		
def formatThrottle(speed, speedType):
	speedStr = "%3d" % int(speed)

	if speedType == ST_FWD128:
		return speedStr
	elif speedType == ST_FWD:
		return "%s/28" % speedStr
	elif speedType == ST_REV128:
		return "(%s)" % speedStr
	elif speedType == ST_REV:
		return "(%s/28)" % speedStr
	else:
		return speedStr


class Train:
	tx = 0
	def __init__(self, name=None):
		if name:
			self.name = name
		else:
			self.name = Train.NextName()
		self.loco = "??"
		self.atc = False
		self.ar = False
		self.sbActive = False
		self.blocks = {}
		self.blockOrder = []
		self.signal = None
		self.throttle = ""
		self.east = True
		self.aspect = None
		self.engineer = None
		self.beingEdited = False
		self.time = None
		
	def SetTime(self, t):
		self.time = t
		
	def AddTime(self, delta=1):
		if self.time is not None:
			self.time += delta
			return True
		return False
			
	def GetTime(self):
		return self.time
		
	def SetBeingEdited(self, flag):
		self.beingEdited = flag
		
	def IsBeingEdited(self):
		return self.beingEdited
		
	def dump(self):
		print("Train %s: %s %s %s" % (self.name, self.loco, self.blockInfo(), self.signalInfo()))
		
	def forSnapshot(self):
		return { "name": self.name, 
			"loco": self.loco,
			"east": self.east,
			"blocks": self.blockOrder }
		
	def blockInfo(self):
		bl = [bl for bl in self.blocks]
		return "[" + ", ".join(bl) + "]"
	
	def signalInfo(self):
		if self.signal is None:
			return "None"
		
		return "%s: %d" % (self.signal.GetName(), self.aspect)
	
	@classmethod	
	def ResetTX(cls):
		Train.tx = 0
		
	@classmethod
	def NextName(cls):
		rv = "??%s" % Train.tx
		Train.tx += 1
		return rv
	
	def GetEast(self):
		return self.east
	
	def SetEast(self, flag=True):
		self.east = flag

	def tstring(self):
		return "%s/%s (%s)" % (self.name, self.loco, str(self.blockOrder))

	def SetName(self, name):
		self.name = name
		
	def SetAR(self, flag):
		self.ar = flag
		
	def IsOnAR(self):
		return self.ar
		
	def SetATC(self, flag=True):
		self.atc = flag
		
	def IsOnATC(self):
		return self.atc

	def SetLoco(self, loco):
		self.loco = loco
		logging.info("changing loco to %s for train %s" % (loco, self.name))
		
	def SetEngineer(self, engineer):
		if engineer is None:
			self.time = None
		elif self.engineer is None:
			self.time = 0
		self.engineer = engineer
		
	def GetEngineer(self):
		return self.engineer

	def GetName(self):
		return self.name

	def GetLoco(self):
		return self.loco
	
	def SetSignal(self, sig):
		self.signal = sig
		self.aspect = sig.GetAspect()
	
	def GetSignal(self):
		return self.signal, self.aspect, None if self.signal is None else self.signal.GetFrozenAspect()
	
	def SetThrottle(self, speed, speedtype):
		self.throttle = formatThrottle(speed, speedtype)
	
	def GetThrottle(self):
		return self.throttle

	def GetBlockNameList(self):
		return list(self.blocks.keys())

	def GetBlockList(self):
		return self.blocks

	def GetBlockCount(self):
		return len(self.blocks)

	def GetNameAndLoco(self):
		return self.name, self.loco
	
	def SetSBActive(self, flag):
		self.sbActive = flag
		
	def GetSBActive(self):
		return self.sbActive

	def Draw(self):
		for blk in self.blocks.values():
			blk.DrawTrain()

	def SetBlocksDirection(self):
		for blk in self.blocks.values():
			blk.SetEast(self.east)
			blk.Draw()

	def AddToBlock(self, blk):
		bn = blk.GetName()
		if bn in self.blocks:
			return

		self.blocks[bn] = blk
		blk.SetTrain(self)
		self.blockOrder.append(bn)
		logging.debug("Added block %s to train %s, new block list = %s" % (bn, self.name, str(self.blockOrder)))

	def RemoveFromBlock(self, blk):
		bn = blk.GetName()
		if bn not in self.blocks:
			return False

		blk.SetTrain(None)
		del self.blocks[bn]
		self.blockOrder.remove(bn)
		logging.debug("Removed block %s from train %s, new block list = %s" % (bn, self.name, str(self.blockOrder)))
		return True
		
	def IsContiguous(self):
		print("check for contiguous: %s" % self.GetName())
		#if self.GetName().startswith("??"):
			# do not test for trains with temporary names
			#return True
		
		bnames = list(self.blocks.keys())
		print("blocks: %s" % str(bnames))
		countBlocks = len(bnames)
		if countBlocks <= 1:
			# only occupying 1 block - contiguous by default
			logging.info("is contiguous returning true because countblocks = %d" % countBlocks)
			return True
		
		count1 = 0
		count2 = 0
		# for each block the train is in, count how many blocks adjacent to that block contain the same train
		adjStr = ""
		blkAdj = ""
		for blk in self.blocks.values():
			adje, adjw = blk.GetAdjacentBlocks()
			print("adjacent to block %s = %s, %s" % (blk.GetName(), "None" if adje is None else adje.GetName(), "None" if adjw is None else adjw.GetName()))
			adjc = 0
			blkAdj += "%s: %s,%s  " % (blk.GetName(), "None" if adje is None else adje.GetName(), "None" if adjw is None else adjw.GetName())
			for adj in adje, adjw:
				if adj is None:
					continue
				if adj.GetName() in bnames:
					adjc += 1
			adjStr += "%s: %s, " % (blk.GetName(), adjc)
			print(adjStr)

			# the count is either 1 (for the blocks at the beginning and the end of the train)
			# or two for all of the blocks in between
			if adjc == 1:
				count1 += 1
			elif adjc == 2:
				count2 += 1
			else:
				logging.error("block %s in train %s adjacent count = %d" % (blk.GetName(), self.GetName(), adjc))

		# so when we reach here, there MUST be 2 blocks whose adjacent count is 1 - the first and last blocks
		# there must also be countBlocks-2 blocks whose count is 2 - this is all the blocks mid train
		print("after block loop, counts = %d, %d" % (count1, count2))						
		if count1 != 2 or count2 != countBlocks-2:
			logging.info("=============================================")
			logging.info("train %s is non contiguous, blocks=%s c1=%d c2=%d countblocks=%d" % (self.GetName(), str(bnames), count1, count2, countBlocks))
			logging.info(adjStr)
			logging.info(blkAdj)
			logging.info("=============================================")
			return False
		
		return True
			
	def FrontInBlock(self, bn):
		if len(self.blockOrder) == 0:
			return False
		return bn == self.blockOrder[-1]
			
	def FrontBlock(self):
		if len(self.blockOrder) == 0:
			return None
		bn = self.blockOrder[-1]
		return self.blocks[bn]
			
	def IsInBlock(self, blk):
		bn = blk.GetName()
		return bn in self.blocks

	def IsInNoBlocks(self):
		return len(self.blocks) == 0
