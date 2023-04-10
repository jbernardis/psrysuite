import wx
BTNSZ = (120, 46)

class OptionsDlg(wx.Dialog):
	def __init__(self, parent, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Options Dialog")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.settings = settings
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsz = wx.BoxSizer(wx.VERTICAL)
		
		vsz.AddSpacer(20)
		
		self.cbSaveLog = wx.CheckBox(self, wx.ID_ANY, "Save Log on Exit")
		self.cbSaveLog.SetFont(textFont)
		vsz.Add(self.cbSaveLog)
		self.Bind(wx.EVT_CHECKBOX, self.onCb, self.cbSaveLog)
		self.cbSaveLog.SetValue(self.settings.savelogonexit)

		
		vsz.AddSpacer(20)
		
		self.cbRerunExtra = wx.CheckBox(self, wx.ID_ANY, "Allow Rerun of Extra Trains")
		self.cbRerunExtra.SetFont(textFont)
		vsz.Add(self.cbRerunExtra)
		self.Bind(wx.EVT_CHECKBOX, self.onCb, self.cbRerunExtra)
		self.cbRerunExtra.SetValue(self.settings.allowextrarerun)
		
		vsz.AddSpacer(20)
		
		btnsz = wx.BoxSizer(wx.HORIZONTAL)
		btnsz.AddSpacer(10)
		bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		bOK.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.onOK, bOK)
		btnsz.Add(bOK)
		
		btnsz.AddSpacer(20)
		bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		bCancel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.onCancel, bCancel)
		btnsz.Add(bCancel)
		
		btnsz.AddSpacer(20)
		
		vsz.Add(btnsz)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit();
		
	def onCb(self, _):
		if self.settings.savelogonexit != self.cbSaveLog.GetValue():
			self.modified = True
			return
		
		if self.settings.allowextrarerun != self.cbRerunExtra.GetValue():
			self.modified = True
			return
		self.modified = False
		
	def onClose(self, _):
		self.doCancel()
		
	def onCancel(self, _):
		self.doCancel()
		
	def onOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		rv1 = self.cbSaveLog.GetValue()
		if rv1 == self.settings.savelogonexit:
			rv1 = None
			
		rv2 = self.cbRerunExtra.GetValue()
		if rv2 == self.settings.allowextrarerun:
			rv2 = None
			
		return rv1, rv2
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Options haves been modified\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)


