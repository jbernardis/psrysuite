import wx

class EngQueueDlg(wx.Dialog):
	def __init__(self, parent, eng, cbClose):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Engineer Queue", style=wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT |wx.STAY_ON_TOP)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.cbClose = cbClose
		
		self.engList = [e for e in eng]
		
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		vsz.AddSpacer(20)
		
		self.lbEngs = wx.ListBox(self, wx.ID_ANY, size=(100, 300), choices=self.engList)
		self.lbEngs.SetFont(textFont)
		vsz.Add(self.lbEngs)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit();
		
	def updateEngQueue(self, eng):
		self.engList = [e for e in eng]
		self.lbEngs.SetItems(self.engList)
		
	def onClose(self, _):
		if callable(self.cbClose):
			self.cbClose()
			
		
		
