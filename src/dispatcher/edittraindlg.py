import wx
import logging

from dispatcher.losttrains import LostTrainsDlg

MAXSTEPS = 9
BUTTONSIZE = (90, 30)

class EditTrainDlg(wx.Dialog):
	def __init__(self, parent, train, block, locos, trains, engineers, existingTrains, atcFlag, arFlag, lostTrains, dx, dy):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Edit Train Details", pos=(dx, dy))
		self.parent = parent
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
		
		self.startingEast = train.GetEast()
		
		self.locos = locos
		self.trains = trains
		self.noEngineer = "<none>"
		self.engineers = [self.noEngineer] + sorted(engineers)
		self.lostTrains = lostTrains
		
		locoList  = sorted(list(locos.keys()), key=self.BuildLocoKey)
		trainList = sorted(list(trains.keys()))
			
		font = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

		lblTrain = wx.StaticText(self, wx.ID_ANY, "Train:", size=(120, -1))
		lblTrain.SetFont(font)
		self.cbTrainID = wx.ComboBox(self, wx.ID_ANY, name,
					choices=trainList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbTrainID.SetFont(font)
		
		self.chosenTrain = name
		
		self.Bind(wx.EVT_COMBOBOX, self.OnTrainChoice, self.cbTrainID)
		self.Bind(wx.EVT_TEXT, self.OnTrainText, self.cbTrainID)
		
		self.chosenLoco = loco
		
		lblLoco  = wx.StaticText(self, wx.ID_ANY, "Loco:", size=(120, -1))
		lblLoco.SetFont(font)
		self.cbLocoID = wx.ComboBox(self, wx.ID_ANY, loco,
					choices=locoList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbLocoID.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnLocoChoice, self.cbLocoID)
		self.Bind(wx.EVT_TEXT, self.OnLocoText, self.cbLocoID)

		self.chosenEngineer = train.GetEngineer()
		if self.chosenEngineer is None:
			self.chosenEngineer = self.noEngineer
			
		if self.chosenEngineer not in self.engineers:
			self.engineers.append(self.chosenEngineer)
		
		lblEngineer  = wx.StaticText(self, wx.ID_ANY, "Engineer:", size=(120, -1))
		lblEngineer.SetFont(font)
		self.cbEngineer = wx.ComboBox(self, wx.ID_ANY, self.chosenEngineer,
					choices=self.engineers,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER, size=(120, -1))
		self.cbEngineer.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnEngChoice, self.cbEngineer)
		self.Bind(wx.EVT_TEXT, self.OnEngText, self.cbEngineer)
		
		self.bClearEng = wx.Button(self, wx.ID_ANY, "Clear", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.OnBClearEng, self.bClearEng)

		lostCt = self.lostTrains.Count()
		if lostCt > 0:		
			self.bLostTrains = wx.Button(self, wx.ID_ANY, "Lost Trains", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBLostTrains, self.bLostTrains)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblTrain)
		hsz.AddSpacer(10)
		hsz.Add(self.cbTrainID)
		if lostCt > 0:
			hsz.AddSpacer(20)
			hsz.Add(self.bLostTrains)
		
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblLoco)
		hsz.AddSpacer(10)
		hsz.Add(self.cbLocoID)
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblEngineer)
		hsz.AddSpacer(10)
		hsz.Add(self.cbEngineer)
		hsz.AddSpacer(20)
		hsz.Add(self.bClearEng)
		vsz.Add(hsz)

		vsz.AddSpacer(20)
		self.cbATC = None
		if self.atcFlag or self.arFlag:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			
			if self.atcFlag:
				self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
				self.cbATC.SetFont(font)
				self.cbATC.SetValue(atc)
				hsz.Add(self.cbATC)
				self.cbATC.Enable(self.chosenLoco != "??")
				
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

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BUTTONSIZE)
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BUTTONSIZE)
		self.bSever = wx.Button(self, wx.ID_ANY, "Split", size=BUTTONSIZE)
		self.bSever.SetToolTip("Split this train into 2 sections")
		self.bMerge = wx.Button(self, wx.ID_ANY, "Merge", size=BUTTONSIZE)
		self.bMerge.SetToolTip("Merge this train with another")
		self.bReverse = wx.Button(self, wx.ID_ANY, "Reverse", size=BUTTONSIZE)
		self.bReverse.SetToolTip("Reverse Direction on this train")

		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)
		bsz.AddSpacer(30)
		bsz.Add(self.bSever)
		bsz.AddSpacer(30)
		bsz.Add(self.bMerge)
		bsz.AddSpacer(30)
		bsz.Add(self.bReverse)

		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.onSever, self.bSever)
		self.Bind(wx.EVT_BUTTON, self.onMerge, self.bMerge)
		self.Bind(wx.EVT_BUTTON, self.onReverse, self.bReverse)

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
		if self.cbATC is not None:
			self.cbATC.Enable(self.chosenLoco != "??")
		self.ShowTrainLocoDesc()

	def OnLocoText(self, evt):
		lid = evt.GetString()
		pos = self.cbLocoID.GetInsertionPoint()
		self.cbLocoID.ChangeValue(lid)
		self.cbLocoID.SetInsertionPoint(pos)
			
		self.chosenLoco = lid
		if self.cbATC is not None:
			self.cbATC.Enable(self.chosenLoco != "??")
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
		
	def OnEngChoice(self, evt):
		self.chosenEngineer = evt.GetString()

	def OnEngText(self, evt):
		nm = evt.GetString()
		pos = self.cbEngineer.GetInsertionPoint()
		self.cbEngineer.ChangeValue(nm)
		self.cbEngineer.SetInsertionPoint(pos)
		self.chosenEngineer = nm
		evt.Skip()
		
	def OnBClearEng(self, evt):
		self.chosenEngineer = self.noEngineer
		self.cbEngineer.SetValue(self.noEngineer)
		
	def OnBLostTrains(self, evt):
		dlg = LostTrainsDlg(self, self.lostTrains)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			trname = dlg.GetResult()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		tr = self.lostTrains.GetTrain(trname)
		if tr is None:
			self.parent.PopupEvent("Unable to identify lost train")
			return

		loco, engineer, east, _ = tr
		east = True if east == 'E' else False
	
		rc = wx.ID_YES		
		if east != self.startingEast:
			mdlg = wx.MessageDialog(self,  'Trains are moving in opposite directions.\nPress "Yes" to proceed',
	                              'Opposite Directions',
	                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
	                              )
			rc = mdlg.ShowModal()
			mdlg.Destroy()


		if rc == wx.ID_YES:
			self.startingEast = east
			self.cbTrainID.SetValue(trname)
			self.cbLocoID.SetValue(loco)
			self.cbEngineer.SetValue(self.noEngineer if engineer is None or engineer == "None" else engineer)
			dlg.Destroy()
			return

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
		
		self.lostTrains.Remove(self.chosenTrain)
		self.EndModal(wx.ID_OK)
		
	def onSever(self, _):
		self.EndModal(wx.ID_CUT)
		
	def onMerge(self, _):
		self.EndModal(wx.ID_PASTE)
		
	def onReverse(self, _):
		self.EndModal(wx.ID_BACKWARD)

	def GetResults(self):
		t = self.chosenTrain
		l = self.chosenLoco
		e = self.chosenEngineer
		if e == self.noEngineer:
			e = None
			
		atc = False if not self.atcFlag else self.cbATC.GetValue()
		ar = False if not self.arFlag else self.cbAR.GetValue()
		try:
			tr = self.trains[self.chosenTrain]
		except KeyError:
			tr = None
		if tr is None:
			east = self.startingEast # using the eastbound value of the train we came into here with
		else:
			east = tr["eastbound"]
		return t, l, e, atc, ar, east
