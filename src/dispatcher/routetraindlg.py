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
		
		self.SetTitle("Route Status")
		
		self.font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.fontTrainID = wx.Font(wx.Font(22, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.bmpArrow = self.parent.bitmaps.arrow
		self.bmpClear = self.parent.bitmaps.clear
		self.lastStepx = None

		vsz = wx.BoxSizer(wx.VERTICAL)

		name, loco = train.GetNameAndLoco()
		self.name = name
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Train:")
		st.SetFont(self.font)
		hsz.Add(st, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(10)
		st = wx.StaticText(self, wx.ID_ANY, train.GetName())
		st.SetFont(self.fontTrainID)
		hsz.Add(st)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)
		vsz.Add(self.AddHeaders())
		vsz.AddSpacer(10)
		
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
		self.CenterOnScreen()


	def OnBRoute(self, evt):
		if self.lastStepx is None:
			return
		
		if self.lastStepx >= len(self.sequence):
			if self.trinfo["startblock"] == self.sequence[-1]["block"]:
				self.ClearArrow(self.lastStepx)
				self.lastStepx = 0
				self.SetArrow(self.lastStepx)
				
		if self.lastStepx >= len(self.sequence):
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
		found = False
		i = 1
		for step in self.sequence:
			if step["block"] in trainBlocks or step["os"] in trainBlocks:
				stepx = i
				found = True
			elif found:
				break
			i += 1
	
		# if the train is in the last block, and if the last block is the same as the start block, and the train
		# is not in the next to last block, then put the train in the first block
		
		if stepx == len(self.sequence) and self.trinfo["startblock"] == self.sequence[-1]["block"] and self.sequence[-2]["block"] not in trainBlocks:
			stepx = 0
			
		if stepx == 0 and self.trinfo["startblock"] not in trainBlocks:
			stepx = None
			self.msg.SetLabel("Train is in unexpected block")
		else:
			self.msg.SetLabel("")
			if stepx != self.lastStepx:
				self.SetArrow(stepx)
			
		if stepx != self.lastStepx:
			self.ClearArrow(self.lastStepx)
			
		self.lastStepx = stepx
		
	def SetArrow(self, sx):
		if sx is None:
			return
		self.bmps[sx].SetBitmap(self.bmpArrow)
		
	def ClearArrow(self, sx):
		if sx is None:
			return
		self.bmps[sx].SetBitmap(self.bmpClear)
		
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
