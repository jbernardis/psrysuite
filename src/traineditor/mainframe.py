import wx
from traineditor.settings import Settings 
from traineditor.rrserver import RRServer
from traineditor.trainsequences.trainblocksequencedlg import TrainBlockSequencesDlg
from traineditor.tracker.traintrackerdlg import TrainTrackerDlg
from traineditor.locomotives.managelocos import ManageLocosDlg


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Train/Locomotive Editor")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.settings = Settings()
		self.RRServer = RRServer()
		self.RRServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.bTrainSeq = wx.Button(self, wx.ID_ANY, "Edit Train Block Sequences", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainBlockSequences, self.bTrainSeq)
				
		self.bTrainTracker = wx.Button(self, wx.ID_ANY, "Edit Train Tracker Data", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainTrackerData, self.bTrainTracker)
				
		self.bLocos = wx.Button(self, wx.ID_ANY, "Edit Locomotive Data", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBLocos, self.bLocos)
				
		self.bLayout = wx.Button(self, wx.ID_ANY, "Generate Layout File", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBLayout, self.bLayout)
				
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		vsz.Add(self.bTrainSeq, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bTrainTracker, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bLocos, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(40)
		vsz.Add(self.bLayout, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(40)
		
		vsz.Add(self.bExit, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(70)
		hsz.Add(vsz)
		hsz.AddSpacer(70)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()
		
	def OnBTrainBlockSequences(self, _):
		dlg = TrainBlockSequencesDlg(self)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBTrainTrackerData(self, _):
		dlg = TrainTrackerDlg(self)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBLocos(self, _):
		dlg = ManageLocosDlg(self)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBLayout(self, _):
		dlg = wx.MessageDialog(self,
				"This requires that both Server, and Dispatcher are running and connected.\n\nPress 'Yes' to proceed, or\nPress 'No' to Cancel",
                "Conform", wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		rv = dlg.ShowModal()
		dlg.Destroy()
		if rv == wx.ID_YES:
			self.RRServer.SendRequest({"genlayout": {}})
		
	def OnBExit(self, _):
		self.doExit()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()
		
