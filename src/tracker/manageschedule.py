import wx
import os
from glob import glob
from tracker.schedule import Schedule

BTNSZ = (120, 46)
wildcardJson = "JSON file (*.json)|*.json|"	 \
				"All files (*.*)|*.*"
				
class ChooseScheduleDlg(wx.Dialog):
	def __init__(self, parent, schedules, allowentry):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.OnCancel)
		self.SetTitle("Choose/Enter schedule name")

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		if allowentry:
			style = wx.CB_DROPDOWN
		else:
			style = wx.CB_DROPDOWN | wx.CB_READONLY					
		
		cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=schedules, style=style)
		self.cbSchedule = cb
		vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
		if not allowentry and len(schedules) > 0:
			self.cbSchedule.SetSelection(0)
		else:
			self.cbSchedule.SetSelection(wx.NOT_FOUND)
		
		vszr.AddSpacer(20)
		
		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		
		bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
		
		bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
		
		btnszr.Add(bOK)
		btnszr.AddSpacer(20)
		btnszr.Add(bCancel)
		
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
				
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(20)
		hszr.Add(vszr)
		
		hszr.AddSpacer(20)
		
		self.SetSizer(hszr)
		self.Layout()
		self.Fit();
		
	def GetValue(self):
		return self.cbSchedule.GetValue()
		
	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
		

