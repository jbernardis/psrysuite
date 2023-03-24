import logging

from dispatcher.constants import EMPTY, OCCUPIED, CLEARED, BLOCK, OVERSWITCH, STOPPINGBLOCK, MAIN, STOP


class Route:
	def __init__(self, screen, osblk, name, blkin, pos, blkout, rtype, turnouts, signals):
		self.screen = screen
		self.name = name
		self.osblk = osblk
		self.blkin = blkin
		self.pos = [x for x in pos]
		self.blkout = blkout
		self.rtype = [x for x in rtype]
		self.turnouts = [x.split(":") for x in turnouts]
		self.signals = [x for x in signals]

	def GetDefinition(self):
		msg = {
			"name": self.name,
			"os":   self.osblk.GetName(),
			"ends": [self.blkin, self.blkout],
			"signals":
				[x for x in self.signals],
			"turnouts":
				["%s:%s" % (x[0], x[1]) for x in self.turnouts]
		}
		return msg

	def GetName(self):
		return self.name

	def GetDescription(self):
		return "%s <=> %s" % (self.blkin, self.blkout)

	def GetPositions(self):
		return self.screen, self.pos

	def Contains(self, screen, pos):
		if screen != self.screen:
			return False
		return pos in self.pos

	def GetStatus(self):
		return self.osblk.GetStatus()

	def GetOS(self):
		return self.osblk

	def GetOSName(self):
		return self.osblk.GetName()

	def GetRouteType(self, reverse=False):
		if self.osblk.east:
			return self.rtype[1] if reverse else self.rtype[0]
		else:
			return self.rtype[0] if reverse else self.rtype[1]

	def GetLockTurnouts(self):
		return [x[0] for x in self.turnouts]

	def GetSetTurnouts(self):
		return self.turnouts

	def GetExitBlock(self, reverse=False):
		if self.osblk.IsReversed():
			return self.blkout if reverse else self.blkin
		else:
			return self.blkin if reverse else self.blkout

	def GetEntryBlock(self, reverse=False):
		if self.osblk.IsReversed():
			return self.blkin if reverse else self.blkout
		else:
			return self.blkout if reverse else self.blkin

	def GetEndPoints(self):
		return [self.blkin, self.blkout]

	def GetSignals(self):
		return self.signals
	
	def RemoveClearStatus(self):
		if self.osblk.IsReversed():
			b = self.blkin
		else:
			b = self.blkout
		blk = self.osblk.frame.blocks[b]
		if blk.GetBlockType() != OVERSWITCH:
			# do NOT clear on an adjacent OS block
			blk.RemoveClearStatus()

	def ReleaseSignalLocks(self):
		frame = self.osblk.frame
		for s in self.signals:
			frame.signals[s].ClearLocks()

	def ToJson(self):
		return {self.name: {"os": self.osblk.GetName(), "ends": [self.blkin, self.blkout], "signals": self.signals, "turnouts": self.turnouts}}


