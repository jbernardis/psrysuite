import logging

from dispatcher.constants import RegAspects, RegSloAspects, AdvAspects, SloAspects, \
	MAIN, SLOW, DIVERGING, RESTRICTING, \
	CLEARED, OCCUPIED, EMPTY, STOP, NORMAL, OVERSWITCH
	
EWCrossoverPoints = [
	["COSSHE", "C20"],
	["YOSCJE", "P50"],
	["YOSCJW", "P50"],
	["POSSJ1", "P30"],
	["SOSE",   "P32"],
	["SOSW",   "P32"],
	["YOSKL4", "Y30"],
	["YOSKL1", "Y70"],
	["YOSKL2", "Y70"]
]

def statusname(status):
	if status == EMPTY:
		return "EMPTY"
	
	elif status == "OCCUPIED":
		return "OCCUPIED"
	
	elif status == CLEARED:
		return "CLEARED"
	
	else:
		return "None"

def aspectname(aspect, atype):
	if atype == RegAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Medium Clear"

		elif aspect == 0b110:
			return "Approach Slow"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == RegSloAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b111:
			return "Slow clear"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Slow Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == AdvAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Clear"

		elif aspect == 0b110:
			return "Advance Approach"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == SloAspects:
		if aspect == 0b01:
			return "Slow Clear"

		elif aspect == 0b11:
			return "Slow Approach"

		elif aspect == 0b10:
			return "Restricting"

		else:
			return "Stop"

	else:
		return "Stop"
	
def restrictedaspect(atype):
	if atype == SloAspects:
		return 0b10
	else:
		return 0b100

def aspecttype(atype):
	if atype == RegAspects:
		return "RegAspects"
	if atype == RegSloAspects:
		return "RegSloAspects"
	if atype == AdvAspects:
		return "AdvAspects"
	if atype == SloAspects:
		return "SloAspects"
	return "unknown aspect type"
		
		
def routetype(rtype):
	if rtype == MAIN:
		return "MAIN"
	if rtype == DIVERGING:
		return "DIVERGING"
	if rtype == SLOW:
		return "SLOW"
	if rtype == RESTRICTING:
		return "RESTRICTING"
	
def statustype(stat):
	if stat == CLEARED:
		return "CLEARED"
	else:
		return "NOT CLEARED"
	

