import logging

from dispatcher.constants import EMPTY, OCCUPIED, CLEARED, BLOCK, OVERSWITCH, STOPPINGBLOCK, MAIN, STOP, FRONT, REAR
from dispatcher.district import CrossingEastWestBoundary


def formatRouteDesignator(rtName):
	return "" if rtName is None else "{%s}" % rtName[3:]


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
			"ends": ["-" if self.blkin is None else self.blkin, "" if self.blkout is None else self.blkout],
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
	
	def RemoveOccupiedStatus(self):
		for t, screen, pos, revflag in self.osblk.tiles:
			if pos in self.pos:
				bmp = t.getBmp(EMPTY, True, revflag)
				self.osblk.frame.DrawTile(screen, pos, bmp)
	
	def RemoveClearStatus(self):
		if self.osblk.IsReversed():
			b = self.blkin
		else:
			b = self.blkout
		blk = self.osblk.frame.blocks[b]

		if blk.GetBlockType() != OVERSWITCH and blk.GetEast() == self.osblk.GetEast():
			# do NOT clear on an adjacent OS block or if the blocks differ in direction
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
		self.unknownTrain = False
		self.cleared = False
		self.turnouts = []
		self.handswitches = []
		self.train = None
		self.trainLoc = []
		self.blkEast = None
		self.blkWest = None
		self.sbEast = None
		self.sbWest = None
		self.sbSigWest = None
		self.sbSigEast = None
		self.sigWest = None
		self.sigEast = None
		self.route = None
		self.determineStatus()
		self.entrySignal = None
		self.entryAspect = 0
		self.lastSubBlockEntered = None
		self.conditionalTrack = None
		self.dbg = self.frame.GetDebugFlags()

	def SetTrain(self, train):
		self.train = train
		if train is None:
			self.unknownTrain = False
		else:
			self.unknownTrain = train.GetName().startswith("??")

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

	def AddTrainLoc(self, screen, loc, routes=None):
		self.trainLoc.append([screen, loc, routes])

	def IsInActiveRoute(self, col, row):
		# not applicable to normal blocks
		return True

	def AddConditionalTrack(self, trk):
		self.conditionalTrack = trk

	def GetTrain(self):
		return self.train

	def GetTrainLoc(self):
		return self.trainLoc

	def GetTiles(self):
		return self.tiles

	def GetSBTiles(self):
		retval = []
		if self.sbEast:
			retval.extend(self.sbEast.GetTiles())
		if self.sbWest:
			retval.extend(self.sbWest.GetTiles())

		return retval

	def SetSignals(self, sigs):
		self.sigWest = sigs[0]
		self.sigEast = sigs[1]

	def GetSignals(self):
		return self.sigWest, self.sigEast
	
	def GetDirectionSignal(self):
		if self.east:
			return self.sigEast
		else:
			return self.sigWest

	def SetSBSignals(self, sigs):
		self.sbSigWest = sigs[0]
		self.sbSigEast = sigs[1]

	def GetSBSignals(self):
		return self.sbSigWest, self.sbSigEast

	def AddHandSwitch(self, hs):
		self.handswitches.append(hs)

	def AreHandSwitchesSet(self):
		for hs in self.handswitches:
			if hs.GetValue():
				return True
		return False
		
	def HasUnknownTrain(self):
		return self.unknownTrain

	def DrawTrain(self, hilite=False):
		if len(self.trainLoc) == 0:
			return

		if self.train is None:
			trainID = "??"
			locoID = "??"
			atc = False
			ar = False
			sbActive = False
		else:
			trainID, locoID = self.train.GetNameAndLoco()
			sbActive = self.train.GetSBActive()
			atc = self.train.IsOnATC()
			ar = self.train.IsOnAR()

		anyOccupied = self.occupied
		if self.sbEast and self.sbEast.IsOccupied():
			anyOccupied = True
		if self.sbWest and self.sbWest.IsOccupied():
			anyOccupied = True

		for screen, loc, routes in self.trainLoc:
			drawTrain = True  # assume that we draw the train here
			if routes and self.IsOS():
				if self.route is None:
					drawTrain = False  # this OS has no route - do not show a train
				elif self.route.GetName() not in routes:
					drawTrain = False  # the current route through this OS is not in the list
					
			if anyOccupied and drawTrain:
				self.frame.DrawTrain(screen, loc, trainID, locoID, sbActive, atc, ar, hilite)
			elif drawTrain:  # don't clear trains from alternate routes that are not surrently set
				self.frame.ClearTrain(screen, loc)

	def StoppingRelayActivated(self):
		active = False
		if self.sbEast and self.sbEast.IsActive():
			active = True
		if self.sbWest and self.sbWest.IsActive():
			active = True
		return active

	def SetStoppingRelays(self, flag=False, force=False):
		if self.sbEast and (self.sbEast.IsActive() or force):
			self.sbEast.Activate(flag)
		if self.sbWest and (self.sbWest.IsActive() or force):
			self.sbWest.Activate(flag)
	
	def SetLastEntered(self, subblk):
		self.lastSubBlockEntered = subblk

	def DrawTurnouts(self):
		pass

	def Reset(self):
		if self.IsOccupied() or self.IsCleared():
			# do not reset the block under a train
			return 
		
		self.SetEast(self.defaultEast)
		self.SetLastEntered(None)
		
	def ForceUnCleared(self):
		if self.IsCleared():
			self.cleared = False
			self.determineStatus()
			self.Draw()

	def SetNextBlockEast(self, blk):
		self.blkEast = blk

	def SetNextBlockWest(self, blk):
		self.blkWest = blk

	def determineStatus(self):
		self.status = OCCUPIED if self.occupied else CLEARED if self.cleared else EMPTY
		if self.occupied:
			if self.train is None:
				self.unknownTrain = False
			else:
				tn = self.train.GetName()
				if tn is None:
					self.unknownTrain = False
				else:
					self.unknownTrain = tn.startswith("??")

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

	def GetRouteDesignator(self):
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

	def GetDefaultEast(self):
		return not self.defaultEast

	def SetEast(self, east, broadcast=True):
		if self.east == east:
			return

		self.east = east
		self.Draw()
		if broadcast:
			self.frame.Request({"blockdir": {"block": self.GetName(), "dir": "E" if east else "W"}})
			for b in [self.sbEast, self.sbWest]:
				if b is not None:
					self.frame.Request({"blockdir": {"block": b.GetName(), "dir": "E" if east else "W"}})

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
	
	def IsOS(self):
		return self.type == OVERSWITCH

	def Draw(self):
		for t, screen, pos, revflag in self.tiles:
			forceEmpty = False
			if self.conditionalTrack:
				if pos in self.conditionalTrack:
					forceEmpty = not self.EvaluateTurnout(self.conditionalTrack[pos])
			bmp = t.getBmp(EMPTY if forceEmpty else self.status, self.east, revflag, unknownTrain=self.unknownTrain)
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

	def GetTurnoutLocations(self):
		retval = []
		for t in self.turnouts:
			retval.append(t.GetScreenPos())
		return retval

	def EvaluateTurnout(self, toinfo):
		toName, toStatus = toinfo
		for to in self.turnouts:
			if toName == to.GetName():
				s = "N" if to.IsNormal() else "R" if to.IsReverse() else None
				return s == toStatus

		return False

	def SetOccupied(self, occupied=True, blockend=None, refresh=False):
		if not occupied:
			self.SetLastEntered(None)

		if blockend in ["E", "W"]:
			b = self.sbEast if blockend == "E" else self.sbWest
			if b is None:
				logging.warning("Stopping block %s not defined for block %s" % (blockend, self.GetName()))
				return
			b.SetOccupied(occupied, refresh)
			if occupied and self.train is None and self.frame.IsDispatcher():
				tr, rear = self.IdentifyTrain(b.IsCleared())
				if tr is None:
					self.frame.SendAlertRequest("Unable to identify train detected in block %s" % self.GetName())

					tr = self.frame.NewTrain()
					# new trains take on the direction of the block
					east = self.GetEast()
					tr.SetEast(east)
				else:
					# known trains push their direction onto the block
					east = tr.GetEast()
					self.SetEast(east)

				trn, loco = tr.GetNameAndLoco()
				self.SetTrain(tr)
				stParams = {"blocks": [self.GetName()], "name": trn, "loco": loco, "east": "1" if east else "0", "action": REAR if rear else FRONT}
				rt = tr.GetChosenRoute()
				if rt is not None:
					stParams["route"] = rt
				req = {"settrain": stParams}
				self.frame.Request(req)
			if refresh:
				self.Draw()
			return

		if self.occupied == occupied:
			# already in the requested state - refresh anyway
			if refresh:
				self.Draw()
			return

		self.occupied = occupied
		if self.occupied:
			previouslyCleared = self.cleared
			self.cleared = False
			self.frame.Request({"blockclear": {"block": self.GetName(), "clear": 0}})

			if self.train is None and self.frame.IsDispatcher():
				tr, rear = self.IdentifyTrain(previouslyCleared)
				if tr is None:
					self.frame.SendAlertRequest("Unable to identify train detected in block %s" % self.GetName())

					tr = self.frame.NewTrain()
					# new trains take on the direction of the block
					east = self.GetEast()
					tr.SetEast(east)
				else:
					# known trains push their direction onto the block
					east = tr.GetEast()
					self.SetEast(east)					

				trn, loco = tr.GetNameAndLoco()
				self.SetTrain(tr)
				stParams = {"blocks": [self.GetName()], "name": trn, "loco": loco, "east": "1" if east else "0", "action": REAR if rear else FRONT}
				rt = tr.GetChosenRoute()
				if rt is not None:
					stParams["route"] = rt
				req = {"settrain": stParams}
				self.frame.Request(req)
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
			self.frame.Request({"settrain": {"blocks": [self.GetName()], "name": None, "loco": None}})

		self.train = None
		self.EvaluateStoppingSections()
		if self.type == OVERSWITCH and self.entrySignal is not None:
			signm = self.entrySignal.GetName()
			atype = self.entrySignal.GetAspectType()
			self.frame.Request({"signal": {"name": signm, "aspect": STOP, "aspecttype": atype}})
			self.entrySignal.SetLock(self.GetName(), 0)

		self.frame.DoFleetPending(self)

	def GetStoppingSections(self):
		return self.sbWest, self.sbEast

	def EvaluateStoppingSections(self):
		if self.east and self.sbEast:
			self.sbEast.EvaluateStoppingSection()
		elif (not self.east) and self.sbWest:
			self.sbWest.EvaluateStoppingSection()

	def IdentifyTrain(self, cleared):
		"""
		returns the identified train, or NOne if no traiun identified
		Also return False if this block is to be added to the front of the train, True otherwise
		"""
		if self.dbg.identifytrain:
			self.frame.DebugMessage("========New Train Identification========")
			self.frame.DebugMessage("Attempting to identify train in block %s" % self.GetName())
		# =======================================================================
		# uncomment the following code to not identify trains that cross into a block against the signal
		#
		# if self.type == OVERSWITCH:
		# 	if not cleared:
		# 		# should not be entering an OS block without clearance
		# 		return None, False
		# =======================================================================
			
		if self.east:
			'''
			first look west, then east, then create a new train
			'''
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Eastbound block - look west first")
			if self.blkWest:
				if self.blkWest.GetName() in ["KOSN10S11", "KOSN20S21"]:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkWest = self.blkWest.blkWest
					if blkWest:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Using block %s instead of null block" % blkWest.GetName())
						tr = blkWest.GetTrain()
						if tr:
							self.CheckEWCross(tr, blkWest)
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Returning train %s" % tr.GetName())
							# so we found a train coming from the west - so it is moving east
							# so if it is an eastbound train we are adding to the front - else to the rear
							return tr, not tr.GetEast()
						else:
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Block %s did not have a train to consider" % blkWest.GetName())
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("No block west to examine")
				else:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Looking at block %s" % self.blkWest.GetName())
					tr = self.blkWest.GetTrain()
					if tr:
						self.CheckEWCross(tr, self.blkWest)
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Returning train %s" % tr.GetName())
						# so we found a train coming from the west - so it is moving east
						# so if it is an eastbound train we are adding to the front - else to the rear
						return tr, not tr.GetEast()
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Block %s did not have a train to consider" % self.blkWest.GetName())

			if self.dbg.identifytrain:
				self.frame.DebugMessage("Eastbound block - nothing found west - now look east")
			if self.blkEast:
				if self.blkEast.GetName() in ["KOSN10S11", "KOSN20S21"]:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkEast = self.blkEast.blkEast
					if blkEast:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Using block %s instead of null block" % blkEast.GetName())
						tr = blkEast.GetTrain()
						if tr:
							self.CheckEWCross(tr, blkEast)
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Returning train %s rear" % tr.GetName())
							# so we found a train coming from the east - so it is moving west
							# so if it is a westbound train we are adding to the front - else to the rear
							return tr, tr.GetEast()
						else:
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Block %s did not have a train to consider" % blkEast.GetName())
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("No block east to examine")

				else:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Looking at block %s" % self.blkEast.GetName())
					tr = self.blkEast.GetTrain()
					if tr:
						self.CheckEWCross(tr, self.blkEast)
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Returning train %s rear" % tr.GetName())
						# so we found a train coming from the east - so it is moving west
						# so if it is a westbound train we are adding to the front - else to the rear
						return tr, tr.GetEast()
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Block %s did not have a train to consider" % self.blkEast.GetName())

		else:
			'''
			first look east, then west, then create a new train
			'''
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Westbound block - look east first")
			if self.blkEast:
				if self.blkEast.GetName() in ["KOSN10S11", "KOSN20S21"]:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkEast = self.blkEast.blkEast
					if blkEast:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Using block %s instead of null block" % blkEast.GetName())
						tr = blkEast.GetTrain()
						if tr:
							self.CheckEWCross(tr, blkEast)
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Returning train %s" % tr.GetName())
							# so we found a train coming from the east - so it is moving west
							# so if it is a westbound train we are adding to the front - else to the rear
							return tr, tr.GetEast()
						else:
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Block %s did not have a train to consider" % blkEast.GetName())
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("No block east to examine")

				else:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Looking at block %s" % self.blkEast.GetName())
					tr = self.blkEast.GetTrain()
					if tr:
						self.CheckEWCross(tr, self.blkEast)
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Returning train %s" % tr.GetName())
						# so we found a train coming from the east - so it is moving west
						# so if it is a westbound train we are adding to the front - else to the rear
						return tr, tr.GetEast()
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Block %s did not have a train to consider" % self.blkEast.GetName())

			if self.dbg.identifytrain:
				self.frame.DebugMessage("Westbound block - nothing found east - now look west")
			if self.blkWest:
				if self.blkWest.GetName() in ["KOSN10S11", "KOSN20S21"]:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkWest = self.blkWest.blkWest
					if blkWest:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Using block %s instead of null block" % blkWest.GetName())
						tr = blkWest.GetTrain()
						if tr:
							self.CheckEWCross(tr, blkWest)
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Returning train %s rear" % tr.GetName())
							# so we found a train coming from the west - so it is moving east
							# so if it is an eastbound train we are adding to the front - else to the rear
							return tr, not tr.GetEast()
						else:
							if self.dbg.identifytrain:
								self.frame.DebugMessage("Block %s did not have a train to consider" % blkWest.GetName())
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("No block west to examine")

				else:
					if self.dbg.identifytrain:
						self.frame.DebugMessage("Looking at block %s" % self.blkWest.GetName())
					tr = self.blkWest.GetTrain()
					if tr:
						self.CheckEWCross(tr, self.blkWest)
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Returning train %s rear" % tr.GetName())
						# so we found a train coming from the west - so it is moving east
						# so if it is an eastbound train we are adding to the front - else to the rear
						return tr, not tr.GetEast()
					else:
						if self.dbg.identifytrain:
							self.frame.DebugMessage("Block %s did not have a train to consider" % self.blkWest.GetName())

		if self.dbg.identifytrain:
			self.frame.DebugMessage("Unable to identify a train")

		return None, False
		
	def CheckEWCross(self, tr, blk):
		if self.type == OVERSWITCH:
			rc = CrossingEastWestBoundary(self, blk)
		else:
			rc = CrossingEastWestBoundary(blk, self)
		if rc:
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Train %s crossed an E/W boundary - reversing train direction" % tr.GetName())
			tr.SetEast(not tr.GetEast())
			self.frame.Request({"renametrain": {"oldname": tr.GetName(), "newname": tr.GetName(), "east": "1" if tr.GetEast() else "0"}})

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
		self.frame.Request({"blockclear": {"block": self.GetName(), "clear": 1 if cleared else 0}})

		if refresh:
			self.Draw()

		for b in [self.sbEast, self.sbWest]:
			if b is not None:
				b.SetCleared(cleared, refresh)
				
	def RemoveClearStatus(self):
		# if self.name == "C13":
		# 	return  # do not do this on single track
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


