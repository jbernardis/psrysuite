import wx

class SimScriptDlg(wx.Dialog):
	def __init__(self, parent, script, trainid):
		self.parent = parent
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Simulator Script for train %s" % trainid)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.script = script
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		tcScript = wx.TextCtrl(self, wx.ID_ANY, script,
				size=(300, 300), style=wx.TE_MULTILINE)
		vsz.Add(tcScript)
		vsz.AddSpacer(10)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bSave)
		bsz.Add(self.bSave)
		bsz.AddSpacer(20)
		
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit")
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
		bsz.Add(self.bExit)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		
		self.Fit()
		self.Layout()

	def OnClose(self, _):
		self.DoClose()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBExit(self, _):
		self.DoClose()
		
	def DoClose(self):
		self.EndModal(wx.ID_CANCEL)