class District:
	def __init__(self, name, frame, screen):
		self.sigLeverMap = None
		self.routes = None
		self.osSignals = None
		self.handswitches = None
		self.buttons = None
		self.osButtons = None
		self.signals = None
		self.indicators = None
		self.turnouts = None
		self.osBlocks = None
		self.blocks = None
		self.tiles = None
		self.totiles = None
		self.sigtiles = None
		self.misctiles = None
		self.sstiles = None
		self.btntiles = None
		self.name = name
		self.frame = frame
		self.screen = screen
		self.eastGroup = {}
		self.westGroup = {}
		self.eastButton = {}
		self.westButton = {}
		logging.info("Creating district %s" % name)

	def SetTiles(self, tiles, totiles, sstiles, sigtiles, misctiles, btntiles):
		self.tiles = tiles
		self.totiles = totiles
		self.sstiles = sstiles
		self.sigtiles = sigtiles
		self.misctiles = misctiles
		self.btntiles = btntiles

	def Initialize(self):
		blist = [self.frame.GetBlockByName(n) for n in self.osBlocks.keys()]
		self.DetermineRoute(blist)

	def OnConnect(self):
		pass

	def Draw(self):
		for b in self.blocks.values():
			b.Draw()
			b.DrawTurnouts()
		for b in self.buttons.values():
			b.Draw()
		for s in self.signals.values():
			s.Draw()
		for h in self.handswitches.values():
			h.Draw()

	def DrawOthers(self, block):
		pass

	def DetermineRoute(self, blocks):
		pass

	#  Perform... routines handle the user clicking on track diagram components.  This includes, switches, signals,
	#  and buttons
	#  in most cases, this does not actually make any changed to the display, but instead sends
	#  requests to the dispatch server
	def PerformButtonAction(self, btn):
		pass

	def DoEntryExitButtons(self, btn, groupName, sendButtons=False, interval = 0):
		bname = btn.GetName()
		if self.westButton[groupName] and not self.westButton[groupName].IsPressed():
			self.westButton[groupName] = None
		if self.eastButton[groupName] and not self.eastButton[groupName].IsPressed():
			self.eastButton[groupName] = None

		if bname in self.westGroup[groupName]:
			if self.westButton[groupName]:
				self.frame.ClearButtonNow(self.westButton[groupName])

			btn.Press(refresh=True)
			self.westButton[groupName] = btn
			self.frame.ClearButtonAfter(5, btn)

		if bname in self.eastGroup[groupName]:
			if self.eastButton[groupName]:
				self.frame.ClearButtonNow(self.eastButton[groupName])

			btn.Press(refresh=True)
			self.eastButton[groupName] = btn
			self.frame.ClearButtonAfter(5, btn)

		wButton = self.westButton[groupName]
		eButton = self.eastButton[groupName]
		if wButton and eButton:
			self.frame.ResetButtonExpiry(2, wButton)
			self.frame.ResetButtonExpiry(2, eButton)
			try:
				rtName = self.NXMap[wButton.GetName()][eButton.GetName()]
				toList = self.routes[rtName].GetSetTurnouts()
			except KeyError:
				toList = None

			if toList is None or self.anyTurnoutLocked(toList):
				wButton.Invalidate(refresh=True)
				eButton.Invalidate(refresh=True)
				self.frame.PopupEvent("No available route" if toList is None else "Route locked out")

			else:
				wButton.Acknowledge(refresh=True)
				eButton.Acknowledge(refresh=True)
				if sendButtons:
					self.frame.Request({"nxbutton": { "entry": wButton.GetName(),  "exit": eButton.GetName()}})
				else:
					self.MatrixTurnoutRequest(toList, interval = interval)

			self.westButton[groupName] = None
			self.eastButton[groupName] = None

	def FindTurnoutCombinations(self, blocks, turnouts):
		# This maps OS name to new route.  Initially assume None for all OSes
		rteMap = {os.GetName(): None for os in blocks if os.GetBlockType() == OVERSWITCH}
		toMap = [[x, 'N' if self.turnouts[x].IsNormal() else 'R'] for x in turnouts]

		for rte in self.routes.values():
			osName = rte.GetOSName()
			if osName in rteMap:
				rteSet = rte.GetSetTurnouts()
				if all(x in toMap for x in rteSet):
					rteMap[osName] = rte
		
		for osn, rte in rteMap.items():
			if rte is None:
				self.blocks[osn].SetRoute(None)
		for osn, rte in rteMap.items():
			if rte is not None:
				self.blocks[osn].SetRoute(rte)

	def MatrixTurnoutRequest(self, tolist, interval = 0):
		first = True
		delay = interval
		for toname, state in tolist:
			if (state == "R" and self.turnouts[toname].IsNormal()) or \
					(state == "N" and self.turnouts[toname].IsReverse()):
				req = {"turnout": {"name": toname, "status": state}}
				if not first and interval != 0:
					req["turnout"]["delay"] = delay
					delay += interval
					
				first = False
				self.frame.Request(req)

	def PerformTurnoutAction(self, turnout, force=False):
		turnout = turnout.GetControlledBy()
		if turnout.IsLocked() and not force:
			self.ReportTurnoutLocked(turnout.GetName())
			return

		if turnout.IsNormal():
			self.frame.Request({"turnout": {"name": turnout.GetName(), "status": "R", "force": force}})
		else:
			self.frame.Request({"turnout": {"name": turnout.GetName(), "status": "N", "force": force}})

	def FindRoute(self, sig):
		signm = sig.GetName()
		# print("find route for signal %s" % signm)
		# print("possible routes: %s" % json.dumps(sig.possibleRoutes))
		for blknm, siglist in self.osSignals.items():
			# print("block, sigs = %s %s" % (blknm, str(siglist)))
			if signm in siglist:
				osblk = self.frame.blocks[blknm]
				#osblknm = blknm
				rname = osblk.GetRouteName()
				# print("os: %s route: %s" % (osblknm, str(rname)))
				if osblk.route is None:
					continue

				rt = self.routes[rname]
				if sig.IsPossibleRoute(blknm, rname):
					# print("good route")
					return rt, osblk
				# print("not a possible route")

		# print("no route found")
		return None, None

	def PerformSignalAction(self, sig, callon=False):
		currentMovement = sig.GetAspect() != 0  # does the CURRENT signal status allow movement
		signm = sig.GetName()
		rt, osblk = self.FindRoute(sig)

		if callon:
			aspect = 0 if currentMovement else restrictedaspect(sig.GetAspectType())
		else:
			if rt is None:
				self.frame.PopupEvent("No available route")
				return False
	
			if osblk.AreHandSwitchesSet():
				self.frame.PopupEvent("Block %s siding(s) unlocked" % osblk.GetName())
				return False
	
			# this is a valid signal for the current route	
			if not currentMovement:  # we are trying to change the signal to allow movement
				aspect = self.CalculateAspect(sig, osblk, rt)
				if aspect is None:
					return False
	
			else:  # we are trying to change the signal to stop the train
				esig = osblk.GetEntrySignal()
				if esig is not None and esig.GetName() != signm:
					self.frame.PopupEvent("Incorrect signal for current route  %s not = %s" % (esig.GetName(), signm))
					return False
				aspect = 0

		self.frame.Request({"signal": {"name": signm, "aspect": aspect, "callon": 1 if callon else 0}})
		
		if not callon:
			sig.SetLock(osblk.GetName(), 0 if aspect == 0 else 1)
			
		return True
	
	def FindBlockForSignal(self, sigName):
		for blkName, sigList in self.frame.blocksignals.items():
			if sigName in sigList:
				return blkName

	def CalculateAspect(self, sig, osblk, rt, silent=False):
		logging.debug("Calculating aspect for signal %s route %s" % (sig.GetName(), rt.GetName()))
		
		if osblk.IsBusy():
			if not silent:
				self.frame.PopupEvent("Block %s is busy" % osblk.GetName())
			logging.debug("Unable to calculate aspect: OS Block is busy")
			return None
		

		msg = []
		sigName = sig.GetName()
		startBlockName = self.FindBlockForSignal(sigName)
		startBlock = self.frame.blocks[startBlockName]
		msg.append("starting block: %s" % startBlockName)
		msg.append("OS: %s Rte: %s  Sig: %s  SigE: %s" % (osblk.GetName(), rt.GetName(), sig.GetName(), sig.GetEast()))
		currentDirection = sig.GetEast()
		
		msg.append("current movement is %s" % currentDirection)
		msg.append("check %s/%s" % (osblk.GetName(), startBlockName))
		if self.CrossingEastWestBoundary(osblk, startBlock):
			currentDirection = not currentDirection
			msg.append("Crossing EW boundary between %s and %s - direction now %s" % (osblk.GetName(), startBlockName, currentDirection))
		
			
		exitBlkNm = rt.GetExitBlock(reverse = currentDirection!=osblk.GetEast())
		rType = rt.GetRouteType(reverse = currentDirection!=osblk.GetEast())
		msg.append("exit block name = %s  Route Type = %s" % (exitBlkNm, routetype(rType)))

		exitBlk = self.frame.blocks[exitBlkNm]
		if exitBlk.IsOccupied():
			self.frame.PopupEvent("Block %s is busy" % exitBlk.GetName())
			logging.debug("Unable to calculate aspect: Block %s is busy" % exitBlkNm)
			return None

		msg.append("check %s/%s" % (osblk.GetName(), exitBlkNm))
		if self.CrossingEastWestBoundary(osblk, exitBlk):
			currentDirection = not currentDirection
			msg.append("Crossing EW boundary between %s and %s - direction now %s" % (osblk.GetName(), exitBlkNm, currentDirection))
			
		if exitBlk.IsCleared():
			if exitBlk.GetEast() != currentDirection:
				self.frame.PopupEvent("Block %s is cleared in opposite direction" % exitBlk.GetName())
				logging.debug("Unable to calculate aspect: Block %s cleared in opposite direction" % exitBlkNm)
				return None

		if exitBlk.AreHandSwitchesSet():
			self.frame.PopupEvent("Block %s is locked" % exitBlk.GetName())
			logging.debug("Unable to calculate aspect: Block %s is locked" % exitBlkNm)
			return None

		nxe, nxw = exitBlk.GetAdjacentBlocks()
		msg.append("Next East = %s, west = %s" % ("None" if nxe is None else nxe.GetName(), "None" if nxw is None else nxw.GetName()))

		
		nb = exitBlk.NextBlock(reverse = currentDirection!=exitBlk.GetEast())
		if nb:
			nbName = nb.GetName()
			msg.append("check %s/%s" % (nbName, exitBlkNm))
			if self.CrossingEastWestBoundary(nb, exitBlk):
				currentDirection = not currentDirection
				msg.append("Crossing EW boundary between %s and %s - direction now %s" % (nbName, exitBlkNm, currentDirection))
			
			nbStatus = nb.GetStatus()
			nbRType = nb.GetRouteType()
			# try to go one more block, skipping past an OS block

			nxbNm = nb.GetExitBlock(reverse = currentDirection!=nb.GetEast())
			if nxbNm is None:
				nnb = None
			else:
				msg.append("nxbnm = %s" % nxbNm)
				try:
					nxb = self.frame.blocks[nxbNm]
				except:
					nxb = None
				if nxb:
					msg.append("check %s/%s" % (nbName, nxbNm))
					if self.CrossingEastWestBoundary(nb, nxb):
						currentDirection = not currentDirection
						msg.append("Crossing EW boundary between %s and %s - direction now %s" % (nbName, nxbNm, currentDirection))
					nnb = nxb.NextBlock(reverse = currentDirection!=nxb.GetEast())
				else:
					nnb = None

			if nnb:
				nnbClear = nnb.GetStatus() == CLEARED
				nnbName = nnb.GetName()
			else:
				nnbClear = False
				nnbName = None
		else:
			nbStatus = None
			nbName = None
			nbRType = None
			nnbClear = False
			nnbName = None

		aType = sig.GetAspectType()
		aspect = self.GetAspect(aType, rType, nbStatus, nbRType, nnbClear)
		
		
		msg.append("RT: %s" % routetype(rType))
		msg.append("NB: %s Stat: %s  NRT: %s" % (nbName, statusname(nbStatus), routetype(nbRType)))
		msg.append("NNB: %s  NNBC: %s" % (nnbName, nnbClear))
		msg.append("Aspect = %s (%x)" % (aspectname(aspect, aType), aspect))
		
		self.frame.MessageDlg("\n".join(msg))
		
		logging.debug("Calculated aspect = %s   aspect type = %s route type = %s next block status = %s next block route type = %s next next block clear = %s" %
					(aspectname(aspect, aType), aspecttype(aType), routetype(rType), statusname(nbStatus), routetype(nbRType), nnbClear))

		#self.CheckBlockSignals(sig, aspect, exitBlk, doReverseExit, rType, nbStatus, nbRType, nnbClear)

		return aspect

	def CheckBlockSignals(self, blkNm, sigNm, blkEast):
		blk = self.frame.blocks[blkNm]
		clear = not blk.IsOccupied()
			
		east = blk.GetEast()

		if east == blkEast:		
			blkNxt = blk.blkEast
		else:
			blkNxt = blk.blkWest
		
		if blkNxt is None:
			nxtclr = False
			nxtrte = None
		
		else:	
			nxtclr = blkNxt.IsCleared()		
			rt = blkNxt.GetRoute()
			if rt is None:
				nxtrte = None
			else:
				nxtrte = rt.rtype[0 if blkEast else 1] # get next route type
		
		if east != blkEast:
			aspect = 0	
		elif clear and nxtclr and (nxtrte == MAIN):
			aspect = 0b011   # clear
		elif clear and nxtclr and (nxtrte == DIVERGING):
			aspect = 0b010   # approach medium
		elif clear and nxtclr and (nxtrte == SLOW):
			aspect = 0b110   # approach slow
		elif clear and not nxtclr:
			aspect = 0b001   # approach
		else:
			aspect = 0       # stop
		
		self.frame.Request({"signal": { "name": sigNm, "aspect": aspect }})


	def CheckBlockSignalsAdv(self, blkNm, blkNxtNm, sigNm, blkEast):
		blk = self.frame.blocks[blkNm]
		clear = not blk.IsOccupied()
			
		east = blk.GetEast()
		
		if east == blkEast:		
			blkNxt = blk.blkEast
		else:
			blkNxt = blk.blkWest
		
		if blkNxt is None:
			nxtclr = False
			nxtrte = None
		
		else:	
			nxtclr = blkNxt.IsCleared()		
			rt = blkNxt.GetRoute()
			if rt is None:
				nxtrte = None
			else:
				nxtrte = rt.rtype[0 if blkEast else 1] # get next route type

		try:
			blknxt = self.frame.blocks[blkNxtNm]
		except KeyError:
			nxtclradv = False
			nxtEast = None
		else:
			nxtEast = blknxt.GetEast()
			if nxtEast != blkEast:
				nxtclradv = False
			else:
				nxtclradv = blknxt.IsCleared()
		
		if east != blkEast or nxtEast != blkEast:
			aspect = 0	
		elif clear and nxtclr and (nxtrte == MAIN) and nxtclradv:
			aspect = 0b011  # clear
		elif clear and nxtclr and (nxtrte == MAIN) and (not nxtclradv):
			aspect = 0b110   # advance approach
		elif clear and nxtclr and (nxtrte == DIVERGING):
			aspect = 0b010   # approach medium
		elif clear and not nxtclr:
			aspect = 0b001   # approach
		else:
			aspect = 0       # stop
		
		self.frame.Request({"signal": { "name": sigNm, "aspect": aspect }})

	def GetRouteDefinitions(self):
		return [r.GetDefinition() for r in self.routes.values()]

	def anyTurnoutLocked(self, toList):
		rv = False
		for toname, stat in toList:
			turnout = self.turnouts[toname]
			tostat = "N" if turnout.IsNormal() else "R"
			if turnout.IsLocked() and tostat != stat:
				rv = True

		return rv

	def GetAspect(self, atype, rtype, nbstatus, nbrtype, nnbclear):
		#print("Get aspect.  Aspect type = %s, route type %s nextblockstatus %s next block route type %s nextnextclear %s" %
		#	(aspecttype(atype), routetype(rtype), statustype(nbstatus), routetype(nbrtype), str(nnbclear)))
		if atype == RegAspects:
			if rtype == MAIN and nbstatus == CLEARED and nbrtype == MAIN:
				return 0b011  # Clear

			elif rtype == MAIN and nbstatus == CLEARED and nbrtype == DIVERGING:
				return 0b010  # Approach Medium

			elif rtype == DIVERGING and nbstatus == CLEARED and nbrtype == MAIN:
				return 0b111  # Medium Clear

			elif rtype in [MAIN, DIVERGING] and nbstatus == CLEARED and nbrtype == SLOW:
				return 0b110  # Approach Slow

			elif rtype == MAIN and (nbstatus != CLEARED or nbrtype == RESTRICTING):
				return 0b001  # Approach

			elif rtype == DIVERGING and (nbstatus != CLEARED or nbrtype != MAIN):
				return 0b101  # Medium Approach

			elif rtype in [RESTRICTING, SLOW]:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == RegSloAspects:
			if rtype == MAIN and nbstatus == CLEARED:
				return 0b011  # Clear

			elif rtype == SLOW and nbstatus == CLEARED:
				return 0b111  # Slow clear

			elif rtype == MAIN:
				return 0b001  # Approach

			elif rtype == SLOW:
				return 0b101  # Slow Approach

			elif rtype == RESTRICTING:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == AdvAspects:
			if rtype == MAIN and nbstatus == CLEARED and nbrtype == MAIN and nnbclear:
				return 0b011  # Clear

			elif rtype == MAIN and nbstatus == CLEARED and nbrtype == DIVERGING:
				return 0b010  # Approach Medium

			elif rtype == DIVERGING and nbstatus == CLEARED and nbrtype == MAIN:
				return 0b111  # Clear

			elif rtype == MAIN and nbstatus == CLEARED and nbrtype == MAIN and not nnbclear:
				return 0b110  # Advance Approach

			elif rtype == MAIN and (nbstatus != CLEARED or nbrtype == RESTRICTING):
				return 0b001  # Approach

			elif rtype == DIVERGING and (nbstatus != CLEARED or nbrtype != MAIN):
				return 0b101  # Medium Approach

			elif rtype == RESTRICTING:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == SloAspects:
			if nbstatus == CLEARED and rtype in [SLOW, DIVERGING]:
				return 0b01  # Slow Clear

			elif nbstatus != CLEARED and rtype == SLOW:
				return 0b11  # Slow Approach

			elif rtype == RESTRICTING:
				return 0b10  # Restricting

			else:
				return 0  # Stop

		else:
			return 0

	def GetBlockAspect(self, atype, rtype, nbstatus, nbrtype, nnbclear):
		if atype == RegAspects:
			if nbstatus == CLEARED and nbrtype == MAIN:
				return 0b011  # clear
			elif nbstatus == CLEARED and nbrtype == DIVERGING:
				return 0b010  # approach medium
			elif nbstatus == CLEARED and nbrtype == SLOW:
				return 0b110  # appproach slow
			elif nbstatus != CLEARED:
				return 0b001  # approach
			else:
				return 0b000  # stop

		elif atype == AdvAspects:
			if nbstatus == CLEARED and nbrtype == MAIN and nnbclear:
				return 0b011  # clear
			elif nbstatus == CLEARED and nbrtype == MAIN and nnbclear:
				return 0b110  # advance approach
			elif nbstatus == CLEARED and nbrtype == DIVERGING:
				return 0b010  # approach medium
			elif nbstatus != CLEARED:
				return 0b001  # approach
			else:
				return 0b000  # stop

		return 0b000  # stop as default

	def PerformHandSwitchAction(self, hs, nv=None):
		if nv and nv == hs.GetValue():
			return

		if not hs.GetValue():
			# currently unlocked - trying to lock

			if hs.IsBlockCleared():
				self.frame.PopupEvent("Block %s is cleared" % hs.GetBlockName())
				return

			stat = 1
		else:
			stat = 0

		self.frame.Request({"handswitch": {"name": hs.GetName(), "status": stat}})

	# The Do... routines handle requests that come in from the dispatch server.  The 3 objects of interest for
	# these requests are blocks, signals, and turnouts
	def DoBlockAction(self, blk, blockend, state):
		bname = blk.GetName()
		blk.SetOccupied(occupied=state == OCCUPIED, blockend=blockend, refresh=True)

		osList = self.frame.GetOSForBlock(bname)
		for osblk in osList:
			osblk.Draw()

	def DoTurnoutAction(self, turnout, state, force=False):
		if state == NORMAL:
			turnout.SetNormal(refresh=True, force=force)
		else:
			turnout.SetReverse(refresh=True, force=force)

	def DoSignalAction(self, sig, aspect, callon=False):
		signm = sig.GetName()
		
		if callon:
			sig.SetAspect(aspect, refresh=True, callon=True)
			return

		osblock = None
		for blknm, siglist in self.osSignals.items():
			if signm in siglist:
				osblock = self.frame.blocks[blknm]
				if osblock.route is None:
					continue
				
				rname = osblock.GetRouteName()
				if sig.IsPossibleRoute(blknm, rname):
					break
		else:
			if aspect != 0:
				logging.info("DoSignalAction returning because no possible routes")
				return

		if aspect < 0:
			aspect = self.CalculateAspect(sig, osblock, self.routes[rname], silent=True)
			#  report calculated aspect back to the server
			if aspect is None:
				aspect = sig.GetAspect()
				
			self.frame.Request({"signal": {"name": signm, "aspect": aspect}})

		if sig.GetAspect() == aspect:
			# no change necessary
			return

		# all checking was done on the sending side, so this is a valid request - just do it
		if aspect != STOP:
			osblock.SetEast(sig.GetEast())

		sig.SetAspect(aspect, refresh=True)
		
		exitBlkNm = osblock.GetExitBlock()
		entryBlkNm = osblock.GetEntryBlock()
		exitBlk  = self.frame.GetBlockByName(exitBlkNm)
		entryBlk = self.frame.GetBlockByName(entryBlkNm)

		if aspect != 0:
			osblock.SetEntrySignal(sig)
			osblock.SetCleared(True, refresh=True)
			self.frame.CheckTrainsInBlock(entryBlkNm, sig)
		else:
			entrySig = osblock.GetEntrySignal()
			if entrySig is not None:
				if sig.GetName() == entrySig.GetName():
					osblock.SetCleared(False, refresh=True)

		if osblock.IsBusy() and aspect == STOP:
			return


		if aspect != 0:
			if self.CrossingEastWestBoundary(osblock, exitBlk):
				nd = not sig.GetEast()
			else:
				nd = sig.GetEast()
				
			exitBlk.SetEast(nd)
			'''
			this next statement handles those situations when a train reverses direction within a block.
			For all other cases, this is redundant.
			'''
			if entryBlk is not None:
				entryBlk.SetEast(nd)

		exitBlk.SetCleared(aspect != STOP, refresh=True)

		self.LockTurnoutsForSignal(osblock.GetName(), sig, aspect != STOP)

		if exitBlk.GetBlockType() == OVERSWITCH:
			rt = exitBlk.GetRoute()
			if rt:
				tolist = rt.GetLockTurnouts()
				self.LockTurnouts(signm, tolist, aspect != STOP)
				
		self.EvaluateDistrictLocks(sig)
		
	def EvaluateDistrictLocks(self, sig, ossLocks=None):
		pass

	def DoSignalLeverAction(self, signame, state, callon):
		sigPrefix = signame.split(".")[0]
		osblknms = self.sigLeverMap[signame]
		signm = None

		for osblknm in osblknms:
			osblk = self.frame.blocks[osblknm]
			route = osblk.GetRoute()
			
			if route:
				sigs = route.GetSignals()
				sigl = None
				sigr = None
				for sig in sigs:
					if sig.startswith(sigPrefix):
						if sig[len(sigPrefix)] == "L":
							sigl = sig
						elif sig[len(sigPrefix)] == "R":
							sigr = sig
							
				if state == "L":
					if sigl is not None:
						signm = sigl
						movement = True   # trying to set to non-stopping aspect
						break
				elif state == 'R':
					if sigr is not None:
						signm = sigr
						movement = True   # trying to set to non-stopping aspect
						break
				elif state == "N":
					if sigl is not None:
						sig = self.frame.signals[sigl]
						if sig and sig.GetAspect() != 0:
							signm = sigl
							movement = False
							break
					if sigr is not None:
						sig = self.frame.signals[sigr]
						if sig and sig.GetAspect() != 0:
							signm = sigr
							movement = False
							break

		if signm is None:
			return

		sig = self.frame.signals[signm]
		if not sig:
			return

		if movement:
			if callon:
				aspect = restrictedaspect(sig.GetAspectType())
			else:
				aspect = self.CalculateAspect(sig, osblk, route)
				if aspect is None:
					return
		else:
			aspect = 0

		self.frame.Request({"signal": {"name": signm, "aspect": aspect, "callon": 1 if callon else 0}})
	
		if not callon:
			sig.SetLock(osblk.GetName(), 0 if aspect == 0 else 1)

	def LockTurnoutsForSignal(self, osblknm, sig, flag):
		signm = sig.GetName()
		if osblknm in sig.possibleRoutes:
			osblk = self.blocks[osblknm]
			rt = osblk.GetRoute()
			if rt:
				tolist = rt.GetLockTurnouts()
				self.LockTurnouts(signm, tolist, flag)

	def LockTurnouts(self, locker, tolist, flag):
		for t in tolist:
			to = self.frame.turnouts[t]
			to.SetLock(locker, flag, refresh=True)
			tp = to.GetPaired()
			if tp:
				tp.SetLock(locker, flag, refresh=True)

	def DoHandSwitchAction(self, hs, stat):
		hs.SetValue(stat != 0, refresh=True)

	def DoIndicatorAction(self, ind, value):
		pass

	def CrossingEastWestBoundary(self, osblk, blk):
		if osblk is None or blk is None:
			return False
		blkNm = blk.GetName()
		osNm = osblk.GetName()
		return [osNm, blkNm] in EWCrossoverPoints

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}
		return {}, {}

	def DefineTurnouts(self, blocks):
		self.turnouts = {}
		return {}

	def DefineIndicators(self):
		self.indicators = {}
		return {}

	def DefineSignals(self):
		self.signals = {}
		return {}

	def DefineButtons(self):
		self.buttons = {}
		return {}

	def DefineHandSwitches(self):
		self.handswitches = {}
		return {}

	def ReportBlockBusy(self, blknm):
		self.frame.PopupEvent("Block %s is busy" % blknm)

	def ReportOSBusy(self, osnm):
		self.frame.PopupEvent("Block %s is busy" % osnm)

	def ReportTurnoutLocked(self, tonm):
		self.frame.PopupEvent("Turnout %s is locked" % tonm)

	def GenerateRouteInformation(self):
		routes = {}
		for r in self.routes.values():
			routes.update(r.ToJson())

		return routes

	def GenerateBlockInformation(self):
		blocks = {}
		for b in self.blocks.values():
			blocks.update(b.ToJson())

		return blocks


