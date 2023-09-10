import wx
		
class DepartureTimerDlg(wx.Dialog):
	def __init__(self, parent, cbClose):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Departure Timer")
		self.cbClose = cbClose
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.running = False

		largeFont     = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		largeFontBold = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD,   faceName="Arial"))
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Time to Next Departure: ")
		st.SetFont(largeFont)
		hsz.Add(st)
		hsz.AddSpacer(10)
		self.tcNextDeparture = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), style=wx.TE_RIGHT+wx.TE_READONLY)
		self.tcNextDeparture.SetFont(largeFontBold)
		hsz.Add(self.tcNextDeparture)
		
		vsizer.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)		
		self.bStart = wx.Button(self, wx.ID_ANY, "Start Timer", size=(140, 40))
		self.bStart.SetFont(largeFontBold)
		self.Bind(wx.EVT_BUTTON, self.onBStart, self.bStart)
		hsz.Add(self.bStart)
		hsz.AddSpacer(10)
		
		self.bResume = wx.Button(self, wx.ID_ANY, "Resume", size=(120, 40))
		self.bResume.SetFont(largeFontBold)
		self.Bind(wx.EVT_BUTTON, self.onBResume, self.bResume)
		hsz.Add(self.bResume)
		self.bResume.Enable(False)
		
		vsizer.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Departure Interval: ")
		st.SetFont(largeFont)
		hsz.Add(st)
		hsz.AddSpacer(20)
		sc = wx.SpinCtrl(self, -1, "", style=wx.SP_ARROW_KEYS+wx.ALIGN_RIGHT)
		sc.SetRange(0, 10)
		sc.SetValue(1)
		sc.SetIncrement(1)
		sc.SetFont(largeFontBold)
		hsz.Add(sc)
		self.scMInterval = sc
		st = wx.StaticText(self, wx.ID_ANY, "min")
		st.SetFont(largeFont)
		hsz.Add(st)
		hsz.AddSpacer(5)
		sc = wx.SpinCtrl(self, -1, "", style=wx.SP_ARROW_KEYS+wx.ALIGN_RIGHT+wx.SP_WRAP)
		sc.SetRange(0, 59)
		sc.SetValue(0)
		sc.SetIncrement(1)
		sc.SetFont(largeFontBold)
		hsz.Add(sc)
		self.scSInterval = sc
		st = wx.StaticText(self, wx.ID_ANY, "sec")
		st.SetFont(largeFont)
		hsz.Add(st)
		
		vsizer.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)		
				
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		self.SetSizer(hsizer)

		self.Layout()
		self.Fit()
		
		self.timeVal = 0
		self.updateTimer()
		
	def tick(self):
		if not self.running:
			return 
		
		if self.timeVal > 0:
			self.timeVal -= 1
			self.updateTimer()
			if self.timeVal == 0:
				pass
			
		else:
			self.timeVal = self.getIntervalValue()
			self.updateTimer()
		
	def onBStart(self, _):
		if self.running:
			self.running = False
			self.bStart.SetLabel("Start Timer")
			self.updateTimer()
			self.tcNextDeparture.Refresh()
			self.bResume.Enable(True)
		else:
			self.running = True
			self.bStart.SetLabel("Stop Timer")
			self.timeVal = self.getIntervalValue()
			self.updateTimer()
			self.bResume.Enable(False)
			
	def onBResume(self, _):
		self.running = True
		self.bStart.SetLabel("Stop Timer")
		self.bResume.Enable(False)
			
	def getIntervalValue(self):
		return self.scMInterval.GetValue() * 60 + self.scSInterval.GetValue()
	
	def hiliteTime(self, flag=True):
		if flag and self.running:
			self.tcNextDeparture.SetBackgroundColour(wx.Colour(255, 0, 0))
			self.tcNextDeparture.SetForegroundColour(wx.Colour(255, 255, 255))
		else:
			self.tcNextDeparture.SetBackgroundColour(wx.Colour(255, 255, 255))
			self.tcNextDeparture.SetForegroundColour(wx.Colour(0, 0, 0))
			
	def updateTimer(self):
		self.hiliteTime(self.timeVal <= 10)
		self.tcNextDeparture.SetValue("%d:%02d" % (int(self.timeVal/60), self.timeVal % 60))
		
	def onClose(self, _):
		self.cbClose()
		self.Destroy()
