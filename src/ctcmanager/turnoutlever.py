import wx
import os

SWNORMAL= "SwNormal"
SWREVERSE = "SwReverse"
SWNEUTRAL = "SwNeutral"
SWNORMALDISABLED = "SwNormalDis"
SWREVERSEDISABLED = "SwReverseDis"
SWNEUTRALDISABLED = "SwNeutralDis"
LAMPOFF = "LampOff"
LAMPRED = "LampRed"
LAMPGREEN = "LampGreen"

NORMAL = "N"
REVERSE= "R"


class TurnoutLever:
	images = None

	def __init__(self, frame, label, name, screen, pos):
		self.frame = frame
		self.label = label
		self.name = name
		self.screen = screen
		self.pos = [x for x in pos]
		self.buffer = None

		if TurnoutLever.images is None:
			TurnoutLever.loadBitmaps()

		self.bmpN = TurnoutLever.images[LAMPGREEN]
		self.bmpR = TurnoutLever.images[LAMPOFF]
		self.bmpPlate = TurnoutLever.images[SWNEUTRAL]

		self.enabled = True

		self.state = NORMAL
		self.requestedState = None

		if len(self.label) == 1:
			ox = 26
		elif len(self.label) == 2:
			ox = 23
		else:
			ox = 20
		self.labelx = self.pos[0]+ox
		self.labely = self.pos[1]+19
		self.labelFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

	def Enable(self, flag=True):
		self.enabled = flag
		self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[SWNEUTRALDISABLED]
		if self.state == NORMAL:
			self.bmpN = TurnoutLever.images[LAMPGREEN]
			self.bmpR = TurnoutLever.images[LAMPOFF]
		elif self.state == REVERSE:
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpR = TurnoutLever.images[LAMPRED]
		else:
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpR = TurnoutLever.images[LAMPOFF]

	def SetTurnoutState(self, state):
		self.requestedState = None

		if state == NORMAL:
			self.bmpR = TurnoutLever.images[LAMPOFF]
			self.bmpN = TurnoutLever.images[LAMPGREEN]
			self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[SWNEUTRALDISABLED]
			self.state = NORMAL
			print("set to normal")
		if state == REVERSE:
			self.bmpR = TurnoutLever.images[LAMPRED]
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[
				SWNEUTRALDISABLED]
			self.state = REVERSE
			print("set to reverse")

	def GetBitmaps(self):
		return [
			[self.screen, (self.pos[0], self.pos[1]+17), self.bmpPlate],
			[self.screen, (self.pos[0], self.pos[1]), self.bmpN],
			[self.screen, (self.pos[0]+40, self.pos[1]), self.bmpR]
		]

	def GetLabel(self):
		return self.label, self.labelFont, self.screen, self.labelx, self.labely

	@classmethod
	def loadBitmaps(self):
		TurnoutLever.images = {}
		for f in [ SWNEUTRAL, SWNORMAL, SWREVERSE,
				   SWNEUTRALDISABLED, SWNORMALDISABLED, SWREVERSEDISABLED,
				   LAMPOFF, LAMPGREEN, LAMPRED ]:
			fp = os.path.join("images", "bitmaps", "CTC", f + ".png")
			png = wx.Image(fp, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			mask = wx.Mask(png, wx.BLUE)
			png.SetMask(mask)
			TurnoutLever.images[f] = png

	def LeverClick(self, direction):
		self.parent.PopupEvent("mouse click turnout %s.%s" % (self.name, direction))
		if not self.enabled:
			return False

		if self.requestedState is not None:
			return False

		revt = None
		if direction == NORMAL:
			if self.state == REVERSE:
				revt = TurnoutLeverEvent(position=NORMAL, label=self.label, name=self.name, panel=self.panel, lever=self)
				self.bmpPlate = TurnoutLever.images[SWNORMAL] if self.enabled else TurnoutLever.images[SWNORMALDISABLED]
				self.requestedState = NORMAL
		else:
			if self.state == NORMAL:
				revt = TurnoutLeverEvent(position=REVERSE, label=self.label, name=self.name, panel=self.panel, lever=self)
				self.bmpPlate = TurnoutLever.images[SWREVERSE] if self.enabled else TurnoutLever.images[SWREVERSEDISABLED]
				self.requestedState = REVERSE

		if revt is not None:
			wx.QueueEvent(self, revt)
			wx.CallLater(3000, self.checkIfCompleted)
			return True

		return False

	def checkIfCompleted(self):
		if self.requestedState is None:
			return

		self.bmpPlate = self.images[SWNEUTRAL]
		self.requestedState = None

	def inHotSpot(self, x, y):
		return 5 <= x <= 55 and 17 <= y <= 60
	#
	# def initBuffer(self):
	# 	self.w, self.h = self.GetClientSize()
	# 	if self.w <= 0 or self.h <= 0:
	# 		return
	# 	self.buffer = wx.Bitmap(self.w, self.h)
	# 	self.redrawImage()
	#
	# def redrawImage(self):
	# 	dc = wx.ClientDC(self)
	# 	self.drawImage(dc)
	#
	# def drawImage(self, dc):
	# 	dc.DrawBitmap(self.bmpN, 0,  0, False)
	# 	dc.DrawBitmap(self.bmpR, 40, 0, False)
	# 	dc.DrawBitmap(self.bmpPlate, 0, 17, False)
	# 	if self.label is not None:
	# 		dc.SetTextForeground(wx.Colour(255, 255, 0))
	# 		dc.SetTextBackground(wx.Colour(0, 0, 0))
	# 		dc.SetFont(self.labelFont)
	# 		dc.DrawText(self.label, self.labelx, self.labely)