class Block:
	def __init__(self, district, frame, name, tiles, east=True):
		self.status = None
		self.district = district
		self.frame = frame
		self.name = name
		self.type = BLOCK
		self.tiles = tiles  # [Tile, screen, coordinates, reverseindication]
		self.east = east
		self.defaultEast = east
		self.occupied = False
		self.cleared = False
		self.turnouts = []
		self.handswitches = []
		self.train = None
		self.trainLoc = []
		self.blkEast = None
		self.blkWest = None
		self.sbEast = None
		self.sbWest = None
		self.sigWest = None
		self.sigEast = None
		self.determineStatus()
		self.entrySignal = None
		self.entryAspect = 0

	def SetTrain(self, train):
		self.train = train

	def SetEntrySignal(self, esig):
		self.entrySignal = esig
		
	def SetEntryAspect(self, aspect):
		self.entryAspect = aspect

	def GetEntrySignal(self):
		return self.entrySignal

	def AddStoppingBlock(self, tiles, eastend=False):
		if eastend:
			self.sbEast = StoppingBlock(self, tiles, eastend)
		else:
			self.sbWest = StoppingBlock(self, tiles, eastend)
		self.determineStatus()

	def AddTrainLoc(self, screen, loc):
		self.trainLoc.append([screen, loc])

	def GetTrain(self):
		return self.train

	def GetTrainLoc(self):
		return self.trainLoc

	def GetTiles(self):
		return self.tiles

	def SetSignals(self, sigs):
		self.sigWest = sigs[0]
		self.sigEast = sigs[1]

	def GetSignals(self):
		return self.sigWest, self.sigEast

	def AddHandSwitch(self, hs):
		self.handswitches.append(hs)

	def AreHandSwitchesSet(self):
		for hs in self.handswitches:
			if hs.GetValue():
				return True
		return False

	def DrawTrain(self):
		if len(self.trainLoc) == 0:
			return

		if self.train is None:
			trainID = "??"
			locoID = "??"
			atc = False
		else:
			trainID, locoID = self.train.GetNameAndLoco()
			atc = self.train.IsOnATC()

		anyOccupied = self.occupied
		if self.sbEast and self.sbEast.IsOccupied():
			anyOccupied = True
		if self.sbWest and self.sbWest.IsOccupied():
			anyOccupied = True

		stopRelay = self.StoppingRelayActivated()

		for screen, loc in self.trainLoc:
			if anyOccupied:
				self.frame.DrawTrain(screen, loc, trainID, locoID, stopRelay, atc)
			else:
				self.frame.ClearTrain(screen, loc)

	def StoppingRelayActivated(self):
		active = False
		if self.sbEast and self.sbEast.IsActive():
			active = True
		if self.sbWest and self.sbWest.IsActive():
			active = True
		return active

	def DrawTurnouts(self):
		pass

	def Reset(self):
		self.SetEast(self.defaultEast)

	def SetNextBlockEast(self, blk):
		if blk is None:
			logging.debug("Block %s: next east block is None" % self.GetName())
		else:
			logging.debug("Block %s: next east block is %s" % (self.GetName(), blk.GetName()))
		self.blkEast = blk

	def SetNextBlockWest(self, blk):
		if blk is None:
			logging.debug("Block %s: next west block is None" % self.GetName())
		else:
			logging.debug("Block %s: next west block is %s" % (self.GetName(), blk.GetName()))
		self.blkWest = blk

	def determineStatus(self):
		self.status = OCCUPIED if self.occupied else CLEARED if self.cleared else EMPTY

	def NextBlock(self, reverse=False):
		if self.east:
			return self.blkWest if reverse else self.blkEast
		else:
			return self.blkEast if reverse else self.blkWest

	def GetRouteType(self):
		return MAIN

	def GetBlockType(self):
		return self.type

	def GetName(self):
		return self.name
	
	def GetAdjacentBlocks(self):
		return self.blkEast, self.blkWest

	def GetDistrict(self):
		return self.district

	def GetStatus(self, blockend=None):
		self.determineStatus()
		if blockend is None:
			return self.status
		elif blockend == 'E' and self.sbEast is not None:
			return self.sbEast.GetStatus()
		elif blockend == 'W' and self.sbWest is not None:
			return self.sbWest.GetStatus()
		else:
			# this should never happen
			return self.status

	def GetEast(self, reverse=False):
		return not self.east if reverse else self.east

	def SetEast(self, east, broadcast=True):
		if self.east == east:
			return

		self.east = east
		if broadcast:
			self.frame.Request({"blockdir": { "block": self.GetName(), "dir": "E" if east else "W"}})
			for b in [self.sbEast, self.sbWest]:
				if b is not None:
					self.frame.Request({"blockdir": { "block": b.GetName(), "dir": "E" if east else "W"}})

	def IsReversed(self):
		return self.east != self.defaultEast

	def IsBusy(self):
		if self.cleared or self.occupied:
			return True
		for b in [self.sbEast, self.sbWest]:
			if b and b.IsBusy():
				return True
		return False

	def IsCleared(self):
		return self.cleared

	def IsSectionOccupied(self, section):
		if section == "E":
			if self.sbEast:
				return self.sbEast.IsOccupied()
			else:
				return False
		elif section == "W":
			if self.sbWest:
				return self.sbWest.IsOccupied()
			else:
				return False
		else:
			return self.occupied

	def IsOccupied(self):
		if self.occupied:
			return True

		if self.sbEast and self.sbEast.IsOccupied():
			return True

		if self.sbWest and self.sbWest.IsOccupied():
			return True

		return False

	def Draw(self):
		for t, screen, pos, revflag in self.tiles:
			bmp = t.getBmp(self.status, self.east, revflag)
			self.frame.DrawTile(screen, pos, bmp)

		for b in [self.sbEast, self.sbWest]:
			if b is not None:
				b.Draw()
				
		for t in self.turnouts:
			t.Draw(self.status, self.east)

		self.district.DrawOthers(self)
		self.DrawTrain()

	def AddTurnout(self, turnout):
		self.turnouts.append(turnout)

	def SetOccupied(self, occupied=True, blockend=None, refresh=False):
		if blockend in ["E", "W"]:
			b = self.sbEast if blockend == "E" else self.sbWest
			if b is None:
				logging.warning("Stopping block %s not defined for block %s" % (blockend, self.GetName()))
				return
			b.SetOccupied(occupied, refresh)
			if occupied and self.train is None and self.frame.IsDispatcher():
				tr = self.IdentifyTrain()
				if tr is None:
					tr = self.frame.NewTrain()

				trn, loco = tr.GetNameAndLoco()
				self.SetTrain(tr)
				self.frame.Request({"settrain": { "block": self.GetName(), "name": trn, "loco": loco}})
			if refresh:
				self.Draw()
			return

		if self.occupied == occupied:
			# already in the requested state
			return

		self.occupied = occupied
		if self.occupied:
			self.cleared = False
			self.frame.Request({"blockclear": { "block": self.GetName(), "clear": 0}})

			if self.train is None:   # and self.frame.IsDispatcher():
				tr = self.IdentifyTrain()
				if tr is None:
					tr = self.frame.NewTrain()

				trn, loco = tr.GetNameAndLoco()

				self.SetTrain(tr)
				self.frame.Request({"settrain": { "block": self.GetName(), "name": trn, "loco": loco}})
		else:
			for b in [self.sbEast, self.sbWest]:
				if b is not None:
					b.SetCleared(False, refresh)

			self.CheckAllUnoccupied()

		self.determineStatus()
		if self.status == EMPTY:
			self.Reset()

		if refresh:
			self.Draw()

	def CheckAllUnoccupied(self):
		if self.occupied:
			return
		if self.sbEast and self.sbEast.IsOccupied():
			return
		if self.sbWest and self.sbWest.IsOccupied():
			return
		# all unoccupied - clean up
		if self.frame.IsDispatcher():
			self.frame.Request({"settrain": { "block": self.GetName(), "name": None, "loco": None}})
		self.train = None
		self.EvaluateStoppingSections()
		if self.entrySignal is not None:
			signm = self.entrySignal.GetName()
			self.frame.Request({"signal": { "name": signm, "aspect": STOP}})
			self.entrySignal.SetLock(self.GetName(), 0)

		self.frame.DoFleetPending(self)

	def GetStoppingSections(self):
		return self.sbWest, self.sbEast

	def EvaluateStoppingSections(self):
		if self.east and self.sbEast:
			self.sbEast.EvaluateStoppingSection()
		elif (not self.east) and self.sbWest:
			self.sbWest.EvaluateStoppingSection()

	def IdentifyTrain(self):
		if self.east:
			if self.blkWest:
				if self.blkWest.GetName() in ["KOSN10S11", "KOSN20S21"]:
					blkWest = self.blkWest.blkWest
					return None if blkWest is None else blkWest.GetTrain()

				return self.blkWest.GetTrain()
			else:
				return None
		else:
			if self.blkEast:
				if self.blkEast.GetName() in ["KOSN10S11", "KOSN20S21"]:
					blkEast = self.blkEast.blkEast
					return None if blkEast is None else blkEast.GetTrain()

				return self.blkEast.GetTrain()
			else:
				return None

	def SetCleared(self, cleared=True, refresh=False):
		if cleared and self.occupied:
			# can't mark an occupied block as cleared
			return

		if self.cleared == cleared:
			# already in the desired state
			return

		self.cleared = cleared
		self.determineStatus()
		if self.status == EMPTY:
			self.Reset()
		self.frame.Request({"blockclear": { "block": self.GetName(), "clear": 1 if cleared else 0}})

		if refresh:
			self.Draw()

		for b in [self.sbEast, self.sbWest]:
			if b is not None:
				b.SetCleared(cleared, refresh)
				
	def RemoveClearStatus(self):
		self.cleared = False
		self.determineStatus()
		for b in [self.sbEast, self.sbWest]:
			if b is not None:
				b.RemoveClearStatus()
		self.Draw()

	def ToJson(self):
		return {self.name: {"east": 1 if self.defaultEast else 0,
							"sbeast": None if self.sbEast is None else self.sbEast.GetName(),
							"sbwest": None if self.sbWest is None else self.sbWest.GetName()}}


