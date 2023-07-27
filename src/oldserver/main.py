import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "oldserver.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "oldserver.err"), "w")

sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "oldserver.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

import wx

from oldserver.mainframe import MainFrame

class App(wx.App):
	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
		self.frame = None

	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()