class Districts:
	def __init__(self):
		self.districts = {}

	def AddDistrict(self, district):
		self.districts[district.name] = district

	def SetTiles(self, tiles, totiles, sstiles, sigtiles, misctiles, btntiles):
		for t in self.districts.values():
			t.SetTiles(tiles, totiles, sstiles, sigtiles, misctiles, btntiles)

	def Initialize(self):
		for t in self.districts.values():
			t.Initialize()

	def OnConnect(self):
		for t in self.districts.values():
			t.OnConnect()

	def Draw(self):
		for t in self.districts.values():
			t.Draw()

	def EvaluateDistrictLocks(self, ossLocks):
		for t in self.districts.values():
			t.EvaluateDistrictLocks(None, ossLocks=ossLocks)

	def DefineBlocks(self):
		blocks = {}
		osBlocks = {}
		for t in self.districts.values():
			bl, osbl = t.DefineBlocks()
			blocks.update(bl)
			osBlocks.update(osbl)

		return blocks, osBlocks

	def DefineTurnouts(self, blocks):
		tos = {}
		for t in self.districts.values():
			tos.update(t.DefineTurnouts(blocks))

		return tos

	def DefineSignals(self):
		sigs = {}
		blocksigs = {}
		for t in self.districts.values():
			sl, bsl = t.DefineSignals()
			sigs.update(sl)
			blocksigs.update(bsl)

		return sigs, blocksigs

	def DefineButtons(self):
		btns = {}
		for t in self.districts.values():
			btns.update(t.DefineButtons())

		return btns

	def DefineHandSwitches(self):
		handswitches = {}
		for t in self.districts.values():
			handswitches.update(t.DefineHandSwitches())

		return handswitches

	def DefineIndicators(self):
		indicators = {}
		for t in self.districts.values():
			indicators.update(t.DefineIndicators())

		return indicators

	def GetRouteDefinitions(self):
		rtes = []
		for t in self.districts.values():
			rtes.extend(t.GetRouteDefinitions())
		return rtes
			
	def GetCrossoverPoints(self):
		return EWCrossoverPoints

