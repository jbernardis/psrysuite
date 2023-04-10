import wx

from activetrainlistctrl import ActiveTrainListCtrl

		
class ActiveTrainListDlg(wx.Dialog):
	def __init__(self, parent, atl, cbClose):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "PSRY Train Ticker", style=wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.modified = False
		self.parent = parent
		self.atl = atl
		self.cbClose = cbClose

		vsz = wx.BoxSizer(wx.VERTICAL)
		
		vsz.AddSpacer(20)
		
		self.lcActive = ActiveTrainListCtrl(self)
		self.lcActive.setShowAttention(False)
		vsz.Add(self.lcActive)
		
		self.atl.addDisplay("dlg", self.lcActive)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def removeActiveTrain(self, tx):
		self.parent.removeActiveTrain(tx)
		
	def reassignTrain(self, tx):
		self.parent.reassignTrain(tx)
		
	def changeLoco(self, tx):
		self.parent.changeLoco(tx)
		
	def showDetails(self, tx):
		self.parent.showDetails(tx)
		
	def returnActiveTrain(self, tx):
		self.parent.returnActiveTrain(tx)
		
	def reportSelection(self, _):
		pass
	
	def reportDoubleClick(self, tx):
		self.parent.reportDoubleClick(tx)
		
	def onClose(self, _):
		self.atl.removeDisplay("dlg")
		if callable(self.cbClose):
			self.cbClose()