class ManageScheduleDlg(wx.Dialog):
	def __init__(self, parent, currentScheduleName, currentSchedule, alltrains, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Train Schedule"
		self.schedName = currentScheduleName
		self.settings = settings
		self.schedDir = os.path.join(os.getcwd(), "data", "schedules")
		
		self.allTrains = sorted([t for t in alltrains])		
		self.setArrays(currentSchedule)
		
		self.modified = None
		self.setModified(False)
		self.setTitle()

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableTrains, size=(120, 330))
		self.lbAll.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		
		self.lbSchedule = wx.ListBox(self, wx.ID_ANY, choices=self.scheduleTrains, size=(120, 150))
		self.lbSchedule.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbScheduleSelect, self.lbSchedule)
			
		self.lbExtra = wx.ListBox(self, wx.ID_ANY, choices=self.extraTrains, size=(120, 150))
		self.lbExtra.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbExtraSelect, self.lbExtra)
		
		self.bRightSch = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightSch.SetFont(btnFont)
		self.bRightSch.SetToolTip("Move the selected train to the right, from the all/available list to the scheduled list")
		self.Bind(wx.EVT_BUTTON, self.bRightSchPressed, self.bRightSch)
		
		self.bLeftSch = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftSch.SetFont(btnFont)
		self.bLeftSch.SetToolTip("Move the selected train to the left, from the scheduled list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftSchPressed, self.bLeftSch)
		
		self.bRightExt = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightExt.SetFont(btnFont)
		self.bRightExt.SetToolTip("Move the selected train to the right, from the all/available list to the extra list")
		self.Bind(wx.EVT_BUTTON, self.bRightExtPressed, self.bRightExt)
		
		self.bLeftExt = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftExt.SetFont(btnFont)
		self.bLeftExt.SetToolTip("Move the selected train to the left, from the extra list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftExtPressed, self.bLeftExt)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "Up")
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected train up to be earlier in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "Down")
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected train down to be later in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Available:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbAll)
		vsz.AddSpacer(10)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bRightSch)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftSch)
		vsz.AddSpacer(110)
		vsz.Add(self.bRightExt)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftExt)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Scheduled:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbSchedule)
		
		vsz.AddSpacer(5)
		st = wx.StaticText(self, wx.ID_ANY, "Extra:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbExtra)
		vsz.AddSpacer(10)
		
		hsizer.Add(vsz)
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bUp)
		vsz.AddSpacer(20)
		vsz.Add(self.bDown)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bLoad = wx.Button(self, wx.ID_ANY, "Load", size=BTNSZ)
		self.bLoad.SetFont(btnFont)
		self.bLoad.SetToolTip("LOad a new train order from a file")
		self.Bind(wx.EVT_BUTTON, self.bLoadPressed, self.bLoad)
		btnSizer.Add(self.bLoad)

		btnSizer.AddSpacer(10)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the train order to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box saving any pending changes to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		btnSizer2.Add(self.bOK)
		
		btnSizer2.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes (since last save)")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		btnSizer2.Add(self.bCancel)

		vsizer = wx.BoxSizer(wx.VERTICAL)		
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer2, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		self.SetSizer(vsizer)
		self.Layout()
		self.Fit();
		
		self.setButtons()
		
	def setTitle(self):
		title = self.titleString
		
		if self.schedName is not None:
			title += " - %s" % self.schedName
		
		if self.modified:
			title += ' *'
			
		self.SetTitle(title)
		
	def setModified(self, flag=True):
		self.modified = flag
		self.setTitle()	
		
	def onLbAllSelect(self, _):
		self.setButtons()
		
	def setButtons(self):
		ix = self.lbAll.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bRightSch.Enable(False)
			self.bRightExt.Enable(False)
		else:
			self.bRightSch.Enable(True)
			self.bRightExt.Enable(True)
			
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
			self.bLeftSch.Enable(False)
		else:
			self.bUp.Enable(ix != 0)
			self.bDown.Enable(ix != len(self.scheduleTrains)-1)
			self.bLeftSch.Enable(True)
		
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bLeftExt.Enable(False)
		else:
			self.bLeftExt.Enable(True)
		
	def onLbScheduleSelect(self, _):
		self.setButtons()
		
	def onLbExtraSelect(self, _):
		self.setButtons()
		
	def bUpPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix == 0:
			return
		
		s = self.scheduleTrains[ix]
		self.scheduleTrains[ix] = self.scheduleTrains[ix-1]
		self.scheduleTrains[ix-1] = s
		
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.lbSchedule.SetSelection(ix-1)
		
		self.setButtons()
		self.setModified()
		
	def bDownPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix >= len(self.scheduleTrains)-1:
			return
		
		s = self.scheduleTrains[ix]
		self.scheduleTrains[ix] = self.scheduleTrains[ix+1]
		self.scheduleTrains[ix+1] = s
		
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.lbSchedule.SetSelection(ix+1)
		
		self.setButtons()
		self.setModified()
		
	def bRightSchPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.scheduleTrains.append(tid)
		self.lbSchedule.SetItems(self.scheduleTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)

		self.bRightSch.Enable(False)
		self.setModified()
		ix = len(self.scheduleTrains)-1
		self.lbSchedule.EnsureVisible(ix)
		self.lbSchedule.SetSelection(ix)
		self.setButtons()


	def bLeftSchPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			return

		tid = self.scheduleTrains[ix]		
		del(self.scheduleTrains[ix])
		self.lbSchedule.SetItems(self.scheduleTrains)
		if ix >= len(self.scheduleTrains):
			ix = len(self.scheduleTrains)-1
		if ix < 0:
			self.lbSchedule.SetSelection(wx.NOT_FOUND)
		else:
			self.lbSchedule.SetSelection(ix)
		self.setAvailableTrains()
		try:
			ix = self.availableTrains.index(tid)
		except:
			ix = None
			
		self.bLeftSch.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()
	
	def bRightExtPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.extraTrains = sorted(self.extraTrains + [tid])
		ix = self.extraTrains.index(tid)
		self.lbExtra.SetItems(self.extraTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)
		self.bRightExt.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbExtra.EnsureVisible(ix)
			self.lbExtra.SetSelection(ix)
		self.setButtons()

	def bLeftExtPressed(self, _):
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			return
		
		tid = self.extraTrains[ix]		
		del(self.extraTrains[ix])
		self.lbExtra.SetItems(self.extraTrains)
		if ix >= len(self.extraTrains):
			ix = len(self.extraTrains)-1
		if ix < 0:
			self.lbExtra.SetSelection(wx.NOT_FOUND)
		else:
			self.lbExtra.SetSelection(ix)
		self.setAvailableTrains()
		ix = self.availableTrains.index(tid)
		self.bLeftExt.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()

	def setArrays(self, schedule):
		if schedule is None:
			self.schedule = None
			self.scheduleTrains = []
			self.extraTrains = []
		else:
			self.schedule = schedule
			self.scheduleTrains = schedule.getSchedule()
			self.extraTrains = schedule.getExtras()
			
		try:
			self.lbSchedule.SetItems(self.scheduleTrains)
		except:
			pass
		try:
			self.lbExtra.SetItems(self.extraTrains)
		except:
			pass
		self.setAvailableTrains()

	def setAvailableTrains(self):
		self.availableTrains = [t for t in self.allTrains if t not in self.scheduleTrains and t not in self.extraTrains]
		try:
			self.lbAll.SetItems(self.availableTrains)
		except:
			pass

	def getSchedFiles(self):
		fxp = os.path.join(self.schedDir, "*.json")
		return [os.path.splitext(os.path.split(x)[1])[0] for x in glob(fxp)]
	
	def bLoadPressed(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train schedule has been changed\nLoading a new file will lose these changes.\nPress "Yes" to proceed and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		dlg = ChooseScheduleDlg(self, self.getSchedFiles(), False)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			schedNm = dlg.GetValue()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return 
		
		
		path = os.path.join(os.getcwd(), "data", "schedules", schedNm + ".json")
		sched = Schedule()
		if not sched.load(path):
			return 
		
		self.setModified(False)

		#determine if schedule references trains than are not in alltrains
		oTrains = sched.getSchedule()
		oMissing = [t for t in oTrains if t not in self.allTrains]
		eTrains = sched.getExtras()
		eMissing = [t for t in eTrains if t not in self.allTrains]

		if len(oMissing) > 0 or len(eMissing) > 0:
			txt = "This schedule file references the following\ntrains that are not in the current roster:\n"
			if len(oMissing) > 0:
				txt += ("Scheduled: %s\n" % ",".join(oMissing))
			if len(eMissing) > 0:
				txt += ("Extra: %s\n" % ",".join(eMissing))
			txt += "\nPress\"Yes\" remove these trains from the schedule, or\n\"No\" to cancel."

			dlg = wx.MessageDialog(self, txt, "Referencing unknown trains",	wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

			oNew = [t for t in oTrains if t in self.allTrains]
			eNew = [t for t in eTrains if t in self.allTrains]

			sched.setNewSchedule(oNew)
			sched.setNewExtras(eNew)
			self.setModified()

		self.setArrays(sched)		
		self.schedName = schedNm
		self.setTitle()

	def bOKPressed(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train schedule has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_OK)
		
	def bSavePressed(self, _):		
		gotFile = False
		while not gotFile:
			slist = self.getSchedFiles()
			dlg = ChooseScheduleDlg(self, slist, True)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				schedNm = dlg.GetValue()
				
			dlg.Destroy()
			
			if rc != wx.ID_OK:
				return 
			
			if schedNm in slist:
				dlg = wx.MessageDialog(self, "Schedule file '%s' already exists.\nPress 'yes' to confirm overwrite, or\n'no' to choose a different name" % schedNm,
									'File already exists', wx.YES_NO | wx.ICON_WARNING)
				rc = dlg.ShowModal()
				dlg.Destroy()
				if rc == wx.ID_YES:
					gotFile = True
			else:
				gotFile = True
		
		self.schedName = schedNm
		sched = Schedule()
		sched.setNewSchedule(self.scheduleTrains)
		sched.setNewExtras(self.extraTrains)
		sched.save(os.path.join(os.getcwd(), "data", "schedules", self.schedName + ".json"))
		self.setTitle()
		self.setModified(False)

	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train schedule has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
		
	def getResults(self):
		results = Schedule()
		results.setNewSchedule(self.scheduleTrains)
		results.setNewExtras(self.extraTrains)
		
		return self.schedName, results
