import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "tester.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "tester.err"), "w")

sys.stdout = ofp
sys.stderr = efp

from tester.mainframe import MainFrame 

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()