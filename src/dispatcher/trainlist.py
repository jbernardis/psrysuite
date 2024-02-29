import wx
import logging

YardBlocks = [
	"C21", "C31", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54",
	"H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43",
	"N32", "N42",
	"P1", "P2", "P3", "P4", "P5", "P6", "P7",
	"Y50", "Y51", "Y52", "Y53", "Y81", "Y82", "Y83", "Y84" ]

profileIndex = ["stop", "slow", "medium", "fast"]

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
			
	def UpdateForSignal(self, sig):
		if sig is None:
			return
		
		if self.dlgTrainList is None:
			return 
		
		signame = sig.GetName()
		for trid, tr in self.trains.items():
			s, _, _ = tr.GetSignal()
			if s and s.GetName() == signame:
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
			
	def RemoveAllTrains(self):
		self.trains = {}
		self.RegenerateLocoMap()
		if self.dlgTrainList is not None:
			self.dlgTrainList.RemoveAllTrains()
			
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
			
	def RefreshTrain(self, trid):
		if self.dlgTrainList is not None:
			self.dlgTrainList.RefreshTrain(trid)
			
	def forSnapshot(self):
		result = {}
		for trid, tr in self.trains.items():
			if not trid.startswith("??"):
				result[trid] = tr.forSnapshot()
		
		return result
			
	def dump(self):
		for tr in self.trains:
			self.trains[tr].dump()
		

