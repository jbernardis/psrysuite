import wx

class EditTrainDlg(wx.Dialog):
	def __init__(self, parent, train, locoList, trainList, dispatcher):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit Train Details")
		self.Bind(wx.EVT_CLOSE, self.onCancel)
		
		self.dispatcher = dispatcher

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		name, loco = train.GetNameAndLoco()
		atc = train.IsOnATC()
			
		font = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

		lblTrain = wx.StaticText(self, wx.ID_ANY, "Train:", size=(90, -1))
		lblTrain.SetFont(font)
		self.cbTrainID = wx.ComboBox(self, wx.ID_ANY, name,
					choices=trainList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
		self.cbTrainID.SetFont(font)
		
		self.chosenTrain = name
		
		self.Bind(wx.EVT_COMBOBOX, self.OnTrainChoice, self.cbTrainID)
		self.Bind(wx.EVT_TEXT, self.OnTrainText, self.cbTrainID)
		
		self.chosenLoco = loco
		
		lblLoco  = wx.StaticText(self, wx.ID_ANY, "Loco:", size=(90, -1))
		lblLoco.SetFont(font)
		self.cbLocoID = wx.ComboBox(self, wx.ID_ANY, loco,
					choices=locoList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
		self.cbLocoID.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnLocoChoice, self.cbLocoID)
		self.Bind(wx.EVT_TEXT, self.OnLocoText, self.cbLocoID)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblTrain)
		hsz.AddSpacer(10)
		hsz.Add(self.cbTrainID)
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblLoco)
		hsz.AddSpacer(10)
		hsz.Add(self.cbLocoID)
		vsz.Add(hsz)

		if dispatcher:
			self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
			self.cbATC.SetValue(atc)
			vsz.AddSpacer(10)
			vsz.Add(self.cbATC, 0, wx.ALIGN_CENTER_HORIZONTAL)
		

		vsz.AddSpacer(30)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
	def OnLocoChoice(self, evt):
		self.chosenLoco = evt.GetString()

	def OnLocoText(self, evt):
		lid = evt.GetString()
		if not lid.isdigit():			
			lid = "".join([c for c in lid if c.isdigit()])
			pos = self.cbLocoID.GetInsertionPoint()
			self.cbLocoID.ChangeValue(lid)
			if pos > 0:
				pos -= 1
			self.cbLocoID.SetInsertionPoint(pos)
			
		self.chosenLoco = lid
		evt.Skip()
		
	def OnTrainChoice(self, evt):
		self.chosenTrain = evt.GetString()

	def OnTrainText(self, evt):
		nm = evt.GetString().upper()
		pos = self.cbTrainID.GetInsertionPoint()
		self.cbTrainID.ChangeValue(nm)
		self.cbTrainID.SetInsertionPoint(pos)
		self.chosenTrain = nm
		evt.Skip()

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		self.EndModal(wx.ID_OK)

	def GetResults(self):
		t = self.chosenTrain
		l = self.chosenLoco
		atc = False if not self.dispatcher else self.cbATC.GetValue()
		return t, l, atc
