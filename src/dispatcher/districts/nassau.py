from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route
from dispatcher.turnout import Turnout, SlipSwitch
from dispatcher.signal import Signal
from dispatcher.button import Button

from dispatcher.constants import LaKr, SloAspects, SLOW, RESTRICTING, SLIPSWITCH, NORMAL, REVERSE, RegAspects, EMPTY


class Nassau (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def PerformSignalAction(self, sig):
		controlOpt = self.frame.rbNassauControl.GetSelection()
		if controlOpt == 0:  # nassau local control
			self.frame.PopupEvent("Nassau control is local")
			return

		signm = sig.GetName()
		if controlOpt == 1:
			mainOnly = False
			if signm == "N28L":
				if not self.CheckIfMainRoute("NEOSRH"):
					mainOnly = True
			elif signm == "N26L":
				if not self.CheckIfMainRoute("NEOSW"):
					mainOnly = True
			elif signm == "N24L":
				if not self.CheckIfMainRoute("NEOSE"):
					mainOnly = True
			elif signm == "N18R":
				if not self.CheckIfMainRoute("NWOSCY"):
					mainOnly = True
			elif signm == "N16R":
				if not self.CheckIfMainRoute("NWOSW"):
					mainOnly = True
			elif signm == "N14R":
				if not self.CheckIfMainRoute("NWOSE"):
					mainOnly = True
			elif signm not in [ "N26RC", "N24RA", "N16L", "N14LA" ]:  # dispatcher: main only
				mainOnly = True

			if mainOnly:
				self.frame.PopupEvent("Nassau control is main only")
				return

		if not District.PerformSignalAction(self, sig):
			return
		currentMovement = sig.GetAspect() != 0  # does the CURRENT signal status allow movement
		rt, osblk = self.FindRoute(sig)
		osblknm = osblk.GetName()
		sigs = rt.GetSignals()

		if osblknm in ["NWOSCY", "NWOSTY", "NWOSW", "NWOSE"]:
			lock = [False, False, False, False]
			if not currentMovement:
				for s in sigs:
					if s.startswith("N20"):
						lock[0] = True
					elif s.startswith("N18"):
						lock[1] = True
					elif s.startswith("N16"):
						lock[2] = True
					elif s.startswith("N14"):
						lock[3] = True
			if lock[0] and lock[3]:
				lock[1] = lock[2] = True
			elif lock[0] and lock[2]:
				lock[1] = True
			elif lock[1] and lock[3]:
				lock[2] = True
			lv = [1 if x else 0 for x in lock]
			self.frame.Request({"districtlock": { "name": "NWSL", "value": lv }})
		elif osblknm in ["NEOSRH", "NEOSW", "NEOSE"]:
			lock = [False, False, False]
			if not currentMovement:
				for s in sigs:
					if s.startswith("N28"):
						lock[0] = True
					elif s.startswith("N26"):
						lock[1] = True
					elif s.startswith("N24"):
						lock[2] = True
			if lock[0] and lock[2]:
				lock[1] = True
			lv = [1 if x else 0 for x in lock]
			self.frame.Request({"districtlock": { "name": "NESL", "value": lv }})

	def CheckIfMainRoute(self, osblknm):
		osblk = self.blocks[osblknm]
		route = osblk.GetRoute()
		if route is None:
			return False

		blk1, blk2 = route.GetEndPoints()
		for b in [ blk1, blk2 ]:
			if not b:
				continue

			if b in [ "N12", "N22" ]:
				return True

		return False

	def PerformButtonAction(self, btn):
		controlOpt = self.frame.rbNassauControl.GetSelection()
		if controlOpt == 0:  # nassau local control
			btn.Press(refresh=False)
			btn.Invalidate(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			self.frame.PopupEvent("Nassau control is local")
			return

		bname = btn.GetName()
		if controlOpt == 1 and bname not in [ "NNXBtnN12W", "NNXBtnN22W", "NNXBtnN12E", "NNXBtnN22E",
												"NNXBtnR10", "NNXBtnB10", "NNXBtnB20",
												"NNXBtnN60", "NNXBtnN11", "NNXBtnN21" ]:  # dispatcher: main only
			btn.Press(refresh=False)
			btn.Invalidate(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			self.frame.PopupEvent("Nassau control is main only")
			return

		District.PerformButtonAction(self, btn)
		if bname in self.eastGroup["NOSW"] + self.westGroup["NOSW"]:
			self.DoEntryExitButtons(btn, "NOSW", sendButtons=True)
		elif bname in self.eastGroup["NOSE"] + self.westGroup["NOSE"]:
			self.DoEntryExitButtons(btn, "NOSE", sendButtons=True)

	def CheckBlockSignals(self, sig, aspect, blk, rev, rType, nbStatus, nbRType, nnbClear):
		if blk is None:
			return

		blkNm = blk.GetName()
		east = blk.GetEast(reverse=rev)

		if blkNm == "N21" and not east:
			signm = "N21W"
			atype = RegAspects

		elif blkNm == "N11" and not east:
			signm = "N11W"
			atype = RegAspects

		else:
			return

		if aspect != 0:
			aspect = self.GetBlockAspect(atype, rType, nbStatus, nbRType, nnbClear)

		self.frame.Request({"signal": { "name": signm, "aspect": aspect }})

	def DoTurnoutAction(self, turnout, state, force=False):
		tn = turnout.GetName()
		if turnout.GetType() == SLIPSWITCH:
			if tn == "NSw29":
				bstat = NORMAL if self.turnouts["NSw27"].IsNormal() else REVERSE
				turnout.SetStatus([bstat, state])
				turnout.Draw()
			elif tn == "NSw31":
				bstat = NORMAL if self.turnouts["NSw29"].IsNormal() else REVERSE
				turnout.SetStatus([bstat, state])
				turnout.Draw()
			elif tn == "NSw23":
				bstat = NORMAL if self.turnouts["NSw21"].IsNormal() else REVERSE
				turnout.SetStatus([bstat, state])
				turnout.Draw()
			elif tn == "NSw43":
				bstat = NORMAL if self.turnouts["NSw45"].IsNormal() else REVERSE
				turnout.SetStatus([state, bstat])
				turnout.Draw()
			elif tn == "NSw45":
				bstat = NORMAL if self.turnouts["NSw47"].IsNormal() else REVERSE
				turnout.SetStatus([state, bstat])
				turnout.Draw()

		else:
			if tn in ["NSw13", "NSw15", "NSw17"]:  # Coach Yard - update display
				for t, screen, pos, _ in self.blocks["N60"].GetTiles():
					bmp = t.getBmp(EMPTY, False, False)
					self.frame.DrawTile(screen, pos, bmp)

				self.turnouts["NSw13"].Draw(blockstat=EMPTY, east=False)
				self.turnouts["NSw15"].Draw(blockstat=EMPTY, east=False)
				self.turnouts["NSw17"].Draw(blockstat=EMPTY, east=False)

			District.DoTurnoutAction(self, turnout, state, force=force)

		if tn == "NSw27":
			trnout = self.turnouts["NSw29"]
			trnout.UpdateStatus()
			trnout.Draw()
		elif tn == "NSw29":
			trnout = self.turnouts["NSw31"]
			trnout.UpdateStatus()
			trnout.Draw()
		elif tn == "NSw21":
			trnout = self.turnouts["NSw23"]
			trnout.UpdateStatus()
			trnout.Draw()
		elif tn == "NSw45":
			trnout = self.turnouts["NSw43"]
			trnout.UpdateStatus()
			trnout.Draw()
		elif tn == "NSw47":
			trnout = self.turnouts["NSw45"]
			trnout.UpdateStatus()
			trnout.Draw()

	def DetermineRoute(self, blocks):
		# block N60 - coach yard - is treated separately, so handle it here if it is in the list of blocks
		has60 = [b for b in blocks if b.GetName() == "N60"]
		if len(has60) > 0:
			block = self.blocks["N60"]
			s13 = 'N' if self.turnouts["NSw13"].IsNormal() else 'R'
			s15 = 'N' if self.turnouts["NSw15"].IsNormal() else 'R'
			s17 = 'N' if self.turnouts["NSw17"].IsNormal() else 'R'
			if s13+s17 == "NR":
				newRoute = "NRtN60A"
			elif s13+s17 == "RR":
				newRoute = "NRtN60B"
			elif s15+s17 == "RN":
				newRoute = "NRtN60C"
			elif s15+s17 == "NN":
				newRoute = "NRtN60D"
			else:
				block.SetRoute(None)
				return
			
			if block.GetRouteName() == newRoute:
				block.Draw()
			else:
				block.SetRoute(self.routes[newRoute])
				
		else:
			# now exclude block N60 from the remainder of the normal processing
			nblocks = [b for b in blocks if b.GetName() != "N60"]
			self.FindTurnoutCombinations(nblocks,
					["NSw19", "NSw21", "NSw23", "NSw25", "NSw27", "NSw29", "NSw31", "NSw33", "NSw35",
					"NSw39", "NSw41", "NSw43", "NSw45", "NSw47", "NSw51", "NSw53", "NSw55", "NSw57",
					"NSw13", "NSw15", "NSw17"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["N21"] = Block(self, self.frame, "N21",
			[
				(self.tiles["horiz"],   LaKr, (153, 13), False),
				(self.tiles["horiznc"], LaKr, (154, 13), False),
				(self.tiles["horiz"],   LaKr, (155, 13), False),
				(self.tiles["horiznc"], LaKr, (156, 13), False),
				(self.tiles["horiz"],   LaKr, (157, 13), False),
				(self.tiles["horiznc"], LaKr, (158, 13), False),
				(self.tiles["horiznc"], self.screen, (0, 13), False),
				(self.tiles["horiz"],   self.screen, (1, 13), False),
				(self.tiles["horiznc"], self.screen, (2, 13), False),
				(self.tiles["horiz"],   self.screen, (3, 13), False),
				(self.tiles["horiznc"], self.screen, (4, 13), False),
			], True)
		self.blocks["N21"].AddStoppingBlock([
				(self.tiles["eobleft"], LaKr, (150, 13), False),
				(self.tiles["horiz"],   LaKr, (151, 13), False),
				(self.tiles["horiznc"], LaKr, (152, 13), False),
			], False)
		self.blocks["N21"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen, (5, 13), False),
				(self.tiles["horiznc"], self.screen, (6, 13), False),
				(self.tiles["horiz"],   self.screen, (7, 13), False),
			], True)
		self.blocks["N21"].AddTrainLoc(LaKr, (154, 13))
		self.blocks["N21"].AddTrainLoc(self.screen, (1, 13))

		self.blocks["N32"] = Block(self, self.frame, "N32",
			[
				(self.tiles["horiz"],   self.screen, (21, 7), False),
				(self.tiles["horiznc"], self.screen, (22, 7), False),
				(self.tiles["horiz"],   self.screen, (23, 7), False),
				(self.tiles["horiznc"], self.screen, (24, 7), False),
				(self.tiles["horiz"],   self.screen, (25, 7), False),
				(self.tiles["horiznc"], self.screen, (26, 7), False),
				(self.tiles["horiz"],   self.screen, (27, 7), False),
				(self.tiles["horiznc"], self.screen, (28, 7), False),
			], False)
		self.blocks["N32"].AddTrainLoc(self.screen, (23, 7))

		self.blocks["N31"] = Block(self, self.frame, "N31",
			[
				(self.tiles["horiz"],   self.screen, (21, 9), False),
				(self.tiles["horiznc"], self.screen, (22, 9), False),
				(self.tiles["horiz"],   self.screen, (23, 9), False),
				(self.tiles["horiznc"], self.screen, (24, 9), False),
				(self.tiles["horiz"],   self.screen, (25, 9), False),
				(self.tiles["horiznc"], self.screen, (26, 9), False),
				(self.tiles["horiz"],   self.screen, (27, 9), False),
				(self.tiles["horiznc"], self.screen, (28, 9), False),
			], False)
		self.blocks["N31"].AddTrainLoc(self.screen, (23, 9))

		self.blocks["N12"] = Block(self, self.frame, "N12",
			[
				(self.tiles["horiz"],   self.screen, (21, 11), False),
				(self.tiles["horiznc"], self.screen, (22, 11), False),
				(self.tiles["horiz"],   self.screen, (23, 11), False),
				(self.tiles["horiznc"], self.screen, (24, 11), False),
				(self.tiles["horiz"],   self.screen, (25, 11), False),
				(self.tiles["horiznc"], self.screen, (26, 11), False),
				(self.tiles["horiz"],   self.screen, (27, 11), False),
				(self.tiles["horiznc"], self.screen, (28, 11), False),
			], False)
		self.blocks["N12"].AddTrainLoc(self.screen, (23, 11))

		self.blocks["N22"] = Block(self, self.frame, "N22",
			[
				(self.tiles["horiz"],   self.screen, (21, 13), False),
				(self.tiles["horiznc"], self.screen, (22, 13), False),
				(self.tiles["horiz"],   self.screen, (23, 13), False),
				(self.tiles["horiznc"], self.screen, (24, 13), False),
				(self.tiles["horiz"],   self.screen, (25, 13), False),
				(self.tiles["horiznc"], self.screen, (26, 13), False),
				(self.tiles["horiz"],   self.screen, (27, 13), False),
				(self.tiles["horiznc"], self.screen, (28, 13), False),
			], True)
		self.blocks["N22"].AddTrainLoc(self.screen, (23, 13))

		self.blocks["N41"] = Block(self, self.frame, "N41",
			[
				(self.tiles["horiz"],   self.screen, (21, 15), False),
				(self.tiles["horiznc"], self.screen, (22, 15), False),
				(self.tiles["horiz"],   self.screen, (23, 15), False),
				(self.tiles["horiznc"], self.screen, (24, 15), False),
				(self.tiles["horiz"],   self.screen, (25, 15), False),
				(self.tiles["horiznc"], self.screen, (26, 15), False),
				(self.tiles["horiz"],   self.screen, (27, 15), False),
				(self.tiles["horiznc"], self.screen, (28, 15), False),
			], True)
		self.blocks["N41"].AddTrainLoc(self.screen, (23, 15))

		self.blocks["N42"] = Block(self, self.frame, "N42",
			[
				(self.tiles["horiz"],   self.screen, (21, 17), False),
				(self.tiles["horiznc"], self.screen, (22, 17), False),
				(self.tiles["horiz"],   self.screen, (23, 17), False),
				(self.tiles["horiznc"], self.screen, (24, 17), False),
				(self.tiles["horiz"],   self.screen, (25, 17), False),
				(self.tiles["horiznc"], self.screen, (26, 17), False),
				(self.tiles["horiz"],   self.screen, (27, 17), False),
				(self.tiles["horiznc"], self.screen, (28, 17), False),
			], True)
		self.blocks["N42"].AddTrainLoc(self.screen, (23, 17))

		self.blocks["W20"] = Block(self, self.frame, "W20",
			[
				(self.tiles["houtline"],  self.screen, (22, 19), False),
				(self.tiles["houtline"],  self.screen, (23, 19), False),
				(self.tiles["houtline"],  self.screen, (24, 19), False),
				(self.tiles["houtline"],  self.screen, (28, 19), False),
				(self.tiles["houtline"],  self.screen, (29, 19), False),
				(self.tiles["houtline"],  self.screen, (30, 19), False),
			], True)

		self.blocks["R10"] = Block(self, self.frame, "R10",
			[
				(self.tiles["horiznc"],  self.screen, (47, 9), False),
				(self.tiles["horiz"],    self.screen, (48, 9), False),
				(self.tiles["horiznc"],  self.screen, (49, 9), False),
			], False)
		self.blocks["R10"].AddStoppingBlock([
				(self.tiles["horiznc"],  self.screen, (45, 9), False),
				(self.tiles["horiz"],    self.screen, (46, 9), False),
			], False)
		self.blocks["R10"].AddTrainLoc(self.screen, (47, 9))

		self.blocks["B10"] = Block(self, self.frame, "B10",
			[
				(self.tiles["horiz"],    self.screen, (48, 11), False),
				(self.tiles["horiznc"],  self.screen, (49, 11), False),
				(self.tiles["horiz"],    self.screen, (50, 11), False),
				(self.tiles["horiznc"],  self.screen, (51, 11), False),
				(self.tiles["eobright"],    self.screen, (52, 11), False),
			], False)
		self.blocks["B10"].AddStoppingBlock([
				(self.tiles["horiznc"],  self.screen, (45, 11), False),
				(self.tiles["horiz"],    self.screen, (46, 11), False),
				(self.tiles["horiznc"],  self.screen, (47, 11), False),
			], False)
		self.blocks["B10"].AddTrainLoc(self.screen, (47, 11))

		self.blocks["W10"] = Block(self, self.frame, "W10",
			[
				(self.tiles["houtline"],  self.screen, (21, 5), False),
				(self.tiles["houtline"],  self.screen, (22, 5), False),
				(self.tiles["houtline"],  self.screen, (23, 5), False),
			], False)

		self.blocks["W11"] = Block(self, self.frame, "W11",
			[
				(self.tiles["houtline"],  self.screen, (29, 5), False),
				(self.tiles["houtline"],  self.screen, (30, 5), False),
				(self.tiles["houtline"],  self.screen, (31, 5), False),
			], False)

		self.blocks["T12"] = Block(self, self.frame, "T12",
			[
				(self.tiles["houtline"],  self.screen, (14, 5), False),
				(self.tiles["houtline"],  self.screen, (15, 5), False),
			], False)

		self.blocks["N60"] = OverSwitch(self, self.frame, "N60",
			[
				(self.tiles["eobleft"],  self.screen, (4, 6), False),
				(self.tiles["eobleft"],  self.screen, (4, 7), False),
				(self.tiles["eobleft"],  self.screen, (4, 8), False),
				(self.tiles["eobleft"],  self.screen, (4, 9), False),
				(self.tiles["turnrightright"],  self.screen, (5, 6), False),
				(self.tiles["turnrightright"],  self.screen, (5, 8), False),
				(self.tiles["horiznc"],  self.screen, (5, 7), False),
				(self.tiles["horiznc"],  self.screen, (5, 9), False),
				(self.tiles["horiznc"],  self.screen, (7, 9), False),
				(self.tiles["diagright"],self.screen, (7, 8), False),
				(self.tiles["houtline"],  self.screen, (1, 6), False),
				(self.tiles["houtline"],  self.screen, (2, 6), False),
				(self.tiles["houtline"],  self.screen, (3, 6), False),
				(self.tiles["houtline"],  self.screen, (1, 7), False),
				(self.tiles["houtline"],  self.screen, (2, 7), False),
				(self.tiles["houtline"],  self.screen, (3, 7), False),
				(self.tiles["houtline"],  self.screen, (1, 8), False),
				(self.tiles["houtline"],  self.screen, (2, 8), False),
				(self.tiles["houtline"],  self.screen, (3, 8), False),
				(self.tiles["houtline"],  self.screen, (1, 9), False),
				(self.tiles["houtline"],  self.screen, (2, 9), False),
				(self.tiles["houtline"],  self.screen, (3, 9), False),
			], True)

		self.blocks["NWOSTY"] = OverSwitch(self, self.frame, "NWOSTY", 
			[
				(self.tiles["horiznc"],   self.screen, (17, 5), False),
				(self.tiles["horiz"],     self.screen, (18, 5), False),
			], 
			False)

		self.blocks["NWOSCY"] = OverSwitch(self, self.frame, "NWOSCY", 
			[
				(self.tiles["horiznc"],   self.screen, (11, 9), False),
				(self.tiles["horiz"],     self.screen, (12, 9), False),
				(self.tiles["horiznc"],   self.screen, (13, 9), False),
				(self.tiles["horiz"],     self.screen, (14, 9), False),
				(self.tiles["diagright"], self.screen, (11, 10), False),
				(self.tiles["diagright"], self.screen, (13, 12), False),
				(self.tiles["diagleft"],  self.screen, (16, 8), False),
				(self.tiles["diagleft"],  self.screen, (18, 6), False),
				(self.tiles["diagright"], self.screen, (15, 14), False),
				(self.tiles["diagright"], self.screen, (17, 16), False),
				(self.tiles["diagright"], self.screen, (19, 18), False),
				(self.tiles["turnrightleft"], self.screen, (20, 19), False),
				(self.tiles["horiznc"],   self.screen, (18, 7), False),
				(self.tiles["horiz"],     self.screen, (19, 7), False),
				(self.tiles["horiznc"],   self.screen, (16, 9), False),
				(self.tiles["horiz"],     self.screen, (17, 9), False),
				(self.tiles["horiznc"],   self.screen, (18, 9), False),
				(self.tiles["horiz"],     self.screen, (19, 9), False),
				(self.tiles["horiznc"],   self.screen, (14, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 11), False),
				(self.tiles["horiznc"],   self.screen, (16, 11), False),
				(self.tiles["horiz"],     self.screen, (17, 11), False),
				(self.tiles["horiznc"],   self.screen, (18, 11), False),
				(self.tiles["horiz"],     self.screen, (19, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 13), False),
				(self.tiles["horiznc"],   self.screen, (16, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 13), False),
				(self.tiles["horiznc"],   self.screen, (18, 13), False),
				(self.tiles["horiz"],     self.screen, (19, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 15), False),
				(self.tiles["horiznc"],   self.screen, (18, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 17), False),
			], 
			False)

		self.blocks["NWOSW"] = OverSwitch(self, self.frame, "NWOSW", 
			[
				(self.tiles["horiznc"],   self.screen, (9, 11), False),
				(self.tiles["horiz"],     self.screen, (10, 11), False),
				(self.tiles["diagright"], self.screen, (13, 12), False),
				(self.tiles["diagleft"],  self.screen, (14, 10), False),
				(self.tiles["diagleft"],  self.screen, (16, 8), False),
				(self.tiles["diagleft"],  self.screen, (18, 6), False),
				(self.tiles["diagright"], self.screen, (15, 14), False),
				(self.tiles["diagright"], self.screen, (17, 16), False),
				(self.tiles["diagright"], self.screen, (19, 18), False),
				(self.tiles["turnrightleft"], self.screen, (20, 19), False),
				(self.tiles["horiznc"],   self.screen, (18, 7), False),
				(self.tiles["horiz"],     self.screen, (19, 7), False),
				(self.tiles["horiznc"],   self.screen, (16, 9), False),
				(self.tiles["horiz"],     self.screen, (17, 9), False),
				(self.tiles["horiznc"],   self.screen, (18, 9), False),
				(self.tiles["horiz"],     self.screen, (19, 9), False),
				(self.tiles["horiznc"],   self.screen, (14, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 11), False),
				(self.tiles["horiznc"],   self.screen, (16, 11), False),
				(self.tiles["horiz"],     self.screen, (17, 11), False),
				(self.tiles["horiznc"],   self.screen, (18, 11), False),
				(self.tiles["horiz"],     self.screen, (19, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 13), False),
				(self.tiles["horiznc"],   self.screen, (16, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 13), False),
				(self.tiles["horiznc"],   self.screen, (18, 13), False),
				(self.tiles["horiz"],     self.screen, (19, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 15), False),
				(self.tiles["horiznc"],   self.screen, (18, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 17), False),
			], 
			False)

		self.blocks["NWOSE"] = OverSwitch(self, self.frame, "NWOSE", 
			[
				(self.tiles["horiznc"],   self.screen, (10, 13), False),
				(self.tiles["horiz"],     self.screen, (11, 13), False),
				(self.tiles["horiznc"],   self.screen, (12, 13), False),
				(self.tiles["horiz"],     self.screen, (13, 13), False),
				(self.tiles["diagleft"],  self.screen, (10, 12), False),
				(self.tiles["diagleft"],  self.screen, (14, 10), False),
				(self.tiles["diagleft"],  self.screen, (16, 8), False),
				(self.tiles["diagleft"],  self.screen, (18, 6), False),
				(self.tiles["diagright"], self.screen, (15, 14), False),
				(self.tiles["diagright"], self.screen, (17, 16), False),
				(self.tiles["diagright"], self.screen, (19, 18), False),
				(self.tiles["turnrightleft"], self.screen, (20, 19), False),
				(self.tiles["horiznc"],   self.screen, (18, 7), False),
				(self.tiles["horiz"],     self.screen, (19, 7), False),
				(self.tiles["horiznc"],   self.screen, (16, 9), False),
				(self.tiles["horiz"],     self.screen, (17, 9), False),
				(self.tiles["horiznc"],   self.screen, (18, 9), False),
				(self.tiles["horiz"],     self.screen, (19, 9), False),
				(self.tiles["horiznc"],   self.screen, (14, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 11), False),
				(self.tiles["horiznc"],   self.screen, (16, 11), False),
				(self.tiles["horiz"],     self.screen, (17, 11), False),
				(self.tiles["horiznc"],   self.screen, (18, 11), False),
				(self.tiles["horiz"],     self.screen, (19, 11), False),
				(self.tiles["horiz"],     self.screen, (15, 13), False),
				(self.tiles["horiznc"],   self.screen, (16, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 13), False),
				(self.tiles["horiznc"],   self.screen, (18, 13), False),
				(self.tiles["horiz"],     self.screen, (19, 13), False),
				(self.tiles["horiz"],     self.screen, (17, 15), False),
				(self.tiles["horiznc"],   self.screen, (18, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 15), False),
				(self.tiles["horiz"],     self.screen, (19, 17), False),
			], 
			True)

		self.blocks["NEOSRH"] = OverSwitch(self, self.frame, "NEOSRH", 
			[
				(self.tiles["horiznc"],   self.screen, (43, 9), False),
				(self.tiles["horiz"],     self.screen, (38, 9), False),
				(self.tiles["horiznc"],   self.screen, (39, 9), False),
				(self.tiles["horiz"],     self.screen, (40, 9), False),
				(self.tiles["horiznc"],   self.screen, (41, 9), False),
				(self.tiles["diagleft"],  self.screen, (41, 10), False),

				(self.tiles["diagright"], self.screen, (36, 8), False),
				(self.tiles["diagright"], self.screen, (35, 7), False),
				(self.tiles["diagright"], self.screen, (34, 6), False),
				(self.tiles["turnrightright"], self.screen, (33,5), False),
				(self.tiles["horiznc"],   self.screen, (30, 11), False),
				(self.tiles["horiz"],     self.screen, (31, 11), False),
				(self.tiles["horiznc"],   self.screen, (32, 11), False),
				(self.tiles["horiz"],     self.screen, (33, 11), False),
				(self.tiles["horiz"],     self.screen, (35, 11), False),
				(self.tiles["horiznc"],   self.screen, (36, 11), False),
				(self.tiles["horiz"],     self.screen, (37, 11), False),
				(self.tiles["horiznc"],   self.screen, (38, 11), False),
				(self.tiles["diagright"], self.screen, (33, 10), False),
				(self.tiles["horiznc"],   self.screen, (30, 9), False),
				(self.tiles["horiz"],     self.screen, (31, 9), False),
				(self.tiles["diagright"], self.screen, (31, 8), False),
				(self.tiles["turnrightright"], self.screen, (30, 7), False),
				(self.tiles["diagleft"],  self.screen, (39, 12), False),
				(self.tiles["horiznc"],   self.screen, (30, 13), False),
				(self.tiles["horiz"],     self.screen, (31, 13), False),
				(self.tiles["horiznc"],   self.screen, (32, 13), False),
				(self.tiles["horiz"],     self.screen, (33, 13), False),
				(self.tiles["horiznc"],   self.screen, (34, 13), False),
				(self.tiles["horiz"],     self.screen, (35, 13), False),
				(self.tiles["horiznc"],   self.screen, (36, 13), False),
				(self.tiles["horiz"],     self.screen, (37, 13), False),
				(self.tiles["diagleft"],  self.screen, (37, 14), False),
				(self.tiles["horiznc"],   self.screen, (30, 15), False),
				(self.tiles["horiz"],     self.screen, (31, 15), False),
				(self.tiles["horiznc"],   self.screen, (32, 15), False),
				(self.tiles["horiz"],     self.screen, (33, 15), False),
				(self.tiles["horiznc"],   self.screen, (34, 15), False),
				(self.tiles["horiz"],     self.screen, (35, 15), False),
				(self.tiles["diagleft"],  self.screen, (35, 16), False),
				(self.tiles["horiznc"],   self.screen, (30, 17), False),
				(self.tiles["horiz"],     self.screen, (31, 17), False),
				(self.tiles["horiznc"],   self.screen, (32, 17), False),
				(self.tiles["horiz"],     self.screen, (33, 17), False),
				(self.tiles["diagleft"],  self.screen, (33, 18), False),
				(self.tiles["turnleftright"],  self.screen, (32, 19), False),
			],
			False)

		self.blocks["NEOSW"] = OverSwitch(self, self.frame, "NEOSW", 
			[
				(self.tiles["horiz"],     self.screen, (42, 11), False),
				(self.tiles["horiznc"],   self.screen, (43, 11), False),

				(self.tiles["diagright"], self.screen, (36, 8), False),
				(self.tiles["diagright"], self.screen, (35, 7), False),
				(self.tiles["diagright"], self.screen, (34, 6), False),
				(self.tiles["diagright"], self.screen, (38, 10), False),
				(self.tiles["turnrightright"], self.screen, (33,5), False),
				(self.tiles["horiznc"],   self.screen, (30, 11), False),
				(self.tiles["horiz"],     self.screen, (31, 11), False),
				(self.tiles["horiznc"],   self.screen, (32, 11), False),
				(self.tiles["horiz"],     self.screen, (33, 11), False),
				(self.tiles["horiz"],     self.screen, (35, 11), False),
				(self.tiles["horiznc"],   self.screen, (36, 11), False),
				(self.tiles["horiz"],     self.screen, (37, 11), False),
				(self.tiles["horiznc"],   self.screen, (38, 11), False),
				(self.tiles["diagright"], self.screen, (33, 10), False),
				(self.tiles["horiznc"],   self.screen, (30, 9), False),
				(self.tiles["horiz"],     self.screen, (31, 9), False),
				(self.tiles["diagright"], self.screen, (31, 8), False),
				(self.tiles["turnrightright"], self.screen, (30, 7), False),
				(self.tiles["diagleft"],  self.screen, (39, 12), False),
				(self.tiles["horiznc"],   self.screen, (30, 13), False),
				(self.tiles["horiz"],     self.screen, (31, 13), False),
				(self.tiles["horiznc"],   self.screen, (32, 13), False),
				(self.tiles["horiz"],     self.screen, (33, 13), False),
				(self.tiles["horiznc"],   self.screen, (34, 13), False),
				(self.tiles["horiz"],     self.screen, (35, 13), False),
				(self.tiles["horiznc"],   self.screen, (36, 13), False),
				(self.tiles["horiz"],     self.screen, (37, 13), False),
				(self.tiles["diagleft"],  self.screen, (37, 14), False),
				(self.tiles["horiznc"],   self.screen, (30, 15), False),
				(self.tiles["horiz"],     self.screen, (31, 15), False),
				(self.tiles["horiznc"],   self.screen, (32, 15), False),
				(self.tiles["horiz"],     self.screen, (33, 15), False),
				(self.tiles["horiznc"],   self.screen, (34, 15), False),
				(self.tiles["horiz"],     self.screen, (35, 15), False),
				(self.tiles["diagleft"],  self.screen, (35, 16), False),
				(self.tiles["horiznc"],   self.screen, (30, 17), False),
				(self.tiles["horiz"],     self.screen, (31, 17), False),
				(self.tiles["horiznc"],   self.screen, (32, 17), False),
				(self.tiles["horiz"],     self.screen, (33, 17), False),
				(self.tiles["diagleft"],  self.screen, (33, 18), False),
				(self.tiles["turnleftright"],  self.screen, (32, 19), False),
			],
			False)

		self.blocks["NEOSE"] = OverSwitch(self, self.frame, "NEOSE", 
			[
				(self.tiles["horiznc"],   self.screen, (39, 13), False),
				(self.tiles["horiz"],     self.screen, (40, 13), False),
				(self.tiles["horiznc"],   self.screen, (41, 13), False),
				(self.tiles["horiz"],     self.screen, (42, 13), False),
				(self.tiles["diagright"], self.screen, (42, 12), False),

				(self.tiles["diagright"], self.screen, (36, 8), False),
				(self.tiles["diagright"], self.screen, (35, 7), False),
				(self.tiles["diagright"], self.screen, (34, 6), False),
				(self.tiles["diagright"], self.screen, (38, 10), False),
				(self.tiles["turnrightright"], self.screen, (33,5), False),
				(self.tiles["horiznc"],   self.screen, (30, 11), False),
				(self.tiles["horiz"],     self.screen, (31, 11), False),
				(self.tiles["horiznc"],   self.screen, (32, 11), False),
				(self.tiles["horiz"],     self.screen, (33, 11), False),
				(self.tiles["horiz"],     self.screen, (35, 11), False),
				(self.tiles["horiznc"],   self.screen, (36, 11), False),
				(self.tiles["horiz"],     self.screen, (37, 11), False),
				(self.tiles["horiznc"],   self.screen, (38, 11), False),
				(self.tiles["diagright"], self.screen, (33, 10), False),
				(self.tiles["horiznc"],   self.screen, (30, 9), False),
				(self.tiles["horiz"],     self.screen, (31, 9), False),
				(self.tiles["diagright"], self.screen, (31, 8), False),
				(self.tiles["turnrightright"], self.screen, (30, 7), False),
				(self.tiles["horiznc"],   self.screen, (30, 13), False),
				(self.tiles["horiz"],     self.screen, (31, 13), False),
				(self.tiles["horiznc"],   self.screen, (32, 13), False),
				(self.tiles["horiz"],     self.screen, (33, 13), False),
				(self.tiles["horiznc"],   self.screen, (34, 13), False),
				(self.tiles["horiz"],     self.screen, (35, 13), False),
				(self.tiles["horiznc"],   self.screen, (36, 13), False),
				(self.tiles["horiz"],     self.screen, (37, 13), False),
				(self.tiles["diagleft"],  self.screen, (37, 14), False),
				(self.tiles["horiznc"],   self.screen, (30, 15), False),
				(self.tiles["horiz"],     self.screen, (31, 15), False),
				(self.tiles["horiznc"],   self.screen, (32, 15), False),
				(self.tiles["horiz"],     self.screen, (33, 15), False),
				(self.tiles["horiznc"],   self.screen, (34, 15), False),
				(self.tiles["horiz"],     self.screen, (35, 15), False),
				(self.tiles["diagleft"],  self.screen, (35, 16), False),
				(self.tiles["horiznc"],   self.screen, (30, 17), False),
				(self.tiles["horiz"],     self.screen, (31, 17), False),
				(self.tiles["horiznc"],   self.screen, (32, 17), False),
				(self.tiles["horiz"],     self.screen, (33, 17), False),
				(self.tiles["diagleft"],  self.screen, (33, 18), False),
				(self.tiles["turnleftright"],  self.screen, (32, 19), False),
			],
			True)

		self.osBlocks["NWOSTY"] = [ "T12", "W10" ]
		self.osBlocks["NWOSCY"] = [ "N60", "W10", "N32", "N31", "N12", "N22", "N41", "N42", "W20" ]
		self.osBlocks["NWOSW"] = [ "N11", "W10", "N32", "N31", "N12", "N22", "N41", "N42", "W20" ]
		self.osBlocks["NWOSE"] = [ "N21", "W10", "N32", "N31", "N12", "N22", "N41", "N42", "W20" ]
		self.osBlocks["NEOSRH"] = [ "W11", "N32", "N31", "N12", "N22", "N41", "N42", "W20", "R10"]
		self.osBlocks["NEOSW"] = [ "W11", "N32", "N31", "N12", "N22", "N41", "N42", "W20", "B10"]
		self.osBlocks["NEOSE"] = [ "W11", "N32", "N31", "N12", "N22", "N41", "N42", "W20", "B20"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}
		
		# these turnouts are controlled by entry/exit buttons and NOT by direct clicks
		toList = [
			[ "NSw19",  "toleftleft",    ["NWOSE", "NWOSW"], (11, 11) ],
			[ "NSw19b", "toleftright",   ["NWOSE", "NWOSW"], (9, 13) ],
			[ "NSw21", "toleftright",    ["NWOSE", "NWOSW", "NWOSCY"], (13, 11) ],
			[ "NSw25",  "toleftleft",    ["NWOSE", "NWOSW", "NWOSCY", "NWOSTY"], (19, 5) ],
			[ "NSw25b", "torightupinv",  ["NWOSE", "NWOSW", "NWOSCY", "NWOSTY"], (17, 7) ],
			[ "NSw27",  "torightright",  ["NWOSE", "NWOSW", "NWOSCY"], (10, 9) ],
			[ "NSw33",  "toleftdown",    ["NWOSE", "NWOSW", "NWOSCY"], (16, 15) ],
			[ "NSw35",  "toleftdown",    ["NWOSE", "NWOSW", "NWOSCY"], (18, 17) ],
			[ "NSw39",  "torightdown",   ["NEOSE", "NEOSW", "NEOSRH"], (34, 17) ],
			[ "NSw41",  "torightdown",   ["NEOSE", "NEOSW", "NEOSRH"], (36, 15) ],
			[ "NSw47",  "toleftleft",    ["NEOSE", "NEOSW", "NEOSRH"], (42, 9) ],
			[ "NSw51",  "toleftup",      ["NEOSE", "NEOSW", "NEOSRH"], (32, 9) ],
			[ "NSw53",  "torightleft",   ["NEOSE", "NEOSW", "NEOSRH"], (34, 11) ],
			[ "NSw55",  "toleftdowninv", ["NEOSE", "NEOSW", "NEOSRH"], (37, 9) ],
			[ "NSw55b", "torightleft",   ["NEOSE", "NEOSW", "NEOSRH"], (39, 11) ],
			[ "NSw57",  "torightleft",   ["NEOSE", "NEOSW", "NEOSRH"], (43, 13) ],
			[ "NSw57b", "torightright",  ["NEOSE", "NEOSW", "NEOSRH"], (41, 11) ],
		]
		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			trnout.SetRouteControl(True)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		# these turnouts are NOT controlled by dis[atcher
		toList = [
			[ "NSw13",  "toleftup",      ["N60"], (6, 7) ],
			[ "NSw15",  "torightleft",   ["N60"], (6, 9) ],
			[ "NSw17",  "torightleft",   ["N60"], (8, 9) ],
		]
		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
				trnout.SetDisabled(True)
			self.turnouts[tonm] = trnout

		trnout = SlipSwitch(self, self.frame, "NSw29", self.screen, self.totiles["ssleft"], (12, 11))
		blocks["NWOSE"].AddTurnout(trnout)
		blocks["NWOSW"].AddTurnout(trnout)
		blocks["NWOSCY"].AddTurnout(trnout)
		trnout.AddBlock("NWOSE")
		trnout.AddBlock("NWOSW")
		trnout.AddBlock("NWOSCY")
		trnout.SetRouteControl(True)
		trnout.SetControllers(self.turnouts["NSw27"], None)
		self.turnouts["NSw29"] = trnout

		trnout = SlipSwitch(self, self.frame, "NSw31", self.screen, self.totiles["ssleft"], (14, 13))
		blocks["NWOSE"].AddTurnout(trnout)
		blocks["NWOSW"].AddTurnout(trnout)
		blocks["NWOSCY"].AddTurnout(trnout)
		trnout.AddBlock("NWOSE")
		trnout.AddBlock("NWOSW")
		trnout.AddBlock("NWOSCY")
		trnout.SetControllers(self.turnouts["NSw29"], None)
		trnout.SetRouteControl(True)
		self.turnouts["NSw31"] = trnout

		trnout = SlipSwitch(self, self.frame, "NSw23", self.screen, self.totiles["ssright"], (15, 9))
		blocks["NWOSE"].AddTurnout(trnout)
		blocks["NWOSW"].AddTurnout(trnout)
		blocks["NWOSCY"].AddTurnout(trnout)
		trnout.AddBlock("NWOSE")
		trnout.AddBlock("NWOSW")
		trnout.AddBlock("NWOSCY")
		trnout.SetControllers(self.turnouts["NSw21"], None)
		trnout.SetRouteControl(True)
		self.turnouts["NSw23"] = trnout

		trnout = SlipSwitch(self, self.frame, "NSw45", self.screen, self.totiles["ssright"], (40, 11))
		blocks["NEOSE"].AddTurnout(trnout)
		blocks["NEOSW"].AddTurnout(trnout)
		blocks["NEOSRH"].AddTurnout(trnout)
		trnout.AddBlock("NEOSE")
		trnout.AddBlock("NEOSW")
		trnout.AddBlock("NEOSRH")
		trnout.SetControllers(None, self.turnouts["NSw47"])
		trnout.SetRouteControl(True)
		self.turnouts["NSw45"] = trnout

		trnout = SlipSwitch(self, self.frame, "NSw43", self.screen, self.totiles["ssright"], (38, 13))
		blocks["NEOSE"].AddTurnout(trnout)
		blocks["NEOSW"].AddTurnout(trnout)
		blocks["NEOSRH"].AddTurnout(trnout)
		trnout.AddBlock("NEOSE")
		trnout.AddBlock("NEOSW")
		trnout.AddBlock("NEOSRH")
		trnout.SetControllers(None, self.turnouts["NSw45"])
		trnout.SetRouteControl(True)
		self.turnouts["NSw43"] = trnout

		self.turnouts["NSw19"].SetPairedTurnout(self.turnouts["NSw19b"])
		self.turnouts["NSw25"].SetPairedTurnout(self.turnouts["NSw25b"])
		self.turnouts["NSw55"].SetPairedTurnout(self.turnouts["NSw55b"])
		self.turnouts["NSw57"].SetPairedTurnout(self.turnouts["NSw57b"])

		return self.turnouts

	def DefineButtons(self):
		self.buttons = {}
		self.osButtons = {}

		for n in ["NOSW", "NOSE"]:
			self.westButton[n] = self.eastButton[n] = None

		self.buttons["NNXBtnN60"] = Button(self, self.screen, self.frame, "NNXBtnN60", (9, 9), self.btntiles)
		self.buttons["NNXBtnN11"] = Button(self, self.screen, self.frame, "NNXBtnN11", (8, 11), self.btntiles)
		self.buttons["NNXBtnN21"] = Button(self, self.screen, self.frame, "NNXBtnN21", (8, 13), self.btntiles)
		self.buttons["NNXBtnT12"] = Button(self, self.screen, self.frame, "NNXBtnT12", (16, 5), self.btntiles)
		self.westGroup["NOSW"] = ["NNXBtnN60", "NNXBtnN11", "NNXBtnN21", "NNXBtnT12"]

		self.buttons["NNXBtnW10"] = Button(self, self.screen, self.frame, "NNXBtnW10", (20, 5), self.btntiles)
		self.buttons["NNXBtnN32W"] = Button(self, self.screen, self.frame, "NNXBtnN32W", (20, 7), self.btntiles)
		self.buttons["NNXBtnN31W"] = Button(self, self.screen, self.frame, "NNXBtnN31W", (20, 9), self.btntiles)
		self.buttons["NNXBtnN12W"] = Button(self, self.screen, self.frame, "NNXBtnN12W", (20, 11), self.btntiles)
		self.buttons["NNXBtnN22W"] = Button(self, self.screen, self.frame, "NNXBtnN22W", (20, 13), self.btntiles)
		self.buttons["NNXBtnN41W"] = Button(self, self.screen, self.frame, "NNXBtnN41W", (20, 15), self.btntiles)
		self.buttons["NNXBtnN42W"] = Button(self, self.screen, self.frame, "NNXBtnN42W", (20, 17), self.btntiles)
		self.buttons["NNXBtnW20W"] = Button(self, self.screen, self.frame, "NNXBtnW20W", (21, 19), self.btntiles)
		self.eastGroup["NOSW"] = ["NNXBtnW10", "NNXBtnN32W", "NNXBtnN31W", "NNXBtnN12W", "NNXBtnN22W", "NNXBtnN41W", "NNXBtnN42W", "NNXBtnW20W"]

		self.buttons["NNXBtnR10"] = Button(self, self.screen, self.frame, "NNXBtnR10", (44, 9), self.btntiles)
		self.buttons["NNXBtnB10"] = Button(self, self.screen, self.frame, "NNXBtnB10", (44, 11), self.btntiles)
		self.buttons["NNXBtnB20"] = Button(self, self.screen, self.frame, "NNXBtnB20", (44, 13), self.btntiles)
		self.eastGroup["NOSE"] = ["NNXBtnR10", "NNXBtnB10", "NNXBtnB20"]

		self.buttons["NNXBtnW11"] = Button(self, self.screen, self.frame, "NNXBtnW11", (32, 5), self.btntiles)
		self.buttons["NNXBtnN32E"] = Button(self, self.screen, self.frame, "NNXBtnN32E", (29, 7), self.btntiles)
		self.buttons["NNXBtnN31E"] = Button(self, self.screen, self.frame, "NNXBtnN31E", (29, 9), self.btntiles)
		self.buttons["NNXBtnN12E"] = Button(self, self.screen, self.frame, "NNXBtnN12E", (29, 11), self.btntiles)
		self.buttons["NNXBtnN22E"] = Button(self, self.screen, self.frame, "NNXBtnN22E", (29, 13), self.btntiles)
		self.buttons["NNXBtnN41E"] = Button(self, self.screen, self.frame, "NNXBtnN41E", (29, 15), self.btntiles)
		self.buttons["NNXBtnN42E"] = Button(self, self.screen, self.frame, "NNXBtnN42E", (29, 17), self.btntiles)
		self.buttons["NNXBtnW20E"] = Button(self, self.screen, self.frame, "NNXBtnW20E", (31, 19), self.btntiles)
		self.westGroup["NOSE"] = ["NNXBtnW11", "NNXBtnN32E", "NNXBtnN31E", "NNXBtnN12E", "NNXBtnN22E", "NNXBtnN41E", "NNXBtnN42E", "NNXBtnW20E"]

		self.NXMap = {
			"NNXBtnT12": {
				"NNXBtnW10":  "NRtT12W10"
			},

			"NNXBtnN60": {
				"NNXBtnW10":  "NRtN60W10",
				"NNXBtnN32W": "NRtN60N32",
				"NNXBtnN31W": "NRtN60N31",
				"NNXBtnN12W": "NRtN60N12",
				"NNXBtnN22W": "NRtN60N22",
				"NNXBtnN41W": "NRtN60N41",
				"NNXBtnN42W": "NRtN60N42",
				"NNXBtnW20W": "NRtN60W20",
			},

			"NNXBtnN11": {
				"NNXBtnW10":  "NRtN11W10",
				"NNXBtnN32W": "NRtN11N32",
				"NNXBtnN31W": "NRtN11N31",
				"NNXBtnN12W": "NRtN11N12",
				"NNXBtnN22W": "NRtN11N22",
				"NNXBtnN41W": "NRtN11N41",
				"NNXBtnN42W": "NRtN11N42",
				"NNXBtnW20W": "NRtN11W20",
			},

			"NNXBtnN21": {
				"NNXBtnW10":  "NRtN21W10",
				"NNXBtnN32W": "NRtN21N32",
				"NNXBtnN31W": "NRtN21N31",
				"NNXBtnN12W": "NRtN21N12",
				"NNXBtnN22W": "NRtN21N22",
				"NNXBtnN41W": "NRtN21N41",
				"NNXBtnN42W": "NRtN21N42",
				"NNXBtnW20W": "NRtN21W20",
			},

			"NNXBtnW11": {
				"NNXBtnR10": "NRtR10W11",
				"NNXBtnB10": "NRtB10W11",
				"NNXBtnB20": "NRtB20W11",
			},

			"NNXBtnN32E": {
				"NNXBtnR10": "NRtR10N32",
				"NNXBtnB10": "NRtB10N32",
				"NNXBtnB20": "NRtB20N32",
			},

			"NNXBtnN31E": {
				"NNXBtnR10": "NRtR10N31",
				"NNXBtnB10": "NRtB10N31",
				"NNXBtnB20": "NRtB20N31",
			},

			"NNXBtnN12E": {
				"NNXBtnR10": "NRtR10N12",
				"NNXBtnB10": "NRtB10N12",
				"NNXBtnB20": "NRtB20N12",
			},

			"NNXBtnN22E": {
				"NNXBtnR10": "NRtR10N22",
				"NNXBtnB10": "NRtB10N22",
				"NNXBtnB20": "NRtB20N22",
			},

			"NNXBtnN41E": {
				"NNXBtnR10": "NRtR10N41",
				"NNXBtnB10": "NRtB10N41",
				"NNXBtnB20": "NRtB20N41",
			},

			"NNXBtnN42E": {
				"NNXBtnR10": "NRtR10N42",
				"NNXBtnB10": "NRtB10N42",
				"NNXBtnB20": "NRtB20N42",
			},

			"NNXBtnW20E": {
				"NNXBtnR10": "NRtR10W20",
				"NNXBtnB10": "NRtB10W20",
				"NNXBtnB20": "NRtB20W20",
			},
		}

		return self.buttons
	
	def DefineSignals(self):
		self.signals = {}
		self.routes = {}
		self.osSignals = {}
		sigList = [
			[ "N20R", SloAspects, True,    "right", (16, 6) ],
			[ "N18R", SloAspects, True,    "right", (9, 10) ],
			[ "N16R", SloAspects, True,    "rightlong", (8, 12) ],
			[ "N14R", SloAspects, True,    "rightlong", (8, 14) ],

			[ "N20L", SloAspects, False,   "left", (20, 4) ],
			[ "N18LA",SloAspects, False,   "left", (20, 6) ],
			[ "N18LB",SloAspects, False,   "leftlong", (20, 8) ],

			[ "N16L", SloAspects, False,   "leftlong", (20, 10) ],

			[ "N14LA",SloAspects, False,   "leftlong", (20, 12) ],
			[ "N14LB",SloAspects, False,   "left", (20, 14) ],
			[ "N14LC",SloAspects, False,   "left", (20, 16) ],
			[ "N14LD",SloAspects, False,   "left", (21, 18) ],


			[ "N28R", SloAspects, True,    "right", (32, 6) ],

			[ "N26RA",SloAspects, True,    "right", (29, 8) ],
			[ "N26RB",SloAspects, True,    "right", (29, 10) ],
			[ "N26RC",SloAspects, True,    "rightlong", (29, 12) ],

			[ "N24RA",SloAspects, True,    "rightlong", (29, 14) ],
			[ "N24RB",SloAspects, True,    "rightlong", (29, 16) ],
			[ "N24RC",SloAspects, True,    "right", (29, 18) ],
			[ "N24RD",SloAspects, True,    "right", (31, 20) ],

			[ "N28L", SloAspects, False,   "leftlong", (44, 8) ],
			[ "N26L", SloAspects, False,   "leftlong", (44, 10) ],
			[ "N24L", SloAspects, False,   "left", (44, 12) ]
		]

		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.sigLeverMap = {
			"N14.lvr": [ "NWOSE" ],
			"N16.lvr": [ "NWOSW" ],
			"N18.lvr": [ "NWOSCY" ],
			"N20.lvr": [ "NWOSTY" ],
			"N24.lvr": [ "NEOSE" ],
			"N26.lvr": [ "NEOSW" ],
			"N28.lvr": [ "NEOSRH" ]
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		blockSbSigs = {
			# # which signals govern stopping sections, west and east
			"B10": ("N26L",  None),
			"N21": ("K2L",   "N14R"),
			"R10": ("N28L",  None),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

			#"N60": (None,     "N18R"),
		blockSigs = {
			# # which signals govern blocks, west and east
			"N12": ("N16L",   "N26RC"),
			"N21": ("K2L",    "N14R"),
			"N22": ("N14LA",  "N24RA"),
			"N31": ("N18LB",  "N26RB"),
			"N32": ("N18LA",  "N26RA"),
			"N41": ("N14LB",  "N24RB"),
			"N42": ("N14LC",  "N24RC"),
			"B10": ("N26L",   "C22R"),
			"R10": ("N28L",   None),
			"T12": (None,     "N20R"),
			"W10": ("N20L",   None),
			"W11": (None,     "N28R"),
			"W20": ("N14LD",  "N24RD")
		}

		for blknm, siglist in blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		block = self.blocks["NWOSTY"]
		self.routes["NRtT12W10"] = Route(self.screen, block, "NRtT12W10", "W10", [ (17, 5), (18, 5), (19, 5) ], "T12", [RESTRICTING, RESTRICTING], ["NSw25:N"], ["N20R", "N20L"])

		block = self.blocks["NWOSCY"]
		self.routes["NRtN60N31"] = Route(self.screen, block, "NRtN60N31", "N31", [ (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (17, 9), (18, 9), (19, 9) ], "N60", [RESTRICTING, RESTRICTING], ["NSw21:N", "NSw23:N", "NSw27:N"], ["N18LB", "N18R"])
		self.routes["NRtN60N32"] = Route(self.screen, block, "NRtN60N32", "N32", [ (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 8), (17, 7), (18, 7), (19, 7) ], "N60", [RESTRICTING, RESTRICTING], ["NSw21:N", "NSw23:R", "NSw25:N", "NSw27:N"], ["N18LA", "N18R"])
		self.routes["NRtN60W10"] = Route(self.screen, block, "NRtN60W10", "W10", [ (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 8), (17, 7), (18, 6), (19, 5) ], "N60", [RESTRICTING, RESTRICTING], ["NSw21:N", "NSw23:R", "NSw25:R", "NSw27:N"], ["N20L", "N18R"])
		self.routes["NRtN60N12"] = Route(self.screen, block, "NRtN60N12", "N12", [ (10, 9), (11, 10), (12, 11), (13, 11), (14, 11), (15, 11), (16, 11), (17, 11), (18, 11), (19, 11) ], "N60", [RESTRICTING, RESTRICTING], ["NSw21:N", "NSw27:R", "NSw29:N"], ["N16L", "N18R"])
		self.routes["NRtN60N22"] = Route(self.screen, block, "NRtN60N22", "N22", [ (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13) ], "N60", [RESTRICTING, RESTRICTING], ["NSw27:R", "NSw29:R", "NSw31:N"], ["N14LA", "N18R"])
		self.routes["NRtN60N41"] = Route(self.screen, block, "NRtN60N41", "N41", [ (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 15), (18, 15), (19, 15) ], "N60", [RESTRICTING, RESTRICTING], ["NSw27:R", "NSw29:R", "NSw31:R", "NSw33:R"], ["N14LB", "N18R"])
		self.routes["NRtN60N42"] = Route(self.screen, block, "NRtN60N42", "N42", [ (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 17) ], "N60", [RESTRICTING, RESTRICTING], ["NSw27:R", "NSw29:R", "NSw31:R", "NSw33:N", "NSw35:R"], ["N14LC", "N18R"])
		self.routes["NRtN60W20"] = Route(self.screen, block, "NRtN60W20", "W20", [ (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19) ], "N60", [RESTRICTING, RESTRICTING], ["NSw27:R", "NSw29:R", "NSw31:R", "NSw33:N", "NSw35:N"], ["N14LD", "N18R"])

		block = self.blocks["NWOSW"]
		self.routes["NRtN11N31"] = Route(self.screen, block, "NRtN11N31", "N31", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 9), (17, 9), (18, 9), (19, 9) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw21:R", "NSw23:N", "NSw27:N", "NSw29:N"], ["N18LB", "N16R"])
		self.routes["NRtN11N32"] = Route(self.screen, block, "NRtN11N32", "N32", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 8), (17, 7), (18, 7), (19, 7) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw21:R", "NSw23:R", "NSw25:N", "NSw27:N", "NSw29:N"], ["N18LA", "N16R"])
		self.routes["NRtN11W10"] = Route(self.screen, block, "NRtN11W10", "W10", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 8), (17, 7), (18, 6), (19, 5) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw21:R", "NSw23:R", "NSw25:R", "NSw27:N", "NSw29:N"], ["N20L", "N16R"])
		self.routes["NRtN11N12"] = Route(self.screen, block, "NRtN11N12", "N12", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 11), (15, 11), (16, 11), (17, 11), (18, 11), (19, 11) ], "N11", [SLOW, SLOW], ["NSw19:N", "NSw21:N", "NSw27:N", "NSw29:N"], ["N16L", "N16R"])
		self.routes["NRtN11N22"] = Route(self.screen, block, "NRtN11N22", "N22", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 12), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13) ], "N11", [SLOW, SLOW], ["NSw19:N", "NSw27:N", "NSw29:R", "NSw31:N"], ["N14LA", "N16R"])
		self.routes["NRtN11N41"] = Route(self.screen, block, "NRtN11N41", "N41", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 15), (18, 15), (19, 15) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw27:N", "NSw29:R", "NSw31:R", "NSw33:R"], ["N14LB", "N16R"])
		self.routes["NRtN11N42"] = Route(self.screen, block, "NRtN11N42", "N42", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 17) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw27:N", "NSw29:R", "NSw31:R", "NSw33:N", "NSw35:R"], ["N14LC", "N16R"])
		self.routes["NRtN11W20"] = Route(self.screen, block, "NRtN11W20", "W20", [ (9, 11), (10, 11), (11, 11), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19) ], "N11", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw27:N", "NSw29:R", "NSw31:R", "NSw33:N", "NSw35:N"], ["N14LD", "N16R"])

		block = self.blocks["NWOSE"]
		self.routes["NRtN21N31"] = Route(self.screen, block, "NRtN21N31", "N21", [ (9, 13), (10, 12), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 9), (17, 9), (18, 9), (19, 9) ], "N31", [RESTRICTING, RESTRICTING], ["NSw19:R", "NSw21:R", "NSw23:N", "NSw27:N", "NSw29:N"], ["N14R", "N18LB"])
		self.routes["NRtN21N32"] = Route(self.screen, block, "NRtN21N32", "N21", [ (9, 13), (10, 12), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 8), (17, 7), (18, 7), (19, 7) ], "N32", [RESTRICTING, RESTRICTING], ["NSw19:R", "NSw21:R", "NSw23:R", "NSw25:N", "NSw27:N", "NSw29:N"], ["N14R", "N18LA"])
		self.routes["NRtN21W10"] = Route(self.screen, block, "NRtN21W10", "N21", [ (9, 13), (10, 12), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9), (16, 8), (17, 7), (18, 6), (19, 5) ], "W10", [RESTRICTING, RESTRICTING], ["NSw19:R", "NSw21:R", "NSw23:R", "NSw25:R", "NSw27:N", "NSw29:N"], ["N14R", "N20L"])
		self.routes["NRtN21N12"] = Route(self.screen, block, "NRtN21N12", "N21", [ (9, 13), (10, 12), (11, 11), (12, 11), (13, 11), (14, 11), (15, 11), (16, 11), (17, 11), (18, 11), (19, 11) ], "N12", [SLOW, SLOW], ["NSw19:R", "NSw21:N", "NSw27:N", "NSw29:N"], ["N14R", "N16L"])
		self.routes["NRtN21N22"] = Route(self.screen, block, "NRtN21N22", "N21", [ (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13) ], "N22", [SLOW, SLOW], ["NSw19:N", "NSw29:N", "NSw31:N"], ["N14R", "N14LA"])
		self.routes["NRtN21N41"] = Route(self.screen, block, "NRtN21N41", "N21", [ (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 14), (16, 15), (17, 15), (18, 15), (19, 15) ], "N41", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw29:N", "NSw31:R", "NSw33:R"], ["N14R", "N14LB"])
		self.routes["NRtN21N42"] = Route(self.screen, block, "NRtN21N42", "N21", [ (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 17) ], "N42", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw29:N", "NSw31:R", "NSw33:N", "NSw35:R"], ["N14R", "N14LC"])
		self.routes["NRtN21W20"] = Route(self.screen, block, "NRtN21W20", "N21", [ (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19) ], "W20", [RESTRICTING, RESTRICTING], ["NSw19:N", "NSw29:N", "NSw31:R", "NSw33:N", "NSw35:N"], ["N14R", "N14LD"])

		self.signals["N20R"].AddPossibleRoutes("NWOSTY", [ "NRtT12W10" ])
		self.signals["N18R"].AddPossibleRoutes("NWOSCY", [ "NRtN60N31", "NRtN60N32", "NRtN60W10", "NRtN60N12", "NRtN60N22", "NRtN60N41", "NRtN60N42", "NRtN60W20" ])
		self.signals["N16R"].AddPossibleRoutes("NWOSW",  [ "NRtN11N31", "NRtN11N32", "NRtN11W10", "NRtN11N12", "NRtN11N22", "NRtN11N41", "NRtN11N42", "NRtN11W20" ])
		self.signals["N14R"].AddPossibleRoutes("NWOSE",  [ "NRtN21N31", "NRtN21N32", "NRtN21W10", "NRtN21N12", "NRtN21N22", "NRtN21N41", "NRtN21N42", "NRtN21W20" ])

		self.signals["N20L"].AddPossibleRoutes("NWOSTY", [ "NRtT12W10" ])
		self.signals["N20L"].AddPossibleRoutes("NWOSCY", [ "NRtN60W10" ])
		self.signals["N20L"].AddPossibleRoutes("NWOSW",  [ "NRtN11W10" ])
		self.signals["N20L"].AddPossibleRoutes("NWOSE",  [ "NRtN21W10" ])

		self.signals["N18LA"].AddPossibleRoutes("NWOSCY", [ "NRtN60N32" ])
		self.signals["N18LA"].AddPossibleRoutes("NWOSW",  [ "NRtN11N32" ])
		self.signals["N18LA"].AddPossibleRoutes("NWOSE",  [ "NRtN21N32" ])

		self.signals["N18LB"].AddPossibleRoutes("NWOSCY", [ "NRtN60N31" ])
		self.signals["N18LB"].AddPossibleRoutes("NWOSW",  [ "NRtN11N31" ])
		self.signals["N18LB"].AddPossibleRoutes("NWOSE",  [ "NRtN21N31" ])

		self.signals["N16L"].AddPossibleRoutes("NWOSCY", [ "NRtN60N12" ])
		self.signals["N16L"].AddPossibleRoutes("NWOSW",  [ "NRtN11N12" ])
		self.signals["N16L"].AddPossibleRoutes("NWOSE",  [ "NRtN21N12" ])

		self.signals["N14LA"].AddPossibleRoutes("NWOSCY", [ "NRtN60N22" ])
		self.signals["N14LA"].AddPossibleRoutes("NWOSW",  [ "NRtN11N22" ])
		self.signals["N14LA"].AddPossibleRoutes("NWOSE",  [ "NRtN21N22" ])

		self.signals["N14LB"].AddPossibleRoutes("NWOSCY", [ "NRtN60N41" ])
		self.signals["N14LB"].AddPossibleRoutes("NWOSW",  [ "NRtN11N41" ])
		self.signals["N14LB"].AddPossibleRoutes("NWOSE",  [ "NRtN21N41" ])

		self.signals["N14LC"].AddPossibleRoutes("NWOSCY", [ "NRtN60N42" ])
		self.signals["N14LC"].AddPossibleRoutes("NWOSW",  [ "NRtN11N42" ])
		self.signals["N14LC"].AddPossibleRoutes("NWOSE",  [ "NRtN21N42" ])

		self.signals["N14LD"].AddPossibleRoutes("NWOSCY", [ "NRtN60W20" ])
		self.signals["N14LD"].AddPossibleRoutes("NWOSW",  [ "NRtN11W20" ])
		self.signals["N14LD"].AddPossibleRoutes("NWOSE",  [ "NRtN21W20" ])

		self.osSignals["NWOSTY"] = [ "N20R", "N20L" ]
		self.osSignals["NWOSCY"] = [ "N18R", "N20L", "N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD" ]
		self.osSignals["NWOSW"]  = [ "N16R", "N20L", "N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD" ]
		self.osSignals["NWOSE"]  = [ "N14R", "N20L", "N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD" ]

		block = self.blocks["N60"]
		self.routes["NRtN60A"] = Route(self.screen, block, "NRtN60A", None, [ (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 7), (7, 8), (8, 9) ], "NWOSCY", [RESTRICTING, RESTRICTING], [], [])
		self.routes["NRtN60B"] = Route(self.screen, block, "NRtN60B", None, [ (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 8), (8, 9) ], "NWOSCY", [RESTRICTING, RESTRICTING], [], [])
		self.routes["NRtN60C"] = Route(self.screen, block, "NRtN60C", None, [ (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 9), (7, 9), (8, 9) ], "NWOSCY", [RESTRICTING, RESTRICTING], [], [])
		self.routes["NRtN60D"] = Route(self.screen, block, "NRtN60D", None, [ (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9) ], "NWOSCY", [RESTRICTING, RESTRICTING], [], [])
		block.SetRoute(self.routes["NRtN60D"])

		block = self.blocks["NEOSRH"]
		self.routes["NRtR10W11"] = Route(self.screen, block, "NRtR10W11", "R10", [ (33, 5), (34, 6), (35, 7), (36, 8), (37, 9), (38, 9), (39, 9), (40, 9), (41, 9), (42, 9), (43, 9) ], "W11", [RESTRICTING, RESTRICTING], ["NSw47:N", "NSw55:N"], ["N28L", "N28R"])
		self.routes["NRtR10N32"] = Route(self.screen, block, "NRtR10N32", "R10", [ (30, 7), (31, 8), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 10), (42, 9), (43, 9) ], "N32", [RESTRICTING, SLOW], ["NSw45:N", "NSw47:R", "NSw51:N", "NSw53:R", "NSw55:N"], ["N28L", "N26RA"])
		self.routes["NRtR10N31"] = Route(self.screen, block, "NRtR10N31", "R10", [ (30, 9), (31, 9), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 10), (42, 9), (43, 9) ], "N31", [RESTRICTING, SLOW], ["NSw45:N", "NSw47:R", "NSw51:R", "NSw53:R", "NSw55:N"], ["N28L", "N26RB"])
		self.routes["NRtR10N12"] = Route(self.screen, block, "NRtR10N12", "R10", [ (30, 11), (31, 11), (32, 11), (33, 11), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 10), (42, 9), (43, 9) ], "N12", [SLOW, SLOW], ["NSw45:N", "NSw47:R", "NSw53:N", "NSw55:N"], ["N28L", "N26RC"])
		self.routes["NRtR10N22"] = Route(self.screen, block, "NRtR10N22", "R10", [ (30, 13), (31, 13), (32, 13), (33, 13), (34, 13), (35, 13), (36, 13), (37, 13), (38, 13), (39, 12), (40, 11), (41, 10), (42, 9), (43, 9) ], "N22", [SLOW, SLOW], ["NSw43:N", "NSw45:R", "NSw47:R"], ["N28L", "N24RA"])
		self.routes["NRtR10N41"] = Route(self.screen, block, "NRtR10N41", "R10", [ (30, 15), (31, 15), (32, 15), (33, 15), (34, 15), (35, 15), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 10), (42, 9), (43, 9) ], "N41", [SLOW, RESTRICTING], ["NSw41:R", "NSw43:R", "NSw45:R", "NSw47:R"], ["N28L", "N24RB"])
		self.routes["NRtR10N42"] = Route(self.screen, block, "NRtR10N42", "R10", [ (30, 17), (31, 17), (32, 17), (33, 17), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 10), (42, 9), (43, 9) ], "N42", [SLOW, RESTRICTING], ["NSw39:R", "NSw41:N", "NSw43:R", "NSw45:R", "NSw47:R"], ["N28L", "N24RC"])
		self.routes["NRtR10W20"] = Route(self.screen, block, "NRtR10W20", "R10", [ (32, 19), (33, 18), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 10), (42, 9), (43, 9) ], "W20", [RESTRICTING, RESTRICTING], ["NSw39:N", "NSw41:N", "NSw43:R", "NSw45:R", "NSw47:R"], ["N28L", "N24RD"])

		block = self.blocks["NEOSW"]
		self.routes["NRtB10W11"] = Route(self.screen, block, "NRtB10W11", "B10", [ (33, 5), (34, 6), (35, 7), (36, 8), (37, 9), (38, 10), (39, 11), (40, 11), (41, 11), (42, 11), (43, 11) ], "W11", [RESTRICTING, RESTRICTING], ["NSw45:N", "NSw47:N", "NSw55:R", "NSw57:N"], ["N26L", "N28R"])
		self.routes["NRtB10N32"] = Route(self.screen, block, "NRtB10N32", "B10", [ (30, 7), (31, 8), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 11), (43, 11) ], "N32", [RESTRICTING, SLOW], ["NSw45:N", "NSw47:N", "NSw51:N", "NSw53:R", "NSw55:N", "NSw57:N"], ["N26L", "N26RA"])
		self.routes["NRtB10N31"] = Route(self.screen, block, "NRtB10N31", "B10", [ (30, 9), (31, 9), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 11), (43, 11) ], "N31", [RESTRICTING, SLOW], ["NSw45:N", "NSw47:N", "NSw51:R", "NSw53:R", "NSw55:N", "NSw57:N"], ["N26L", "N26RB"])
		self.routes["NRtB10N12"] = Route(self.screen, block, "NRtB10N12", "B10", [ (30, 11), (31, 11), (32, 11), (33, 11), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 11), (43, 11) ], "N12", [RESTRICTING, SLOW], ["NSw45:N", "NSw47:N", "NSw53:N", "NSw55:N", "NSw57:N"], ["N26L", "N26RC"])
		self.routes["NRtB10N22"] = Route(self.screen, block, "NRtB10N22", "B10", [ (30, 13), (31, 13), (32, 13), (33, 13), (34, 13), (35, 13), (36, 13), (37, 13), (38, 13), (39, 12), (40, 11), (41, 11), (42, 11), (43, 11) ], "N22", [RESTRICTING, SLOW], ["NSw43:N", "NSw45:R", "NSw47:N", "NSw57:N"], ["N26L", "N24RA"])
		self.routes["NRtB10N41"] = Route(self.screen, block, "NRtB10N41", "B10", [ (30, 15), (31, 15), (32, 15), (33, 15), (34, 15), (35, 15), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 11), (42, 11), (43, 11) ], "N41", [RESTRICTING, RESTRICTING], ["NSw41:R", "NSw43:R", "NSw45:R", "NSw47:N", "NSw57:N"], ["N26L", "N24RB"])
		self.routes["NRtB10N42"] = Route(self.screen, block, "NRtB10N42", "B10", [ (30, 17), (31, 17), (32, 17), (33, 17), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 11), (42, 11), (43, 11) ], "N42", [RESTRICTING, RESTRICTING], ["NSw39:R", "NSw41:N", "NSw43:R", "NSw45:R", "NSw47:N", "NSw57:N"], ["N26L", "N24RC"])
		self.routes["NRtB10W20"] = Route(self.screen, block, "NRtB10W20", "B10", [ (32, 19), (33, 18), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 12), (40, 11), (41, 11), (42, 11), (43, 11) ], "W20", [RESTRICTING, RESTRICTING], ["NSw39:N", "NSw41:N", "NSw43:R", "NSw45:R", "NSw47:N", "NSw57:N"], ["N26L", "N24RD"])

		block = self.blocks["NEOSE"]
		self.routes["NRtB20W11"] = Route(self.screen, block, "NRtB20W11", "W11", [ (33, 5), (34, 6), (35, 7), (36, 8), (37, 9), (38, 10), (39, 11), (40, 11), (41, 11), (42, 12), (43, 13) ], "B20", [RESTRICTING, RESTRICTING], ["NSw45:N", "NSw47:N", "NSw55:R", "NSw57:R"], ["N28R", "N24L"])
		self.routes["NRtB20N32"] = Route(self.screen, block, "NRtB20N32", "N32", [ (30, 7), (31, 8), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 12), (43, 13) ], "B20", [RESTRICTING, RESTRICTING], ["NSw45:N", "NSw47:N", "NSw51:N", "NSw53:R", "NSw55:N", "NSw57:R"], ["N26RA", "N24L"])
		self.routes["NRtB20N31"] = Route(self.screen, block, "NRtB20N31", "N31", [ (30, 9), (31, 9), (32, 9), (33, 10), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 12), (43, 13) ], "B20", [RESTRICTING, RESTRICTING], ["NSw45:N", "NSw47:N", "NSw51:R", "NSw53:R", "NSw55:N", "NSw57:R"], ["N26RB", "N24L"])
		self.routes["NRtB20N12"] = Route(self.screen, block, "NRtB20N12", "N12", [ (30, 11), (31, 11), (32, 11), (33, 11), (34, 11), (35, 11), (36, 11), (37, 11), (38, 11), (39, 11), (40, 11), (41, 11), (42, 12), (43, 13) ], "B20", [SLOW, RESTRICTING], ["NSw45:N", "NSw47:N", "NSw53:N", "NSw55:N", "NSw57:R"], ["N26RC", "N24L"])
		self.routes["NRtB20N22"] = Route(self.screen, block, "NRtB20N22", "N22", [ (30, 13), (31, 13), (32, 13), (33, 13), (34, 13), (35, 13), (36, 13), (37, 13), (38, 13), (39, 13), (40, 13), (41, 13), (42, 13), (43, 13) ], "B20", [SLOW, RESTRICTING], ["NSw43:N", "NSw45:N", "NSw57:N"], ["N24RA", "N24L"])
		self.routes["NRtB20N41"] = Route(self.screen, block, "NRtB20N41", "N41", [ (30, 15), (31, 15), (32, 15), (33, 15), (34, 15), (35, 15), (36, 15), (37, 14), (38, 13), (39, 13), (40, 13), (41, 13), (42, 13), (43, 13) ], "B20", [SLOW, RESTRICTING], ["NSw41:R", "NSw43:R", "NSw45:N", "NSw57:N"], ["N24RB", "N24L"])
		self.routes["NRtB20N42"] = Route(self.screen, block, "NRtB20N42", "N42", [ (30, 17), (31, 17), (32, 17), (33, 17), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 13), (40, 13), (41, 13), (42, 13), (43, 13) ], "B20", [SLOW, RESTRICTING], ["NSw39:R", "NSw41:N", "NSw43:R", "NSw45:N", "NSw57:N"], ["N24RC", "N24L"])
		self.routes["NRtB20W20"] = Route(self.screen, block, "NRtB20W20", "W20", [ (32, 19), (33, 18), (34, 17), (35, 16), (36, 15), (37, 14), (38, 13), (39, 13), (40, 13), (41, 13), (42, 13), (43, 13) ], "B20", [RESTRICTING, RESTRICTING], ["NSw39:N", "NSw41:N", "NSw43:R", "NSw45:N", "NSw57:N"], ["N24RD", "N24L"])

		self.signals["N28L"].AddPossibleRoutes("NEOSRH", [ "NRtR10W11", "NRtR10N32", "NRtR10N31", "NRtR10N12", "NRtR10N22", "NRtR10N41", "NRtR10N42", "NRtR10W20" ])
		self.signals["N26L"].AddPossibleRoutes("NEOSW",  [ "NRtB10W11", "NRtB10N32", "NRtB10N31", "NRtB10N12", "NRtB10N22", "NRtB10N41", "NRtB10N42", "NRtB10W20" ])
		self.signals["N24L"].AddPossibleRoutes("NEOSE",  [ "NRtB20W11", "NRtB20N32", "NRtB20N31", "NRtB20N12", "NRtB20N22", "NRtB20N41", "NRtB20N42", "NRtB20W20" ])

		self.signals["N28R"].AddPossibleRoutes("NEOSRH", [ "NRtR10W11" ])
		self.signals["N28R"].AddPossibleRoutes("NEOSW", [ "NRtB10W11" ])
		self.signals["N28R"].AddPossibleRoutes("NEOSE", [ "NRtB20W11" ])

		self.signals["N26RA"].AddPossibleRoutes("NEOSRH", [ "NRtR10N32" ])
		self.signals["N26RA"].AddPossibleRoutes("NEOSW", [ "NRtB10N32" ])
		self.signals["N26RA"].AddPossibleRoutes("NEOSE", [ "NRtB20N32" ])

		self.signals["N26RB"].AddPossibleRoutes("NEOSRH", [ "NRtR10N31" ])
		self.signals["N26RB"].AddPossibleRoutes("NEOSW", [ "NRtB10N31" ])
		self.signals["N26RB"].AddPossibleRoutes("NEOSE", [ "NRtB20N31" ])

		self.signals["N26RC"].AddPossibleRoutes("NEOSRH", [ "NRtR10N12" ])
		self.signals["N26RC"].AddPossibleRoutes("NEOSW", [ "NRtB10N12" ])
		self.signals["N26RC"].AddPossibleRoutes("NEOSE", [ "NRtB20N12" ])

		self.signals["N24RA"].AddPossibleRoutes("NEOSRH", [ "NRtR10N22" ])
		self.signals["N24RA"].AddPossibleRoutes("NEOSW", [ "NRtB10N22" ])
		self.signals["N24RA"].AddPossibleRoutes("NEOSE", [ "NRtB20N22" ])

		self.signals["N24RB"].AddPossibleRoutes("NEOSRH", [ "NRtR10N41" ])
		self.signals["N24RB"].AddPossibleRoutes("NEOSW", [ "NRtB10N41" ])
		self.signals["N24RB"].AddPossibleRoutes("NEOSE", [ "NRtB20N41" ])

		self.signals["N24RC"].AddPossibleRoutes("NEOSRH", [ "NRtR10N42" ])
		self.signals["N24RC"].AddPossibleRoutes("NEOSW", [ "NRtB10N42" ])
		self.signals["N24RC"].AddPossibleRoutes("NEOSE", [ "NRtB20N42" ])

		self.signals["N24RD"].AddPossibleRoutes("NEOSRH", [ "NRtR10W20" ])
		self.signals["N24RD"].AddPossibleRoutes("NEOSW", [ "NRtB10W20" ])
		self.signals["N24RD"].AddPossibleRoutes("NEOSE", [ "NRtB20W20" ])

		self.osSignals["NEOSRH"] = [ "N28L", "N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD" ]
		self.osSignals["NEOSW"] = [ "N26L", "N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD" ]
		self.osSignals["NEOSE"] = [ "N24L", "N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD" ]

		return self.signals

