import wx

BSIZE = (100, 26)


class LostTrains:
	def __init__(self):
		self.trains = {}
		
	def Add(self, train, loco, engineer, east, block, route):
		if train.startswith("??"):
			return False
		
		self.trains[train] = (loco, engineer, east, block, route)
		return True
		
	def Remove(self, train):
		try:
			del(self.trains[train])
		except KeyError:
			return False
			
		return True
	
	def GetTrain(self, tid):
		if tid is None or tid not in self.trains:
			return None
		
		return self.trains[tid]
	
	def GetList(self):
		return [(train, info[0], info[1], info[2], info[3], info[4]) for train, info in self.trains.items()]
	
	def Count(self):
		return len(self.trains)
	
class LostTrainsDlg(wx.Dialog):
	def __init__(self, parent, lostTrains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.lostTrains = lostTrains
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.pendingDeletions = []
		self.chosenTrain = None

		self.choices = self.DetermineChoices()
		
		self.SetTitle("Lost Trains")
		

		vsz = wx.BoxSizer(wx.VERTICAL)

		
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, 'Train / Dir / Loco / Engineer / Block / Route')
		vsz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(10)

		self.ch = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self.ch)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDClick, self.ch)
	
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "Select", size=BSIZE)
		self.bOK.SetToolTip("Perform pending removals and return with the checked train as the selection")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)		
		hsz.Add(self.bOK)
		self.bOK.Enable(False)
		
		hsz.AddSpacer(20)
		
		self.bRemove = wx.Button(self, wx.ID_ANY, "Remove", size=BSIZE)
		self.bRemove.SetToolTip("Mark the checked trains for removal.  Removal is pending until the dialog box is exited")
		self.Bind(wx.EVT_BUTTON, self.OnBRemove, self.bRemove)		
		hsz.Add(self.bRemove)
		self.bRemove.Enable(False)
		
		hsz.AddSpacer(20)
		
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=BSIZE)
		self.bExit.SetToolTip("Perform pending removals and exit the dialog box without selecting a train")
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)		
		hsz.Add(self.bExit)
		
		hsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
		self.bCancel.SetToolTip("Exit the dialog box without doing pending removals and without selecting a train")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)		
		hsz.Add(self.bCancel)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()
		
	def DetermineChoices(self):
		self.trainNames =  [t[0] for t in self.lostTrains.GetList() if t[0] not in self.pendingDeletions]
		return ["%s / %s / %s / %s / %s / %s" % (t[0], "E" if t[3] else "W", t[1], t[2], t[4], t[5]) for t in self.lostTrains.GetList() if t[0] not in self.pendingDeletions]
	
	def DoPendingRemoval(self):
		for tname in self.pendingDeletions:
			self.lostTrains.Remove(tname)
		
	def OnDClick(self, evt):
		# perform pending deletions and return the current item
		tx = evt.GetSelection()
		self.chosenTrain = self.trainNames[tx]
		self.EndModal(wx.ID_OK)

	def OnCheck(self, event):
		checkedItems = self.ch.GetCheckedItems()
		n = len(checkedItems)
		if n == 0:
			self.bOK.Enable(False)
			self.bRemove.Enable(False)
		elif n == 1:
			self.bOK.Enable(True)
			self.bRemove.Enable(True)
		else:
			self.bOK.Enable(False)
			self.bRemove.Enable(True)
		
	def OnBRemove(self, evt):
		checkedItems = self.ch.GetCheckedItems()
		self.pendingDeletions.extend([self.trainNames[i] for i in checkedItems])
		self.ch.SetItems(self.DetermineChoices())
		self.bOK.Enable(False)
		self.bRemove.Enable(False)
		
	def OnBOK(self, evt):
		# dopending removals and set up the selected train for retrieval
		self.DoPendingRemoval()
		checkedItems = self.ch.GetCheckedItems()
		if len(checkedItems) == 0:
			return 
		
		tx = checkedItems[0]
		self.chosenTrain = self.trainNames[tx]
		self.EndModal(wx.ID_OK)
		
	def OnBExit(self, evt):
		# perform pendingg deletions and exit without selecting a lost train
		self.DoPendingRemoval()
		self.chosenTrain = None
		self.EndModal(wx.ID_CANCEL)
		
	def OnBCancel(self, evt):
		self.DoCancel()
		
	def OnClose(self, evt):
		self.DoCancel()
		
	def DoCancel(self):
		# exit without doing anything
		self.chosenTrain = None
		self.EndModal(wx.ID_CANCEL)
		
	def GetResult(self):
		return self.chosenTrain


