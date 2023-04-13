import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open("trainedit.out", "w")
efp = open("trainedit.err", "w")

sys.stdout = ofp
sys.stderr = efp

from traineditor.mainframe import MainFrame 

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()