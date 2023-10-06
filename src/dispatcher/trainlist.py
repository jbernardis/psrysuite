import wx
import logging

YardBlocks = [
	"C21", "C31", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54",
	"H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43",
	"N32", "N42",
	"P1", "P2", "P3", "P4", "P5", "P6", "P7",
	"Y50", "Y51", "Y52", "Y53", "Y81", "Y82", "Y83", "Y84" ]

class ActiveTrainList:
	def __init__(self):
		self.trains = {}
		self.dlgTrainList = None
		self.locoMap = {}
		
	def RegenerateLocoMap(self):
		self.locoMap = {tr.GetLoco(): tr for tr in self.trains.values() if tr.GetLoco() != "??"}
		
	def AddTrain(self, tr):
		self.trains[tr.GetName()] = tr
		self.RegenerateLocoMap()
		if self.dlgTrainList is not None:
			self.dlgTrainList.AddTrain(tr)
			
	def UpdateTrain(self, trid):
		if self.dlgTrainList is not None:
			self.dlgTrainList.UpdateTrain(trid)
			
	def RenameTrain(self, oldName, newName):
		self.trains[newName] = self.trains[oldName]
		del(self.trains[oldName])
		self.RegenerateLocoMap()
		if self.dlgTrainList is not None:
			self.dlgTrainList.RenameTrain(oldName, newName)
			
	def RemoveTrain(self, trid):
		del(self.trains[trid])
		self.RegenerateLocoMap()
		if self.dlgTrainList is not None:
			self.dlgTrainList.RemoveTrain(trid)
			
	def SetLoco(self, tr, loco):
		tr.SetLoco(loco)
		self.RegenerateLocoMap()
			
	def FindTrainByLoco(self, loco):
		try:
			return self.locoMap[loco]
		except:
			return None
			
	def ShowTrainList(self, parent):
		if self.dlgTrainList is None:
			self.dlgTrainList = ActiveTrainsDlg(parent, self.HideTrainList)
			for tr in self.trains.values():
				self.dlgTrainList.AddTrain(tr)
				
			self.dlgTrainList.Show()
	
	def HideTrainList(self):
		if self.dlgTrainList is not None:
			self.dlgTrainList.Destroy()
			self.dlgTrainList = None
			
	def forSnapshot(self):
		result = {}
		for trid, tr in self.trains.items():
			result[trid] = tr.forSnapshot()
		
		return result
			
	def dump(self):
		for tr in self.trains:
			self.trains[tr].dump()
		

class ActiveTrainsDlg(wx.Dialog):
	def __init__(self, parent, dlgExit):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Trains", size=(1000, 500), style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)
		
		self.settings = parent.settings
		self.suppressYards =   self.settings.activesuppressyards
		self.suppressUnknown = self.settings.activesuppressunknown
		self.suppressNonATC =  self.settings.activeonlyatc

		self.resized = False

		self.dlgExit = dlgExit

		vsz = wx.BoxSizer(wx.VERTICAL)	   
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		hsz.AddSpacer(30)
		
		self.cbYardTracks = wx.CheckBox(self, wx.ID_ANY, "Suppress Yard Tracks")
		self.cbYardTracks.SetValue(self.suppressYards)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressYard, self.cbYardTracks)
		hsz.Add(self.cbYardTracks)
		
		hsz.AddSpacer(30)
		
		self.cbUnknown = wx.CheckBox(self, wx.ID_ANY, "Suppress Unknown Trains")
		self.cbUnknown.SetValue(self.suppressUnknown)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressUnknown, self.cbUnknown)
		hsz.Add(self.cbUnknown)

		hsz.AddSpacer(30)
		
		self.cbATCOnly = wx.CheckBox(self, wx.ID_ANY, "Show only ATC Trains")
		self.cbATCOnly.SetValue(self.suppressNonATC)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonATC, self.cbATCOnly)
		hsz.Add(self.cbATCOnly)

		hsz.AddSpacer(30)
		
		vsz.Add(hsz)
				
		vsz.AddSpacer(10)
	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.trCtl = TrainListCtrl(self)
		hsz.Add(self.trCtl)
		
		hsz.AddSpacer(20)
		
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		self.trCtl.SetSuppressNonATC(self.suppressNonATC)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
	def OnSuppressYard(self, _):
		self.suppressYards = self.cbYardTracks.GetValue()
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		
	def OnSuppressUnknown(self, _):
		self.suppressUnknown = self.cbUnknown.GetValue()
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		
	def OnSuppressNonATC(self, _):
		self.suppressNonATC = self.cbATCOnly.GetValue()
		self.trCtl.SetSuppressNonATC(self.suppressNonATC)
		
	def AddTrain(self, tr):
		self.trCtl.AddTrain(tr)
		
	def UpdateTrain(self, trid):
		self.trCtl.UpdateTrain(trid)
		
	def RenameTrain(self, oldName, newName):
		self.trCtl.RenameTrain(oldName, newName)
		
	def RemoveTrain(self, trid):
		self.trCtl.RemoveTrain(trid)
		
	def OnResize(self, evt):
		self.resized = True
		
	def OnIdle(self, evt):
		if not self.resized:
			return 
		
		self.resized = False
		self.trCtl.ChangeSize(self.GetSize())

	def OnClose(self, _):
		self.dlgExit()
		
class TrainListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(1010, 160), style=wx.LC_REPORT + wx.LC_VIRTUAL)
		self.parent = parent
		self.trains = {}
		self.order = []
		self.filtered = []
		
		self.suppressYards = True
		self.suppressUnknown = False
		self.suppressNonATC = False
		
		self.SetFont(wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.BOLD, wx.NORMAL, faceName="Arial")))

		self.InsertColumn(0, "Train")
		self.SetColumnWidth(0, 80)
		self.InsertColumn(1, "Loco")
		self.SetColumnWidth(1, 80)
		self.InsertColumn(2, "Engineer")
		self.SetColumnWidth(2, 100)
		self.InsertColumn(3, "ATC")
		self.SetColumnWidth(3, 50)
		self.InsertColumn(4, "AR")
		self.SetColumnWidth(4, 50)
		self.InsertColumn(5, "SB")
		self.SetColumnWidth(5, 50)
		self.InsertColumn(6, "Signal")
		self.SetColumnWidth(6, 100)
		self.InsertColumn(7, "Throttle")
		self.SetColumnWidth(7, 100)
		self.InsertColumn(8, "Blocks")
		self.SetColumnWidth(8, 400)
		self.SetItemCount(0)
		
	def ChangeSize(self, sz):
		self.SetSize(sz[0]-56, sz[1]-84)
		self.SetColumnWidth(8, sz[0]-566)
		
	def AddTrain(self, tr):
		nm = tr.GetName()
		if nm in self.order:
			logging.warning("Attempt to add a duplicate train: %s" % nm)
			return 
		
		self.trains[nm] = tr
		self.order.append(nm)

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def RenameTrain(self, oldName, newName):
		try:
			tx = self.order.index(oldName)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % oldName)
			return 
		
		self.order[tx] = newName
		
		self.trains[newName] = self.trains[oldName]
		del(self.trains[oldName])
		
		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def UpdateTrain(self, trid):
		try:
			tx = self.order.index(trid)
		except ValueError:
			logging.warning("Attempt to update a non-existent train: %s" % trid)
			return 
		
		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def RemoveTrain(self, trid):
		try:
			tx = self.order.index(trid)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % trid)
			return 
		del(self.order[tx])
		del(self.trains[trid])

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressYardTracks(self, flag):
		self.suppressYards = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressUnknown(self, flag):
		self.suppressUnknown = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressNonATC(self, flag):
		self.suppressNonATC = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
		
	def filterTrains(self):
		self.filtered = []
		for trid in sorted(self.order):
			if not self.suppressed(trid):
				self.filtered.append(trid)
				
	def suppressed(self, trid):
		if self.suppressUnknown and trid.startswith("??"):
			return True
		
		tr = self.trains[trid]
		if self.suppressNonATC and not tr.IsOnATC():
			return True

		if not self.suppressYards:
			return False
		
		blkNms = tr.GetBlockNameList()
		for bn in blkNms:
			if bn not in YardBlocks:
				return False
					
		return True

	def OnGetItemText(self, item, col):
		trid = self.filtered[item]
		tr = self.trains[trid]
		
		if col == 0:
			return tr.GetName()
		
		elif col == 1:
			return tr.GetLoco()
		
		elif col == 2:
			nm = tr.GetEngineer()
			return "" if nm is None else nm
		
		elif col == 3:
			return u"\u2713" if tr.IsOnATC() else " "
		
		elif col == 4:
			return u"\u2713" if tr.IsOnAR() else " "
		
		elif col == 5:
			return u"\u2713" if tr.GetSBActive() else " "
		
		elif col == 6:
			sig, aspect = tr.GetSignal()
			if sig is None:
				return ""
			resp = sig.GetName()
			if aspect is not None:
				resp += ":%d" % aspect
			return resp 
		
		elif col == 7:
			throttle = tr.GetThrottle()
			return throttle
		
		elif col == 8:
			return ", ".join(tr.GetBlockNameList())
