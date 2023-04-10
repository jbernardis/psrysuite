import wx
		
class DetailsDlg(wx.Dialog):
	def __init__(self, parent, tid, tinfo, desc, engineer):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Train Details")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		labelFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		labelFontLargeBold = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		
		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st1 = wx.StaticText(self, wx.ID_ANY, tid, size=(80, -1))
		st1.SetFont(labelFontLargeBold)

		descText ="%sbound %s" % ("East" if tinfo["eastbound"] else "West", tinfo["desc"])
		if tinfo["cutoff"]:
			descText += "(via cutoff)"
		st2 = wx.StaticText(self, wx.ID_ANY, descText)
		st2.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st1)
		hsz.Add(st2)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)

		print(str(desc))		
		if desc is None:
			ldesc = ""
		else:
			ldesc = desc.replace('&', '&&')
		st = wx.StaticText(self, wx.ID_ANY, "Loco: %s - %s" % (tinfo["loco"], ldesc))
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Engineer: %s" % engineer)
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		for stp in tinfo["tracker"]:
			st1 = wx.StaticText(self, wx.ID_ANY, "" if stp[0] is None else stp[0], size=(80, -1))
			st1.SetFont(labelFontBold)
			st2 = wx.StaticText(self, wx.ID_ANY, "(%2d)" % stp[2] if stp[2] > 0 else "", size=(60, -1))
			st2.SetFont(labelFontBold)
			st3 = wx.StaticText(self, wx.ID_ANY, "" if stp[1] is None else stp[1])
			st3.SetFont(labelFontBold)
			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(120)
			hsz.Add(st1)
			hsz.Add(st2)
			hsz.Add(st3)
			
			vsizer.Add(hsz)
			vsizer.AddSpacer(2)
			
		vsizer.AddSpacer(10)
		
		if tinfo["block"] is None or tinfo["block"] == "":
			block = "<unknown>"
		else:
			block = tinfo["block"]
			
		st = wx.StaticText(self, wx.ID_ANY, "Block: %s" % block)
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
				
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		self.SetSizer(hsizer)

		self.Layout()
		self.Fit()
		
	def onClose(self, _):
		self.Destroy()