class StoppingBlock:  # (Block):
	def __init__(self, block, tiles, eastend):
		self.block = block
		self.east = False
		self.tiles = tiles
		self.eastend = eastend
		self.type = STOPPINGBLOCK
		self.frame = self.block.frame
		self.status = None
		self.active = False
		self.occupied = False
		self.cleared = False
		self.determineStatus()
		self.lastSignalGreen = False
		self.lastBlockEmpty = False

	def EvaluateStoppingSection(self):
		if (self.block.east and (not self.eastend)) or ((not self.block.east) and self.eastend):
			# wrong end of the block - assert stopping section is inactive
			self.Activate(False)
			return
		
		if not self.occupied:
			logging.debug("Deactivating stopping block %s because block is not occupied" % self.GetName())
			self.Activate(False)
			return
		
		mainBlk = self.block
		# district = self.block.GetDistrict()
		bname = self.block.GetName()
		direction = "East" if self.eastend else "West"

		blk = self.block.blkEast if self.block.east else self.block.blkWest
		if blk is None:
			logging.debug("no known exit block from %s" % mainBlk.GetName())
			# we don't know the exit block - this means the OS is set to a different
			# route and the signal should be red - assert that stopping block is active
			logging.debug("===activating stopping relay for block %s %s because unable to identify next block" % (bname, direction))
			self.Activate(True)
			return

		signm = self.block.sbSigEast if self.block.east else self.block.sbSigWest
		if not signm:
			logging.debug("No action on stopping block because no signal identified")
			return 
		
		logging.debug("evaluate stopping section, %s -> %s" % (mainBlk.GetName(), blk.GetName()))
		
		# identify the train that is in this block
		tr = self.block.GetTrain()
		if tr is None:
			logging.debug("no train identified in current block %s" % self.block.GetName())
			return
		
		logging.debug("train %s" % tr.GetName())
		
		# identify the train that is in the next block
		trnext = blk.GetTrain()
		
		if trnext:
			logging.debug("train next = %s" % tr.GetName())
		
		if trnext and tr.GetName() == trnext.GetName():
			# the same train is in the stopping section and the exit block - this is normal Condition
			# and the stopping section is irrelevant - assert that it's inactive
			self.Activate(False)
			return
		
		elif trnext is not None:
			# there is some other train in the next block - the signal should be red
			logging.debug("===activating stopping relay for block %s %s because train ahead = %s and this train = %s" % (bname, direction, tr.GetName(), trnext.GetName()))
			logging.debug("blocks for train %s = %s" % (tr.GetName(), ",".join(tr.GetBlockNameList())))
			self.Activate(True)
			return
		
		# in all other cases, activate based solely on the signal value
		sv = self.frame.GetSignalByName(signm).GetAspect()

		# activate the stopping block if the signal is red, deactivate if not
		if sv == 0:
			logging.debug("===activating stopping relay for block %s %s because signal aspect = %x" % (bname, direction, sv))
			logging.debug("blocks for train %s = %s" % (tr.GetName(), ",".join(tr.GetBlockNameList())))
		self.Activate(sv == 0)

	def Activate(self, flag=True):
		if flag == self.active:
			return

		tr = self.block.GetTrain()
		if tr is None:
			tname = "??"
		else:
			tname = tr.GetName()
			tr.SetSBActive(flag)
			self.frame.activeTrains.UpdateTrain(tname)
			
		direction = "East" if self.eastend else "West"

		self.active = flag

		self.frame.Request({"relay": {"block": self.block.GetName(), "state": 1 if flag else 0, "direction": direction, "train": tname}})

		if tr is None:
			self.block.DrawTrain()
		else:
			tr.Draw()

	def IsActive(self):
		return self.active

	def Draw(self):
		self.east = self.block.east
		# self.frame.Request({"blockdir": { "block": self.GetName(), "dir": "E" if self.east else "W"}})
		for t, screen, pos, revflag in self.tiles:
			bmp = t.getBmp(self.status, self.east, revflag, unknownTrain=self.block.unknownTrain)
			self.frame.DrawTile(screen, pos, bmp)

	def determineStatus(self):
		self.status = OCCUPIED if self.occupied else CLEARED if self.cleared else EMPTY

	def GetStatus(self):
		self.determineStatus()
		return self.status

	def GetRouteType(self):
		return self.block.GetRouteType()

	def GetTiles(self):
		return self.tiles

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

	@staticmethod
	def GetDistrict():
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

		self.frame.Request({"blockclear": {"block": self.GetName(), "clear": 1 if cleared else 0}})
		self.cleared = cleared
		self.determineStatus()
		if refresh:
			self.Draw()

	def IsCleared(self):
		return self.cleared

	def RemoveClearStatus(self):
		self.cleared = False
		self.determineStatus()
		self.Draw()

	def SetLastEntered(self, subblk):
		self.block.SetLastEntered(subblk)

	def SetOccupied(self, occupied=True, blockend=None, refresh=False):
		if self.occupied == occupied:
			# already in the requested state
			return

		self.occupied = occupied
		if self.occupied:
			self.frame.Request({"blockclear": {"block": self.GetName(), "clear": 0}})
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


