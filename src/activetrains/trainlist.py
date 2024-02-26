import wx
import logging
from dispatcher.trainlist import TrainListCtrl

YardBlocks = [
	"C21", "C31", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54",
	"H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43",
	"N32", "N42",
	"P1", "P2", "P3", "P4", "P5", "P6", "P7",
	"Y50", "Y51", "Y52", "Y53", "Y81", "Y82", "Y83", "Y84" ]

class ActiveTrainList:
	def __init__(self):
		self.trains = {}
		self.panelTrainList = None
		self.locoMap = {}
		
	def RegenerateLocoMap(self):
		self.locoMap = {tr.GetLoco(): tr for tr in self.trains.values() if tr.GetLoco() != "??"}
		
	def AddTrain(self, tr):
		self.trains[tr.GetName()] = tr
		self.RegenerateLocoMap()
		if self.panelTrainList is not None:
			self.panelTrainList.AddTrain(tr)
			
	def UpdateTrain(self, trid):
		if self.panelTrainList is not None:
			self.panelTrainList.UpdateTrain(trid)
			
	def RenameTrain(self, oldName, newName):
		self.trains[newName] = self.trains[oldName]
		del(self.trains[oldName])
		self.RegenerateLocoMap()
		if self.panelTrainList is not None:
			self.panelTrainList.RenameTrain(oldName, newName)
			
	def RemoveTrain(self, trid):
		del(self.trains[trid])
		self.RegenerateLocoMap()
		if self.panelTrainList is not None:
			self.panelTrainList.RemoveTrain(trid)
			
	def RemoveAllTrains(self):
		self.trains = {}
		self.RegenerateLocoMap()
		if self.panelTrainList is not None:
			self.panelTrainList.RemoveAllTrains()
			
	def SetLoco(self, tr, loco):
		tr.SetLoco(loco)
		self.RegenerateLocoMap()
			
	def FindTrainByLoco(self, loco):
		try:
			return self.locoMap[loco]
		except:
			return None
			
	def CreateTrainListPanel(self, parent, lines):
		if self.panelTrainList is None:
			self.panelTrainList = ActiveTrainsPanel(parent, lines)
			for tr in self.trains.values():
				self.panelTrainList.AddTrain(tr)
		self.EnableTrainListPanel(False)
		return self.panelTrainList
				

	
	def EnableTrainListPanel(self, flag=True):
		if self.panelTrainList is not None:
			self.panelTrainList.Enable(flag)
			
	def RefreshTrain(self, trid):
		if self.panelTrainList is not None:
			self.panelTrainList.RefreshTrain(trid)
		

class ActiveTrainsPanel(wx.Panel):
	def __init__(self, parent, lines):
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.parent = parent
		
		self.settings = parent.settings
		self.suppressYards =   self.settings.activesuppressyards
		self.suppressUnknown = self.settings.activesuppressunknown
		self.suppressNonATC =  self.settings.activeonlyatc
		self.suppressNonAssigned =  self.settings.activeonlyassigned
		self.suppressNonAssignedAndKnown = self.settings.activeonlyassignedorunknown
		
		self.resized = False

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

		self.trCtl = TrainListCtrl(self, lines*32)
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
		
	def DoubleClickTrain(self, evt):
		tr = self.trCtl.GetActiveTrain(evt.Index)
		self.parent.TrainSelected(tr)
		
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
		self.cbAssignedOrUnknown.Enable(not flag)
		self.cbAssignedOnly.Enable(not flag)

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
