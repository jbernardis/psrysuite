import wx
import wx.lib.newevent
from wx.lib.gizmos.ledctrl import LEDNumberCtrl

import os
import sys
import json
import logging
import time
from subprocess import Popen
from glob import glob

from dispatcher.constants import BLOCK

from dispatcher.bitmaps import BitMaps
from dispatcher.district import Districts
from dispatcher.trackdiagram import TrackDiagram
from dispatcher.tile import loadTiles
from dispatcher.train import Train
from dispatcher.trainlist import ActiveTrainList

from dispatcher.breaker import BreakerDisplay, BreakerName
from dispatcher.toaster import Toaster
from dispatcher.listdlg import ListDlg
from dispatcher.delayedrequest import DelayedRequests

from dispatcher.districts.hyde import Hyde
from dispatcher.districts.yard import Yard
from dispatcher.districts.latham import Latham
from dispatcher.districts.dell import Dell
from dispatcher.districts.shore import Shore
from dispatcher.districts.krulish import Krulish
from dispatcher.districts.nassau import Nassau
from dispatcher.districts.bank import Bank
from dispatcher.districts.cliveden import Cliveden
from dispatcher.districts.cliff import Cliff
from dispatcher.districts.port import Port

from dispatcher.constants import HyYdPt, LaKr, NaCl, screensList, EMPTY, OCCUPIED, NORMAL, REVERSE, OVERSWITCH
from dispatcher.listener import Listener
from dispatcher.rrserver import RRServer

from dispatcher.edittraindlg import EditTrainDlg

MENU_ATC_REMOVE  = 900
MENU_ATC_STOP    = 901
MENU_ATC_ADD     = 902
MENU_AR_ADD      = 903
MENU_AR_REMOVE   = 904
MENU_ATC_REM_REQ = 905
MENU_ATC_ADD_REQ = 906

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 

allowedCommands = [ "settrain", "renametrain", "identify", "refresh", "atcrequest" ]

wildcardTrain = "train files (*.trn)|*.trn|"	 \
			"All files (*.*)|*.*"
wildcardLoco = "locomotive files (*.loco)|*.loco|"	 \
			"All files (*.*)|*.*"

class Node:
	def __init__(self, screen, bitmapName, offset):
		self.screen = screen
		self.bitmap = bitmapName
		self.offset = offset

BTNDIM = (80, 23)