class OSProxy:
	def __init__(self, district, name):
		self.district = district
		self.name = name
		self.occupied = False
		self.routes = {}
		self.osList = ()
		
	def GetDistrict(self):
		return self.district

	def GetName(self):
		return self.name
		
	def SetOccupied(self, flag=True):
		self.occupied = flag
		
	def IsOccupied(self):
		return self.occupied
		
	def AddRoute(self, route):
		self.routes[route.GetName()] = route
		self.osList = set(route.GetOS() for route in self.routes.values())
		
	def HasRoute(self, rtnm):
		return rtnm in self.routes
	
	def Evaluate(self):
		routeName = None
		osName = None
		rlist = self.routes.keys()
		for osb in self.osList:
			rte = osb.GetRoute()
			if rte is not None:
				rtname = rte.GetName()
				if rtname in rlist:
					routeName = rtname
					osName = rte.GetOSName()
					
		return routeName, self.occupied, osName
	
	def __str__(self):
		rtes = []
		rlist = self.routes.keys()
		for osb in self.osList:
			rte = osb.GetRoute()
			if rte is not None:
				rtname = rte.GetName()
				if rtname in rlist:
					rtes.append(rtname)
		o = "True" if self.occupied else "False"
		orlist = ", ".join(rtes)
		return f'OS: {self.name} occupied: {o} OS routes: {orlist}'
		
		
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
		else:
			newName = route.GetName()
			
		if oldName == newName:
			return  # no change

		if self.route is not None:
			self.route.ReleaseSignalLocks()  # release locks along the old route
			# this should never affect the appearance on other blocks.
			# self.route.RemoveClearStatus()
			self.route.RemoveOccupiedStatus()

		self.route = route
		self.rtName = newName

		self.SendRouteRequest()

		if route is None:
			return

		entryBlkName = self.route.GetEntryBlock()
		entryBlk = self.frame.GetBlockByName(entryBlkName)
		exitBlkName = self.route.GetExitBlock()
		exitBlk = self.frame.GetBlockByName(exitBlkName)

		if entryBlkName is not None and entryBlk is None:
			logging.warning("could not determine entry block for %s/%s from name %s" % (self.name, self.rtName, entryBlkName))
			
		if exitBlkName is not None and exitBlk is None:
			logging.warning("could not determine exit block for %s/%s from name %s" % (self.name, self.rtName, exitBlkName))
			
		if self.east:
			if entryBlk:
				if CrossingEastWestBoundary(self, entryBlk):
					entryBlk.SetNextBlockWest(self)
				else:
					entryBlk.SetNextBlockEast(self)
			self.SetNextBlockWest(entryBlk)
			if exitBlk:
				if CrossingEastWestBoundary(self, exitBlk):
					exitBlk.SetNextBlockEast(self)
				else:
					exitBlk.SetNextBlockWest(self)
			self.SetNextBlockEast(exitBlk)
		else:
			if entryBlk:
				if CrossingEastWestBoundary(self, entryBlk):
					entryBlk.SetNextBlockEast(self)
				else:
					entryBlk.SetNextBlockWest(self)
			self.SetNextBlockEast(entryBlk)
			if exitBlk:
				if CrossingEastWestBoundary(self, exitBlk):
					exitBlk.SetNextBlockWest(self)
				else:
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
			msg["setroute"]["ends"] = ["-" if e is None else e for e in self.route.GetEndPoints()]
			msg["setroute"]["signals"] = self.route.GetSignals()
		self.frame.Request(msg)

	def GetExitBlock(self, reverse=False):
		if self.route is None:
			return None

		return self.route.GetExitBlock(reverse)

	def GetEntryBlock(self, reverse=False):
		if self.route is None:
			return None

		return self.route.GetEntryBlock(reverse)

	def GetRoute(self):
		return self.route

	def IsInActiveRoute(self, col, row):
		for _, loc, rte in self.trainLoc:
			if rte is None:
				# if the route list is NOne, it is an unconditional train location
				return True

			if loc[0] == col and loc[1] == row and self.rtName in rte:
				return True

		return False

	def GetRouteName(self):
		return self.rtName

	def GetRouteDesignator(self):
		if self.route is None:
			return self.GetName()
		else:
			return formatRouteDesignator(self.GetRouteName())

	def GetRouteType(self, reverse=False):
		if self.route is None:
			return None

		return self.route.GetRouteType(reverse=reverse)

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
		if occupied == self.IsOccupied():
			return  # we're already in the desired state
		
		Block.SetOccupied(self, occupied, blockend, refresh)
		
		if self.route:
			tolist = self.route.GetLockTurnouts()
			self.district.LockTurnouts(self.name, tolist, occupied)
			rtName = self.route.GetName()
		else:
			rtName = None

		if occupied:
			if self.entrySignal is not None:
				signm = self.entrySignal.GetName()
				atype = self.entrySignal.GetAspectType()
				aspect = self.entrySignal.GetAspect()
				if self.route:
					exitBlkName = self.route.GetExitBlock()
					exitBlk = self.frame.GetBlockByName(exitBlkName)
					exitBlk.SetEntrySignal(self.entrySignal)
					
					# lock the entry signal by the exitblock name

					# self.entrySignal.SetLock(exitBlkName, 1)
					self.entrySignal.SetLock(self.name, 1)
					self.entrySignal.SetFleetPending(self.entrySignal.GetAspect() != 0, self, rtName, exitBlk)
				else:
					self.entrySignal.SetFleetPending(False, self, None, None)
				# turn the signal we just passed red, but hold onto the lock to be cleared when we exit the block
				# also retain the old aspect, used to govern train speed
				self.entrySignal.SetFrozenAspect(aspect)
				self.frame.Request({"signal": {"name": signm, "aspect": STOP, "aspecttype": atype, "frozenaspect": aspect}})
				tr = self.GetTrain()
				if tr is not None:
					self.frame.activeTrains.UpdateTrain(tr.GetName())
				self.district.LockTurnoutsForSignal(self.GetName(), self.entrySignal, False)
		else:
			if self.route and self.entrySignal is not None:
				self.district.EvaluateDistrictLocks(self.entrySignal)
			if self.entrySignal is not None and self.entrySignal.GetFrozenAspect() is not None:
				atype = self.entrySignal.GetAspectType()
				aspect = self.entrySignal.GetAspect()
				self.entrySignal.SetFrozenAspect(None)
				self.frame.Request({"signal": {"name": self.entrySignal.GetName(), "aspect": aspect, "aspecttype": atype, "frozenaspect": None}})
				tr = self.GetTrain()
				if tr is not None:
					self.frame.activeTrains.UpdateTrain(tr.GetName())
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
				bmp = t.getBmp(stat, self.east, revflag, unknownTrain=self.unknownTrain)
				self.frame.DrawTile(screen, pos, bmp)

		for t in self.turnouts:
			draw, stat = self.GetTileInRoute(t.GetScreen(), t.GetPos())
			if draw:
				t.SetContainingBlock(self)
				t.Draw(stat, self.east)

		self.district.DrawOthers(self)
		self.DrawTrain()

	def DrawTurnouts(self):
		for t in self.turnouts:
			t.Draw(EMPTY, self.east)
