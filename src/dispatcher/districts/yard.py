from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route
from dispatcher.turnout import Turnout, SlipSwitch
from dispatcher.signal import Signal
from dispatcher.button import Button
from dispatcher.indicator import Indicator

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING, SLOW, NORMAL, REVERSE, EMPTY, SLIPSWITCH, RegAspects, AdvAspects, RegSloAspects

CJBlocks = ["YOSCJE", "YOSCJW"]
EEBlocks = ["YOSEJE", "YOSEJW"]


class Yard (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)
		self.buttonToRoute = None
		self.sw17 = None
		self.sw21 = None

	def Draw(self):
		District.Draw(self)
		self.drawCrossover()

	def DrawOthers(self, block):
		if block.GetName() in ["YOSKL1", "YOSKL2", "YOSKL3"]:
			self.drawCrossover()

	def drawCrossover(self):
		s17 = NORMAL if self.sw17.IsNormal() else REVERSE
		s21 = NORMAL if self.sw21.IsNormal() else REVERSE

		if s17 == REVERSE:
			blkstat = self.sw17.GetBlockStatus()
		elif s21 == REVERSE:
			blkstat = self.sw21.GetBlockStatus()
		else:
			blkstat = EMPTY

		bmp = "diagright" if s17 == REVERSE else "diagleft" if s21 == REVERSE else "cross"
		bmp = self.misctiles["crossover"].getBmp(blkstat, bmp)
		self.frame.DrawTile(self.screen, (104, 12), bmp)

	def DoTurnoutAction(self, turnout, state, force=False):
		tn = turnout.GetName()
		if turnout.GetType() == SLIPSWITCH:
			if tn == "YSw19":
				bstat = NORMAL if self.turnouts["YSw17"].IsNormal() else REVERSE
				turnout.SetStatus([state, bstat])
				turnout.Draw()

		else:
			District.DoTurnoutAction(self, turnout, state, force=force)

		if tn in [ "YSw17", "YSw19", "YSw21" ]:
			self.drawCrossover()
			if tn == "YSw17":
				trnout = self.turnouts["YSw19"]
				trnout.UpdateStatus()
				trnout.Draw()

	def DoBlockAction(self, blk, blockend, state):
		District.DoBlockAction(self, blk, blockend, state)

		bname = blk.GetName()
		if bname != "Y20":
			return

		Y20H = not blk.IsSectionOccupied(None) and not blk.IsSectionOccupied("E") and blk.GetEast()
		Y20D = Y20H and blk.IsClear and blk.GetEast()
		self.indicators["Y20H"].SetValue(1 if Y20H else 0)
		self.indicators["Y20D"].SetValue(1 if Y20D else 0)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, [
			"YSw1", "YSw3", "YSw7", "YSw9", "YSw11", "YSw17", "YSw19", "YSw21", "YSw23", "YSw25",
			"YSw27", "YSw29", "YSw33", "YSw113", "YSw115", "YSw116", "YSw131", "YSw132", "YSw134"])

	def CrossingEastWestBoundary(self, blk1, blk2):
		if blk1.GetName() == "YOSKL4" and blk2.GetName() == "Y30":
			return True
		if blk1.GetName() == "YOSKL1" and blk2.GetName() == "Y70":
			return True
		if blk1.GetName() == "YOSKL2" and blk2.GetName() == "Y70":
			return True

		return False

	def PerformSignalAction(self, sig):
		controlOpt = self.frame.rbYardControl.GetSelection()
		if controlOpt == 0:  # Yard local control
			self.frame.PopupEvent("Yard control is local")
			return

		District.PerformSignalAction(self, sig)

	def PerformButtonAction(self, btn):
		controlOpt = self.frame.rbYardControl.GetSelection()
		if controlOpt == 0:  # yard local control
			btn.Press(refresh=False)
			btn.Invalidate(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			self.frame.PopupEvent("Yard control is local")
			return

		District.PerformButtonAction(self, btn)
		bname = btn.GetName()
		if bname in self.osButtons["YOSCJW"]:
			self.DoEntryExitButtons(btn, "YOSCJ", interval=2)
		elif bname in self.osButtons["YOSEJW"]:
			self.DoEntryExitButtons(btn, "YOSEJ", interval=2)
		elif bname in self.osButtons["YOSKL1"]:
			self.DoEntryExitButtons(btn, "YOSKL", interval=2)
		else:
			rtname = self.buttonToRoute[bname]
			rte = self.routes[rtname]
			tolist = rte.GetSetTurnouts()
			osBlk = rte.GetOS()
			osname = osBlk.GetName()
			if osBlk.IsBusy():
				self.ReportBlockBusy(osname)
				return

			btn.Press(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			self.MatrixTurnoutRequest(tolist, interval=2)
			self.frame.Request({"nxbutton": { "button": bname}})

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["Y10"] = Block(self, self.frame, "Y10",
			[
				(self.tiles["horiz"],    self.screen, (107, 11), False),
				(self.tiles["horiznc"],  self.screen, (108, 11), False),
				(self.tiles["horiz"],    self.screen, (109, 11), False),
				(self.tiles["horiznc"],  self.screen, (110, 11), False),
				(self.tiles["horiz"],    self.screen, (111, 11), False),
				(self.tiles["horiznc"],  self.screen, (112, 11), False),
				(self.tiles["horiz"],    self.screen, (113, 11), False),
			], False)
		self.blocks["Y10"].AddTrainLoc(self.screen, (108, 11))

		self.blocks["Y11"] = Block(self, self.frame, "Y11",
			[
				(self.tiles["horiz"],    self.screen, (124, 11), False),
				(self.tiles["horiznc"],  self.screen, (125, 11), False),
				(self.tiles["horiz"],    self.screen, (126, 11), False),
				(self.tiles["horiznc"],  self.screen, (127, 11), False),
				(self.tiles["horiz"],    self.screen, (128, 11), False),
			], False)
		self.blocks["Y11"].AddTrainLoc(self.screen, (123, 11))
		self.blocks["Y11"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (122, 11), False),
				(self.tiles["horiznc"],  self.screen, (123, 11), False),
			], False)

		self.blocks["Y20"] = Block(self, self.frame, "Y20",
			[
				(self.tiles["horiz"],    self.screen, (107, 13), False),
				(self.tiles["horiznc"],  self.screen, (108, 13), False),
				(self.tiles["horiz"],    self.screen, (109, 13), False),
				(self.tiles["horiznc"],  self.screen, (110, 13), False),
				(self.tiles["horiz"],    self.screen, (111, 13), False),
			], True)
		self.blocks["Y20"].AddTrainLoc(self.screen, (108, 13))
		self.blocks["Y20"].AddStoppingBlock([
				(self.tiles["horiznc"],  self.screen, (112, 13), False),
				(self.tiles["horiz"],    self.screen, (113, 13), False),
			], True)

		self.blocks["Y21"] = Block(self, self.frame, "Y21",
			[
				(self.tiles["horiz"],    self.screen, (124, 13), False),
				(self.tiles["horiznc"],  self.screen, (125, 13), False),
				(self.tiles["horiz"],    self.screen, (126, 13), False),
			], True)
		self.blocks["Y21"].AddTrainLoc(self.screen, (123, 13))
		self.blocks["Y21"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (122, 13), False),
				(self.tiles["horiznc"],  self.screen, (123, 13), False),
			], False)
		self.blocks["Y21"].AddStoppingBlock([
				(self.tiles["horiznc"],  self.screen, (127, 13), False),
				(self.tiles["horiz"],    self.screen, (128, 13), False),
			], True)

		self.blocks["Y30"] = Block(self, self.frame, "Y30",
			[
				(self.tiles["turnrightleft"],  self.screen, (110, 7), False),
				(self.tiles["diagright"],      self.screen, (109, 6), False),
				(self.tiles["diagright"],      self.screen, (108, 5), False),
				(self.tiles["diagright"],      self.screen, (107, 4), False),
				(self.tiles["turnrightright"], self.screen, (106, 3), False),
				(self.tiles["horiz"],          self.screen, (83, 3), False),
				(self.tiles["horiznc"],        self.screen, (84, 3), False),
				(self.tiles["horiz"],          self.screen, (85, 3), False),
				(self.tiles["horiznc"],        self.screen, (86, 3), False),
				(self.tiles["horiz"],          self.screen, (87, 3), False),
				(self.tiles["horiznc"],        self.screen, (88, 3), False),
				(self.tiles["horiz"],          self.screen, (89, 3), False),
				(self.tiles["horiznc"],        self.screen, (90, 3), False),
				(self.tiles["horiz"],          self.screen, (91, 3), False),
				(self.tiles["horiznc"],        self.screen, (92, 3), False),
				(self.tiles["horiz"],          self.screen, (93, 3), False),
				(self.tiles["horiznc"],        self.screen, (94, 3), False),
				(self.tiles["horiz"],          self.screen, (95, 3), False),
				(self.tiles["horiznc"],        self.screen, (96, 3), False),
				(self.tiles["horiz"],          self.screen, (97, 3), False),
				(self.tiles["horiznc"],        self.screen, (98, 3), False),
				(self.tiles["horiz"],          self.screen, (99, 3), False),
				(self.tiles["horiznc"],        self.screen, (100, 3), False),
				(self.tiles["horiz"],          self.screen, (101, 3), False),
				(self.tiles["horiznc"],        self.screen, (102, 3), False),
				(self.tiles["horiz"],          self.screen, (103, 3), False),
				(self.tiles["horiznc"],        self.screen, (104, 3), False),
				(self.tiles["horiz"],          self.screen, (105, 3), False),
				(self.tiles["turnleftleft"],   self.screen, (82, 3), False),
				(self.tiles["turnrightup"],    self.screen, (81, 4), False),
				(self.tiles["vertical"],       self.screen, (81, 5), False),
				(self.tiles["verticalnc"],     self.screen, (81, 6), False),
				(self.tiles["vertical"],       self.screen, (81, 7), False),
				(self.tiles["verticalnc"],     self.screen, (81, 8), False),
				(self.tiles["vertical"],       self.screen, (81, 9), False),
				(self.tiles["verticalnc"],     self.screen, (81, 10), False),
				(self.tiles["vertical"],       self.screen, (81, 11), False),
				(self.tiles["turnleftdown"],   self.screen, (81, 12), False),
				(self.tiles["turnrightleft"],  self.screen, (82, 13), False),
				(self.tiles["eobright"],       self.screen, (83, 13), False),
			], False)
		self.blocks["Y30"].AddTrainLoc(self.screen, (85, 3))

		self.blocks["Y50"] = Block(self, self.frame, "Y50",
			[
				(self.tiles["horiznc"],        self.screen, (89, 15), False),
				(self.tiles["horiz"],          self.screen, (90, 15), False),
				(self.tiles["horiznc"],        self.screen, (91, 15), False),
				(self.tiles["horiz"],          self.screen, (92, 15), False),
				(self.tiles["horiznc"],        self.screen, (93, 15), False),
				(self.tiles["horiz"],          self.screen, (94, 15), False),
				(self.tiles["horiznc"],        self.screen, (95, 15), False),
			], True)
		self.blocks["Y50"].AddTrainLoc(self.screen, (90, 15))

		self.blocks["Y51"] = Block(self, self.frame, "Y51",
			[
				(self.tiles["horiznc"],        self.screen, (89, 13), False),
				(self.tiles["horiz"],          self.screen, (90, 13), False),
				(self.tiles["horiznc"],        self.screen, (91, 13), False),
				(self.tiles["horiz"],          self.screen, (92, 13), False),
				(self.tiles["horiznc"],        self.screen, (93, 13), False),
				(self.tiles["horiz"],          self.screen, (94, 13), False),
				(self.tiles["horiznc"],        self.screen, (95, 13), False),
			], True)
		self.blocks["Y51"].AddTrainLoc(self.screen, (90, 13))

		self.blocks["Y52"] = Block(self, self.frame, "Y52",
			[
				(self.tiles["eobleft"],        self.screen, (85, 9), False),
				(self.tiles["horiz"],          self.screen, (86, 9), False),
				(self.tiles["horiznc"],        self.screen, (87, 9), False),
				(self.tiles["horiz"],          self.screen, (88, 9), False),
				(self.tiles["horiznc"],        self.screen, (89, 9), False),
				(self.tiles["horiz"],          self.screen, (90, 9), False),
				(self.tiles["horiznc"],        self.screen, (91, 9), False),
				(self.tiles["horiz"],          self.screen, (92, 9), False),
				(self.tiles["horiznc"],        self.screen, (93, 9), False),
				(self.tiles["horiz"],          self.screen, (94, 9), False),
			], True)
		self.blocks["Y52"].AddTrainLoc(self.screen, (86, 9))

		self.blocks["Y53"] = Block(self, self.frame, "Y53",
			[
				(self.tiles["eobleft"],        self.screen, (85, 7), False),
				(self.tiles["horiz"],          self.screen, (86, 7), False),
				(self.tiles["horiznc"],        self.screen, (87, 7), False),
				(self.tiles["horiz"],          self.screen, (88, 7), False),
				(self.tiles["horiznc"],        self.screen, (89, 7), False),
				(self.tiles["horiz"],          self.screen, (90, 7), False),
				(self.tiles["horiznc"],        self.screen, (91, 7), False),
				(self.tiles["horiz"],          self.screen, (92, 7), False),
				(self.tiles["horiznc"],        self.screen, (93, 7), False),
				(self.tiles["horiz"],          self.screen, (94, 7), False),
			], True)
		self.blocks["Y53"].AddTrainLoc(self.screen, (86, 7))

		self.blocks["Y60"] = Block(self, self.frame, "Y60",
			[
				(self.tiles["houtline"],       self.screen, (93, 5), False),
				(self.tiles["houtline"],       self.screen, (94, 5), False),
			], True)

		self.blocks["Y70"] = Block(self, self.frame, "Y70",
			[
				(self.tiles["houtline"],       self.screen, (93, 11), False),
				(self.tiles["houtline"],       self.screen, (94, 11), False),
				(self.tiles["houtline"],       self.screen, (95, 11), False),
				(self.tiles["horiznc"],        self.screen, (13, 30), False),
				(self.tiles["horiz"],          self.screen, (14, 30), False),
				(self.tiles["horiznc"],        self.screen, (15, 30), False),
				(self.tiles["horiz"],          self.screen, (16, 30), False),
				(self.tiles["horiznc"],        self.screen, (17, 30), False),
				(self.tiles["horiz"],          self.screen, (18, 30), False),
				(self.tiles["horiznc"],        self.screen, (19, 30), False),
				(self.tiles["eobright"],       self.screen, (20, 30), False),
			], False)
		self.blocks["Y70"].AddTrainLoc(self.screen, (14, 30))

		self.blocks["Y81"] = Block(self, self.frame, "Y81",
			[
				(self.tiles["horiznc"],        self.screen, (33, 30), False),
				(self.tiles["horiz"],          self.screen, (34, 30), False),
				(self.tiles["horiznc"],        self.screen, (35, 30), False),
				(self.tiles["horiz"],          self.screen, (36, 30), False),
				(self.tiles["horiznc"],        self.screen, (37, 30), False),
				(self.tiles["horiz"],          self.screen, (38, 30), False),
				(self.tiles["horiznc"],        self.screen, (39, 30), False),
				(self.tiles["horiz"],          self.screen, (40, 30), False),
				(self.tiles["horiznc"],        self.screen, (41, 30), False),
				(self.tiles["horiz"],          self.screen, (42, 30), False),
				(self.tiles["horiznc"],        self.screen, (43, 30), False),
				(self.tiles["horiz"],          self.screen, (44, 30), False),
			], False)
		self.blocks["Y81"].AddTrainLoc(self.screen, (34, 30))

		self.blocks["Y82"] = Block(self, self.frame, "Y82",
			[
				(self.tiles["horiznc"],        self.screen, (33, 32), False),
				(self.tiles["horiz"],          self.screen, (34, 32), False),
				(self.tiles["horiznc"],        self.screen, (35, 32), False),
				(self.tiles["horiz"],          self.screen, (36, 32), False),
				(self.tiles["horiznc"],        self.screen, (37, 32), False),
				(self.tiles["horiz"],          self.screen, (38, 32), False),
				(self.tiles["horiznc"],        self.screen, (39, 32), False),
				(self.tiles["horiz"],          self.screen, (40, 32), False),
				(self.tiles["horiznc"],        self.screen, (41, 32), False),
				(self.tiles["horiz"],          self.screen, (42, 32), False),
				(self.tiles["horiznc"],        self.screen, (43, 32), False),
				(self.tiles["horiz"],          self.screen, (44, 32), False),
			], False)
		self.blocks["Y82"].AddTrainLoc(self.screen, (34, 32))

		self.blocks["Y83"] = Block(self, self.frame, "Y83",
			[
				(self.tiles["horiznc"],        self.screen, (33, 34), False),
				(self.tiles["horiz"],          self.screen, (34, 34), False),
				(self.tiles["horiznc"],        self.screen, (35, 34), False),
				(self.tiles["horiz"],          self.screen, (36, 34), False),
				(self.tiles["horiznc"],        self.screen, (37, 34), False),
				(self.tiles["horiz"],          self.screen, (38, 34), False),
				(self.tiles["horiznc"],        self.screen, (39, 34), False),
				(self.tiles["horiz"],          self.screen, (40, 34), False),
				(self.tiles["horiznc"],        self.screen, (41, 34), False),
				(self.tiles["horiz"],          self.screen, (42, 34), False),
				(self.tiles["horiznc"],        self.screen, (43, 34), False),
				(self.tiles["horiz"],          self.screen, (44, 34), False),
			], False)
		self.blocks["Y83"].AddTrainLoc(self.screen, (34, 34))

		self.blocks["Y84"] = Block(self, self.frame, "Y84",
			[
				(self.tiles["horiznc"],        self.screen, (33, 36), False),
				(self.tiles["horiz"],          self.screen, (34, 36), False),
				(self.tiles["horiznc"],        self.screen, (35, 36), False),
				(self.tiles["horiz"],          self.screen, (36, 36), False),
				(self.tiles["horiznc"],        self.screen, (37, 36), False),
				(self.tiles["horiz"],          self.screen, (38, 36), False),
				(self.tiles["horiznc"],        self.screen, (39, 36), False),
				(self.tiles["horiz"],          self.screen, (40, 36), False),
				(self.tiles["horiznc"],        self.screen, (41, 36), False),
				(self.tiles["horiz"],          self.screen, (42, 36), False),
				(self.tiles["horiznc"],        self.screen, (43, 36), False),
				(self.tiles["horiz"],          self.screen, (44, 36), False),
			], False)
		self.blocks["Y84"].AddTrainLoc(self.screen, (34, 36))

		self.blocks["Y87"] = Block(self, self.frame, "Y87",
			[
				(self.tiles["eobleft"],        self.screen, (56, 30), False),
				(self.tiles["horiz"],          self.screen, (57, 30), False),
				(self.tiles["horiznc"],        self.screen, (58, 30), False),
				(self.tiles["horiz"],          self.screen, (59, 30), False),
				(self.tiles["horiznc"],        self.screen, (60, 30), False),
				(self.tiles["horiz"],          self.screen, (61, 30), False),
				(self.tiles["horiznc"],        self.screen, (62, 30), False),
				(self.tiles["horiz"],          self.screen, (63, 30), False),
				(self.tiles["horiznc"],        self.screen, (64, 30), False),
				(self.tiles["houtline"],       self.screen, (110, 9), False),
				(self.tiles["houtline"],       self.screen, (111, 9), False),
				(self.tiles["houtline"],       self.screen, (112, 9), False),
			], False)
		self.blocks["Y87"].AddTrainLoc(self.screen, (57, 30))

		self.blocks["YOSEJW"] = OverSwitch(self, self.frame, "YOSEJW", 
			[
				(self.tiles["horiznc"],        self.screen, (112, 7), False),
				(self.tiles["turnrightright"], self.screen, (113, 7), False),
				(self.tiles["diagright"],      self.screen, (114, 8), False),
				(self.tiles["diagright"],      self.screen, (116, 10), False),
				(self.tiles["horiz"],          self.screen, (114, 9), False),
				(self.tiles["horiz"],          self.screen, (115, 11), False),
				(self.tiles["horiznc"],        self.screen, (116, 11), False),
				(self.tiles["horiz"],          self.screen, (119, 11), False),
				(self.tiles["horiznc"],        self.screen, (120, 11), False),
			],
			False)

		self.blocks["YOSEJE"] = OverSwitch(self, self.frame, "YOSEJE", 
			[
				(self.tiles["horiznc"],        self.screen, (112, 7), False),
				(self.tiles["turnrightright"], self.screen, (113, 7), False),
				(self.tiles["diagright"],      self.screen, (114, 8), False),
				(self.tiles["diagright"],      self.screen, (116, 10), False),
				(self.tiles["horiz"],          self.screen, (114, 9), False),
				(self.tiles["horiz"],          self.screen, (115, 11), False),
				(self.tiles["horiznc"],        self.screen, (116, 11), False),
				(self.tiles["diagright"],      self.screen, (119, 12), False),
				(self.tiles["horiz"],          self.screen, (115, 13), False),
				(self.tiles["horiznc"],        self.screen, (116, 13), False),
				(self.tiles["horiz"],          self.screen, (117, 13), False),
				(self.tiles["horiznc"],        self.screen, (118, 13), False),
				(self.tiles["horiz"],          self.screen, (119, 13), False),
			],
			True)

		self.blocks["YOSCJE"] = OverSwitch(self, self.frame, "YOSCJE", 
			[
				(self.tiles["horiznc"],  self.screen, (130, 13), False),
				(self.tiles["horiznc"],  self.screen, (131, 13), False),
				(self.tiles["horiz"],    self.screen, (134, 13), False),
				(self.tiles["horiznc"],  self.screen, (135, 13), False),
				(self.tiles["diagright"], self.screen, (134, 14), False),
				(self.tiles["turnrightleft"], self.screen, (135, 15), True),
			],
			True)

		self.blocks["YOSCJW"] = OverSwitch(self, self.frame, "YOSCJW", 
			[
				(self.tiles["horiznc"],  self.screen, (131, 11), False),
				(self.tiles["horiz"],    self.screen, (132, 11), False),
				(self.tiles["horiznc"],  self.screen, (133, 11), False),
				(self.tiles["horiz"],    self.screen, (134, 11), False),
				(self.tiles["horiznc"],  self.screen, (135, 11), False),
				(self.tiles["diagright"],self.screen, (131, 12), False),
				(self.tiles["horiz"],    self.screen, (134, 13), False),
				(self.tiles["horiznc"],  self.screen, (135, 13), False),
				(self.tiles["diagright"], self.screen, (134, 14), False),
				(self.tiles["turnrightleft"], self.screen, (135, 15), True),
			],
			False)

		self.blocks["YOSKL2"] = OverSwitch(self, self.frame, "YOSKL2", 
			[
				(self.tiles["horiznc"],       self.screen, (104, 11), False),
				(self.tiles["turnrightright"],self.screen, (96, 7), False),
				(self.tiles["diagright"],     self.screen, (97, 8), False),
				(self.tiles["diagright"],     self.screen, (99, 10), False),
				(self.tiles["horiz"],         self.screen, (101, 11), False),
				(self.tiles["horiznc"],       self.screen, (102, 11), False),
				(self.tiles["horiz"],         self.screen, (96, 9), False),
				(self.tiles["horiznc"],       self.screen, (97, 9), False),
				(self.tiles["turnrightright"],self.screen, (97, 11), False),
				(self.tiles["diagright"],     self.screen, (98, 12), False),
				(self.tiles["horiznc"],       self.screen, (101, 13), False),
				(self.tiles["horiz"],         self.screen, (97, 13), False),
				(self.tiles["horiznc"],       self.screen, (98, 13), False),
				(self.tiles["horiz"],         self.screen, (97, 15), False),
				(self.tiles["turnleftright"], self.screen, (98, 15), False),
				(self.tiles["diagleft"],      self.screen, (99, 14), False),
			],
			False)

		self.blocks["YOSKL3"] = OverSwitch(self, self.frame, "YOSKL3", 
			[
				(self.tiles["horiz"],         self.screen, (96, 5), False),
				(self.tiles["turnrightright"],self.screen, (97, 5), False),
				(self.tiles["diagright"],     self.screen, (98, 6), False),
				(self.tiles["diagright"],     self.screen, (99, 7), False),
				(self.tiles["diagright"],     self.screen, (100, 8), False),
				(self.tiles["diagright"],     self.screen, (101, 9), False),
				(self.tiles["diagright"],     self.screen, (102, 10), False),
				(self.tiles["horiznc"],       self.screen, (104, 11), False),
			],
			False)

		self.blocks["YOSKL1"] = OverSwitch(self, self.frame, "YOSKL1", 
			[
				(self.tiles["horiznc"],       self.screen, (104, 13), False),
				(self.tiles["turnrightright"],self.screen, (96, 7), False),
				(self.tiles["diagright"],     self.screen, (97, 8), False),
				(self.tiles["diagright"],     self.screen, (99, 10), False),
				(self.tiles["diagright"],     self.screen, (101, 12), False),
				(self.tiles["horiznc"],       self.screen, (102, 11), False),
				(self.tiles["horiz"],         self.screen, (96, 9), False),
				(self.tiles["horiznc"],       self.screen, (97, 9), False),
				(self.tiles["turnrightright"],self.screen, (97, 11), False),
				(self.tiles["diagright"],     self.screen, (98, 12), False),
				(self.tiles["horiznc"],       self.screen, (101, 13), False),
				(self.tiles["horiz"],         self.screen, (97, 13), False),
				(self.tiles["horiznc"],       self.screen, (98, 13), False),
				(self.tiles["horiz"],         self.screen, (97, 15), False),
				(self.tiles["turnleftright"], self.screen, (98, 15), False),
				(self.tiles["diagleft"],      self.screen, (99, 14), False),
			],
			True)

		self.blocks["YOSKL4"] = OverSwitch(self, self.frame, "YOSKL4", 
			[
				(self.tiles["eobleft"],       self.screen, (84, 13), False),
				(self.tiles["horiznc"],       self.screen, (86, 13), False),
				(self.tiles["horiz"],         self.screen, (87, 13), False),
				(self.tiles["diagright"],     self.screen, (86, 14), False),
				(self.tiles["turnrightleft"], self.screen, (87, 15), False),
			],
			True)

		self.blocks["YOSWYE"] = OverSwitch(self, self.frame, "YOSWYE", 
			[
				(self.tiles["horiznc"],       self.screen, (46, 30), False),
				(self.tiles["horiz"],         self.screen, (47, 30), False),
				(self.tiles["horiznc"],       self.screen, (48, 30), False),
				(self.tiles["horiz"],         self.screen, (49, 30), False),
				(self.tiles["horiznc"],       self.screen, (50, 30), False),
				(self.tiles["horiz"],         self.screen, (52, 30), False),
				(self.tiles["horiznc"],       self.screen, (53, 30), False),
				(self.tiles["eobright"],      self.screen, (55, 30), False),
				(self.tiles["horiznc"],       self.screen, (46, 32), False),
				(self.tiles["horiz"],         self.screen, (47, 32), False),
				(self.tiles["horiznc"],       self.screen, (48, 32), False),
				(self.tiles["diagleft"],      self.screen, (50, 31), False),
				(self.tiles["diagleft"],      self.screen, (48, 33), False),
				(self.tiles["diagleft"],      self.screen, (53, 31), False),
				(self.tiles["diagleft"],      self.screen, (52, 32), False),
				(self.tiles["diagleft"],      self.screen, (51, 33), False),
				(self.tiles["diagleft"],      self.screen, (50, 34), False),
				(self.tiles["diagleft"],      self.screen, (49, 35), False),
				(self.tiles["turnleftright"], self.screen, (47, 34), False),
				(self.tiles["turnleftright"], self.screen, (48, 36), False),
				(self.tiles["horiz"],         self.screen, (46, 34), False),
				(self.tiles["horiz"],         self.screen, (46, 36), False),
				(self.tiles["horiznc"],       self.screen, (47, 36), False),
			],
			True)

		self.blocks["YOSWYW"] = OverSwitch(self, self.frame, "YOSWYW", 
			[
				(self.tiles["eobleft"],       self.screen, (21, 30), False),
				(self.tiles["horiznc"],       self.screen, (23, 30), False),
				(self.tiles["horiz"],         self.screen, (24, 30), False),
				(self.tiles["horiznc"],       self.screen, (26, 30), False),
				(self.tiles["horiz"],         self.screen, (27, 30), False),
				(self.tiles["horiznc"],       self.screen, (28, 30), False),
				(self.tiles["horiz"],         self.screen, (29, 30), False),
				(self.tiles["horiznc"],       self.screen, (30, 30), False),
				(self.tiles["horiz"],         self.screen, (31, 30), False),
				(self.tiles["diagright"],     self.screen, (23, 31), False),
				(self.tiles["diagright"],     self.screen, (24, 32), False),
				(self.tiles["diagright"],     self.screen, (25, 33), False),
				(self.tiles["diagright"],     self.screen, (26, 34), False),
				(self.tiles["diagright"],     self.screen, (27, 35), False),
				(self.tiles["turnrightleft"], self.screen, (28, 36), False),
				(self.tiles["horiznc"],       self.screen, (29, 36), False),
				(self.tiles["horiz"],         self.screen, (30, 36), False),
				(self.tiles["horiznc"],       self.screen, (31, 36), False),
				(self.tiles["diagright"],     self.screen, (26, 31), False),
				(self.tiles["horiznc"],       self.screen, (28, 32), False),
				(self.tiles["horiz"],         self.screen, (29, 32), False),
				(self.tiles["horiznc"],       self.screen, (30, 32), False),
				(self.tiles["horiz"],         self.screen, (31, 32), False),
				(self.tiles["diagright"],     self.screen, (28, 33), False),
				(self.tiles["turnrightleft"], self.screen, (29, 34), False),
				(self.tiles["horiznc"],       self.screen, (30, 34), False),
				(self.tiles["horiz"],         self.screen, (31, 34), False),
			],
			False)
			
		self.osBlocks["YOSCJW"] = [ "Y11", "L10", "L20", "P50" ]
		self.osBlocks["YOSCJE"] = [ "Y21", "L20", "P50" ]
		self.osBlocks["YOSEJW"] = [ "Y11", "Y10", "Y87", "Y30" ]
		self.osBlocks["YOSEJE"] = [ "Y21", "Y20", "Y10", "Y87", "Y30" ]
		self.osBlocks["YOSKL2"] = [ "Y10", "Y70", "Y53", "Y52", "Y51", "Y50" ]
		self.osBlocks["YOSKL1"] = [ "Y20", "Y70", "Y53", "Y52", "Y51", "Y50" ]
		self.osBlocks["YOSKL3"] = [ "Y10", "Y20", "Y60" ]
		self.osBlocks["YOSKL4"] = [ "Y30", "Y50", "Y51" ]
		self.osBlocks["YOSWYW"] = [ "Y70", "Y81", "Y82", "Y83", "Y84" ]
		self.osBlocks["YOSWYE"] = [ "Y81", "Y82", "Y83", "Y84", "Y87" ]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			[ "YSw1",  "torightright",   CJBlocks, (133, 13) ],
			[ "YSw3",  "torightright",   CJBlocks, (130, 11) ],
			[ "YSw3b",  "torightleft",   CJBlocks, (132, 13) ],

			[ "YSw7",  "torightleft",    EEBlocks, (120, 13) ],
			[ "YSw7b", "torightright",   EEBlocks, (118, 11) ],
			[ "YSw9",  "torightleft",    EEBlocks, (117, 11) ],
			[ "YSw11", "toleftupinv",    EEBlocks, (115, 9) ],

			[ "YSw17", "torightleft",    ["YOSKL1", "YOSKL2", "YOSKL3"], (105, 13) ],
			[ "YSw21", "toleftleft",     ["YOSKL1", "YOSKL2", "YOSKL3"], (105, 11) ],
			[ "YSw21b","toleftright",    ["YOSKL1", "YOSKL2"], (103, 13) ],
			[ "YSw23", "torightleft",    ["YOSKL1", "YOSKL2"], (102, 13) ],
			[ "YSw23b","toleftdowninv",  ["YOSKL1", "YOSKL2"], (100, 11) ],
			[ "YSw25", "toleftleft",     ["YOSKL1", "YOSKL2"], (100, 13) ],
			[ "YSw27", "torightleft",    ["YOSKL1", "YOSKL2"], (99, 13) ],
			[ "YSw29", "toleftupinv",    ["YOSKL1", "YOSKL2"], (98, 9) ],

			[ "YSw33", "torightright",   ["YOSKL4"], (85, 13) ],

			[ "YSw113", "torightright",  ["YOSWYW"], (22, 30) ],
			[ "YSw115", "torightright",  ["YOSWYW"], (25, 30) ],
			[ "YSw116", "toleftdown",    ["YOSWYW"], (27, 32) ],
			[ "YSw131", "torightdown",   ["YOSWYE"], (49, 32) ],
			[ "YSw132", "toleftleft",    ["YOSWYE"], (51, 30) ],
			[ "YSw134", "toleftleft",    ["YOSWYE"], (54, 30) ],
		]

		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			trnout.SetDisabled(True)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		for t in [ "YSw113", "YSw115", "YSw116", "YSw131", "YSw132", "YSw134" ]:
			self.turnouts[t].SetRouteControl(True)

		trnout = SlipSwitch(self, self.frame, "YSw19", self.screen, self.totiles["ssleft"], (103, 11))
		blocks["YOSKL2"].AddTurnout(trnout)
		blocks["YOSKL1"].AddTurnout(trnout)
		blocks["YOSKL3"].AddTurnout(trnout)
		trnout.AddBlock("YOSKL1")
		trnout.AddBlock("YOSKL2")
		trnout.AddBlock("YOSKL3")
		trnout.SetControllers(None, self.turnouts["YSw17"])
		trnout.SetDisabled(True)
		self.turnouts["YSw19"] = trnout
		
		self.turnouts["YSw3"].SetPairedTurnout(self.turnouts["YSw3b"])
		self.turnouts["YSw7"].SetPairedTurnout(self.turnouts["YSw7b"])
		self.turnouts["YSw21"].SetPairedTurnout(self.turnouts["YSw21b"])
		self.turnouts["YSw23"].SetPairedTurnout(self.turnouts["YSw23b"])

		# preserve these values so we can efficiently draw the slip switch and crossover when necessary
		self.sw17 = self.turnouts["YSw17"]
		self.sw21 = self.turnouts["YSw21"]

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}

		sigList = [
			[ "Y2R",  RegAspects, True,    "right", (129, 12) ],
			[ "Y2L",  RegAspects, False,   "leftlong",  (136, 10) ],
			[ "Y4R",  RegAspects, True,    "rightlong", (129, 14) ],
			[ "Y4LA", RegAspects, False,   "leftlong",  (136, 14) ],
			[ "Y4LB", RegAspects, False,   "left",  (136, 12) ],

			[ "Y8RA", RegAspects, True,    "right", (114, 12) ],
			[ "Y8RB", RegAspects, True,    "right", (113, 10) ],
			[ "Y8RC", RegAspects, True,    "right", (112, 8)  ],
			[ "Y8L",  RegAspects, False,   "leftlong",  (121, 10) ],
			[ "Y10R", AdvAspects, True,    "rightlong", (114, 14) ],
			[ "Y10L", RegAspects, False,   "left",  (121, 12) ],

			[ "Y22R",  RegAspects, True,   "right", (95, 6) ],
			[ "Y22L",  RegSloAspects, False,  "leftlong",  (106, 10) ],
			[ "Y24RA", RegAspects, True,   "right", (95, 10) ],
			[ "Y24RB", RegAspects, True,   "right", (95, 8) ],
			[ "Y26RA", RegAspects, True,   "right", (96, 16) ],
			[ "Y26RB", RegAspects, True,   "right", (96, 14) ],
			[ "Y26RC", RegAspects, True,   "right", (96, 12) ],
			[ "Y26L",  RegAspects, False,  "left",  (106, 12)],

			[ "Y34R",  RegAspects, True,   "rightlong", (84, 14) ],
			[ "Y34LA", RegAspects, False,  "left",  (88, 14) ],
			[ "Y34LB", RegAspects, False,  "left",  (88, 12) ],

			[ "Y40LA", RegAspects, False,  "left",  (32, 29) ],
			[ "Y40LB", RegAspects, False,  "left",  (32, 31) ],
			[ "Y40LC", RegAspects, False,  "left",  (32, 33) ],
			[ "Y40LD", RegAspects, False,  "left",  (32, 35) ],
			[ "Y40R",  RegAspects, True,   "right", (21, 31) ],

			[ "Y42L",  RegAspects, False,  "left",  (55, 29) ],
			[ "Y42RA", RegAspects, True,   "right", (45, 31) ],
			[ "Y42RB", RegAspects, True,   "right", (45, 33) ],
			[ "Y42RC", RegAspects, True,   "right", (45, 35) ],
			[ "Y42RD", RegAspects, True,   "right", (45, 37) ],
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.sigLeverMap = {
			"Y2.lvr": [ "YOSCJW", "YOSCJE" ],
			"Y4.lvr": [ "YOSCJW", "YOSCJE" ],
			"Y8.lvr": [ "YOSEJW", "YOSEJE" ],
			"Y10.lvr": [ "YOSEJW", "YOSEJE" ],
			"Y22.lvr": [ "YOSKL1", "YOSKL2", "YOSKL3" ],
			"Y24.lvr": [ "YOSKL1", "YOSKL2", "YOSKL3" ],
			"Y26.lvr": [ "YOSKL1", "YOSKL2", "YOSKL3" ],
			"Y34.lvr": [ "YOSKL4" ],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		blockSbSigs = {
			# which signals govern stopping sections, west and east
			"Y11": ("Y8L",  None),
			"Y20": (None, "Y10R"),
			"Y21": ("Y10L", "Y4R"),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		blockSigs = {
			# which signals govern blocks, west and east
			"Y10": ("Y22L", "Y8RA"),
			"Y11": ("Y8L",  "Y2R"),
			"Y20": ("Y26L", "Y10R"),
			"Y21": ("Y10L", "Y4R"),
			"Y30": ("Y34R", "Y8RC"),
			"Y50": ("Y34LA", "Y26RA"),
			"Y51": ("Y34LB", "Y26RB"),
			"Y52": (None, "Y24RA"),
			"Y53": (None, "Y24RB"),
			"Y60": (None, "Y22R"),
			"Y70": (None, "Y26RC"),
			"Y81": ("Y40LA", "Y42RA"),
			"Y82": ("Y40LB", "Y42RB"),
			"Y83": ("Y40LC", "Y42RC"),
			"Y84": ("Y40LD", "Y42RD"),
			"Y87": ("Y42L", "Y8RB"),
		}

		for blknm, siglist in blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}
		self.buttonToRoute = {}

		# cornell junction
		block = self.blocks["YOSCJW"]
		self.routes["YRtY11L10"] = Route(self.screen, block, "YRtY11L10", "L10", [ (130, 11), (131, 11), (132, 11), (133, 11), (134, 11), (135, 11) ], "Y11", [RESTRICTING, MAIN], ["YSw3:N"], ["Y2L", "Y2R"])
		self.routes["YRtY11L20"] = Route(self.screen, block, "YRtY11L20", "L20", [ (130, 11), (131, 12), (132, 13), (133, 13), (134, 13), (135, 13) ], "Y11", [RESTRICTING, RESTRICTING], ["YSw1:N", "YSw3:R"], ["Y4LB", "Y2R"])
		self.routes["YRtY11P50"] = Route(self.screen, block, "YRtY11P50", "P50", [ (130, 11), (131, 12), (132, 13), (133, 13), (134, 14), (135, 15) ], "Y11", [RESTRICTING, DIVERGING], ["YSw1:R", "YSw3:R"], ["Y4LA", "Y2R"])

		block = self.blocks["YOSCJE"]
		self.routes["YRtY21L20"] = Route(self.screen, block, "YRtY21L20", "Y21", [ (130, 13), (131, 13), (132, 13), (133, 13), (134, 13), (135, 13) ], "L20", [MAIN, RESTRICTING], ["YSw1:N", "YSw3:N"], ["Y4R", "Y4LB"])
		self.routes["YRtY21P50"] = Route(self.screen, block, "YRtY21P50", "Y21", [ (130, 13), (131, 13), (132, 13), (133, 13), (134, 14), (135, 15) ], "P50", [DIVERGING, RESTRICTING], ["YSw1:R", "YSw3:N"], ["Y4R", "Y4LA"])

		self.signals["Y2R"].AddPossibleRoutes("YOSCJW", [ "YRtY11L10", "YRtY11L20", "YRtY11P50" ])
		self.signals["Y2L"].AddPossibleRoutes("YOSCJW", [ "YRtY11L10" ])

		self.signals["Y4R"].AddPossibleRoutes("YOSCJE", [ "YRtY21L20", "YRtY21P50" ])
		self.signals["Y4LB"].AddPossibleRoutes("YOSCJE", [ "YRtY21L20" ])
		self.signals["Y4LB"].AddPossibleRoutes("YOSCJW", [ "YRtY11L20" ])
		self.signals["Y4LA"].AddPossibleRoutes("YOSCJE", [ "YRtY21P50" ])
		self.signals["Y4LA"].AddPossibleRoutes("YOSCJW", [ "YRtY11P50" ])

		self.osSignals["YOSCJW"] = [ "Y2R", "Y2L", "Y4LA", "Y4LB" ]
		self.osSignals["YOSCJE"] = [ "Y2R", "Y4R", "Y4LA", "Y4LB" ]

		# east end junction
		block = self.blocks["YOSEJW"] 
		self.routes["YRtY10Y11"] = Route(self.screen, block, "YRtY10Y11", "Y11", [ (115, 11), (116, 11), (117, 11), (118, 11), (119, 11), (120, 11) ], "Y10", [RESTRICTING, MAIN], ["YSw7:N", "YSw9:N"], ["Y8L", "Y8RA"])
		self.routes["YRtY30Y11"] = Route(self.screen, block, "YRtY30Y11", "Y11", [ (112, 7), (113, 7), (114, 8), (115, 9), (116, 10), (117, 11), (118, 11), (119, 11), (120, 11) ], "Y30", [RESTRICTING, DIVERGING], ["YSw7:N", "YSw9:R", "YSw11:R"], ["Y8L", "Y8RC"])
		self.routes["YRtY87Y11"] = Route(self.screen, block, "YRtY87Y11", "Y11", [ (114, 9), (115, 9), (116, 10), (117, 11), (118, 11), (119, 11), (120, 11) ], "Y87", [RESTRICTING, RESTRICTING], ["YSw7:N", "YSw9:R", "YSw11:N"], ["Y8L", "Y8RB"])

		block = self.blocks["YOSEJE"]
		self.routes["YRtY20Y21"] = Route(self.screen, block, "YRtY20Y21", "Y20", [ (115, 13), (116, 13), (117, 13), (118, 13), (119, 13), (120, 13) ], "Y21", [MAIN, RESTRICTING], ["YSw7:N"], ["Y10R", "Y10L"])
		self.routes["YRtY30Y21"] = Route(self.screen, block, "YRtY30Y21", "Y30", [ (112, 7), (113, 7), (114, 8), (115, 9), (116, 10), (117, 11), (118, 11), (119, 12), (120, 13) ], "Y21", [RESTRICTING, RESTRICTING], ["YSw7:R", "YSw9:R", "YSw11:R"], ["Y8RC", "Y10L"])
		self.routes["YRtY87Y21"] = Route(self.screen, block, "YRtY87Y21", "Y87", [ (114, 9), (115, 9), (116, 10), (117, 11), (118, 11), (119, 12), (120, 13) ], "Y21", [RESTRICTING, RESTRICTING], ["YSw7:R", "YSw9:R", "YSw11:N"], ["Y8RB", "Y10L"])
		self.routes["YRtY10Y21"] = Route(self.screen, block, "YRtY10Y21", "Y10", [ (115, 11), (116, 11), (117, 11), (118, 11), (119, 12), (120, 13) ], "Y21", [RESTRICTING, RESTRICTING], ["YSw7:R", "YSw9:N"], ["Y8RA", "Y10L"])

		self.signals["Y8RA"].AddPossibleRoutes("YOSEJW", ["YRtY10Y11"])
		self.signals["Y8RA"].AddPossibleRoutes("YOSEJE", ["YRtY10Y21"])
		self.signals["Y8RB"].AddPossibleRoutes("YOSEJW", ["YRtY87Y11"])
		self.signals["Y8RB"].AddPossibleRoutes("YOSEJE", ["YRtY87Y21"])
		self.signals["Y8RC"].AddPossibleRoutes("YOSEJW", ["YRtY30Y11"])
		self.signals["Y8RC"].AddPossibleRoutes("YOSEJE", ["YRtY30Y21"])
		self.signals["Y8L"].AddPossibleRoutes("YOSEJW", ["YRtY10Y11", "YRtY87Y11", "YRtY30Y11"])
		self.signals["Y10R"].AddPossibleRoutes("YOSEJE", ["YRtY20Y21"])
		self.signals["Y10L"].AddPossibleRoutes("YOSEJE", ["YRtY20Y21", "YRtY10Y21", "YRtY87Y21", "YRtY30Y21"])

		self.osSignals["YOSEJW"] = [ "Y8RA", "Y8RB", "Y8RC", "Y8L" ]
		self.osSignals["YOSEJE"] = [ "Y8RA", "Y8RB", "Y8RC", "Y10R", "Y10L" ]

		# Kale interlocking
		block = self.blocks["YOSKL1"]
		self.routes["YRtY20Y51"] = Route(self.screen, block, "YRtY20Y51", "Y51", [ (97, 13), (98, 13), (99, 13), (100, 13), (101, 13), (102, 13), (103, 13), (104, 13), (105, 13) ], "Y20", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:N", "YSw23:N", "YSw25:N", "YSw27:N"], ["Y26RB", "Y26L"])
		self.routes["YRtY20Y50"] = Route(self.screen, block, "YRtY20Y50", "Y50", [ (97, 15), (98, 15), (99, 14), (100, 13), (101, 13), (102, 13), (103, 13), (104, 13), (105, 13) ], "Y20", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:N", "YSw23:N", "YSw25:R"], ["Y26RA", "Y26L"])
		self.routes["YRtY20Y70"] = Route(self.screen, block, "YRtY20Y70", "Y70", [ (97, 11), (98, 12), (99, 13), (100, 13), (101, 13), (102, 13), (103, 13), (104, 13), (105, 13) ], "Y20", [RESTRICTING, DIVERGING], ["YSw17:N", "YSw21:N", "YSw23:N", "YSw25:N", "YSw27:R"], ["Y26RC", "Y26L"])
		self.routes["YRtY20Y52"] = Route(self.screen, block, "YRtY20Y52", "Y52", [ (96, 9), (97, 9), (98, 9), (99, 10), (100, 11), (101, 12), (102, 13), (103, 13), (104, 13), (105, 13) ], "Y20", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:N", "YSw23:R", "YSw29:N"], ["Y24RA", "Y26L"])
		self.routes["YRtY20Y53"] = Route(self.screen, block, "YRtY20Y53", "Y53", [ (96, 7), (97, 8), (98, 9), (99, 10), (100, 11), (101, 12), (102, 13), (103, 13), (104, 13), (105, 13) ], "Y20", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:N", "YSw23:R", "YSw29:R"], ["Y24RB", "Y26L"])

		block = self.blocks["YOSKL3"]
		self.routes["YRtY20Y60"] = Route(self.screen, block, "YRtY20Y60", "Y20", [ (96, 5), (97, 5), (98, 6), (99, 7), (100, 8), (101, 9), (102, 10), (103, 11), (104, 12), (105, 13) ], "Y60", [RESTRICTING, RESTRICTING], ["YSw17:R", "YSw19:R", "YSw21:N"], ["Y26L", "Y22R"])

		block = self.blocks["YOSKL2"]
		self.routes["YRtY10Y52"] = Route(self.screen, block, "YRtY10Y52", "Y10", [ (96, 9), (97, 9), (98, 9), (99, 10), (100, 11), (101, 11), (102, 11), (103, 11), (104, 11), (105, 11) ], "Y52", [RESTRICTING, SLOW], ["YSw17:N", "YSw19:N", "YSw21:N", "YSw23:N", "YSw29:N"], ["Y22L", "Y24RA"])
		self.routes["YRtY10Y50"] = Route(self.screen, block, "YRtY10Y50", "Y10", [ (97, 15), (98, 15), (99, 14), (100, 13), (101, 13), (102, 13), (103, 13), (104, 12), (105, 11) ], "Y50", [RESTRICTING, SLOW], ["YSw17:N", "YSw21:R", "YSw23:N", "YSw25:R"], ["Y22L", "Y26RA"])
		self.routes["YRtY10Y51"] = Route(self.screen, block, "YRtY10Y51", "Y10", [ (97, 13), (98, 13), (99, 13), (100, 13), (101, 13), (102, 13), (103, 13), (104, 12), (105, 11) ], "Y51", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:R", "YSw23:N", "YSw25:N", "YSw27:N"], ["Y22L", "Y26RB"])
		self.routes["YRtY10Y70"] = Route(self.screen, block, "YRtY10Y70", "Y10", [ (97, 11), (98, 12), (99, 13), (100, 13), (101, 13), (102, 13), (103, 13), (104, 12), (105, 11) ], "Y70", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw21:R", "YSw23:N", "YSw25:N", "YSw27:R"], ["Y22L", "Y26RC"])
		self.routes["YRtY10Y53"] = Route(self.screen, block, "YRtY10Y53", "Y10", [ (96, 7), (97, 8), (98, 9), (99, 10), (100, 11), (101, 11), (102, 11), (103, 11), (104, 11), (105, 11) ], "Y53", [RESTRICTING, SLOW], ["YSw17:N", "YSw19:N", "YSw21:N", "YSw23:N", "YSw29:R"], ["Y22L", "Y24RB"])

		block = self.blocks["YOSKL3"]
		self.routes["YRtY10Y60"] = Route(self.screen, block, "YRtY10Y60", "Y10", [ (96, 5), (97, 5), (98, 6), (99, 7), (100, 8), (101, 9), (102, 10), (103, 11), (104, 11), (105, 11) ], "Y60", [RESTRICTING, RESTRICTING], ["YSw17:N", "YSw19:R", "YSw21:N"], ["Y22L", "Y22R"])

		self.signals["Y22L"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y50", "YRtY10Y51", "YRtY10Y52", "YRtY10Y53", "YRtY10Y70" ])
		self.signals["Y22L"].AddPossibleRoutes("YOSKL3", [ "YRtY10Y60" ])
		self.signals["Y26L"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y50", "YRtY20Y51", "YRtY20Y52", "YRtY20Y53", "YRtY20Y70" ])
		self.signals["Y26L"].AddPossibleRoutes("YOSKL3", [ "YRtY20Y60" ])
		self.signals["Y22R"].AddPossibleRoutes("YOSKL3", [ "YRtY10Y60", "YRtY20Y60" ])
		self.signals["Y24RA"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y52" ])
		self.signals["Y24RA"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y52" ])
		self.signals["Y24RB"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y53" ])
		self.signals["Y24RB"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y53" ])
		self.signals["Y26RA"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y50" ])
		self.signals["Y26RA"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y50" ])
		self.signals["Y26RB"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y51" ])
		self.signals["Y26RB"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y51" ])
		self.signals["Y26RC"].AddPossibleRoutes("YOSKL2", [ "YRtY10Y70" ])
		self.signals["Y26RC"].AddPossibleRoutes("YOSKL1", [ "YRtY20Y70" ])

		self.osSignals["YOSKL2"] = [ "Y22L", "Y24RA", "Y24RB", "Y26RA", "Y26RB", "Y26RC" ]
		self.osSignals["YOSKL1"] = [ "Y26L", "Y24RA", "Y24RB", "Y26RA", "Y26RB", "Y26RC" ]
		self.osSignals["YOSKL3"] = [ "Y22R", "Y22L", "Y26L" ]

		# Kale west end
		block = self.blocks["YOSKL4"]
		self.routes["YRtY30Y51"] = Route(self.screen, block, "YRtY30Y51", "Y30", [ (84, 13), (85, 13), (86, 13), (87, 13)], "Y51", [RESTRICTING, SLOW], ["YSw33:N"], ["Y34R", "Y34LB"])
		self.routes["YRtY30Y50"] = Route(self.screen, block, "YRtY30Y50", "Y30", [ (84, 13), (85, 13), (86, 14), (87, 15) ], "Y50", [RESTRICTING, SLOW], ["YSw33:R"], ["Y34R", "Y34LA"])
		self.buttonToRoute["YY51W"] = "YRtY30Y51"
		self.buttonToRoute["YY50W"] = "YRtY30Y50"

		self.signals["Y34R"].AddPossibleRoutes("YOSKL4", [ "YRtY30Y51", "YRtY30Y50" ])
		self.signals["Y34LA"].AddPossibleRoutes("YOSKL4", [ "YRtY30Y50" ])
		self.signals["Y34LB"].AddPossibleRoutes("YOSKL4", [ "YRtY30Y51" ])

		self.osSignals["YOSKL4"] = [ "Y34R", "Y34LA", "Y34LB" ]

		# Waterman yard
		block = self.blocks["YOSWYW"]
		self.routes["YRtY70Y81"] = Route(self.screen, block, "YRtY70Y81", "Y81", [ (21, 30), (22, 30), (23, 30), (24, 30), (25, 30), (26, 30), (27, 30), (28, 30), (29, 30), (30, 30), (31, 30) ], "Y70", [RESTRICTING, DIVERGING], ["YSw113:N", "YSw115:N"], ["Y40LA", "Y40R"])
		self.routes["YRtY70Y82"] = Route(self.screen, block, "YRtY70Y82", "Y82", [ (21, 30), (22, 30), (23, 30), (24, 30), (25, 30), (26, 31), (27, 32), (28, 32), (29, 32), (30, 32), (31, 32) ], "Y70", [RESTRICTING, DIVERGING], ["YSw113:N", "YSw115:R", "YSw116:R"], ["Y40LB", "Y40R"])
		self.routes["YRtY70Y83"] = Route(self.screen, block, "YRtY70Y83", "Y83", [ (21, 30), (22, 30), (23, 30), (24, 30), (25, 30), (26, 31), (27, 32), (28, 33), (29, 34), (30, 34), (31, 34) ], "Y70", [RESTRICTING, DIVERGING], ["YSw113:N", "YSw115:R", "YSw116:N"], ["Y40LC", "Y40R"])
		self.routes["YRtY70Y84"] = Route(self.screen, block, "YRtY70Y84", "Y84", [ (21, 30), (22, 30), (23, 31), (24, 32), (25, 33), (26, 34), (27, 35), (28, 36), (29, 36), (30, 36), (31, 36) ], "Y70", [RESTRICTING, DIVERGING], ["YSw113:R"], ["Y40LD", "Y40R"])
		self.buttonToRoute["YWWB1"] = "YRtY70Y81"
		self.buttonToRoute["YWWB2"] = "YRtY70Y82"
		self.buttonToRoute["YWWB3"] = "YRtY70Y83"
		self.buttonToRoute["YWWB4"] = "YRtY70Y84"

		block = self.blocks["YOSWYE"]
		self.routes["YRtY87Y81"] = Route(self.screen, block, "YRtY87Y81", "Y81", [ (46, 30), (47, 30), (48, 30), (49, 30), (50, 30), (51, 30), (52, 30), (53, 30), (54, 30), (55, 30) ], "Y87", [RESTRICTING, RESTRICTING], ["YSw134:N", "YSw132:N"], ["Y42RA", "Y42L"])
		self.routes["YRtY87Y82"] = Route(self.screen, block, "YRtY87Y82", "Y82", [ (46, 32), (47, 32), (48, 32), (49, 32), (50, 31), (51, 30), (52, 30), (53, 30), (54, 30), (55, 30) ], "Y87", [RESTRICTING, RESTRICTING], ["YSw134:N", "YSw132:R", "YSw131:R"], ["Y42RB", "Y42L"])
		self.routes["YRtY87Y83"] = Route(self.screen, block, "YRtY87Y83", "Y83", [ (46, 34), (47, 34), (48, 33), (49, 32), (50, 31), (51, 30), (52, 30), (53, 30), (54, 30), (55, 30) ], "Y87", [RESTRICTING, RESTRICTING], ["YSw134:N", "YSw132:R", "YSw131:N"], ["Y42RC", "Y42L"])
		self.routes["YRtY87Y84"] = Route(self.screen, block, "YRtY87Y84", "Y84", [ (46, 36), (47, 36), (48, 36), (49, 35), (50, 34), (51, 33), (52, 32), (53, 31), (54, 30), (55, 30) ], "Y87", [RESTRICTING, RESTRICTING], ["YSw134:R"], ["Y42RD", "Y42L"])
		self.buttonToRoute["YWEB1"] = "YRtY87Y81"
		self.buttonToRoute["YWEB2"] = "YRtY87Y82"
		self.buttonToRoute["YWEB3"] = "YRtY87Y83"
		self.buttonToRoute["YWEB4"] = "YRtY87Y84"

		self.signals["Y40R"].AddPossibleRoutes("YOSWYW", [ "YRtY70Y81", "YRtY70Y82", "YRtY70Y83", "YRtY70Y84" ])
		self.signals["Y40LA"].AddPossibleRoutes("YOSWYW", [ "YRtY70Y81" ])
		self.signals["Y40LB"].AddPossibleRoutes("YOSWYW", [ "YRtY70Y82" ])
		self.signals["Y40LC"].AddPossibleRoutes("YOSWYW", [ "YRtY70Y83" ])
		self.signals["Y40LD"].AddPossibleRoutes("YOSWYW", [ "YRtY70Y84" ])
		self.signals["Y42L"].AddPossibleRoutes("YOSWYE", [ "YRtY87Y81", "YRtY87Y82", "YRtY87Y83", "YRtY87Y84" ])
		self.signals["Y42RA"].AddPossibleRoutes("YOSWYE", [ "YRtY87Y81" ])
		self.signals["Y42RB"].AddPossibleRoutes("YOSWYE", [ "YRtY87Y82" ])
		self.signals["Y42RC"].AddPossibleRoutes("YOSWYE", [ "YRtY87Y83" ])
		self.signals["Y42RD"].AddPossibleRoutes("YOSWYE", [ "YRtY87Y84" ])

		self.osSignals["YOSWYW"] = [ "Y40R", "Y40LA", "Y40LB", "Y40LC", "Y40LD" ]
		self.osSignals["YOSWYE"] = [ "Y42L", "Y42RA", "Y42RB", "Y42RC", "Y42RD" ]

		return self.signals

	def DefineButtons(self):
		self.buttons = {}
		self.osButtons = {}

		buttons = [
			["YWWB1", (32, 30)],
			["YWWB2", (32, 32)],
			["YWWB3", (32, 34)],
			["YWWB4", (32, 36)],

			["YWEB1", (45, 30)],
			["YWEB2", (45, 32)],
			["YWEB3", (45, 34)],
			["YWEB4", (45, 36)],

			["YY51W", (88, 13)],
			["YY50W", (88, 15)],

			["YY51E", (96, 13)],
			["YY50E", (96, 15)],
			["YY60", (95, 5)],
			["YY53", (95, 7)],
			["YY52", (95, 9)],
			["YY70", (96, 11)],
			["YY10W", (106, 11)],
			["YY20W", (106, 13)],

			["YY10E", (114, 11)],
			["YY20E", (114, 13)],
			["YY30", (111, 7)],
			["YY87", (113, 9)],
			["YY11W", (121, 11)],
			["YY21W", (121, 13)],

			["YY11E", (129, 11)],
			["YY21E", (129, 13)],
			["YL10", (136, 11)],
			["YL20", (136, 13)],
			["YP50", (136, 15)]
		]

		for bname, pos in buttons:
			self.buttons[bname] = Button(self, self.screen, self.frame, bname, pos, self.btntiles)

		self.osButtons["YOSWYW"] = [ "YWWB1", "YWWB2", "YWWB3", "YWWB4" ]
		self.osButtons["YOSWYE"] = [ "YWEB1", "YWEB2", "YWEB3", "YWEB4" ]
		self.osButtons["YOSKL4"] = [ "YY51W", "YY50W" ]
		self.osButtons["YOSKL1"] = [ "YY60", "YY53", "YY52", "YY70", "YY51E", "YY50E", "YY10W", "YY20W" ]
		self.osButtons["YOSKL2"] = self.osButtons["YOSKL1"]
		self.osButtons["YOSKL3"] = self.osButtons["YOSKL1"]
		self.osButtons["YOSEJW"] = [ "YY30", "YY87", "YY10E", "YY20E", "YY11W", "YY21W" ]
		self.osButtons["YOSEJE"] = self.osButtons["YOSEJW"]
		self.osButtons["YOSCJW"] = [ "YY11E", "YY21E", "YL10", "YL20", "YP50" ]
		self.osButtons["YOSCJE"] = self.osButtons["YOSCJW"]

		self.westGroup["YOSCJ"] = [ "YY11E", "YY21E" ]
		self.eastGroup["YOSCJ"] = [ "YL10", "YL20", "YP50"]

		self.westGroup["YOSEJ"] = [ "YY30", "YY87", "YY10E", "YY20E" ]
		self.eastGroup["YOSEJ"] = [ "YY11W", "YY21W"]

		self.westGroup["YOSKL"] = [ "YY60", "YY53", "YY52", "YY70", "YY51E", "YY50E" ]
		self.eastGroup["YOSKL"] = [ "YY10W", "YY20W"]

		for n in ["YOSCJ", "YOSKL", "YOSEJ"]:
			self.westButton[n] = self.eastButton[n] = None

		self.NXMap = {
			"YY11E": {
				"YL10":  "YRtY11L10",
				"YL20":  "YRtY11L20",
				"YP50":  "YRtY11P50"
			},
			"YY21E": {
				"YL20":  "YRtY21L20",
				"YP50":  "YRtY21P50"
			},

			"YY30": {
				"YY11W": "YRtY30Y11",
				"YY21W": "YRtY30Y21"
			},
			"YY87": {
				"YY11W": "YRtY87Y11",
				"YY21W": "YRtY87Y21"
			},
			"YY10E": {
				"YY11W": "YRtY10Y11",
				"YY21W": "YRtY10Y21"
			},
			"YY20E": {
				"YY21W": "YRtY20Y21"
			},

			"YY60": {
				"YY10W": "YRtY10Y60",
				"YY20W": "YRtY20Y60"
			},
			"YY53": {
				"YY10W": "YRtY10Y53",
				"YY20W": "YRtY20Y53"
			},
			"YY52": {
				"YY10W": "YRtY10Y52",
				"YY20W": "YRtY20Y52"
			},
			"YY70": {
				"YY10W": "YRtY10Y70",
				"YY20W": "YRtY20Y70"
			},
			"YY51E": {
				"YY10W": "YRtY10Y51",
				"YY20W": "YRtY20Y51"
			},
			"YY50E": {
				"YY10W": "YRtY10Y50",
				"YY20W": "YRtY20Y50"
			}
		}

		return self.buttons

	def DefineIndicators(self):
		self.indicators = {}
		indNames = [ "CBKale", "CBEastEnd", "CBCornellJct", "CBEngineYard", "CBWaterman", "Y20H", "Y20D" ]
		for ind in indNames:
			self.indicators[ind] = Indicator(self.frame, self, ind)

		return self.indicators
