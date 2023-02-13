import wx

import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import logging
logging.basicConfig(filename=os.path.join("logs", "atc.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from atc.mainframe import MainFrame 


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame(cmdFolder)
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()