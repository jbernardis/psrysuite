import wx
import os, sys 
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings

settings = Settings()

if settings.dispatch:
	fn = "dispatch"
else:
	fn = "display"

ofp = open(os.path.join(os.getcwd(), "output", "%s.out" % fn), "w")
efp = open(os.path.join(os.getcwd(), "output", "%s.err" % fn), "w")

sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "%s.log" % fn), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from dispatcher.mainframe import MainFrame 

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame(settings)
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()