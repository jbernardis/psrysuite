import wx
import wx.lib.newevent
import os

SIGLEFT = "SigLeft"
SIGRIGHT = "SigRight"
SIGNEUTRAL = "SigNeutral"
SIGLEFTDISABLED = "SigLeftDis"
SIGRIGHTDISABLED = "SigRightDis"
SIGNEUTRALDISABLED = "SigNeutralDis"
LAMPOFF = "LampOff"
LAMPRED = "LampRed"
LAMPGREEN = "LampGreen"

NEUTRAL = "N"
LEFT = "L"
RIGHT = "R"

(SignalLeverEvent,   EVT_SIGNAL_LEVER)  = wx.lib.newevent.NewEvent()


class SigLever(wx.Panel):
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

		if SigLever.images is None:
			SigLever.loadBitmaps()

		self.bmpL = SigLever.images[LAMPOFF]
		self.bmpR = SigLever.images[LAMPOFF]
		self.bmpN = SigLever.images[LAMPRED]
		self.bmpPlate = SigLever.images[SIGNEUTRAL]

		self.enabled = True

		self.state = NEUTRAL
		self.requestedState = None

		if len(self.label) == 1:
			self.labelx = 27
		elif len(self.label) == 2:
			self.labelx = 24
		else:
			self.labelx = 21
		self.labely = 27
		self.labelFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

	def Enable(self, flag=True):
		self.enabled = flag
		if self.state == RIGHT:
			self.bmpPlate = SigLever.images[SIGRIGHT] if self.enabled else SigLever.images[SIGRIGHTDISABLED]
		elif self.state == LEFT:
			self.bmpPlate = SigLever.images[SIGLEFT] if self.enabled else SigLever.images[SIGLEFTDISABLED]
		else:
			self.bmpPlate = SigLever.images[SIGNEUTRAL] if self.enabled else SigLever.images[SIGNEUTRALDISABLED]
		self.Refresh()

	def SetSignalAspect(self, aspect, lr):
		if aspect == 0:
			self.bmpL = SigLever.images[LAMPOFF]
			self.bmpR = SigLever.images[LAMPOFF]
			self.bmpN = SigLever.images[LAMPRED]
			self.bmpPlate = SigLever.images[SIGNEUTRAL] if self.enabled else SigLever.images[SIGNEUTRALDISABLED]
			self.state = NEUTRAL

		elif lr == "R":
			self.bmpL = SigLever.images[LAMPOFF]
			self.bmpR = SigLever.images[LAMPGREEN]
			self.bmpN = SigLever.images[LAMPOFF]
			self.bmpPlate = SigLever.images[SIGRIGHT] if self.enabled else SigLever.images[SIGRIGHTDISABLED]
			self.state = RIGHT

		elif lr == "L":
			self.bmpL = SigLever.images[LAMPGREEN]
			self.bmpR = SigLever.images[LAMPOFF]
			self.bmpN = SigLever.images[LAMPOFF]
			self.bmpPlate = SigLever.images[SIGLEFT] if self.enabled else SigLever.images[SIGLEFTDISABLED]
			self.state = LEFT

		else:
			self.bmpL = SigLever.images[LAMPOFF]
			self.bmpR = SigLever.images[LAMPOFF]
			self.bmpN = SigLever.images[LAMPRED]
			self.bmpPlate = SigLever.images[SIGNEUTRAL] if self.enabled else SigLever.images[SIGNEUTRALDISABLED]
			self.state = NEUTRAL

		self.requestedState = None
		self.Refresh()

	@classmethod
	def loadBitmaps(self):
		SigLever.images = {}
		for f in [ SIGNEUTRAL, SIGLEFT, SIGRIGHT,
				   SIGNEUTRALDISABLED, SIGLEFTDISABLED, SIGRIGHTDISABLED,
				   LAMPOFF, LAMPGREEN, LAMPRED ]:
			fp = os.path.join("images", "bitmaps", "CTC", f + ".png")
			png = wx.Image(fp, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			mask = wx.Mask(png, wx.BLUE)
			png.SetMask(mask)
			SigLever.images[f] = png
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
			click = LEFT if x < 30 else RIGHT
			print("click: %s %s %s" % (click, self.state, self.requestedState))
			revt = None
			if click == LEFT:
				if self.state == RIGHT:
					revt = SignalLeverEvent(position=NEUTRAL, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = SigLever.images[SIGNEUTRAL] if self.enabled else SigLever.images[SIGNEUTRALDISABLED]
					self.requestedState = NEUTRAL
				elif self.state == LEFT:
					pass
				else:
					revt = SignalLeverEvent(position=LEFT, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = SigLever.images[SIGLEFT] if self.enabled else SigLever.images[SIGLEFTDISABLED]
					self.requestedState = LEFT
					wx.CallLater(5000, self.checkIfCompleted)
			else:
				if self.state == LEFT:
					revt = SignalLeverEvent(position=NEUTRAL, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = SigLever.images[SIGNEUTRAL] if self.enabled else SigLever.images[SIGNEUTRALDISABLED]
					self.requestedState = NEUTRAL
				elif self.state == RIGHT:
					pass
				else:
					revt = SignalLeverEvent(position=RIGHT, label=self.label, name=self.name, panel=self.panel, lever=self)
					self.bmpPlate = SigLever.images[SIGRIGHT] if self.enabled else SigLever.images[SIGRIGHTDISABLED]
					self.requestedState = RIGHT
					wx.CallLater(5000, self.checkIfCompleted)

			self.Refresh()
			if revt is not None:
				wx.QueueEvent(self, revt)


		evt.Skip()

	def checkIfCompleted(self):
		if self.requestedState is None:
			return

		if self.state == NEUTRAL:
			self.bmpPlate = self.images[SIGNEUTRAL]
			self.requestedState = None
			self.Refresh()

	def inHotSpot(self, x, y):
		return 5 <= x <= 55 and 20 <= y <= 60

	def initBuffer(self):
		self.w, self.h = self.GetClientSize()
		if self.w <= 0 or self.h <= 0:
			return
		self.buffer = wx.Bitmap((self.w, self.h))
		self.redrawImage()

	def redrawImage(self):
		dc = wx.ClientDC(self)
		self.drawImage(dc)

	def drawImage(self, dc):
		dc.DrawBitmap(self.bmpL, 0,  8, False)
		dc.DrawBitmap(self.bmpN, 20, 0, False)
		dc.DrawBitmap(self.bmpR, 40, 8, False)
		dc.DrawBitmap(self.bmpPlate, 0, 25, False)
		if self.label is not None:
			dc.SetTextForeground(wx.Colour(255, 255, 0))
			dc.SetTextBackground(wx.Colour(0, 0, 0))
			dc.SetFont(self.labelFont)
			dc.DrawText(self.label, self.labelx, self.labely)