class ActiveTrainsDlg(wx.Dialog):
	def __init__(self, parent, dlgExit):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Trains", size=(1000, 500), style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)
		
		self.settings = parent.settings
		self.suppressYards =   self.settings.activesuppressyards
		self.suppressUnknown = self.settings.activesuppressunknown
		self.suppressNonATC =  self.settings.activeonlyatc
		self.suppressNonAssigned =  self.settings.activeonlyassigned
		self.suppressNonAssignedAndKnown = self.settings.activeonlyassignedorunknown
		
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
		
		self.cbAssignedOrUnknown = wx.CheckBox(self, wx.ID_ANY, "Show only Assigned or Unknown Trains")
		self.cbAssignedOrUnknown.SetValue(self.suppressNonAssignedAndKnown)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonAssignedAndKnown, self.cbAssignedOrUnknown)
		hsz.Add(self.cbAssignedOrUnknown)
		
		hsz.AddSpacer(30)
		
		self.cbUnknown = wx.CheckBox(self, wx.ID_ANY, "Show Only Known Trains")
		self.cbUnknown.SetValue(self.suppressUnknown)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressUnknown, self.cbUnknown)
		hsz.Add(self.cbUnknown)

		hsz.AddSpacer(30)
		
		self.cbAssignedOnly = wx.CheckBox(self, wx.ID_ANY, "Show only Assigned Trains")
		self.cbAssignedOnly.SetValue(self.suppressNonAssigned)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonAssigned, self.cbAssignedOnly)
		hsz.Add(self.cbAssignedOnly)

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
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.DoubleClickTrain, self.trCtl)
		
		hsz.AddSpacer(20)
		
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		self.trCtl.SetSuppressNonATC(self.suppressNonATC)
		self.trCtl.SetSuppressNonAssigned(self.suppressNonAssigned)
		self.trCtl.SetSuppressNonAssignedAndKnown(self.suppressNonAssignedAndKnown)
		
		if self.suppressNonAssignedAndKnown:
			self.cbAssignedOnly.Enable(False)
			self.cbUnknown.Enable(False)
			self.cbATCOnly.Enable(False)
		elif self.suppressNonAssigned:
			self.cbAssignedOrUnknown.Enable(False)
			self.cbUnknown.Enable(False)
			self.cbATCOnly.Enable(False)
		elif self.suppressUnknown:
			self.cbAssignedOrUnknown.Enable(False)
			self.cbAssignedOnly.Enable(False)
			self.cbATCOnly.Enable(False)
		elif self.suppressNonATC:
			self.cbAssignedOrUnknown.Enable(False)
			self.cbAssignedOnly.Enable(False)
			self.cbUnknown.Enable(False)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
	def DoubleClickTrain(self, evt):
		tr = self.trCtl.GetActiveTrain(evt.Index)
		blk = tr.FrontBlock()
		self.parent.EditTrain(tr, blk)
		
	def GetLocoInfo(self, loco):
		return self.parent.GetLocoInfo(loco)
		
	def OnSuppressYard(self, _):
		self.suppressYards = self.cbYardTracks.GetValue()
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		
	def OnSuppressNonATC(self, _):
		flag = self.cbATCOnly.GetValue()
		self.suppressNonATC = flag
		self.trCtl.SetSuppressNonATC(self.suppressNonATC)
		self.cbUnknown.Enable(not flag)
		self.cbAssignedOnly.Enable(not flag)
		self.cbAssignedOrUnknown.Enable(not flag)

	def OnSuppressNonAssignedAndKnown(self, _):
		flag = self.cbAssignedOrUnknown.GetValue()
		self.suppressNonAssignedAndKnown = flag
		self.trCtl.SetSuppressNonAssignedAndKnown(self.suppressNonAssignedAndKnown)
		self.cbUnknown.Enable(not flag)
		self.cbAssignedOnly.Enable(not flag)
		self.cbATCOnly.Enable(not flag)
		
	def OnSuppressUnknown(self, _):
		flag = self.cbUnknown.GetValue()
		self.suppressUnknown = flag
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		self.cbAssignedOrUnknown.Enable(not flag)
		self.cbAssignedOnly.Enable(not flag)
		self.cbATCOnly.Enable(not flag)
		
	def OnSuppressNonAssigned(self, _):
		flag = self.cbAssignedOnly.GetValue()
		self.suppressNonAssigned = flag
		self.trCtl.SetSuppressNonAssigned(self.suppressNonAssigned)
		self.cbAssignedOrUnknown.Enable(not flag)
		self.cbUnknown.Enable(not flag)
		self.cbATCOnly.Enable(not flag)
				
	def AddTrain(self, tr):
		self.trCtl.AddTrain(tr)
		
	def UpdateTrain(self, trid):
		self.trCtl.UpdateTrain(trid)
		
	def RefreshTrain(self, trid):
		self.trCtl.UpdateTrain(trid)
		
	def RenameTrain(self, oldName, newName):
		self.trCtl.RenameTrain(oldName, newName)
		
	def RemoveTrain(self, trid):
		self.trCtl.RemoveTrain(trid)
		
	def RemoveAllTrains(self):
		self.trCtl.RemoveAllTrains()
		
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
	def __init__(self, parent, height=160):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(1286, height), style=wx.LC_REPORT + wx.LC_VIRTUAL)
		self.parent = parent
		self.trains = {}
		self.order = []
		self.filtered = []
		
		self.suppressYards = True
		self.suppressUnknown = False
		self.suppressNonATC = False
		self.suppressNonAssigned = False		
		self.SetFont(wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.BOLD, wx.NORMAL, faceName="Arial")))
		
		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.InsertColumn(0, "Train")
		self.SetColumnWidth(0, 100)
		self.InsertColumn(1, "E/W")
		self.SetColumnWidth(1, 56)
		self.InsertColumn(2, "Loco")
		self.SetColumnWidth(2, 80)
		self.InsertColumn(3, "Engineer")
		self.SetColumnWidth(3, 100)
		self.InsertColumn(4, "ATC")
		self.SetColumnWidth(4, 50)
		self.InsertColumn(5, "AR")
		self.SetColumnWidth(5, 50)
		self.InsertColumn(6, "SB")
		self.SetColumnWidth(6, 50)
		self.InsertColumn(7, "Signal")
		self.SetColumnWidth(7, 300)
		self.InsertColumn(8, "Throttle")
		self.SetColumnWidth(8, 100)
		self.InsertColumn(9, "Blocks")
		self.SetColumnWidth(9, 400)
		self.SetItemCount(0)
		
	def ChangeSize(self, sz):
		self.SetSize(sz[0]-56, sz[1]-84)
		self.SetColumnWidth(9, sz[0]-886)
		
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
		
	def RemoveAllTrains(self):
		self.trains = {}
		self.order = []
		self.filtered = []
		self.SetItemCount(len(self.filtered))	
		
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
		
	def SetSuppressNonAssigned(self, flag):
		self.suppressNonAssigned = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)

	def SetSuppressNonAssignedAndKnown(self, flag):
		self.suppressNonAssignedAndKnown = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		self.RefreshItems(0, len(self.filtered)-1)
			
	def filterTrains(self):
		self.filtered = []
		for trid in sorted(self.order, key=self.BuildTrainKey):
			if not self.suppressed(trid):
				self.filtered.append(trid)
				
	def BuildTrainKey(self, trid):
		if trid.startswith("??"):
			return "ZZ%s" % trid
		else:
			return "AA%s" % trid

				
	def suppressed(self, trid):
		tr = self.trains[trid]
		if self.suppressYards:
			blkNms = tr.GetBlockNameList()
			allYard = True # assume all blocks are yard tracks
			for bn in blkNms:
				if bn not in YardBlocks:
					allYard = False
					break
			if allYard:
				return True
			
		if self.suppressNonAssignedAndKnown:
			if not trid.startswith("??") and tr.GetEngineer() is None:
				return True
			
		if self.suppressUnknown and trid.startswith("??"):
			return True
		
		if self.suppressNonAssigned and tr.GetEngineer() is None:
			return True
		
		
		if self.suppressNonATC and not tr.IsOnATC():
			return True
					
		return False
	
	def GetActiveTrain(self, index):
		try:
			trid = self.filtered[index]
		except:
			return None
		
		return self.trains[trid]

	def OnGetItemText(self, item, col):
		trid = self.filtered[item]
		tr = self.trains[trid]
		
		if col == 0:
			return tr.GetName()
		
		elif col == 1:
			return "E" if tr.GetEast() else "W"
		
		elif col == 2:
			return tr.GetLoco()
		
		elif col == 3:
			nm = "ATC" if tr.IsOnATC() else tr.GetEngineer()
			return "" if nm is None else nm
		
		elif col == 4:
			return u"\u2713" if tr.IsOnATC() else " "
		
		elif col == 5:
			return u"\u2713" if tr.IsOnAR() else " "
		
		elif col == 6:
			return u"\u2713" if tr.GetSBActive() else " "
		
		elif col == 7:
			sig, aspect, _ = tr.GetSignal()
			if sig is None:
				return ""
			resp = sig.GetName()
			if aspect is not None:
				resp += ":%s" % sig.GetAspectName()
			return resp 
		
		elif col == 8:
			throttle = tr.GetThrottle()
			if throttle is None:
				throttle = ""
				
			if throttle == "":
				throttle = "<>"
			
			sig, asp, fasp = tr.GetSignal()
			aspect = fasp if fasp is not None else asp
			if sig is None or aspect is None:
				throttlelimit = 0
			else:
				throttlelimit = sig.GetAspectProfileIndex(aspect)
			loco =  tr.GetLoco()
			locoinfo = self.parent.GetLocoInfo(loco)
			if locoinfo is None:
				limit = 0
			else:
				try:
					limit = locoinfo["prof"][profileIndex[throttlelimit]]
				except (IndexError, KeyError):
					limit = 0

			return "%s - %d" % (throttle, limit)
		
		elif col == 9:
			return ", ".join(tr.GetBlockNameList())

	def OnGetItemAttr(self, item):	
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
