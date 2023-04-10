import wx
		
class AboutDlg(wx.Dialog):
	def __init__(self, parent, bmp, versiondate):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Train Tracker")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		largeFontBold = wx.Font(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "TRAIN TRACKER")
		st.SetFont(largeFontBold)
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(10)
		
		self.SetSizer(vsizer)
		b = wx.StaticBitmap(self, wx.ID_ANY, bmp)
		vsizer.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "version:", size=(100, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, versiondate, size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "github:", size=(100, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "https://github.com/jbernardis/traintracker", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "written by:", size=(100, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "Jeff Bernardis", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)


		self.Layout()
		self.Fit()
		
	def onClose(self, _):
		self.Destroy()
