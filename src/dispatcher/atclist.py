import wx

class ATCListCtrl(wx.ListCtrl):
	def __init__(self, parent, pos):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(280, 80), pos=pos,
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL|wx.LC_NO_HEADER
			)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

#		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Loco")
		self.InsertColumn(2, "Spd")
		self.InsertColumn(3, "Dir")
		self.InsertColumn(4, "L")
		self.InsertColumn(5, "H")
		self.InsertColumn(6, "B")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 40)
		self.SetColumnWidth(3, 20)
		self.SetColumnWidth(4, 20)
		self.SetColumnWidth(5, 20)
		self.SetColumnWidth(6, 20)

		self.SetItemCount(0)
		self.trains = {}
		self.trainNames = []

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))
		
	def AddTrain(self, tr):
		print("ATC Add train")
		nm = tr.GetName()
		print("name = %s" % nm)
		if nm in self.trainNames:
			return 
		
		self.trainNames.append(nm)
		self.trains[nm] = tr
		ct = len(self.trainNames)
		print("train list now has %d" % ct)
		self.SetItemCount(ct)
		print("after set item count")
		self.RefreshItem(ct-1)
		print("after refresh item")
		
	def DelTrain(self, tr):
		nm = tr.GetName()
		return self.DelTrainByName(nm)
	
	def DelTrainByName(self, nm):
		if nm not in self.trainNames:
			return False
		
		del(self.trains[nm])
		self.trainNames.remove(nm)
		ct = len(self.trainNames)
		self.SetItemCount(ct)
		self.RefreshItems(0, ct-1)
		return True
	
	def UpdateTrainName(self, tr, oldName):
		try:
			idx = self.trainNames.index(oldName)
		except ValueError:
			return 
		
		self.trainNames[idx] = tr.GetName()
		del(self.trains[oldName])
		self.trains[tr.GetName()] = tr
		self.RefreshItem(idx)
	
	def ClearAll(self):
		self.SetItemCount = 0
		self.trainNames = []
		self.trains = {}
		self.RefreshItem(0)
			
	def setSelection(self, tx, dclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		if dclick:
			print("report double click %s" % str(tx))
			#self.parent.reportDoubleClick(tx)
		else:
			print("report select %s" % str(tx))
			#self.parent.reportSelection(tx)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemText(self, item, col):
		nm = self.trainNames[item]
		if col == 0:
			return nm
		elif col == 1:
			return self.trains[nm].GetLoco()
		elif col == 2:
			return "128"
		elif col == 3:
			return "F"
		elif col == 4:
			return "l"
		elif col == 5:
			return "h"
		elif col == 6:
			return "b"
		else:
			return "?"

	def OnGetItemAttr(self, item):	
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