class StoppingBlock (Block):
	def __init__(self, block, tiles, eastend):
		self.block = block
		self.tiles = tiles
		self.eastend = eastend
		self.type = STOPPINGBLOCK
		self.frame = self.block.frame
		self.active = False
		self.occupied = False
		self.cleared = False
		self.determineStatus()
		self.lastSignalGreen = False
		self.lastBlockEmpty = False

	def EvaluateStoppingSection(self):
		if not self.occupied:
			self.Activate(False)
			return

		if self.block.east and self.eastend:
			signm = self.block.sigEast
			blk = self.block.blkEast
		elif (not self.block.east) and (not self.eastend):
			signm = self.block.sigWest
			blk = self.block.blkWest
		else:
			return
		
		if signm:
			if blk:
				tr = self.block.GetTrain()
				if tr is None:
					return
				blkOccupied = blk.IsOccupied()
				if blkOccupied:
					trnext = blk.GetTrain()
					if trnext is None:
						return
					if tr.GetName() == trnext.GetName():
						return
			else:
				blkOccupied = True

			sv = self.frame.GetSignalByName(signm).GetAspect()
			if not(self.lastSignalGreen and self.lastBlockEmpty and sv == 0 and blkOccupied):
				self.Activate(sv == 0)
			self.lastSignalGreen = sv != 0
			self.lastBlockEmpty = not blkOccupied

	def Activate(self, flag=True):
		if flag == self.active:
			return
		
		tr = self.block.GetTrain()
		if tr is None:
			tname = "??"
		else:
			tname = tr.GetName()
			
		bname = self.block.GetName()
		direction = "East" if self.eastend else "West"

		self.active = flag
		if flag:
			self.frame.PopupEvent("Stop Relay: %s %s by %s" % (bname, direction, tname))
		logging.debug("Block %s stopping relay %s %s end by train %s" % (bname, "activated" if flag else "cleared", direction, tname))
		self.frame.Request({"relay": { "block": self.block.GetName(), "status": 1 if flag else 0}})

		self.block.DrawTrain()

	def IsActive(self):
		return self.active

	def Draw(self):
		self.east = self.block.east
		# self.frame.Request({"blockdir": { "block": self.GetName(), "dir": "E" if self.east else "W"}})
		for t, screen, pos, revflag in self.tiles:
			bmp = t.getBmp(self.status, self.east, revflag)
			self.frame.DrawTile(screen, pos, bmp)

	def determineStatus(self):
		self.status = OCCUPIED if self.occupied else CLEARED if self.cleared else EMPTY

	def GetStatus(self):
		self.determineStatus()
		return self.status

	def GetRouteType(self):
		return self.block.GetRouteType()

	def Reset(self):
		pass

	def GetEast(self, reverse=False):
		return self.block.GetEast(reverse)

	def IsOccupied(self):
		return self.occupied

	def IsReversed(self):
		return self.block.east != self.block.defaultEast

	def IsBusy(self):
		return self.cleared or self.occupied

	def GetDistrict(self):
		return None

	def GetName(self):
		return self.block.GetName() + "." + ("E" if self.eastend else "W")

	def SetCleared(self, cleared=True, refresh=False):
		if cleared and self.occupied:
			# can't mark an occupied block as cleared
			return

		if self.cleared == cleared:
			# already in the desired state
			return

		self.frame.Request({"blockclear": { "block": self.GetName(), "clear": 1 if cleared else 0}})
		self.cleared = cleared
		self.determineStatus()
		if refresh:
			self.Draw()
			
	def RemoveClearStatus(self):
		self.cleared = False
		self.determineStatus()
		self.Draw()

	def SetOccupied(self, occupied=True, refresh=False):
		if self.occupied == occupied:
			# already in the requested state
			return

		self.occupied = occupied
		if self.occupied:
			self.frame.Request({"blockclear": { "block": self.GetName(), "clear": 0}})
			self.cleared = False
			self.EvaluateStoppingSection()

		else:
			self.EvaluateStoppingSection()
			self.block.CheckAllUnoccupied()

		self.determineStatus()
		if self.status == EMPTY:
			self.Reset()

		if refresh:
			self.Draw()


