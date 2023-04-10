import wx

BTNSZ = (120, 46)

class AssignLocosDlg(wx.Dialog):
	def __init__(self, parent, trains, order, extras, locos):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		self.titleString = "Assign Locos"
		self.modified = None
		self.setModified(False)
		self.extraTrains = extras
		self.timeOrder = [x for x in order] + self.extraTrains
		self.order = [x for x in order] + self.extraTrains
		
		self.parent = parent
		
		self.trains = trains
		
		self.locos = locos
		
		self.selectedTx = None
		
		self.currentLoco = {}
		for tid in self.order:
			tinfo = trains.getTrain(tid)
			self.currentLoco[tid] = tinfo["loco"]
			
		self.allLocos = locos.getLocoList()
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		self.rbSequence = wx.RadioButton(self, wx.ID_ANY, " Time Sequence ", style = wx.RB_GROUP )
		self.rbSequence.SetFont(textFontBold)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSortOrder, self.rbSequence)
		self.rbTID = wx.RadioButton(self, wx.ID_ANY, " Train ID " )
		self.rbTID.SetFont(textFontBold)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSortOrder, self.rbTID)
		self.rbOrigin = wx.RadioButton(self, wx.ID_ANY, " Origin " )
		self.rbOrigin.SetFont(textFontBold)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSortOrder, self.rbOrigin)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(self.rbSequence)
		sz.AddSpacer(20)
		sz.Add(self.rbTID)
		sz.AddSpacer(20)
		sz.Add(self.rbOrigin)
		
		vsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		self.currentLocoList = CurrentLocoList(self)
		self.currentLocoList.SetFont(textFont)
		self.currentLocoList.setData(self.trains, self.currentLoco, self.order, self.locos)
		
		vsizer.Add(self.currentLocoList, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		self.bUnassign = wx.Button(self, wx.ID_ANY, "Unassign", size=BTNSZ)
		self.bUnassign.SetFont(btnFont)
		self.bUnassign.SetToolTip("Remove the locomotive number from the currently selected train")
		self.Bind(wx.EVT_BUTTON, self.onBUnassign, self.bUnassign)
		self.bUnassign.Enable(False)
		hsizer.Add(self.bUnassign)
		
		hsizer.AddSpacer(10)
				
		self.bAssign = wx.Button(self, wx.ID_ANY, "Assign", size=BTNSZ)
		self.bAssign.SetFont(btnFont)
		self.bAssign.SetToolTip("Assign the currently selected locomotive number to the currently selected train")
		self.Bind(wx.EVT_BUTTON, self.onBAssign, self.bAssign)
		self.bAssign.Enable(False)
		hsizer.Add(self.bAssign)
		
		hsizer.AddSpacer(10)
		self.chAvail = wx.Choice(self, wx.ID_ANY, choices=[])
		self.chAvail.SetFont(textFont)
		self.Bind(wx.EVT_CHOICE, self.onChAvail, self.chAvail)
		hsizer.Add(self.chAvail, 0, wx.TOP, 10)
		
		hsizer.AddSpacer(50)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box and.  The currently loaded train roster will be updated and saved")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		hsizer.Add(self.bOK)
		hsizer.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		hsizer.Add(self.bCancel)

		vsizer.Add(hsizer);

		vsizer.AddSpacer(20)

		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.determineAvailability()
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();

	def onSortOrder(self, _):
		if self.rbSequence.GetValue():
			self.order = [x for x in self.timeOrder]
		elif self.rbTID.GetValue():
			self.order = sorted(self.timeOrder)
		elif self.rbOrigin.GetValue():
			self.order = sorted(self.timeOrder, key=self.useOrigin)
		else:
			return
		
		self.currentLocoList.setData(self.trains, self.currentLoco, self.order, self.locos)
		
	def useOrigin(self, tid):
		tr = self.trains.getTrain(tid)

		loc = tr['origin']['loc']
		if loc is None:
			loc = "  "
		trk = tr['origin']['track']
		if trk is None:
			trk = "  "

		return (loc+trk+tid).lower()

	def determineAvailability(self):
		self.locosInUse = [self.currentLoco[x] for x in self.currentLoco.keys() if self.currentLoco[x] is not None]
		self.availLocos = ["%s - %s" % (x, self.locos.getLoco(x)) for x in self.allLocos] # if x not in self.locosInUse]
		self.chAvail.SetItems(self.availLocos)
		if len(self.availLocos) == 0:
			self.chAvail.Enable(False)
		else:
			self.chAvail.Enable(True)
			self.chAvail.SetSelection(0)
		
	def reportSelection(self, tx):
		self.selectedTx = tx
		if tx is None:
			self.bUnassign.Enable(False)
			self.bAssign.Enable(False)
		else:
			self.bAssign.Enable(len(self.availLocos) > 0) 
			tid = self.order[tx]
			lId = self.currentLoco[tid]
			self.bUnassign.Enable(lId is not None)
			
	def onBUnassign(self, _):
		if self.selectedTx is None:
			return
		tid = self.order[self.selectedTx]
		self.currentLoco[tid] = None
		self.determineAvailability()
		self.currentLocoList.RefreshItem(self.selectedTx)
		self.bUnassign.Enable(False)
		self.bAssign.Enable(True)
		self.setModified()
		
	def onBAssign(self, _):
		if self.selectedTx is None:
			return
		tid = self.order[self.selectedTx]
		
		lx = self.chAvail.GetSelection()
		if lx == wx.NOT_FOUND:
			return
		
		lid = self.chAvail.GetString(lx).split(" ")[0]
		self.currentLoco[tid] = lid
		self.determineAvailability()
		self.currentLocoList.RefreshItem(self.selectedTx)
		self.bUnassign.Enable(True)
		self.bAssign.Enable(len(self.availLocos) > 0)
		self.setModified()
		
	def onChAvail(self, _):
		self.bAssign.Enable(self.selectedTx is not None)
		
	def setModified(self, flag=True):
		if self.modified == flag:
			return
		
		self.modified = flag
		title = self.titleString
		if self.modified:
			title += " *"
			
		self.SetTitle(title)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.currentLoco
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Locomotive assignments have changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
		
		
class CurrentLocoList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(660, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Origin")
		self.InsertColumn(2, "Loco")
		self.InsertColumn(3, "Description")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 360)

		self.SetItemCount(0)
		self.selected = None

		self.attr1 = wx.ItemAttr()
		self.attr2 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.attr2.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		
	def setData(self, trains, currentLocos, order, locos):
		self.trains = trains
		self.currentLocos = currentLocos
		self.order = order
		self.locos = locos
		self.SetItemCount(0)
		self.SetItemCount(len(self.order))
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None
		
		return self.order[self.selected]
			
	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx)
		
				
	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.order):
			return None
		
		tid = self.order[item]
		lId = self.currentLocos[tid]
		if col == 0:
			return tid 

		elif col == 1:
			tinfo = self.trains.getTrain(tid)
			if tinfo["origin"]["loc"] is None:
				rv = ""
			elif tinfo["origin"]["track"] is None:
				rv = tinfo["origin"]["loc"]
			else:
				rv = "%s / %s" % (tinfo["origin"]["loc"], tinfo["origin"]["track"])
			return rv

		elif col == 2:
			if lId is None:
				return "<none>"
			else:
				return self.currentLocos[tid]

		elif col == 3:
			if lId is None:
				return ""
			else:
				d = self.locos.getLoco(lId)
				if d is None:
					return ""
				else:
					return d
				

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
