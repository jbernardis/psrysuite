import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

#from settings import Settings

#settings = Settings()

from monitor.mainframe import MainFrame

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()