class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.events = None
		self.advice = None
		self.listener = None
		self.sessionid = None
		self.subscribed = False
		self.ATCEnabled = False
		self.AREnabled = False
		self.pidATC	= None
		self.procATC = None
		self.pidAdvisor = None
		self.OSSLocks = True
		
		self.shift = False
		self.shiftXOffset = 0
		self.shiftYOffset = 0
		
		self.ToD = True
		self.timeValue = self.GetToD()
		self.clockRunning = False # only applies to non-TOD clock
		
		self.eventsList = []
		self.adviceList = []
		self.dlgEvents = None
		self.dlgAdvice = None
		
		self.locoList = []
		self.trainList = []
		self.activeTrains = ActiveTrainList()
			
		self.settings = settings
			
		logging.info("%s process starting" % "dispatcher" if self.settings.dispatch else "display")

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "dispatch.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.logCount = 6
		
		self.turnoutMap = {}
		self.buttonMap = {}
		self.signalMap = {}
		self.handswitchMap = {}
		
		self.delayedRequests = DelayedRequests()

		self.title = "PSRY Dispatcher" if self.settings.dispatch else "PSRY Monitor"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.bitmaps = BitMaps(os.path.join(os.getcwd(), "data", "bitmaps"))
		singlePage = self.settings.pages == 1
		self.bmpw, self.bmph = self.bitmaps.diagrams.HydeYardPort.GetSize()
		self.diagrams = {
			HyYdPt: Node(HyYdPt, self.bitmaps.diagrams.HydeYardPort, 0),
			LaKr:   Node(LaKr,   self.bitmaps.diagrams.LathamKrulish, self.bmpw if singlePage else 0),
			NaCl:   Node(NaCl,   self.bitmaps.diagrams.NassauCliff, self.bmpw*2 if singlePage else 0)
		}
		topSpace = 120
		
		ht = None # diagram height.  None => use bitmap size.  use a number < 800 to trim bottom off of diagram bitmaps
		self.diagramWidth = 2560

		if self.settings.pages == 1:  # set up a single ultra-wide display accross 3 monitors
			dp = TrackDiagram(self, [self.diagrams[sn] for sn in screensList], ht)
			dp.SetPosition((16, 120))
			_, diagramh = dp.GetSize()
			self.panels = {self.diagrams[sn].screen : dp for sn in screensList}  # all 3 screens just point to the same diagram
			totalw = self.diagramWidth*3
			self.centerOffset = self.diagramWidth

		else:  # set up three separate screens for a single monitor
			self.panels = {}
			diagramh = 0
			for d in [self.diagrams[sn] for sn in screensList]:
				dp = TrackDiagram(self, [d], ht)
				_, diagramh = dp.GetSize()
				dp.Hide()
				dp.SetPosition((8, 120))
				self.panels[d.screen] = dp

			# add buttons to switch from screen to screen
			voffset = topSpace+diagramh+20
			b = wx.Button(self, wx.ID_ANY, "Hyde/Yard/Port", pos=(500, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(HyYdPt), b)
			self.bScreenHyYdPt = b
			b = wx.Button(self, wx.ID_ANY, "Latham/Dell/Shore/Krulish", pos=(1145, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(LaKr), b)
			self.bScreenLaKr = b
			b = wx.Button(self, wx.ID_ANY, "Nassau/Bank/Cliff",   pos=(1790, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(NaCl), b)
			self.bScreenNaCl = b
			totalw = self.diagramWidth+20
			self.centerOffset = 0

		self.ToasterSetup()

		if self.settings.showcameras:
			self.DrawCameras()

		voffset = topSpace+diagramh+10
		self.widgetMap = {HyYdPt: [], LaKr: [], NaCl: []}
		self.DefineWidgets(voffset)

		if self.settings.pages == 3:
			self.currentScreen = None
			self.SwapToScreen(LaKr)
		else:
			self.PlaceWidgets()

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect", pos=(self.centerOffset+50, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", pos=(self.centerOffset+50, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		self.bThrottle = wx.Button(self, wx.ID_ANY, "Throttle", pos=(self.centerOffset+150, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnThrottle, self.bThrottle)

		self.bEditTrains = wx.Button(self, wx.ID_ANY, "Edit Trains", pos=(self.centerOffset+150, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnEditTrains, self.bEditTrains)

		self.bLoadTrains = wx.Button(self, wx.ID_ANY, "Load Train IDs", pos=(self.centerOffset+250, 15), size=BTNDIM)
		self.bLoadTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBLoadTrains, self.bLoadTrains)
		
		self.bSaveTrains = wx.Button(self, wx.ID_ANY, "Save Train IDs", pos=(self.centerOffset+250, 45), size=BTNDIM)
		self.bSaveTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBSaveTrains, self.bSaveTrains)
		
		self.bClearTrains = wx.Button(self, wx.ID_ANY, "Clear Train IDs", pos=(self.centerOffset+250, 75), size=BTNDIM)
		self.bClearTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBClearTrains, self.bClearTrains)
		
		self.bLoadLocos = wx.Button(self, wx.ID_ANY, "Load Loco #s", pos=(self.centerOffset+350, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBLoadLocos, self.bLoadLocos)
		self.bLoadLocos.Enable(False)
		
		self.bSaveLocos = wx.Button(self, wx.ID_ANY, "Save Loco #s", pos=(self.centerOffset+350, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBSaveLocos, self.bSaveLocos)
		self.bSaveLocos.Enable(False)
		
		self.bActiveTrains = wx.Button(self, wx.ID_ANY, "Active Trains", pos=(self.centerOffset+350, 75), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBActiveTrains, self.bActiveTrains)
		
		if not self.IsDispatcher():
			self.bLoadTrains.Hide()
			self.bLoadLocos.Hide()
			self.bSaveTrains.Hide()
			self.bSaveLocos.Hide()
			self.bClearTrains.Hide()
			self.bEditTrains.Hide()

		self.scrn = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), pos=(self.centerOffset+2200, 25), style=wx.TE_READONLY)
		self.xpos = wx.TextCtrl(self, wx.ID_ANY, "", size=(40, -1), pos=(self.centerOffset+2300, 25), style=wx.TE_READONLY)
		self.ypos = wx.TextCtrl(self, wx.ID_ANY, "", size=(40, -1), pos=(self.centerOffset+2360, 25), style=wx.TE_READONLY)
		
		self.bResetScreen = wx.Button(self, wx.ID_ANY, "Reset Screen", pos=(self.centerOffset+2200, 75), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnResetScreen, self.bResetScreen)

		self.breakerDisplay = BreakerDisplay(self, pos=(int(totalw/2-400/2), 30), size=(400, 40))
	
		self.cbOSSLocks = wx.CheckBox(self, -1, "OSS Locks", (int(totalw/2-100/2), 80))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBOSSLocks, self.cbOSSLocks)
		self.cbOSSLocks.SetValue(self.OSSLocks)

		self.timeDisplay = LEDNumberCtrl(self, wx.ID_ANY, pos=(self.centerOffset+480, 10), size=(150, 50))

		if self.IsDispatcher():
			self.DisplayTimeValue()
			self.cbToD = wx.CheckBox(self, wx.ID_ANY, "Time of Day", pos=(self.centerOffset+515, 65))
			self.cbToD.SetValue(True)
			self.Bind(wx.EVT_CHECKBOX, self.OnCBToD, self.cbToD)
			
			self.bStartClock = wx.Button(self, wx.ID_ANY, "Start", pos=(self.centerOffset+485, 90), size=(60, 23))
			self.Bind(wx.EVT_BUTTON, self.OnBStartClock, self.bStartClock)
			self.bStartClock.Enable(False)
			
			self.bResetClock = wx.Button(self, wx.ID_ANY, "Reset", pos=(self.centerOffset+565, 90), size=(60, 23))
			self.Bind(wx.EVT_BUTTON, self.OnBResetClock, self.bResetClock)
			self.bResetClock.Enable(False)

			self.cbAutoRouter = wx.CheckBox(self, wx.ID_ANY, "Auto-Router", pos=(self.centerOffset+670, 25))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBAutoRouter, self.cbAutoRouter)
			self.cbAutoRouter.Enable(False)
			self.cbATC = wx.CheckBox(self, wx.ID_ANY, "Automatic Train Control", pos=(self.centerOffset+670, 50))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBATC, self.cbATC)
			self.cbATC.Enable(False)
			self.cbAdvisor = wx.CheckBox(self, wx.ID_ANY, "Advisor", pos=(self.centerOffset+670, 75))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBAdvisor, self.cbAdvisor)
			self.cbAdvisor.Enable(False)
			
			self.bEvents = wx.Button(self, wx.ID_ANY, "Events Log", pos=(self.centerOffset+840, 25), size=BTNDIM)
			self.Bind(wx.EVT_BUTTON, self.OnBEventsLog, self.bEvents)
			self.bAdvice = wx.Button(self, wx.ID_ANY, "Advice Log", pos=(self.centerOffset+840, 65), size=BTNDIM)
			self.Bind(wx.EVT_BUTTON, self.OnBAdviceLog, self.bAdvice)
			
		self.totalw = totalw
		self.totalh = diagramh + 280 # 1080 if diagram is full 800 height
		self.centerw = int(self.totalw/2)
		self.centerh = int(self.totalh/2)
		self.showSplash = True
		self.ResetScreen()
		self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
		
	def OnKeyDown(self, evt):
		kcd = evt.GetKeyCode()
		if kcd == wx.WXK_PAGEUP:
			if self.settings.pages == 3:
				if self.currentScreen == LaKr:
					self.SwapToScreen(HyYdPt)
				elif self.currentScreen == NaCl:
					self.SwapToScreen(LaKr)
			else:
				self.shiftXOffset += self.diagramWidth
				if self.shiftXOffset > 0:
					self.shiftXOffset = 0
				self.SetPosition((self.shiftXOffset, self.shiftYOffset))
				
		elif kcd == wx.WXK_PAGEDOWN:
			if self.settings.pages == 3:
				if self.currentScreen == HyYdPt:
					self.SwapToScreen(LaKr)
				elif self.currentScreen == LaKr:
					self.SwapToScreen(NaCl)
			else:
				self.shiftXOffset -= self.diagramWidth
				if self.shiftXOffset < -2*self.diagramWidth:
					self.shiftXOffset = -2*self.diagramWidth
				self.SetPosition((self.shiftXOffset, self.shiftYOffset))

		elif kcd == wx.WXK_LEFT:
			self.shiftXOffset -= 10
			if self.shiftXOffset < -2*self.diagramWidth:
				self.shiftXOffset = -2*self.diagramWidth
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
				
		elif kcd == wx.WXK_RIGHT:
			self.shiftXOffset += 10
			if self.shiftXOffset > 0:
				self.shiftXOffset = 0
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
					
		elif kcd == wx.WXK_UP:
			self.shiftYOffset -= 10
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
					
		elif kcd == wx.WXK_DOWN:
			self.shiftYOffset += 10
			if self.shiftYOffset > 0:
				self.shiftYOffset = 0
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
							
		elif kcd == wx.WXK_SHIFT:
			self.SetShift(True)
			evt.Skip()
			
		elif kcd == wx.WXK_HOME:
			self.ResetScreen()
			evt.Skip()
			
		elif kcd == wx.WXK_SHIFT:
			self.SetShift(True)
			
		elif kcd == wx.WXK_ESCAPE and self.shift:
			self.CloseProgram()
				
		else:
			evt.Skip()

	def OnKeyUp(self, evt):
		kcd = evt.GetKeyCode()
		if kcd == wx.WXK_SHIFT:
			self.SetShift(False)

		evt.Skip()
			
	def SetShift(self, flag):
		self.shift = flag
		
	def OnResetScreen(self, _):
		self.ResetScreen()
		
	def ResetScreen(self):
		self.SetMaxSize((self.totalw, self.totalh))
		self.SetSize((self.totalw, self.totalh))
		self.SetPosition((-self.centerOffset, 0))
		
		self.shiftXOffset = -self.centerOffset
		self.shiftYOffset = 0
		
		if self.ATCEnabled:
			self.Request({"atc": { "action": "reset"}})
			
		self.DoRefresh()

		wx.CallAfter(self.Initialize)
		
	def OnBResetClock(self, _):
		self.tickerCount = 0
		self.timeValue = 360 # 6:00
		self.DisplayTimeValue()
		
	def OnBStartClock(self, _):
		self.clockRunning = not self.clockRunning
		self.bStartClock.SetLabel("Stop" if self.clockRunning else "Start")
		self.bResetClock.Enable(not self.clockRunning)
		if self.clockRunning:
			self.tickerCount = 0

	def OnCBToD(self, _):
		if self.cbToD.IsChecked():
			self.ToD = True
			self.bStartClock.Enable(False)
			self.bResetClock.Enable(False)
			self.timeValue = self.GetToD()
		else:		
			self.ToD = False
			self.bStartClock.Enable(True)
			self.bResetClock.Enable(True)
			#self.timeValue = 360 # initial value 6:00
			
		self.clockRunning = False
		self.bStartClock.SetLabel("Start")
			
		self.DisplayTimeValue()
		
	def GetToD(self):
		tm = time.localtime()
		return (tm.tm_hour%12) * 60 + tm.tm_min
		
	def DisplayTimeValue(self):
		hours = int(self.timeValue/60)
		if hours == 0:
			hours = 12
		minutes = self.timeValue % 60
		self.timeDisplay.SetValue("%2d:%02d" % (hours, minutes))
		if self.subscribed and self.IsDispatcher():
			self.Request({"clock": { "value": self.timeValue}})
					
	def OnThrottle(self, _):
		throttleExec = os.path.join(os.getcwd(), "throttle", "main.py")
		throttleProc = Popen([sys.executable, throttleExec])
		logging.info("Throttle started as PID %d" % throttleProc.pid)
					
	def OnEditTrains(self, _):
		treditExec = os.path.join(os.getcwd(), "traineditor", "main.py")
		treditProc = Popen([sys.executable, treditExec])
		logging.info("Train Editor started as PID %d" % treditProc.pid)

	def OnBActiveTrains(self, _):		
		self.activeTrains.ShowTrainList(self)

	def DefineWidgets(self, voffset):
		if not self.IsDispatcher():
			return

		self.rbNassauControl = wx.RadioBox(self, wx.ID_ANY, "Nassau", (150, voffset), wx.DefaultSize,
				["Nassau", "Dispatcher: Main", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBNassau, self.rbNassauControl)
		self.rbNassauControl.Hide()
		self.widgetMap[NaCl].append(self.rbNassauControl)
		self.rbNassauControl.SetSelection(2)
		self.nassauControl = 2

		self.rbCliffControl = wx.RadioBox(self, wx.ID_ANY, "Cliff", (1550, voffset), wx.DefaultSize,
				["Cliff", "Dispatcher: Bank/Cliveden", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBCliff, self.rbCliffControl)
		self.rbCliffControl.Hide()
		self.widgetMap[NaCl].append(self.rbCliffControl)
		self.rbCliffControl.SetSelection(2)
		self.cliffControl = 2

		self.rbYardControl = wx.RadioBox(self, wx.ID_ANY, "Yard", (1450, voffset), wx.DefaultSize,
				["Yard", "Dispatcher"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBYard, self.rbYardControl)
		self.rbYardControl.Hide()
		self.widgetMap[HyYdPt].append(self.rbYardControl)

		self.rbS4Control = wx.RadioBox(self, wx.ID_ANY, "Signal 4L/4R", (150, voffset), wx.DefaultSize,
				["Port", "Dispatcher"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBS4, self.rbS4Control)
		self.rbS4Control.Hide()
		self.widgetMap[LaKr].append(self.rbS4Control)

		self.cbLathamFleet = wx.CheckBox(self, -1, "Latham Fleeting", (300, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBLathamFleet, self.cbLathamFleet)
		self.cbLathamFleet.Hide()
		self.widgetMap[LaKr].append(self.cbLathamFleet)
		self.LathamFleetSignals =  ["L8R", "L8L", "L6RA", "L6RB", "L6L", "L4R", "L4L"]

		self.cbCarltonFleet = wx.CheckBox(self, -1, "Carlton Fleeting", (300, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBCarltonFleet, self.cbCarltonFleet)
		self.cbCarltonFleet.Hide()
		self.widgetMap[LaKr].append(self.cbCarltonFleet)
		self.CarltonFleetSignals = ["L18R", "L18L", "L16R", "L14R", "L14L"]

		self.cbValleyJctFleet = wx.CheckBox(self, -1, "Valley Junction Fleeting", (900, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBValleyJctFleet, self.cbValleyJctFleet)
		self.cbValleyJctFleet.Hide()
		self.widgetMap[LaKr].append(self.cbValleyJctFleet)
		self.ValleyJctFleetSignals = ["D6RA", "D6RB", "D6L", "D4RA", "D4RB", "D4L"]

		self.cbFossFleet = wx.CheckBox(self, -1, "Foss Fleeting", (900, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBFossFleet, self.cbFossFleet)
		self.cbFossFleet.Hide()
		self.widgetMap[LaKr].append(self.cbFossFleet)
		self.FossFleetSignals = ["D10R", "D10L", "D12R", "D12L"]

		self.cbShoreFleet = wx.CheckBox(self, -1, "Shore Fleeting", (1500, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBShoreFleet, self.cbShoreFleet)
		self.cbShoreFleet.Hide()
		self.widgetMap[LaKr].append(self.cbShoreFleet)
		self.ShoreFleetSignals = ["S4R", "S12R", "S4LA", "S4LB", "S4LC", "S12LA", "S12LB", "S12LC"]

		self.cbHydeJctFleet = wx.CheckBox(self, -1, "Hyde Junction Fleeting", (1500, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBHydeJctFleet, self.cbHydeJctFleet)
		self.cbHydeJctFleet.Hide()
		self.widgetMap[LaKr].append(self.cbHydeJctFleet)
		self.HydeJctFleetSignals = ["S20R", "S18R", "S16R", "S20L", "S18LA", "S18LB", "S16L"]

		self.cbKrulishFleet = wx.CheckBox(self, -1, "Krulish Fleeting", (2100, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBKrulishFleet, self.cbKrulishFleet)
		self.cbKrulishFleet.Hide()
		self.widgetMap[LaKr].append(self.cbKrulishFleet)
		self.KrulishFleetSignals = ["K8R", "K4R", "K2R", "K8LA", "K8LB", "K2L"]

		self.cbNassauFleet = wx.CheckBox(self, -1, "Nassau Fleeting", (300, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBNassauFleet, self.cbNassauFleet)
		self.cbNassauFleet.Hide()
		self.widgetMap[NaCl].append(self.cbNassauFleet)
		self.NassauFleetSignalsMain = ["N16R", "N14R",
						"N18LB", "N16L", "N14LA", "N14LB",
						"N26RB", "N26RC", "N24RA", "N24RB",
						"N26L", "N24L"]
		self.NassauFleetSignalsAll = ["N18R", "N16R", "N14R",
						"N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD",
						"N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD",
						"N28L", "N26L", "N24L"]
		self.NassauFleetSignals = self.NassauFleetSignalsAll

		self.cbBankFleet = wx.CheckBox(self, -1, "Martinsville Fleeting", (900, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBBankFleet, self.cbBankFleet)
		self.cbBankFleet.Hide()
		self.widgetMap[NaCl].append(self.cbBankFleet)
		self.BankFleetSignals = ["C22L", "C24L", "C22R", "C24R"]

		self.cbClivedenFleet = wx.CheckBox(self, -1, "Cliveden Fleeting", (1400, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBClivedenFleet, self.cbClivedenFleet)
		self.cbClivedenFleet.Hide()
		self.widgetMap[NaCl].append(self.cbClivedenFleet)
		self.ClivedenFleetSignals = ["C10L", "C12L", "C10R", "C12R", "C14L", "C14RA", "C14RB", "C18LA", "C18LB", "C18R"]

		self.cbYardFleet = wx.CheckBox(self, -1, "Yard Fleeting", (1650, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBYardFleet, self.cbYardFleet)
		self.cbYardFleet.Hide()
		self.widgetMap[HyYdPt].append(self.cbYardFleet)
		self.YardFleetSignals = [ "Y2R", "Y2L", "Y4RA", "Y4RB", "Y4L", "Y8R", "Y8LA", "Y8LB", "Y8LC", "Y10R", "Y10L",
					"Y22R", "Y22L", "Y24LA", "Y24LB", "Y26R", "Y26LA", "Y26LB", "Y26LC", "Y34RA", "Y34RB", "Y34L",
					"Y40RA", "Y40RB", "Y40RC", "Y40RD", "Y40L", "Y42R", "Y42LA", "Y42LB", "Y42LC", "Y42LD" ]

		self.cbCliffFleet = wx.CheckBox(self, -1, "Cliff Fleeting", (2100, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBCliffFleet, self.cbCliffFleet)
		self.cbCliffFleet.Hide()
		self.widgetMap[NaCl].append(self.cbCliffFleet)
		self.CliffFleetSignals = [ "C2LA", "C2LB", "C2LC", "C2LD", "C2R",
					"C4L", "C4RA", "C4RB", "C4RC", "C4RD",
					"C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL", "C6R",
					"C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL" ]

		self.cbHydeFleet = wx.CheckBox(self, -1, "Hyde Fleeting", (250, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBHydeFleet, self.cbHydeFleet)
		self.cbHydeFleet.Hide()
		self.widgetMap[HyYdPt].append(self.cbHydeFleet)
		self.HydeFleetSignals = [ "H4R", "H4LA", "H4LB", "H4LC", "H4LD", "H6R", "H6LA", "H6LB", "H6LC", "H6LD", "H8R", "H8L",
					"H10L", "H10RA", "H10RB", "H10RC", "H10RD", "H10RE", "H12L", "H12RA", "H12RB", "H12RC", "H12RD", "H12RE"  ]

	def GetFleetMap(self, signm):
		siglists = [
			[ self.NassauFleetSignals,    self.cbNassauFleet ],
			[ self.LathamFleetSignals,    self.cbLathamFleet ],
			[ self.CarltonFleetSignals,   self.cbCarltonFleet ],
			[ self.ValleyJctFleetSignals, self.cbValleyJctFleet ],
			[ self.FossFleetSignals,      self.cbFossFleet ],
			[ self.ShoreFleetSignals,     self.cbShoreFleet ],
			[ self.HydeJctFleetSignals,   self.cbHydeJctFleet ],
			[ self.KrulishFleetSignals,   self.cbKrulishFleet ],
			[ self.BankFleetSignals,      self.cbBankFleet ],
			[ self.ClivedenFleetSignals,  self.cbClivedenFleet ],
			[ self.HydeFleetSignals,      self.cbHydeFleet ],
			[ self.YardFleetSignals,      self.cbYardFleet ],
			[ self.CliffFleetSignals,      self.cbCliffFleet ],
		]
		for siglist, checkbox in siglists:
			if signm in siglist:
				return siglist, checkbox
			
		return None, None

	def UpdateControlWidget(self, name, value):
		if not self.IsDispatcher():
			return
		if name == "nassau":
			self.rbNassauControl.SetSelection(value)
			self.nassauControl = value
			self.cbNassauFleet.Enable(value != 0)
			
		elif name == "cliff":
			self.rbCliffControl.SetSelection(value)
			self.cliffControl = value
			
		elif name == "yard":
			self.rbYardControl.SetSelection(value)
			self.cbYardFleet.Enable(value != 0)
			
		elif name == "signal4":
			self.rbS4Control.SetSelection(value)
			
		elif name == "cliff.fleet":
			ctl = self.rbCliffControl.GetSelection()
			self.cliffControl = ctl
			if ctl == 0:
				self.cbCliffFleet.SetValue(value != 0)
				self.cbClivedenFleet.SetValue(value != 0)
				self.cbBankFleet.SetValue(value != 0)
				f = 1 if value != 0 else 0
				for signm in self.CliffFleetSignals + self.ClivedenFleetSignals + self.BankFleetSignals:
					self.Request({"fleet": { "name": signm, "value": f}})
			elif ctl == 1:
				self.cbCliffFleet.SetValue(value != 0)
				f = 1 if value != 0 else 0
				for signm in self.CliffFleetSignals:
					self.Request({"fleet": { "name": signm, "value": f}})
			
		elif name == "hyde.fleet":
			self.cbHydeFleet.SetValue(value != 0)			
			f = 1 if value != 0 else 0
			for signm in self.HydeFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})
			
		elif name == "yard.fleet":
			self.cbYardFleet.SetValue(value != 0)
			f = 1 if value != 0 else 0
			for signm in self.YardFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})			
			
		elif name == "latham.fleet":
			self.cbLathamFleet.SetValue(value != 0)
			
		elif name == "shore.fleet":
			self.cbShoreFleet.SetValue(value != 0)
			
		elif name == "hydejct.fleet":
			self.cbHydeJctFleet.SetValue(value != 0)
			
		elif name == "krulish.fleet":
			self.cbKrulishFleet.SetValue(value != 0)
			
		elif name == "nassau.fleet":
			self.cbNassauFleet.SetValue(value != 0)
			f = 1 if value != 0 else 0
			for signm in self.NassauFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})			
			
		elif name == "bank.fleet":
			self.cbBankFleet.SetValue(value != 0)
			
		elif name == "cliveden.fleet":
			self.cbClivedenFleet.SetValue(value != 0)
			
		elif name == "carlton.fleet":
			self.cbCarltonFleet.SetValue(value != 0)
			
		elif name == "foss.fleet":
			self.cbFossFleet.SetValue(value != 0)
			
		elif name == "valleyjct.fleet":
			self.cbValleyJctFleet.SetValue(value != 0)

	def SendControlValues(self):
		if not self.IsDispatcher():
			return
		
		ctl = self.rbNassauControl.GetSelection()
		self.cbNassauFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "nassau", "value": ctl}})
		self.nassauControl = ctl
			
		ctl = self.rbCliffControl.GetSelection()
		self.cbCliffFleet.Enable(ctl == 2)
		self.cbBankFleet.Enable(ctl != 0)
		self.cbClivedenFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "cliff", "value": ctl}})
		self.cliffControl = ctl
		
		ctl = self.rbYardControl.GetSelection()
		self.cbYardFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "yard", "value": ctl}})

		ctl = self.rbS4Control.GetSelection()
		self.Request({"control": { "name": "signal4", "value": ctl}})
			
		f = 1 if self.cbCliffFleet.IsChecked() else 0
		for signm in self.CliffFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliff.fleet", "value": f}})

		f = 1 if self.cbLathamFleet.IsChecked() else 0
		for signm in self.LathamFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "latham.fleet", "value": f}})

		f = 1 if self.cbHydeFleet.IsChecked() else 0
		for signm in self.HydeFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hyde.fleet", "value": f}})

		f = 1 if self.cbYardFleet.IsChecked() else 0
		for signm in self.YardFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "yard.fleet", "value": f}})

		f = 1 if self.cbShoreFleet.IsChecked() else 0
		for signm in self.ShoreFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "shore.fleet", "value": f}})

		f = 1 if self.cbHydeJctFleet.IsChecked() else 0
		for signm in self.HydeJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hydejct.fleet", "value": f}})
			
		f = 1 if self.cbKrulishFleet.IsChecked() else 0
		for signm in self.KrulishFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "krulish.fleet", "value": f}})

		f = 1 if self.cbNassauFleet.IsChecked() else 0
		if self.nassauControl == 1:
			self.NassauFleetSignals = self.NassauFleetSignalsMain
		elif self.nassauControl == 2:
			self.NassauFleetSignals = self.NassauFleetSignalsAll

		for signm in self.NassauFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "nassau.fleet", "value": f}})
			
		f = 1 if self.cbBankFleet.IsChecked() else 0
		for signm in self.BankFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "bank.fleet", "value": f}})

		f = 1 if self.cbClivedenFleet.IsChecked() else 0
		for signm in self.ClivedenFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliveden.fleet", "value": f}})

		f = 1 if self.cbCarltonFleet.IsChecked() else 0
		for signm in self.CarltonFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "carlton.fleet", "value": f}})
			

		f = 1 if self.cbValleyJctFleet.IsChecked() else 0
		for signm in self.ValleyJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "valleyjct.fleet", "value": f}})

		f = 1 if self.cbFossFleet.IsChecked() else 0
		for signm in self.FossFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "foss.fleet", "value": f}})
		
		self.SendOSSLocks()

	def OnCBAutoRouter(self, evt):
		self.AREnabled = self.cbAutoRouter.IsChecked()
		if self.AREnabled:
			rqStatus = "on"
		else:
			rqStatus = "off"
		self.Request({"autorouter": { "status": rqStatus}})

	def OnCBATC(self, evt):
		# ATC must run on the same machine as this dispatcher because it has a windowing interface
		self.ATCEnabled = self.cbATC.IsChecked()
		if self.ATCEnabled:
			#self.pidATC = 1
			if self.procATC is None or self.procATC.poll() is not None:			
				atcExec = os.path.join(os.getcwd(), "atc", "main.py")
				self.procATC = Popen([sys.executable, atcExec])
				self.pidATC = self.procATC.pid
				logging.debug("atc server started as PID %d" % self.pidATC)
				self.pendingATCShowCmd = {"atc": {"action": ["show"], "x": 1600, "y": 31}}
				wx.CallLater(750, self.sendPendingATCShow)
			else:
				self.Request( {"atc": {"action": ["show"], "x": 1600, "y": 31}})

		else:
			self.Request({"atc": { "action": "hide", "x": 1600, "y": 31}})

	def OnCBOSSLocks(self, evt):
		self.SendOSSLocks()
		
	def SendOSSLocks(self):
		self.OSSLocks = self.cbOSSLocks.IsChecked()		
		self.Request({"control": {"name": "osslocks", "value": 1 if self.OSSLocks else 0}})

	def OnCBAdvisor(self, evt):
		self.AdvisorEnabled = self.cbAdvisor.IsChecked()
		if self.AdvisorEnabled:
			rqStatus = "on"
		else:
			rqStatus = "off"
		self.Request({"advisor": { "status": rqStatus}})
		
	def sendPendingATCShow(self):
		self.Request(self.pendingATCShowCmd)
		
	def OnRBNassau(self, evt):
		ctl = evt.GetInt()
		self.cbNassauFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "nassau", "value": ctl}})
		self.nassauControl = ctl

	def OnRBCliff(self, evt):
		ctl = evt.GetInt()
		self.cbCliffFleet.Enable(ctl == 2)
		self.cbBankFleet.Enable(ctl != 0)
		self.cbClivedenFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "cliff", "value": ctl}})
		self.cliffControl = ctl

	def OnRBYard(self, evt):
		ctl = evt.GetInt()
		self.cbYardFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "yard", "value": ctl}})

	def OnRBS4(self, evt):
		self.Request({"control": { "name": "signal4", "value": evt.GetInt()}})

	def OnCBLathamFleet(self, _):
		f = 1 if self.cbLathamFleet.IsChecked() else 0
		for signm in self.LathamFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "latham.fleet", "value": f}})

	def OnCBShoreFleet(self, _):
		f = 1 if self.cbShoreFleet.IsChecked() else 0
		for signm in self.ShoreFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "shore.fleet", "value": f}})

	def OnCBHydeJctFleet(self, _):
		f = 1 if self.cbHydeJctFleet.IsChecked() else 0
		for signm in self.HydeJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hydejct.fleet", "value": f}})

	def OnCBKrulishFleet(self, _):
		f = 1 if self.cbKrulishFleet.IsChecked() else 0
		for signm in self.KrulishFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "krulish.fleet", "value": f}})

	def OnCBNassauFleet(self, _):
		f = 1 if self.cbNassauFleet.IsChecked() else 0
		if self.nassauControl == 1:
			self.NassauFleetSignals = self.NassauFleetSignalsMain
		elif self.nassauControl == 2:
			self.NassauFleetSignals = self.NassauFleetSignalsAll

		for signm in self.NassauFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "nassau.fleet", "value": f}})
		

	def OnCBBankFleet(self, _):
		f = 1 if self.cbBankFleet.IsChecked() else 0
		for signm in self.BankFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "bank.fleet", "value": f}})

	def OnCBClivedenFleet(self, _):
		f = 1 if self.cbClivedenFleet.IsChecked() else 0
		for signm in self.ClivedenFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliveden.fleet", "value": f}})

	def OnCBCarltonFleet(self, _):
		f = 1 if self.cbCarltonFleet.IsChecked() else 0
		for signm in self.CarltonFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "carlton.fleet", "value": f}})

	def OnCBValleyJctFleet(self, _):
		f = 1 if self.cbValleyJctFleet.IsChecked() else 0
		for signm in self.ValleyJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "valleyjct.fleet", "value": f}})

	def OnCBFossFleet(self, _):
		f = 1 if self.cbFossFleet.IsChecked() else 0
		for signm in self.FossFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "foss.fleet", "value": f}})

	def OnCBCliffFleet(self, _):
		f = 1 if self.cbCliffFleet.IsChecked() else 0
		for signm in self.CliffFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliff.fleet", "value": f}})

	def OnCBYardFleet(self, _):
		f = 1 if self.cbYardFleet.IsChecked() else 0
		for signm in self.YardFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "yard.fleet", "value": f}})

	def OnCBHydeFleet(self, _):
		f = 1 if self.cbHydeFleet.IsChecked() else 0
		for signm in self.HydeFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hyde.fleet", "value": f}})

	def FleetCheckBoxes(self, signm):
		if not self.IsDispatcher():
			return
		siglist, checkbox = self.GetFleetMap(signm)
		if siglist is not None:
			fltct = nfltct = 0
			for sn in siglist:
				sig = self.signals[sn]
				if sig.IsFleeted():
					fltct += 1
				else:
					nfltct += 1
			checkbox.SetValue(nfltct == 0)

	def DrawCameras(self):
		cams = {LaKr: [
			[(242, 32), self.bitmaps.cameras.lakr.cam7],
			[(464, 32), self.bitmaps.cameras.lakr.cam8],
			[(768, 32), self.bitmaps.cameras.lakr.cam8],
			[(890, 32), self.bitmaps.cameras.lakr.cam10],
			[(972, 32), self.bitmaps.cameras.lakr.cam12],
			[(1186, 32), self.bitmaps.cameras.lakr.cam3],
			[(1424, 32), self.bitmaps.cameras.lakr.cam4],
			[(1634, 32), self.bitmaps.cameras.lakr.cam13],
			[(1884, 32), self.bitmaps.cameras.lakr.cam14],
			[(2152, 32), self.bitmaps.cameras.lakr.cam15],
			[(2198, 32), self.bitmaps.cameras.lakr.cam16],
			[(2362, 32), self.bitmaps.cameras.lakr.cam9],
			[(2416, 32), self.bitmaps.cameras.lakr.cam10],
		], HyYdPt: [
			[(282, 72), self.bitmaps.cameras.hyydpt.cam15],
			[(838, 72), self.bitmaps.cameras.hyydpt.cam16],
			[(904, 576), self.bitmaps.cameras.hyydpt.cam1],
			[(1712, 10), self.bitmaps.cameras.hyydpt.cam1],
			[(1840, 10), self.bitmaps.cameras.hyydpt.cam2],
			[(1960, 10), self.bitmaps.cameras.hyydpt.cam3],
			[(2090, 10), self.bitmaps.cameras.hyydpt.cam4],
			[(2272, 236), self.bitmaps.cameras.hyydpt.cam5],
			[(2292, 444), self.bitmaps.cameras.hyydpt.cam6],
		], NaCl: [
			[(364, 28), self.bitmaps.cameras.nacl.cam11],
			[(670, 28), self.bitmaps.cameras.nacl.cam12],
			[(918, 28), self.bitmaps.cameras.nacl.cam1],
			[(998, 28), self.bitmaps.cameras.nacl.cam2],
			[(1074, 28), self.bitmaps.cameras.nacl.cam3],
			[(1248, 28), self.bitmaps.cameras.nacl.cam4],
			[(1442, 28), self.bitmaps.cameras.nacl.cam7],
			[(2492, 502), self.bitmaps.cameras.nacl.cam8],
		]}

		for screen in cams:
			offset = self.diagrams[screen].offset
			for pos, bmp in cams[screen]:
				self.panels[screen].DrawFixedBitmap(pos[0], pos[1], offset, bmp)

	def UpdatePositionDisplay(self, x, y, scr):
		self.xpos.SetValue("%4d" % x)
		self.ypos.SetValue("%4d" % y)
		self.scrn.SetValue("%s" % scr)

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def Initialize(self):
		self.listener = None
		self.ShowTitle()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.tiles, self.totiles, self.sstiles, self.sigtiles, self.misctiles = loadTiles(self.bitmaps)
		self.districts = Districts()
		self.signalLeverMap = {}
		self.districts.AddDistrict(Yard("Yard", self, HyYdPt))
		self.districts.AddDistrict(Latham("Latham", self, LaKr))
		self.districts.AddDistrict(Dell("Dell", self, LaKr))
		self.districts.AddDistrict(Shore("Shore", self, LaKr))
		self.districts.AddDistrict(Krulish("Krulish", self, LaKr))
		self.districts.AddDistrict(Nassau("Nassau", self, NaCl))
		self.districts.AddDistrict(Bank("Bank", self, NaCl))
		self.districts.AddDistrict(Cliveden("Cliveden", self, NaCl))
		self.districts.AddDistrict(Cliff("Cliff", self, NaCl))
		self.districts.AddDistrict(Hyde("Hyde", self, HyYdPt))
		self.districts.AddDistrict(Port("Port", self, HyYdPt))

		self.districts.SetTiles(self.tiles, self.totiles, self.sstiles, self.sigtiles, self.misctiles, self.bitmaps.buttons)

		self.blocks, self.osBlocks = self.districts.DefineBlocks()
		self.turnouts = self.districts.DefineTurnouts(self.blocks)
		self.signals =  self.districts.DefineSignals()
		self.buttons =  self.districts.DefineButtons()
		self.handswitches =  self.districts.DefineHandSwitches()
		self.indicators = self.districts.DefineIndicators()

		self.pendingFleets = {}

		self.resolveObjects()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.trains = {}

		#self.districts.Initialize()

		# only set up hot spots on the diagram for dispatchr - not for remote display
		if self.settings.dispatch:
			self.turnoutMap = { (t.GetScreen(), t.GetPos()): t for t in self.turnouts.values() if not t.IsRouteControlled() }
			self.buttonMap = { (b.GetScreen(), b.GetPos()): b for b in self.buttons.values() }
			self.signalMap = { (s.GetScreen(), s.GetPos()): s for s in self.signals.values() }
			self.handswitchMap = { (l.GetScreen(), l.GetPos()): l for l in self.handswitches.values() }

		# set up hot spots for entering/modifying train/loco ID - displays can do this too
		self.blockMap = self.BuildBlockMap(self.blocks)

		self.buttonsToClear = []

		self.districts.Draw()
		
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)
		self.tickerFlag = False
		self.tickerCount = 0
		self.ticker.Start(500)
		
		self.splash()
		
	def splash(self):
		if self.showSplash:
			self.showSplash = False
			splashExec = os.path.join(os.getcwd(), "splash", "main.py")
			pid = Popen([sys.executable, splashExec]).pid
			logging.debug("displaying splash screen as PID %d" % pid)


	def AddSignalLever(self, slname, district):
		self.signalLeverMap[slname] = district

	def GetSignalLeverDistrict(self, slname):
		if slname not in self.signalLeverMap:
			return None

		return self.signalLeverMap[slname]

	def IsDispatcher(self):
		return self.settings.dispatch

	def resolveObjects(self):
		for _, bk in self.blocks.items():
			sgWest, sgEast = bk.GetSBSignals()
			if sgWest is not None:
				try:
					self.signals[sgWest].SetGuardBlock(bk)
				except KeyError:
					sgWest = None

			if sgEast is not None:
				try:
					self.signals[sgEast].SetGuardBlock(bk)
				except KeyError:
					sgEast = None
			bk.SetSBSignals((sgWest, sgEast))

		# invert osBlocks so the we can easily map a block into the OS's it interconnects
		self.blockOSMap = {}
		for osblknm, blklist in self.osBlocks.items():
			for blknm in blklist:
				if blknm in self.blockOSMap:
					self.blockOSMap[blknm].append(self.blocks[osblknm])
				else:
					self.blockOSMap[blknm] = [ self.blocks[osblknm] ]

	def GetOSForBlock(self, blknm):
		if blknm not in self.blockOSMap:
			return []
		else:
			return self.blockOSMap[blknm]

	def AddPendingFleet(self, block, sig):
		self.pendingFleets[block.GetName()] = sig

	def DelPendingFleet(self, block):
		bname = block.GetName()
		if bname not in self.pendingFleets:
			return

		del(self.pendingFleets[bname])

	def DoFleetPending(self, block):
		bname = block.GetName()
		print("in do fleeting for block %s" % bname)
		if bname not in self.pendingFleets:
			print("but there are no pending fleets here")
			return

		sig = self.pendingFleets[bname]
		print("that block has a pending fleet for signal %s" % sig.GetName())
		del(self.pendingFleets[bname])

		sig.DoFleeting()		

	def BuildBlockMap(self, bl):
		blkMap = {}
		for b in bl.values():
			tl = b.GetTrainLoc()
			for scrn, pos in tl:
				lkey = (scrn, pos[1])
				if lkey not in blkMap.keys():
					blkMap[lkey] = []
				blkMap[lkey].append((pos[0], b))

		return blkMap

	def onTicker(self, _):
		self.tickerFlag = not self.tickerFlag
		if self.tickerFlag:
			# call 1sec every other time to simulate a 1 second timer
			self.onTicker1Sec()
			
		self.tickerCount += 1
		if self.tickerCount == 120:
			self.tickerCount = 0
			self.onTicker1Min()
			
		self.delayedRequests.CheckForExpiry(self.Request)

	def onTicker1Sec(self):
		self.ClearExpiredButtons()
		self.breakerDisplay.ticker()
		
	def onTicker1Min(self):
		logging.info("ticker 1 minute, timevalue = %d" % self.timeValue )
		if self.IsDispatcher():
			if self.ToD:
				self.timeValue = self.GetToD()
				self.DisplayTimeValue()
			else:
				if self.clockRunning:
					self.timeValue += 1
					self.DisplayTimeValue()

	def ClearExpiredButtons(self):
		collapse = False
		for b in self.buttonsToClear:
			b[0] -= 1
			if b[0] <= 0:
				b[1].Release(refresh=True)
				collapse = True

		if collapse:
			self.buttonsToClear = [x for x in self.buttonsToClear if x[0] > 0]

	def ClearButtonAfter(self, secs, btn):
		self.buttonsToClear.append([secs, btn])

	def ClearButtonNow(self, btn):
		bnm = btn.GetName()
		collapse = False
		for bx in range(len(self.buttonsToClear)):
			if self.buttonsToClear[bx][1].GetName() == bnm:
				self.buttonsToClear[bx][0] = 0
				self.buttonsToClear[bx][1].Release(refresh=True)
				collapse = True

		if collapse:
			self.buttonsToClear = [x for x in self.buttonsToClear if x[0] > 0]

	def ResetButtonExpiry(self, secs, btn):
		bnm = btn.GetName()
		for bx in range(len(self.buttonsToClear)):
			if self.buttonsToClear[bx][1].GetName() == bnm:
				self.buttonsToClear[bx][0] = secs

	def ProcessClick(self, screen, pos, shift=False, right=False, screenpos=None):
		# ignore screen clicks if not connected
		if not self.subscribed:
			return
		
		#logging.debug("%s click %s %d, %d %s" % ("right" if right else "left", screen, pos[0], pos[1], "shift" if shift else ""))
		try:
			to = self.turnoutMap[(screen, pos)]
		except KeyError:
			to = None

		if to:
			if right:  # only process left clicks here
				return
			
			if to.IsDisabled():
				return

			to.GetDistrict().PerformTurnoutAction(to, force=shift)
			return

		try:
			btn = self.buttonMap[(screen, pos)]
		except KeyError:
			btn = None

		if btn:
			if right or shift:  # only process left clicks here
				return
			
			btn.GetDistrict().PerformButtonAction(btn)
			return

		try:
			sig = self.signalMap[(screen, pos)]
		except KeyError:
			sig = None

		if sig:
			if right:  # only process left clicks here
				return
			
			if sig.IsDisabled():
				return

			sig.GetDistrict().PerformSignalAction(sig, oncall=shift)

		try:
			hs = self.handswitchMap[(screen, pos)]
		except KeyError:
			hs = None

		if hs:
			if right or shift:  # only process left clicks here
				return
			
			if hs.IsDisabled():
				return
			
			hs.GetDistrict().PerformHandSwitchAction(hs)

		try:
			ln = self.blockMap[(screen, pos[1])]
		except KeyError:
			ln = None

		if ln:
			if shift:
				return
			
			for col, blk in ln:
				if col <= pos[0] <= col+3:
					break
			else:
				blk = None

			if blk:
				if blk.IsOccupied():
					tr = blk.GetTrain()
					if right:
						menu = wx.Menu()
						self.menuTrain = tr
						addedMenuItem = False
						if not self.IsDispatcher():
							if self.settings.allowatcrequests:
								if tr.IsOnATC():
									menu.Append( MENU_ATC_REM_REQ, "Request: ATC Remove" )
									self.Bind(wx.EVT_MENU, self.OnATCRemReq, id=MENU_ATC_REM_REQ)
								else:
									menu.Append( MENU_ATC_ADD_REQ, "Request: ATC Add" )
									self.Bind(wx.EVT_MENU, self.OnATCAddReq, id=MENU_ATC_ADD_REQ)
								addedMenuItem = True
						
						else: # IS Dispatcher								
							if self.ATCEnabled:
								if tr.IsOnATC():
									menu.Append( MENU_ATC_REMOVE, "Remove from ATC" )
									self.Bind(wx.EVT_MENU, self.OnATCRemove, id=MENU_ATC_REMOVE)
									menu.Append( MENU_ATC_STOP, "ATC Stop/Resume Train" )
									self.Bind(wx.EVT_MENU, self.OnATCStop, id=MENU_ATC_STOP)
									addedMenuItem = True
								else:
									loco = tr.GetLoco()
									if loco != "??":
										menu.Append( MENU_ATC_ADD, "Add to ATC")
										self.Bind(wx.EVT_MENU, self.OnATCAdd, id=MENU_ATC_ADD)
										addedMenuItem = True
								
							if self.AREnabled:
								if tr.IsOnAR():
									menu.Append( MENU_AR_REMOVE, "Remove from Auto Router")
									self.Bind(wx.EVT_MENU, self.OnARRemove, id=MENU_AR_REMOVE)
								else:
									menu.Append( MENU_AR_ADD, "Add to Auto Router")
									self.Bind(wx.EVT_MENU, self.OnARAdd, id=MENU_AR_ADD)
								addedMenuItem = True

						if addedMenuItem:
							self.PopupMenu( menu, (screenpos[0], screenpos[1]+50) )
						menu.Destroy()

					else:
						oldName, oldLoco = tr.GetNameAndLoco()
						oldATC = tr.IsOnATC() if self.IsDispatcher() else False
						oldAR = tr.IsOnAR() if self.IsDispatcher() else False
						dlgx = self.centerw - 500 - self.centerOffset
						dlgy = self.totalh - 660
						dlg = EditTrainDlg(self, tr, blk, self.locoList, self.trainList, self.trains, self.IsDispatcher() and self.ATCEnabled, self.IsDispatcher() and self.AREnabled, dlgx, dlgy)
						rc = dlg.ShowModal()
						if rc == wx.ID_OK:
							trainid, locoid, atc, ar = dlg.GetResults()
						dlg.Destroy()
						
						if rc == wx.ID_CUT:
							newTr = Train()
							newName = newTr.GetName()
							newLoco = newTr.GetLoco()

							tr.RemoveFromBlock(blk)
							newTr.AddToBlock(blk)
							blk.SetTrain(newTr)
							
							self.trains[newName] = newTr
							newTr.SetEast(blk.GetEast()) # train takes on the direction of the block
							
							self.activeTrains.AddTrain(newTr)
							self.activeTrains.UpdateTrain(oldName)
							
							self.Request({"settrain": { "block": blk.GetName()}})
							self.Request({"settrain": { "block": blk.GetName(), "name": newName, "loco": newLoco}})


							if self.IsDispatcher():
								self.CheckTrainsInBlock(blk.GetName(), None)
							
							tr.Draw()
							newTr.Draw()
							return 
						
						if rc != wx.ID_OK:
							return
	
						if oldName != trainid or oldLoco != locoid:
							self.Request({"renametrain": { "oldname": oldName, "newname": trainid, "oldloco": oldLoco, "newloco": locoid}})
							
						if self.IsDispatcher() and atc != oldATC:
							if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
								tr.SetATC(atc)
								self.activeTrains.UpdateTrain(trainid)
								self.Request({"atc": {"action": "add" if atc else "remove", "train": trainid, "loco": locoid}})
							
						if self.IsDispatcher() and ar != oldAR:
							if self.VerifyTrainID(trainid):
								tr.SetAR(ar)
								self.activeTrains.UpdateTrain(trainid)
								self.Request({"ar": {"action": "add" if ar else "remove", "train": trainid}})
	
						tr.Draw()

	def VerifyTrainID(self, trainid):
		if trainid is None or trainid.startswith("??"):
			self.PopupEvent("Train ID is required")
			return False
		return True
	
	def VerifyLocoID(self, locoid):		
		if locoid is None or locoid.startswith("??"):
			self.PopupEvent("locomotive ID is required")
			return False
		
		return True
	
	def OnATCAdd(self, _):
		trainid, locoid = self.menuTrain.GetNameAndLoco()
		if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
			self.menuTrain.SetATC(True)
			self.activeTrains.UpdateTrain(trainid)
			self.Request({"atc": {"action": "add", "train": trainid, "loco": locoid}})
			self.menuTrain.Draw()

	def OnATCAddReq(self, evt):
		trainid, locoid = self.menuTrain.GetNameAndLoco()
		if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
			self.Request({"atcrequest": {"action": "add", "train": trainid, "loco": locoid}})
							
	def OnATCRemove(self, evt):
		trainid, locoid = self.menuTrain.GetNameAndLoco()
		if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
			self.menuTrain.SetATC(False)
			self.activeTrains.UpdateTrain(trainid)
			self.Request({"atc": {"action": "remove", "train": trainid, "loco": locoid}})
			self.menuTrain.Draw()
							
	def OnATCRemReq(self, evt):
		trainid, locoid = self.menuTrain.GetNameAndLoco()
		if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
			self.Request({"atcrequest": {"action": "remove", "train": trainid, "loco": locoid}})
		
	def OnATCStop(self, evt):
		trainid, locoid = self.menuTrain.GetNameAndLoco()
		if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
			self.Request({"atc": {"action": "forcestop", "train": trainid, "loco": locoid}})
		
	def OnARAdd(self, evt):
		trainid = self.menuTrain.GetName()
		if self.VerifyTrainID(trainid):
			self.menuTrain.SetAR(True)
			self.activeTrains.UpdateTrain(trainid)
			self.Request({"ar": {"action": "add", "train": trainid}})
			self.menuTrain.Draw()
		
	def OnARRemove(self, evt):
		trainid = self.menuTrain.GetName()
		if self.VerifyTrainID(trainid):
			self.menuTrain.SetAR(False)
			self.activeTrains.UpdateTrain(trainid)
			self.Request({"ar": {"action": "remove", "train": trainid}})
			self.menuTrain.Draw()

	def DrawTile(self, screen, pos, bmp):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawTile(pos[0], pos[1], offset, bmp)

	def DrawText(self, screen, pos, text):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawText(pos[0], pos[1], offset, text)

	def ClearText(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearText(pos[0], pos[1], offset)

	def DrawTrain(self, screen, pos, trainID, locoID, stopRelay, atc, ar):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawTrain(pos[0], pos[1], offset, trainID, locoID, stopRelay, atc, ar)

	def ClearTrain(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearTrain(pos[0], pos[1], offset)
		
	def CheckTrainsInBlock(self, blkNm, sig):
		# either a train is new in a block or the signal at the end of that block has changed.  See what trains are affected
		blk = self.GetBlockByName(blkNm)
		if blk is None:
			logging.info("Bad block name: %s" % blkNm)
			return 
		
		if blk.GetBlockType() != BLOCK:
			# skip OS and stopping sections
			return 
		
		if sig is None:
			sigNm = blk.GetDirectionSignal()
			if sigNm is None:
				# no signal at the end of this block
				return 
			sig = self.GetSignalByName(sigNm)
			if sig is None:
				return

		# check for trains in the entry block.  If it is the front of the train, then this signal change applies to that train.
		for trid, tr in self.trains.items():
			if tr.FrontInBlock(blkNm):
				# we found a train
				tr.SetSignal(sig)
				self.activeTrains.UpdateTrain(trid)
				req = {"trainsignal": { "train": trid, "block": blkNm, "signal": sig.GetName(), "aspect": sig.GetAspect()}}
				self.Request(req)

	def SwapToScreen(self, screen):
		if screen == HyYdPt:
			self.bScreenHyYdPt.Enable(False)
			self.bScreenLaKr.Enable(True)
			self.bScreenNaCl.Enable(True)
		elif screen == LaKr:
			self.bScreenHyYdPt.Enable(True)
			self.bScreenLaKr.Enable(False)
			self.bScreenNaCl.Enable(True) 
		elif screen == NaCl:
			self.bScreenHyYdPt.Enable(True) 
			self.bScreenLaKr.Enable(True)
			self.bScreenNaCl.Enable(False) 
		else:
			return False

		if screen == self.currentScreen:
			return True
		self.panels[screen].Show()
		if self.currentScreen:
			self.panels[self.currentScreen].Hide()
		self.currentScreen = screen

		for scr in self.widgetMap:
			for w in self.widgetMap[scr]:
				if scr == self.currentScreen:
					w.Show()
				else:
					w.Hide()

		return True

	def PlaceWidgets(self):
		for scr in self.widgetMap:
			if scr == HyYdPt:
				offset = 0
			elif scr == LaKr:
				offset = self.bmpw
			elif scr == NaCl:
				offset = self.bmpw*2
			else:
				offset = 0

			for w in self.widgetMap[scr]:
				pos = w.GetPosition()
				pos[0] += offset
				w.SetPosition(pos)
				w.Show()

	def GetBlockStatus(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			return EMPTY

		return blk.GetStatus()

	def GetBlockByName(self, blknm):
		try:
			return self.blocks[blknm]
		except:
			return None

	def GetSignalByName(self, signm):
		try:
			return self.signals[signm]
		except:
			return None

	def NewTrain(self):
		tr = Train(None)
		name, _ = tr.GetNameAndLoco()
		self.trains[name] = tr
		self.activeTrains.AddTrain(tr)
		return tr

	def ToasterSetup(self):
		self.events = Toaster()
		self.events.SetOffsets(0, 150)
		self.events.SetFont(wx.Font(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial")))
		self.events.SetBackgroundColour(wx.Colour(255, 179, 154))
		self.events.SetTextColour(wx.Colour(0, 0, 0))
		
		self.advice = Toaster()
		self.advice.SetOffsets(0, 150)
		self.advice.SetFont(wx.Font(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial")))
		self.advice.SetBackgroundColour(wx.Colour(120, 255, 154))
		self.advice.SetTextColour(wx.Colour(0, 0, 0))

	def PopupEvent(self, message):
		self.events.Append(message)
		self.eventsList.append(message)
		
	def OnBEventsLog(self, _):
		if self.dlgEvents is None:
			self.dlgEvents = ListDlg(self, "Events List", self.eventsList, self.DlgEventsExit)
			self.dlgEvents.Show()
			
	def DlgEventsExit(self):
		self.dlgEvents.Destroy()
		self.dlgEvents = None

	def PopupAdvice(self, message):
		self.advice.Append(message)
		self.adviceList.append(message)
		
	def OnBAdviceLog(self, _):
		if self.dlgAdvice is None:
			self.dlgAdvice = ListDlg(self, "Advice List", self.adviceList, self.DlgAdviceExit)
			self.dlgAdvice.Show()
			
	def DlgAdviceExit(self):
		self.dlgAdvice.Destroy()
		self.dlgAdvice = None
		
	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			self.bLoadTrains.Enable(False)
			self.bLoadLocos.Enable(False)
			self.bSaveTrains.Enable(False)
			self.bClearTrains.Enable(False)
			self.bSaveLocos.Enable(False)
			if self.IsDispatcher():
				self.cbAutoRouter.Enable(False)
				self.cbATC.Enable(False)
				self.cbAdvisor.Enable(False)
			
		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				logging.error("Unable to establish connection with server")
				self.listener = None
				return

			self.listener.start()
			self.subscribed = True
			self.bSubscribe.SetLabel("Disconnect")
			self.bRefresh.Enable(True)
			self.bLoadTrains.Enable(True)
			self.bLoadLocos.Enable(True)
			self.bSaveTrains.Enable(True)
			self.bClearTrains.Enable(True)
			self.bSaveLocos.Enable(True)
			if self.IsDispatcher():
				self.cbAutoRouter.Enable(True)
				self.cbATC.Enable(True)
				self.cbAdvisor.Enable(True)
				
			self.RetrieveData()
			self.districts.Initialize()
			self.SendControlValues()

		self.breakerDisplay.UpdateDisplay()
		self.ShowTitle()

	def RetrieveData(self):
		locos = self.Get("getlocos", {})
		if locos is None:
			logging.error("Unable to retrieve locos")
			locos = {}
			
		self.locoList = locos

		trains = self.Get("gettrains", {})
		if trains is None:
			logging.error("Unable to retrieve trains")
			trains = {}
			
		self.trainList = trains

	def OnRefresh(self, _):
		self.DoRefresh()
		
	def DoRefresh(self):
		if self.IsDispatcher():
			self.Request({"clock": { "value": self.timeValue}})

		self.Request({"refresh": {"SID": self.sessionid}})

	def raiseDeliveryEvent(self, data): # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.warning("Unable to parse (%s)" % data)
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			#logging.info("Dispatch: %s: %s" % (cmd, parms))
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					try:
						force = p["force"]
					except:
						force = False
						
					try:
						to = self.turnouts[turnout]
					except KeyError:
						to = None
						
					if to is not None and state != to.GetStatus():
						district = to.GetDistrict()
						st = REVERSE if state == "R" else NORMAL
						district.DoTurnoutAction(to, st, force=force)

			elif cmd == "fleet":
				for p in parms:
					signm = p["name"]
					try:
						value = int(p["value"])
					except:
						value = 0

					sig = self.signals[signm]
					sig.EnableFleeting(value == 1)
					self.FleetCheckBoxes(signm)

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]

					blk = None
					try:
						blk = self.blocks[block]
						blockend = None
					except KeyError:
						if block.endswith(".E") or block.endswith(".W"):
							blockend = block[-1]
							block = block[:-2]
							try:
								blk = self.blocks[block]
							except KeyError:
								blk = None

					stat = OCCUPIED if state == 1 else EMPTY
					if blk is not None:
						if blk.GetStatus(blockend) != stat:
							district = blk.GetDistrict()
							district.DoBlockAction(blk, blockend, stat)
							if self.IsDispatcher():
								self.CheckTrainsInBlock(block, None)

			elif cmd == "blockdir":
				for p in parms:
					block = p["block"]
					try:
						direction = p["dir"] == 'E'
					except KeyError:
						direction = True  # east

					blk = None
					try:
						blk = self.blocks[block]
						blockend = None
					except KeyError:
						if block.endswith(".E") or block.endswith(".W"):
							blockend = block[-1]
							block = block[:-2]
							try:
								blk = self.blocks[block]
							except KeyError:
								blk = None
					if blk is not None:
						blk.SetEast(direction, broadcast=False)

			elif cmd == "blockclear":
				pass
					
			elif cmd == "signal":
				for p in parms:
					print("signal paranmeters: %s" % str(parms))
					sigName = p["name"]
					aspect = p["aspect"]
					try:
						oncall = int(p["oncall"])
					except:
						oncall = 0

					try:
						sig = self.signals[sigName]
					except:
						sig = None

					if sig is not None and aspect != sig.GetAspect():
						district = sig.GetDistrict()
						district.DoSignalAction(sig, aspect, oncall=oncall)

			elif cmd == "siglever":
				if self.IsDispatcher():
					for p in parms:
						signame = p["name"]
						state = p["state"]

						district = self.GetSignalLeverDistrict(signame)
						if district is None:
							# unable to find district for signal lever
							return
						district.DoSignalLeverAction(signame, state)
						
			elif cmd == "handswitch":
				for p in parms:
					hsName = p["name"]
					state = p["state"]
					
					try:
						hs = self.handswitches[hsName]
					except:
						hs = None

					if hs is not None and state != hs.GetValue():
						district = hs.GetDistrict()
						district.DoHandSwitchAction(hs, state)
						
			elif cmd == "indicator":
				for p in parms:
					iName = p["name"]
					value = int(p["value"])
					
					try:
						ind = self.indicators[iName]
					except:
						ind = None

					if ind is not None:
						district = ind.GetDistrict()
						district.DoIndicatorAction(ind, value)

			elif cmd == "breaker":
				for p in parms:
					name = p["name"]
					val = p["value"]
					if val == 0:
						self.PopupEvent("Breaker: %s" % BreakerName(name))
						self.breakerDisplay.AddBreaker(name)
					else:
						self.breakerDisplay.DelBreaker(name)

					if name in self.indicators:
						ind = self.indicators[name]
						if val != ind.GetValue():
							ind.SetValue(val, silent=True)

			elif cmd == "settrain":
				for p in parms:
					block = p["block"]
					name = p["name"]
					loco = p["loco"]

					try:
						blk = self.blocks[block]
					except:
						logging.warning("unable to identify block (%s)" % block)
						blk = None

					if blk:
						tr = blk.GetTrain()
						if name is None:
							if tr:
								tr.RemoveFromBlock(blk)
								self.activeTrains.UpdateTrain(tr.GetName())
								if not tr.IsContiguous():
									self.PopupEvent("Train %s is non-contiguous" % tr.GetName())

							delList = []
							for trid, tr in self.trains.items():
								if tr.IsInBlock(blk):
									tr.RemoveFromBlock(blk)
									self.activeTrains.UpdateTrain(tr.GetName())
									if tr.IsInNoBlocks():
										delList.append(trid)
									elif not tr.IsContiguous():
										self.PopupEvent("Train %s is non-contiguous" % tr.GetName())

							for trid in delList:
								try:
									self.activeTrains.RemoveTrain(trid)
									del(self.trains[trid])
								except:
									logging.warning("can't delete train %s from train list" % trid)

							return

						if not blk.IsOccupied():
							logging.warning("Set train for block %s, but that block is unoccupied" % block)
							return

						if tr:
							oldName = tr.GetName()
							if oldName and oldName != name:
								if name in self.trains:
									# merge the two trains under the new "name"
									try:
										bl = self.trains[oldName].GetBlockList()
									except:
										bl = {}
									for blk in bl.values():
										self.trains[name].AddToBlock(blk)
									self.activeTrains.UpdateTrain(name)
								else:
									tr.SetName(name)
									self.trains[name] = tr
									self.activeTrains.RenameTrain(oldName, name)

								try:
									self.activeTrains.RemoveTrain(oldName)
								except:
									logging.warning("can't delete train %s from train list" % oldName)

								try:
									del(self.trains[oldName])
								except:
									logging.warning("can't delete train %s from train list" % oldName)
						
						try:
							# trying to find train in existing list
							tr = self.trains[name]
						except:
							# not there - create a new one")
							tr = Train(name)
							self.trains[name] = tr
							self.activeTrain.AddTrain(tr)
							
						tr.AddToBlock(blk)
						tr.SetEast(blk.GetEast()) # train takes on the direction of the block
						if not tr.IsContiguous():
							self.PopupEvent("Train %s is non-contiguous" % tr.GetName())

						if self.IsDispatcher():
							self.CheckTrainsInBlock(block, None)
						
						if loco:
							tr.SetLoco(loco)
							
						self.activeTrains.UpdateTrain(tr.GetName())

						blk.SetTrain(tr)
						blk.EvaluateStoppingSections()
						if tr:
							tr.Draw()
						else:
							blk.DrawTrain()
							
			elif cmd == "traincomplete": # from simulator when a train reaches its terminus
				for p in parms:
					train = p["train"]

					try:
						tr = self.trains[train]
					except:
						logging.error("Unknown train name (%s) in traincomplete message" % train)
						return
						
					if self.ATCEnabled and tr.IsOnATC():
						locoid = tr.GetLoco()
						self.Request({"atc": {"action": "remove", "train": train, "loco": locoid}})
						tr.SetATC(False)
						self.activeTrains.UpdateTrain(train)
						
					if self.AREnabled and tr.IsOnAR():				
						tr.SetAR(False)
						self.Request({"ar": {"action": "remove", "train": train}})
						self.activeTrains.UpdateTrain(train)
						
					tr.Draw()
					
			elif cmd == "clock":
				if not self.IsDispatcher():
					self.timeValue = int(parms[0]["value"])
					self.DisplayTimeValue()

			elif cmd == "control":
				for p in parms:
					name = p["name"]
					value = int(p["value"])
					self.UpdateControlWidget(name, value)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("connected to railroad server with session ID %d" % self.sessionid)
				self.Request({"identify": {"SID": self.sessionid, "function": "DISPATCH" if self.settings.dispatch else "DISPLAY"}})
				self.DoRefresh()
				self.districts.OnConnect()
				self.ShowTitle()

			elif cmd == "end":
				if parms["type"] == "layout":
					if self.settings.dispatch:
						self.SendBlockDirRequests()
						self.SendOSRoutes()
						self.SendCrossoverPoints()
					self.Request({"refresh": {"SID": self.sessionid, "type": "trains"}})
					
			elif cmd == "advice":
				self.PopupAdvice(parms["msg"][0])
					
			elif cmd == "alert":
				self.PopupEvent(parms["msg"][0])
				
			elif cmd == "ar":
				trnm = parms["train"][0]
				try:
					tr = self.trains[trnm]
				except KeyError:
					logging.warning("AR train %s does not exist" % trnm)
					return
				
				action = parms["action"][0]
				tr.SetAR(action == "add")
				self.activeTrains.UpdateTrain(trnm)
				tr.Draw()
				
			elif cmd == "atc":
				trnm = parms["train"][0]
				try:
					tr = self.trains[trnm]
				except KeyError:
					logging.warning("ATC train %s does not exist" % trnm)
					return
				
				action = parms["action"][0]
				tr.SetATC(action == "add")
				self.activeTrains.UpdateTrain(trnm)
				tr.Draw()
				
			elif cmd == "atcrequest":
				trnm = parms["train"][0]
				if self.ATCEnabled:
					logging.info("atcrequest: %s" % str(parms))
					try:
						tr = self.trains[trnm]
					except KeyError:
						logging.warning("ATC train %s does not exist" % trnm)
						return
					
					action = parms["action"][0]
					
					tr.SetATC(action == "add")
					self.activeTrains.UpdateTrain(trnm)
					tr.Draw()
					
					trainid, locoid = tr.GetNameAndLoco()
					self.Request({"atc": {"action": action, "train": trainid, "loco": locoid}})
					self.menuTrain.Draw()
				
				else:
					self.PopupEvent("ATC request for %s - not enabled" % trnm)

					
			elif cmd == "atcstatus":
				action = parms["action"][0]
				if action == "reject":
					trnm = parms["train"][0]
					try:
						tr = self.trains[trnm]
					except KeyError:
						logging.warning("ATC rejected train %s does not exist" % trnm)
						return
	
					self.PopupEvent("Rejected ATC train %s - no script" % trnm)				
					tr.SetATC(False)
					self.activeTrains.UpdateTrain(trnm)
					tr.Draw()
					
				elif action in [ "complete", "remove" ]:
					trnm = parms["train"][0]
					try:
						tr = self.trains[trnm]
					except KeyError:
						logging.warning("ATC completed train %s does not exist" % trnm)
						return
	
					if action == "complete":
						self.PopupEvent("ATC train %s has completed" % trnm)	
					else:			
						self.PopupEvent("Train %s removed from ATC" % trnm)	
						
					tr.SetATC(False)
					if self.AREnabled and tr.IsOnAR():				
						tr.SetAR(False)
						self.Request({"ar": {"action": "remove", "train": trnm}})
						
					self.activeTrains.UpdateTrain(trnm)
			
					tr.Draw()

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		try:
			wx.PostEvent(self, evt)
		except RuntimeError:
			logging.info("Runtime error caught while trying to post disconnect event - not a problem if this is during shutdown")

	def Request(self, req, force=False):
		command = list(req.keys())[0]
		if self.IsDispatcher() or command in allowedCommands:
			
			if self.subscribed or force:
				if "delay" in req[command] and req[command]["delay"] > 0:
					self.delayedRequests.Append(req)
				else:
					#logging.debug(json.dumps(req))
					if command == "signal":
						print("sending %s" % json.dumps(req))
					self.rrServer.SendRequest(req)
		else:
			logging.info("disallowing command %s from non dispatcher" % command)
					
	def Get(self, cmd, parms):
		return self.rrServer.Get(cmd, parms)

	def SendBlockDirRequests(self):
		bdirs = []
		for b in self.blocks.values():
			bdirs.append({ "block": b.GetName(), "dir": "E" if b.GetEast() else "W"})
			sbw, sbe = b.GetStoppingSections()
			for sb in [sbw, sbe]:
				if sb:
					bdirs.append({ "block": sb.GetName(), "dir": "E" if b.GetEast() else "W"})
		self.Request({"blockdirs": { "data": json.dumps(bdirs)}})

	def SendOSRoutes(self):
		for b in self.blocks.values():
			if b.GetBlockType() == OVERSWITCH:
				b.SendRouteRequest()
		self.Request({"routedefs": { "data": json.dumps(self.districts.GetRouteDefinitions())}})
			
	def SendCrossoverPoints(self):
		self.Request({"crossover": {"data": ["%s:%s" % (b[0], b[1]) for b in self.districts.GetCrossoverPoints()]}})

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		self.bLoadTrains.Enable(False)
		self.bLoadLocos.Enable(False)
		self.bSaveTrains.Enable(False)
		self.bClearTrains.Enable(False)
		self.bSaveLocos.Enable(False)
		if self.IsDispatcher():
			self.cbAutoRouter.Enable(False)
			self.cbATC.Enable(False)
			self.cbAdvisor.Enable(False)
		logging.info("Server socket closed")
		self.breakerDisplay.UpdateDisplay()

		dlg = wx.MessageDialog(self, "The railroad server connection has gone down.",
			"Server Connection Error",
			wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		
		self.ShowTitle()

	def OnBSaveTrains(self, _):
		self.SaveTrains()
		
	def OnBClearTrains(self, _):
		dlg = wx.MessageDialog(self, 'This clears all train IDs.  Are you sure you want to continue?\nPress "Yes" to confirm,\nor "No" to cancel.',
				'Clear Train IDs', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		newnames = []
		for trid, tr in self.trains.items():
			oldname = trid
			newname = Train.NextName()
			tr.SetName(newname)
			self.activeTrains.RenameTrain(oldname, newname)
			newnames.append([oldname, newname])
			self.Request({"renametrain": { "oldname": oldname, "newname": newname}}) #, "oldloco": oldLoco, "newloco": locoid}})
		
		for oname, nname in newnames:
			tr = self.trains[oname]
			del(self.trains[oname])
			self.trains[nname] = tr
		
	def SaveTrains(self):
		dlg = ChooseItemDlg(self, True, True)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file = dlg.GetValue()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		trDict = {}
		for trid, tr in self.trains.items():
			if not trid.startswith("??"):
				trDict[trid] = tr.GetBlockNameList()

		with open(file, "w") as fp:
			json.dump(trDict, fp, indent=4, sort_keys=True)

	def OnBLoadTrains(self, _):
		dlg = ChooseItemDlg(self, True, False)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file = dlg.GetValue()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		with open(file, "r") as fp:
			trDict = json.load(fp)

		for tid, blist in trDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk:
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, _ = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": tid}})
					else:
						self.PopupEvent("Block %s not occupied, expecting train %s" % (bname, tid))

	def OnBSaveLocos(self, _):
		self.SaveLocos()
		
	def SaveLocos(self):
		dlg = ChooseItemDlg(self, False, True)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file = dlg.GetValue()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		locoDict = {}
		for _, tr in self.trains.items():
			loco = tr.GetLoco()
			if loco is not None and not loco.startswith("??"):
				locoDict[loco] = tr.GetBlockNameList()

		with open(file, "w") as fp:
			json.dump(locoDict, fp, indent=4, sort_keys=True)

	def OnBLoadLocos(self, _):
		dlg = ChooseItemDlg(self, False, False)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file = dlg.GetValue()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		with open(file, "r") as fp:
			locoDict = json.load(fp)

		for lid, blist in locoDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk:
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, oldLoco = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": oldName, "oldloco": oldLoco, "newloco": lid}})
					else:
						self.PopupEvent("Block %s not occupied, expecting locomotive %s" % (bname, lid))

	def OnClose(self, _):
		self.CloseProgram()
		
	def CloseProgram(self):
		killServer = False
		if self.IsDispatcher():
			dlg = ExitDlg(self)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				killServer = dlg.GetResults()

			dlg.Destroy()
			if rc != wx.ID_OK:
				return	
			
		self.events.Close()
		self.advice.Close()
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		
		if killServer:
			self.rrServer.SendRequest({"quit": {}})
			
		self.Destroy()
		logging.info("%s process ending" % ("Dispatcher" if self.IsDispatcher() else "Display"))
		

class ChooseItemDlg(wx.Dialog):
	def __init__(self, parent, trains, allowentry):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.OnCancel)
		self.trains = trains
		self.allowentry = allowentry
		if trains:
			if allowentry:
				self.SetTitle("Choose/Enter train IDs file")
			else:
				self.SetTitle("Choose train IDs file")
		else:
			if allowentry:
				self.SetTitle("Choose/Enter loco #s file")
			else:
				self.SetTitle("Choose loco #s file")
		
		self.allowentry = allowentry

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		if allowentry:
			style = wx.CB_DROPDOWN
		else:
			style = wx.CB_DROPDOWN | wx.CB_READONLY	
			
		self.GetFiles()				
		
		cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=self.files, style=style)
		self.cbItems = cb
		vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
		if not allowentry and len(self.files) > 0:
			self.cbItems.SetSelection(0)
		else:
			self.cbItems.SetSelection(wx.NOT_FOUND)
		
		vszr.AddSpacer(20)
		
		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		
		bOK = wx.Button(self, wx.ID_ANY, "OK")
		bOK.SetDefault()
		self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
		
		bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
		
		bDelete = wx.Button(self, wx.ID_ANY, "Delete")
		self.Bind(wx.EVT_BUTTON, self.OnDelete, bDelete)
		
		btnszr.Add(bOK)
		btnszr.AddSpacer(20)
		btnszr.Add(bCancel)
		btnszr.AddSpacer(20)
		btnszr.Add(bDelete)
		
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
				
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(20)
		hszr.Add(vszr)
		
		hszr.AddSpacer(20)
		
		self.SetSizer(hszr)
		self.Layout()
		self.Fit();
		
	def GetFiles(self):
		if self.trains:
			fxp = os.path.join(os.getcwd(), "data", "trains", "*.trn")
		else:
			fxp = os.path.join(os.getcwd(), "data", "locos", "*.loco")
		self.files = [os.path.splitext(os.path.split(x)[1])[0] for x in glob(fxp)]
		
	def GetValue(self):
		fn = self.cbItems.GetValue()
		if fn is None or fn == "":
			return None
		
		if self.trains:
			return os.path.join(os.getcwd(), "data", "trains", fn+".trn")
		else:
			return os.path.join(os.getcwd(), "data", "locos", fn+".loco")
		
	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)
		
	def OnBOK(self, _):
		fn = self.cbItems.GetValue()
		if fn in self.files and self.allowentry:
			dlg = wx.MessageDialog(self, "File '%s' already exists.\n Are you sure you want to over-write it?" % fn,
				"File exists", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rv = dlg.ShowModal()
			dlg.Destroy()
			if rv == wx.ID_NO:
				return

		self.EndModal(wx.ID_OK)
		
	def OnDelete(self, _):
		dlg = ChooseItemsDlg(self, self.files, self.trains)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			l = dlg.GetValue()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 

		if len(l) == 0:
			return 
				
		for fn in l:
			if self.trains:
				path = os.path.join(os.getcwd(), "data", "trains", fn+".trn")
			else:
				path = os.path.join(os.getcwd(), "data", "locos", fn+".loco")
			os.unlink(path)
			
		self.GetFiles()
		self.cbItems.SetItems(self.files)
		if not self.allowentry and len(self.files) > 0:
			self.cbItems.SetSelection(0)
		else:
			self.cbItems.SetSelection(wx.NOT_FOUND)

class ChooseItemsDlg(wx.Dialog):
	def __init__(self, parent, items, trains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.OnCancel)
		if trains:
			self.SetTitle("Choose train file(s) to delete")
		else:
			self.SetTitle("Choose loco file(s) to delete")

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=items)
		self.cbItems = cb
		vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		
		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		
		bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
		
		bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
		
		btnszr.Add(bOK)
		btnszr.AddSpacer(20)
		btnszr.Add(bCancel)
		
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
				
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(20)
		hszr.Add(vszr)
		
		hszr.AddSpacer(20)
		
		self.SetSizer(hszr)
		self.Layout()
		self.Fit();
		
	def GetValue(self):
		return self.cbItems.GetCheckedStrings()
		
	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)

class ExitDlg (wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Save Trains/Locomotives")
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		dw, dh = wx.GetDisplaySize()
		sw, sh = self.GetSize()
		px = (dw-sw)/2
		py = (dh-sh)/2
		self.SetPosition(wx.Point(int(px), int(py)))

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.bTrains = wx.Button(self, wx.ID_ANY, "Save Trains")
		self.bLocos  = wx.Button(self, wx.ID_ANY, "Save Locos")

		vsz.Add(self.bTrains, 0, wx.ALIGN_CENTER)
		vsz.AddSpacer(10)
		vsz.Add(self.bLocos, 0, wx.ALIGN_CENTER)
		vsz.AddSpacer(20)
	
		self.cbKillServer = wx.CheckBox(self, wx.ID_ANY, "Shutdown Server")
		self.cbKillServer.SetValue(self.parent.settings.precheckshutdownserver)

  # self.activesuppressyards = True
  # self.activesuppressunknown = False
  # self.activeonlyatc = False
		
		vsz.Add(self.cbKillServer, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(10)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onSaveTrains, self.bTrains)
		self.Bind(wx.EVT_BUTTON, self.onSaveLocos, self.bLocos)
		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(vsz)
		hsz.AddSpacer(10)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.bOK.SetFocus()

	def onSaveTrains(self, _):
		self.parent.SaveTrains()

	def onSaveLocos(self, _):
		self.parent.SaveLocos()
		
	def GetResults(self):
		return self.cbKillServer.GetValue()

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		self.EndModal(wx.ID_OK)

