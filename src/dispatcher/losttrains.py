import wx

class LostTrains:
	def __init__(self):
		self.trains = {}
		
	def Add(self, train, loco, engineer, east, block):
		if train.startswith("??"):
			return False
		
		self.trains[train] = (loco, engineer, east, block)
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
		return [(train, info[0], info[1], info[2], info[3]) for train, info in self.trains.items()]
	
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
		
		st = wx.StaticText(self, wx.ID_ANY, 'Train / Dir / Loco / Engineer / Block')
		vsz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(10)

		self.ch = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self.ch)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDClick, self.ch)
	
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "Select")
		self.bOK.SetToolTip("Perform pending removals and return with the checked train as the selection")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)		
		hsz.Add(self.bOK)
		self.bOK.Enable(False)
		
		hsz.AddSpacer(20)
		
		self.bRemove = wx.Button(self, wx.ID_ANY, "Remove")
		self.bRemove.SetToolTip("Mark the checked trains for removal.  Removal is pending until the dialog box is exited")
		self.Bind(wx.EVT_BUTTON, self.OnBRemove, self.bRemove)		
		hsz.Add(self.bRemove)
		self.bRemove.Enable(False)
		
		hsz.AddSpacer(20)
		
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit")
		self.bExit.SetToolTip("Perform pending removals and exit the dialog box without selecting a train")
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)		
		hsz.Add(self.bExit)
		
		hsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
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
		return ["%s / %s / %s / %s / %s" % (t[0], "E" if t[3] else "W", t[1], t[2], t[4]) for t in self.lostTrains.GetList() if t[0] not in self.pendingDeletions]
	
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
