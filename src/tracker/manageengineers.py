import os
import wx

wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
				"All files (*.*)|*.*"

BTNSZ = (120, 46)

class ManageEngineersDlg(wx.Dialog):
	def __init__(self, parent, allEngs, actEngs, busyEngs, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Engineers")
		self.titleString = "Manage Engineers"
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.reloadNeeded = False
	
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		self.busyEngs = busyEngs
		
		self.parent = parent
		self.settings = settings
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, wx.ID_ANY, "All Engineers")
		st1.SetFont(textFontBold)
		st2 = wx.StaticText(self, wx.ID_ANY, "Active Engineers")
		st2.SetFont(textFontBold)
		sz.Add(st1)
		sz.AddSpacer(210)
		sz.Add(st2)
		
		vsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.allEngs = [x for x in allEngs]
		self.activeEngs = [x for x in actEngs]
		self.updateArrays()
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableEngs, size=(160, 200))
		self.lbAll.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bRightPressed, self.lbAll)

		self.stCountAll = wx.StaticText(self, wx.ID_ANY, "(0 Available/0 Total)")
		self.stCountAll.SetFont(textFont)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(self.lbAll)
		vsz.AddSpacer(5)
		vsz.Add(self.stCountAll)
		
		sz.Add(vsz)
		
		sz.AddSpacer(40)
		
		btnsizer = wx.BoxSizer(wx.VERTICAL)
		btnsizer.AddSpacer(20)
		
		self.bRight = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRight.SetFont(btnFont)
		self.bRight.SetToolTip("Move the selected engineer to the right, from the all/available list to the active list")
		btnsizer.Add(self.bRight)
		
		btnsizer.AddSpacer(10)
		
		self.bLeft = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeft.SetFont(btnFont)
		self.bLeft.SetToolTip("Move the selected engineer to the left, from the active list to the all/available list")
		btnsizer.Add(self.bLeft)
		
		btnsizer.AddSpacer(30)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "up")
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected engineer up in the active list")
		btnsizer.Add(self.bUp)
		
		btnsizer.AddSpacer(10)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "down")
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected engineer down in the active list")
		btnsizer.Add(self.bDown)
		
		btnsizer.AddSpacer(20)
		self.Bind(wx.EVT_BUTTON, self.bRightPressed, self.bRight)
		self.Bind(wx.EVT_BUTTON, self.bLeftPressed, self.bLeft)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		sz.Add(btnsizer)
		
		sz.AddSpacer(40)
		
		self.lbActive = wx.ListBox(self, wx.ID_ANY, choices=self.activeEngs, size=(160, 200))
		self.lbActive.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbActiveSelect, self.lbActive)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bLeftPressed, self.lbActive)

		self.stCountActive = wx.StaticText(self, wx.ID_ANY, "(0 Active)")
		self.stCountActive.SetFont(textFont)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(self.lbActive)
		vsz.AddSpacer(5)
		vsz.Add(self.stCountActive)
				
		sz.Add(vsz)
		
		vsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		self.bAddEng = wx.Button(self, wx.ID_ANY, "Add\nEngineer", size=BTNSZ)
		self.bAddEng.SetFont(btnFont)
		self.bAddEng.SetToolTip("Add a new engineer to the all/available list")
		sz.Add(self.bAddEng)
		self.Bind(wx.EVT_BUTTON, self.bAddEngPressed, self.bAddEng)
		
		sz.AddSpacer(20)
		self.bDelEng = wx.Button(self, wx.ID_ANY, "Delete\nEngineer", size=BTNSZ)
		self.bDelEng.SetFont(btnFont)
		self.bDelEng.SetToolTip("Delete the selected engineer from the all/available list")
		sz.Add(self.bDelEng)
		self.Bind(wx.EVT_BUTTON, self.bDelEngPressed, self.bDelEng)
		self.bDelEng.Enable(False)

		sz.AddSpacer(20)
		
		vsizer.Add(sz, 1, wx.ALIGN_CENTER_HORIZONTAL)		
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the full list of ALL engineers, including active engineers, to the current file")
		sz.Add(self.bSave)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		
		sz.AddSpacer(20)
		
		vsizer.Add(sz, 1, wx.ALIGN_CENTER_HORIZONTAL)		
		vsizer.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		sz.AddSpacer(20)
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box and replace the loaded engineer list with the above active list")
		sz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		sz.AddSpacer(20)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)
		
		vsizer.Add(sz, 1, wx.ALIGN_CENTER_HORIZONTAL)		
		vsizer.AddSpacer(20)
		
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.bRight.Enable(False)
		self.bLeft.Enable(False)
		self.bUp.Enable(False)
		self.bDown.Enable(False)
		
		self.setModified(False)
		self.activeModified = False

		self.setCounts()
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();

		self.setTitle()

	def setTitle(self):
		title = self.titleString
		if self.modified:
			title += " *"

		self.SetTitle(title)
		
	def setModified(self, flag=True):
		self.modified = flag
		self.setTitle()

	def updateArrays(self):
		self.availableEngs = sorted([x for x in self.allEngs if x not in self.activeEngs])
		
	def onLbAllSelect(self, _):
		sx = self.lbAll.GetSelection()
		self.setAllSelection(sx)
		
	def setAllSelection(self, sx):
		self.lbAll.SetSelection(sx)
		self.bRight.Enable(sx != wx.NOT_FOUND)
		self.bDelEng.Enable(sx != wx.NOT_FOUND)
		
	def onLbActiveSelect(self, _):
		sx = self.lbActive.GetSelection()
		self.setActiveSelection(sx)
		
	def setActiveSelection(self, sx):
		self.lbActive.SetSelection(sx)
		if sx == wx.NOT_FOUND:
			self.bLeft.Enable(False)
			self.bUp.Enable(False)
			self.bDown.Enable(False)
		else:
			self.bLeft.Enable(True)
			if len(self.activeEngs) == 1:
				self.bDown.Enable(False)
				self.bUp.Enable(False)
			elif sx == 0:
				self.bDown.Enable(True)
				self.bUp.Enable(False)
			elif sx == len(self.activeEngs)-1:
				self.bDown.Enable(False)
				self.bUp.Enable(True)
			else:
				self.bDown.Enable(True)
				self.bUp.Enable(True)

		
	def bRightPressed(self, _):
		sx = self.lbAll.GetSelection()
		if sx == wx.NOT_FOUND:
			return
		
		eng = self.lbAll.GetString(sx)
		self.availableEngs.remove(eng)
		self.activeEngs.append(eng)
		
		self.lbAll.SetItems(self.availableEngs)
		self.lbActive.SetItems(self.activeEngs)
		self.setCounts()
		
		self.setActiveSelection(len(self.activeEngs)-1)
		if sx >= len(self.availableEngs):
			sx = len(self.availableEngs)-1
			if sx < 0:
				sx = wx.NOT_FOUND
		self.setAllSelection(sx)
		self.activeModified = True
		
	def bLeftPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND:
			return
		
		eng = self.lbActive.GetString(sx)
		self.activeEngs.remove(eng)
		newAvl = self.availableEngs + [eng]
		self.availableEngs = sorted(newAvl)
		
		self.lbAll.SetItems(self.availableEngs)
		self.lbActive.SetItems(self.activeEngs)
		self.setCounts()
		
		self.setAllSelection(len(self.availableEngs)-1)
		if sx >= len(self.activeEngs):
			sx = len(self.activeEngs)-1
			if sx < 0:
				sx = wx.NOT_FOUND
		self.setActiveSelection(sx)
		self.activeModified = True
		
	def bUpPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND or sx == 0:
			return
		
		e1 = self.activeEngs[sx-1]
		e2 = self.activeEngs[sx]

		if sx == 1:
			nl = [e2, e1] + self.activeEngs[2:]
		elif sx == len(self.activeEngs)-1:
			nl = self.activeEngs[:-2] + [e2, e1]
		else:
			nl = self.activeEngs[:sx-1] + [e2, e1] +  self.activeEngs[sx+1:]
			
		self.activeEngs = nl
		self.lbActive.SetItems(self.activeEngs)
		self.lbActive.SetSelection(sx-1)
		
		self.setActiveSelection(sx-1)
		self.activeModified = True
		
	def bDownPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND or sx == len(self.activeEngs)-1:
			return
		
		e1 = self.activeEngs[sx]
		e2 = self.activeEngs[sx+1]
		
		if sx == 0:
			nl = [e2, e1] + self.activeEngs[2:]
		elif sx == len(self.activeEngs)-2:
			nl = self.activeEngs[:-2] + [e2, e1]
		else:
			nl = self.activeEngs[:sx] + [e2, e1] +  self.activeEngs[sx+2:]
			
		self.activeEngs = nl
		self.lbActive.SetItems(self.activeEngs)
		self.lbActive.SetSelection(sx+1)
		
		self.setActiveSelection(sx+1)
		self.activeModified = True
		
	def bAddEngPressed(self, _):
		dlg = wx.TextEntryDialog(
				self, 'Enter Name of new engineer',
				'Add Engineer', '')

		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			eng = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if eng in self.allEngs or eng in self.busyEngs:
			dlg = wx.MessageDialog(self, "Engineer \"%s\" is already in the list" % eng, 
					"Duplicate Name", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		newAvl = self.availableEngs + [eng]
		self.availableEngs = sorted(newAvl)
		self.allEngs.append(eng)
		
		self.lbAll.SetItems(self.availableEngs)
		ix = self.availableEngs.index(eng)
		self.setCounts()

		self.lbAll.SetSelection(ix)		
		self.setAllSelection(ix)
		self.setModified()
		
	def bDelEngPressed(self, _):
		sx = self.lbAll.GetSelection()
		if sx == wx.NOT_FOUND or sx == len(self.activeEngs)-1:
			return
		
		eng = self.lbAll.GetString(sx)
		self.lbAll.Delete(sx)
		self.allEngs.remove(eng)
		self.availableEngs.remove(eng)
		self.setCounts()
		sx = self.lbAll.GetSelection()
		self.setAllSelection(sx)
		self.setModified()
		
	def setCounts(self):
		cAll = len(self.allEngs)
		cAvail = len(self.availableEngs)
		cActive = len(self.activeEngs)
		self.stCountAll.SetLabel("( %d Available/%d total)" % (cAvail, cAll))
		self.stCountActive.SetLabel("(%d Active)" % cActive)

	def bSavePressed(self, _):
		print("saving")
		fn = os.path.join(os.getcwd(), "data", "engineers", "engineers.txt")
		with open(fn, "w") as ofp:
			for ln in self.allEngs:
				ofp.write("%s\n" % ln)
		
		self.setModified(False)
		self.reloadNeeded = True
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.activeEngs
	
	def IsReloadNeeded(self):
		return self.reloadNeeded
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Engineer list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
