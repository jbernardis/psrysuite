import wx

		
class ARBlockDlg(wx.Dialog):
	def __init__(self, parent, blist):
		self.parent = parent
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("AR Blocks")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.blist = blist
		self.nblocks = len(blist)
		
		self.clbBlocks = wx.CheckListBox(self, wx.ID_ANY, choices=self.blist)

		self.bCheckAll = wx.Button(self, wx.ID_ANY, "All", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBAll, self.bCheckAll)
		self.bCheckNone = wx.Button(self, wx.ID_ANY, "None", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBNone, self.bCheckNone)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		vsz.Add(wx.StaticText(self, wx.ID_ANY, "Choose block transitions for automatic routing"))	
		vsz.AddSpacer(5)	
		vsz.Add(self.clbBlocks, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(10)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.Add(self.bCheckAll)
		bsz.AddSpacer(5)
		bsz.Add(self.bCheckNone)
		bsz.AddSpacer(20)
		bsz.Add(self.bOK)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()
		
		self.CheckAll(True)
		
	def OnBAll(self, _):
		self.CheckAll(True)
		
	def OnBNone(self, _):
		self.CheckAll(False)
		
	def CheckAll(self, flag):
		for i in range(self.nblocks):
			self.clbBlocks.Check(i, flag)
				
	def GetResults(self):
		return self.clbBlocks.GetCheckedItems()

	def OnClose(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)

