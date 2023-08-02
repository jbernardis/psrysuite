import wx
import logging

MAXSTEPS = 9

class EditTrainDlg(wx.Dialog):
	def __init__(self, parent, train, block, locos, trains, existingTrains, atcFlag, arFlag, dx, dy):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit Train Details", pos=(dx, dy))
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		self.existingTrains = existingTrains		
		self.atcFlag = atcFlag
		self.arFlag = arFlag

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		name, loco = train.GetNameAndLoco()
		self.name = name
		atc = train.IsOnATC()
		ar = train.IsOnAR()
		self.block = block
		
		self.locos = locos
		self.trains = trains
		
		locoList  = sorted(list(locos.keys()), key=self.BuildLocoKey)
		trainList = sorted(list(trains.keys()))
			
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

		vsz.AddSpacer(20)
		if self.atcFlag or self.arFlag:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			
			if self.atcFlag:
				self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
				self.cbATC.SetFont(font)
				self.cbATC.SetValue(atc)
				hsz.Add(self.cbATC)
				
			if self.atcFlag and self.arFlag:
				hsz.AddSpacer(20)
	
			if self.arFlag:
				self.cbAR = wx.CheckBox(self, wx.ID_ANY, "Auto Router")
				self.cbAR.SetFont(font)
				self.cbAR.SetValue(ar)
				hsz.Add(self.cbAR)
				
			vsz.AddSpacer(20)
			vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		self.stDescr = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
		self.stDescr.SetFont(font)		
		vsz.Add(self.stDescr)
			
		vsz.AddSpacer(20)
		self.stFlags = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
		self.stFlags.SetFont(font)
		vsz.Add(self.stFlags)

		vsz.AddSpacer(20)
		self.stTrainInfo = []
		for _ in range(MAXSTEPS):
			st = wx.StaticText(self, wx.ID_ANY, "", size=(600, -1))
			st.SetFont(font)
			vsz.Add(st)
			self.stTrainInfo.append(st)
			
		vsz.AddSpacer(30)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.bSever = wx.Button(self, wx.ID_ANY, "Sever")
		self.bSever.SetToolTip("Sever this block from the rest of the train")

		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)
		bsz.AddSpacer(30)
		bsz.Add(self.bSever)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.onSever, self.bSever)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
		self.ShowTrainLocoDesc()

	def BuildLocoKey(self, lid):
		return int(lid)
		
	def OnLocoChoice(self, evt):
		self.chosenLoco = evt.GetString()
		self.ShowTrainLocoDesc()

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
		self.ShowTrainLocoDesc()
		evt.Skip()
		
	def OnTrainChoice(self, evt):
		self.chosenTrain = evt.GetString()
		self.ShowTrainLocoDesc()

	def OnTrainText(self, evt):
		nm = evt.GetString().upper()
		pos = self.cbTrainID.GetInsertionPoint()
		self.cbTrainID.ChangeValue(nm)
		self.cbTrainID.SetInsertionPoint(pos)
		self.chosenTrain = nm
		self.ShowTrainLocoDesc()
		evt.Skip()

	def ShowTrainLocoDesc(self):
		if self.chosenLoco in self.locos and self.locos[self.chosenLoco]["desc"] != None:
			self.stDescr.SetLabel(self.locos[self.chosenLoco]["desc"])
		else:
			self.stDescr.SetLabel("")
			
		if self.chosenTrain in self.trains:
			tr = self.trains[self.chosenTrain]
			track = tr["tracker"]
			for lx in range(MAXSTEPS):
				if lx >= len(track):
					self.stTrainInfo[lx].SetLabel("")
				else:
					self.stTrainInfo[lx].SetLabel("%-12.12s  %-4.4s  %s" % (track[lx][0], "(%d)" % track[lx][2], track[lx][1]))
					
			details = "Eastbound" if tr["eastbound"] else "Westbound"
			if tr["cutoff"]:
				details += " via cutoff"
			self.stFlags.SetLabel(details)
			
		else:
			for st in self.stTrainInfo:
				st.SetLabel("")
			self.stFlags.SetLabel("")

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		if self.chosenTrain != self.name and self.chosenTrain in self.existingTrains:
			blist = self.existingTrains[self.chosenTrain].GetBlockNameList()
			bstr = ", ".join(blist)
			
			adje, adjw = self.block.GetAdjacentBlocks()
			adjacent = False
			for adj in adje, adjw:
				if adj is not  None and adj.GetName() in blist:
					adjacent = True
					break

			if not adjacent:
				dlg = wx.MessageDialog(self, "Train %s already exists on the layout\nin block(s) %s" % (self.chosenTrain, bstr),
						   'Duplicate Train', wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				return

		self.EndModal(wx.ID_OK)
		
	def onSever(self, _):
		self.EndModal(wx.ID_CUT)

	def GetResults(self):
		t = self.chosenTrain
		l = self.chosenLoco
		atc = False if not self.atcFlag else self.cbATC.GetValue()
		ar = False if not self.arFlag else self.cbAR.GetValue()
		return t, l, atc, ar
