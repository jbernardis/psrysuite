import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open("dispatcher.out", "w")
efp = open("dispatcher.err", "w")

sys.stdout = ofp
sys.stderr = efp

try:
	os.mkdir(os.path.join(os.getcwd(), "logs"))
except FileExistsError:
	pass

import logging
logging.basicConfig(filename=os.path.join("logs", "dispatch.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from dispatcher.mainframe import MainFrame 

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()