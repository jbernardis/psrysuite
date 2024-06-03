import wx
import wx.lib.newevent
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

(TurnoutLeverEvent,   EVT_TURNOUT_LEVER)  = wx.lib.newevent.NewEvent()


class TurnoutLever(wx.Panel):
	images = None

	def __init__(self, parent, label, name, panel):
		self.parent = parent
		self.label = label
		self.name = name
		self.panel = panel
		wx.Panel.__init__(self, parent, size=(60, 85))
		self.buffer = None
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_MOTION, self.onMouseMove)
		self.Bind(wx.EVT_LEFT_DOWN, self.onMouseClick)

		if TurnoutLever.images is None:
			TurnoutLever.loadBitmaps()

		self.bmpN = TurnoutLever.images[LAMPGREEN]
		self.bmpR = TurnoutLever.images[LAMPOFF]
		self.bmpPlate = TurnoutLever.images[SWNEUTRAL]

		self.enabled = True

		self.state = NORMAL
		self.requestedState = None

		if len(self.label) == 1:
			self.labelx = 27
		elif len(self.label) == 2:
			self.labelx = 24
		else:
			self.labelx = 21
		self.labely = 19
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

		self.Refresh()

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
		self.Refresh()

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

	def onSize(self, _):
		self.initBuffer()

	def onPaint(self, _):
		dc = wx.PaintDC(self)
		self.drawImage(dc)

	def onMouseMove(self, evt):
		x, y = evt.GetPosition()
		if self.inHotSpot(x, y) is not None:
			self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
		else:
			self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

	def onMouseClick(self, evt):
		if not self.parent.IsConnected():
			evt.Skip()
			return

		if not self.enabled:
			evt.Skip()
			return

		if self.requestedState is not None:
			evt.Skip()
			return

		x, y = evt.GetPosition()
		if self.inHotSpot(x, y):
			click = NORMAL if x < 30 else REVERSE
			print("click: %s %s %s" % (click, self.state, self.requestedState))
			revt = None
			if click == NORMAL:
				if self.state == REVERSE:
					revt = TurnoutLeverEvent(position=NORMAL, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = TurnoutLever.images[SWNORMAL] if self.enabled else TurnoutLever.images[SWNORMALDISABLED]
					self.requestedState = NORMAL
			else:
				if self.state == NORMAL:
					revt = TurnoutLeverEvent(position=REVERSE, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = TurnoutLever.images[SWREVERSE] if self.enabled else TurnoutLever.images[SWREVERSEDISABLED]
					self.requestedState = REVERSE

			self.Refresh()
			if revt is not None:
				wx.QueueEvent(self, revt)


		evt.Skip()

	def checkIfCompleted(self):
		pass

	def inHotSpot(self, x, y):
		return 5 <= x <= 55 and 17 <= y <= 60

	def initBuffer(self):
		self.w, self.h = self.GetClientSize()
		if self.w <= 0 or self.h <= 0:
			return
		self.buffer = wx.Bitmap(self.w, self.h)
		self.redrawImage()

	def redrawImage(self):
		dc = wx.ClientDC(self)
		self.drawImage(dc)

	def drawImage(self, dc):
		dc.DrawBitmap(self.bmpN, 0,  0, False)
		dc.DrawBitmap(self.bmpR, 40, 0, False)
		dc.DrawBitmap(self.bmpPlate, 0, 17, False)
		if self.label is not None:
			dc.SetTextForeground(wx.Colour(255, 255, 0))
			dc.SetTextBackground(wx.Colour(0, 0, 0))
			dc.SetFont(self.labelFont)
			dc.DrawText(self.label, self.labelx, self.labely)
