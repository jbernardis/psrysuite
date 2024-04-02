import wx
from dispatcher.constants import BlockName

BUTTONSIZE = (90, 30)
COLSIG = 100
COLOS = 350
COLBLK = 60

class RouteTrainDlg(wx.Dialog):
	def __init__(self, parent, train, trinfo, isDispatcher):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.train = train
		self.trinfo = trinfo
		self.sequence = trinfo["sequence"]
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.SetTitle("Route Status for Train %s" % train.GetName())
		
		self.font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.bmpArrow = self.parent.bitmaps.arrow
		self.bmpClear = self.parent.bitmaps.clear
		self.lastStepx = None

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(self.AddHeaders())
		vsz.AddSpacer(10)

		name, loco = train.GetNameAndLoco()
		self.name = name

		self.bmps = []		
		vsz.Add(self.AddLine(None, None, None, trinfo["startblock"]))
		
		for step in trinfo["sequence"]:
			vsz.Add(self.AddLine(step["signal"], step["os"], step["route"], step["block"]))
			
		vsz.AddSpacer(20)
		
		if isDispatcher:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
		
			self.bRoute = wx.Button(self, wx.ID_ANY, "Set Route", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBRoute, self.bRoute);
			hsz.Add(self.bRoute)
			
			hsz.AddSpacer(50)
			
			self.bSignal = wx.Button(self, wx.ID_ANY, "Set Signal", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBSignal, self.bSignal);
			hsz.Add(self.bSignal)
			
			vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
			vsz.AddSpacer(10)
		
		self.msg = wx.StaticText(self, wx.ID_ANY, "                                      ")
		self.msg.SetFont(self.font)
			
		vsz.Add(self.msg)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def OnBRoute(self, evt):
		if self.lastStepx is None:
			return

		sx = self.lastStepx				
		rc, msg = self.parent.SetRouteThruOS(self.sequence[sx]["os"], self.sequence[sx]["route"], self.sequence[sx]["block"], self.sequence[sx]["signal"])
		
		if not rc or (rc and msg is not None):
			self.parent.PopupEvent(msg)

	def OnBSignal(self, evt):
		if self.lastStepx is None:
			return

		sx = self.lastStepx				
		rc, msg = self.parent.SetRouteSignal(self.sequence[sx]["os"], self.sequence[sx]["route"], self.sequence[sx]["block"], self.sequence[sx]["signal"])
		
		if not rc or (rc and msg is not None):
			self.parent.PopupEvent(msg)
		
	def UpdateTrainStatus(self):
		self.DetermineTrainPosition()
		
	def DetermineTrainPosition(self):
		'''
		find the furthest forward block
		'''
		trainBlocks = self.train.GetBlockList()
		stepx = 0
		i = 1
		for step in self.sequence:
			if step["block"] in trainBlocks or step["os"] in trainBlocks:
				stepx = i
			i += 1
			
		if stepx == 0 and self.trinfo["startblock"] not in trainBlocks:
			stepx = None
			
		if stepx is None:
			self.msg.SetLabel("Train is in unexpected block")
		elif stepx != self.lastStepx:
			self.bmps[stepx].SetBitmap(self.bmpArrow)
			
			if self.lastStepx is not None:
				self.bmps[self.lastStepx].SetBitmap(self.bmpClear)
			
		self.lastStepx = stepx
		
	def onClose(self, evt):
		self.parent.CloseRouteTrainDlg(self.name)
		
	def AddHeaders(self):
		sigst = wx.StaticText(self, wx.ID_ANY, "Signal", size=(COLSIG, -1))
		sigst.SetFont(self.font)
			
		rtest = wx.StaticText(self, wx.ID_ANY, "OS(Route)", size=(COLOS, -1))
		rtest.SetFont(self.font)
			
		blkst = wx.StaticText(self, wx.ID_ANY, "Block", size=(COLBLK, -1))
		blkst.SetFont(self.font)
		
		bmp = wx.StaticBitmap(self, wx.ID_ANY, self.bmpClear)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(bmp)
		hsz.AddSpacer(10)
		hsz.Add(sigst)
		hsz.Add(rtest)
		hsz.Add(blkst)
		
		return hsz
		
	def AddLine(self, signame, osname, rtname, blkname):
		if signame is None:
			sigst = wx.StaticText(self, wx.ID_ANY, "", size=(COLSIG, -1))
		else:
			sigst = wx.StaticText(self, wx.ID_ANY, signame, size=(COLSIG, -1))
		sigst.SetFont(self.font)
			
		if osname is None or rtname is None:
			rtest = wx.StaticText(self, wx.ID_ANY, "", size=(	COLOS, -1))
		else:
			try:
				rn = rtname.split("Rt")[1]
			except IndexError:
				rn = rtname
			rtest = wx.StaticText(self, wx.ID_ANY, "%s(%s)" % (BlockName(osname), rn), size=(COLOS, -1))
		rtest.SetFont(self.font)
			
		blkst = wx.StaticText(self, wx.ID_ANY, blkname, size=(COLBLK, -1))
		blkst.SetFont(self.font)
		
		bmp = wx.StaticBitmap(self, wx.ID_ANY, self.bmpClear)
		self.bmps.append(bmp)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(bmp)
		hsz.AddSpacer(10)
		hsz.Add(sigst)
		hsz.Add(rtest)
		hsz.Add(blkst)
		
		return hsz