class OverSwitch (Block):
	def __init__(self, district, frame, name, tiles, east=True):
		Block.__init__(self, district, frame, name, tiles, east)
		self.type = OVERSWITCH
		self.route = None
		self.rtName = ""
		self.entrySignal = None
		self.entryAspect = 0

	def SetRoute(self, route):
		if self.route is None:
			oldName = "<None>"
		else:
			oldName = self.rtName

		if route is None:
			newName = "<None>"
			logging.info("Block %s: route is None" % self.name)
		else:
			newName = route.GetName()

		if oldName == newName:
			return  # no change

		if self.route is not None:
			self.route.ReleaseSignalLocks()  # release locks along the old route
			self.route.RemoveClearStatus()

		self.route = route
		self.rtName = newName

		self.SendRouteRequest()

		if route is None:
			return

		entryBlkName = self.route.GetEntryBlock()
		entryBlk = self.frame.GetBlockByName(entryBlkName)
		exitBlkName = self.route.GetExitBlock()
		exitBlk = self.frame.GetBlockByName(exitBlkName)

		if not entryBlk:
			logging.warning("could not determine entry block for %s/%s from name %s" % (self.name, self.rtName, entryBlkName))
		if not exitBlk:
			logging.warning("could not determine exit block for %s/%s from name %s" % (self.name, self.rtName, exitBlkName))
		if self.east:
			if entryBlk:
				entryBlk.SetNextBlockEast(self)
			self.SetNextBlockWest(entryBlk)
			if exitBlk:
				exitBlk.SetNextBlockWest(self)
			self.SetNextBlockEast(exitBlk)
		else:
			if entryBlk:
				entryBlk.SetNextBlockWest(self)
			self.SetNextBlockEast(entryBlk)
			if exitBlk:
				exitBlk.SetNextBlockEast(self)
			self.SetNextBlockWest(exitBlk)
		self.Draw()
		
	def EvaluateStoppingSections(self):
		return

	def SendRouteRequest(self):
		msg = {
			"setroute": {
				"block": self.GetName(),
				"route": None if self.route is None else self.rtName
			}
		}
		if self.route is not None:
			msg["setroute"]["ends"] = self.route.GetEndPoints()
			msg["setroute"]["signals"] = self.route.GetSignals()
		self.frame.Request(msg)

	def GetExitBlock(self, reverse=False):
		if self.route is None:
			return None

		return self.route.GetExitBlock(reverse)

	def SetSignals(self, signms):
		pass # does not apply to OS blocks

	def GetRoute(self):
		return self.route

	def GetRouteName(self):
		return self.rtName

	def GetRouteType(self):
		if self.route is None:
			return None

		return self.route.GetRouteType()

	def SetEntrySignal(self, sig):
		self.entrySignal = sig
		if self.occupied:
			# do not change the aspect if the block is occupied
			return 
		
		if sig is None:
			asp = 0
		else:
			asp = sig.GetAspect()
		self.SetEntryAspect(asp)
		
		exitBlkName = self.route.GetExitBlock()
		if exitBlkName is None:
			return
		
		exitBlk = self.frame.GetBlockByName(exitBlkName)
		if exitBlk is None:
			return 
		
		exitBlk.SetEntryAspect(asp)
		
	def SetEntryAspect(self, aspect):
		self.entryAspect = aspect

	def GetEntrySignal(self):
		return self.entrySignal

	def HasRoute(self, rtName):
		return rtName == self.rtName

	def IsBusy(self):
		return self.occupied or self.cleared

	def SetOccupied(self, occupied=True, blockend=None, refresh=False):
		Block.SetOccupied(self, occupied, blockend, refresh)
		
		if self.route:
			tolist = self.route.GetLockTurnouts()
			self.district.LockTurnouts(self.name, tolist, occupied)

		if occupied:
			if self.entrySignal is not None:
				signm = self.entrySignal.GetName()
				if self.route:
					exitBlkName = self.route.GetExitBlock()
					exitBlk = self.frame.GetBlockByName(exitBlkName)
					exitBlk.SetEntrySignal(self.entrySignal)
					# lock the entry signal by the exitblock name
					self.entrySignal.SetLock(exitBlkName, 1)
					self.entrySignal.SetFleetPending(self.entrySignal.GetAspect() != 0, exitBlk)
				else:
					self.entrySignal.SetFleetPending(False, None)
				# turn the signal we just passed red, but hold onto the lock to be cleared when we exit the block
				self.frame.Request({"signal": { "name": signm, "aspect": STOP}})
				self.district.LockTurnoutsForSignal(self.GetName(), self.entrySignal, False)
				self.entrySignal = None
		
	def GetTileInRoute(self, screen, pos):
		if self.route is None:
			return False, EMPTY
		elif self.route.Contains(screen, pos):
			return True, self.status

		return False, EMPTY

	def Draw(self):
		for t, screen, pos, revflag in self.tiles:
			draw, stat = self.GetTileInRoute(screen, pos)
			if draw:
				bmp = t.getBmp(stat, self.east, revflag)
				self.frame.DrawTile(screen, pos, bmp)

		for t in self.turnouts:
			draw, stat = self.GetTileInRoute(t.GetScreen(), t.GetPos())
			if draw:
				t.Draw(stat, self.east)

		self.district.DrawOthers(self)
		self.DrawTrain()

	def DrawTurnouts(self):
		for t in self.turnouts:
			t.Draw(EMPTY, self.east)

	def DrawTrain(self):
		if len(self.trainLoc) == 0:
			return

		if self.train is None:
			trainID = "??"
			locoID = "??"
			atc = False
		else:
			trainID, locoID = self.train.GetNameAndLoco()
			atc = self.train.IsOnATC()

		for screen, loc in self.trainLoc:
			if self.occupied:
				self.frame.DrawTrain(screen, loc, trainID, locoID, False, atc)
			else:
				self.frame.ClearTrain(screen, loc)