class LostTrainsRecoveryDlg(wx.Dialog):
	def __init__(self, parent, lostTrains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.lostTrains = lostTrains
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.pendingDeletions = []
		self.chosenTrain = None

		self.choices = self.DetermineChoices()
		
		self.SetTitle("Recover Lost Trains")
		

		vsz = wx.BoxSizer(wx.VERTICAL)

		
		vsz.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "Select train(s) to recover")
		vsz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		
		vszl = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, 'Train / Dir / Loco / Engineer / Block / Route')
		vszl.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszl.AddSpacer(10)

		self.ch = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices, size=(-1, 220))
		vszl.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self.ch)
		self.ch.SetCheckedItems(range(len(self.choices)))
	
		vszl.AddSpacer(20)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		
		self.bAll = wx.Button(self, wx.ID_ANY, "Select All", size=BSIZE)
		self.bAll.SetToolTip("Select All trains")
		self.Bind(wx.EVT_BUTTON, self.OnBAll, self.bAll)		
		vszr.Add(self.bAll)
		
		vszr.AddSpacer(10)
		
		self.bSheffield = wx.Button(self, wx.ID_ANY, "Sheffield", size=BSIZE)
		self.bSheffield.SetToolTip("Select trains in Sheffield yard")
		self.Bind(wx.EVT_BUTTON, self.OnBSheffield, self.bSheffield)		
		vszr.Add(self.bSheffield)
		
		vszr.AddSpacer(10)
		
		self.bNassau = wx.Button(self, wx.ID_ANY, "Nassau", size=BSIZE)
		self.bNassau.SetToolTip("Select trains in Wilson City")
		self.Bind(wx.EVT_BUTTON, self.OnBNassau, self.bNassau)		
		vszr.Add(self.bNassau)
		
		vszr.AddSpacer(10)
		
		self.bHyde = wx.Button(self, wx.ID_ANY, "Hyde", size=BSIZE)
		self.bHyde.SetToolTip("Select trains in Hyde yard")
		self.Bind(wx.EVT_BUTTON, self.OnBHyde, self.bHyde)		
		vszr.Add(self.bHyde)
		
		vszr.AddSpacer(10)
		
		self.bPort = wx.Button(self, wx.ID_ANY, "Port", size=BSIZE)
		self.bPort.SetToolTip("Select trains in Southport")
		self.Bind(wx.EVT_BUTTON, self.OnBPort, self.bPort)		
		vszr.Add(self.bPort)
		
		vszr.AddSpacer(10)
		
		self.bWaterman = wx.Button(self, wx.ID_ANY, "Waterman", size=BSIZE)
		self.bWaterman.SetToolTip("Select trains in Waterman yard")
		self.Bind(wx.EVT_BUTTON, self.OnBWaterman, self.bWaterman)		
		vszr.Add(self.bWaterman)
		
		vszr.AddSpacer(10)
		
		self.bYard = wx.Button(self, wx.ID_ANY, "Koehlstadt", size=BSIZE)
		self.bYard.SetToolTip("Select trains in Koehlstadt")
		self.Bind(wx.EVT_BUTTON, self.OnBYard, self.bYard)		
		vszr.Add(self.bYard)
		
		vszr.AddSpacer(10)
		
		self.bNone = wx.Button(self, wx.ID_ANY, "Select None", size=BSIZE)
		self.bNone.SetToolTip("Deselect All trains")
		self.Bind(wx.EVT_BUTTON, self.OnBNone, self.bNone)		
		vszr.Add(self.bNone)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(vszl, 2)
		hsz.AddSpacer(20)
		hsz.Add(vszr, 1)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
		self.bOK.SetToolTip("Recover the selected trains")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)		
		hsz.Add(self.bOK)
		
		hsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
		self.bCancel.SetToolTip("Exit the dialog box without making any changes")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)		
		hsz.Add(self.bCancel)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()
		
	def DetermineChoices(self):
		self.trainNames =  [t[0] for t in self.lostTrains]
		return ["%s / %s / %s / %s / %s / %s" % (t[0], "E" if t[3] else "W", t[1], t[2], t[4], t[5]) for t in self.lostTrains]
	
	def ApplyBlockFilter(self, blocks):
		for idx in range(len(self.lostTrains)):
			lt = self.lostTrains[idx]
			self.ch.Check(idx, check=lt[4] in blocks)
		self.SetOKButton()

	def OnCheck(self, event):
		self.SetOKButton()
		
	def SetOKButton(self):
		checkedItems = self.ch.GetCheckedItems()
		n = len(checkedItems)
		if n == 0:
			self.bOK.Enable(False)
		else:
			self.bOK.Enable(True)
			
	def OnBAll(self, evt):
		self.ch.SetCheckedItems(range(len(self.choices)))
		self.bOK.Enable(True)
			
	def OnBNone(self, evt):
		self.ch.SetCheckedItems([])
		self.bOK.Enable(False)
		
	def OnBSheffield(self, evt):
		self.ApplyBlockFilter(["C21", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54"])
		
	def OnBNassau(self, evt):
		self.ApplyBlockFilter(["N12", "N22", "N31", "N32", "N41", "N42"])
		
	def OnBHyde(self, evt):
		self.ApplyBlockFilter(["H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43"])
		
	def OnBPort(self, evt):
		self.ApplyBlockFilter(["P1", "P2", "P3", "P4", "P5", "P6", "P7"])
		
	def OnBYard(self, evt):
		self.ApplyBlockFilter(["Y50", "Y51", "Y52", "Y53"])
		
	def OnBWaterman(self, evt):
		self.ApplyBlockFilter(["Y81", "Y82", "Y83", "Y84"])
		
	def OnBOK(self, evt):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, evt):
		self.DoCancel()
		
	def OnClose(self, evt):
		self.DoCancel()
		
	def DoCancel(self):
		self.EndModal(wx.ID_CANCEL)
		
	def GetResult(self):
		checkedItems = self.ch.GetCheckedItems()
		results = [self.lostTrains[i] for i in checkedItems]

		return results
