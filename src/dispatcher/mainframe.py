#import wx
import wx.lib.newevent

import os
import json
import logging

from dispatcher.settings import Settings
from dispatcher.bitmaps import BitMaps
from dispatcher.district import Districts
from dispatcher.trackdiagram import TrackDiagram
from dispatcher.tile import loadTiles
from dispatcher.train import Train

from dispatcher.breaker import BreakerDisplay, BreakerName
from dispatcher.toaster import Toaster, TB_CENTER

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
from dispatcher.atclist import ATCListCtrl

from dispatcher.edittraindlg import EditTrainDlg

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 

allowedCommands = [ "settrain", "renametrain" ]

wildcardTrain = "train files (*.trn)|*.trn|"	 \
			"All files (*.*)|*.*"
wildcardLoco = "locomotive files (*.loco)|*.loco|"	 \
			"All files (*.*)|*.*"

class Node:
	def __init__(self, screen, bitmapName, offset):
		self.screen = screen
		self.bitmap = bitmapName
		self.offset = offset


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.toaster = None
		self.listener = None
		self.sessionid = None
		self.subscribed = False
		logging.info("Display process starting")
		self.settings = Settings()

		self.logCount = 6
		
		self.turnoutMap = {}
		self.buttonMap = {}
		self.signalMap = {}
		self.handswitchMap = {}

		self.title = "PSRY Dispatcher" if self.settings.dispatch else "PSRY Monitor"
		self.ToasterSetup()
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

		if self.settings.pages == 1:  # set up a single ultra-wide display accross 3 monitors
			dp = TrackDiagram(self, [self.diagrams[sn] for sn in screensList])
			dp.SetPosition((16, 120))
			diagramw, diagramh = dp.GetSize()
			self.panels = {self.diagrams[sn].screen : dp for sn in screensList}  # all 3 screens just point to the same diagram
			totalw = 2560*3
			centeroffset = 2560

		else:  # set up three separate screens for a single monitor
			self.panels = {}
			diagramh = 0
			for d in [self.diagrams[sn] for sn in screensList]:
				dp = TrackDiagram(self, [d])
				diagramw, diagramh = dp.GetSize()
				dp.Hide()
				dp.SetPosition((8, 120))
				self.panels[d.screen] = dp

			# add buttons to switch from screen to screen
			voffset = topSpace+diagramh+20
			b = wx.Button(self, wx.ID_ANY, "Hyde/Yard/Port", pos=(500, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(HyYdPt), b)
			b = wx.Button(self, wx.ID_ANY, "Latham/Krulish", pos=(1145, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(LaKr), b)
			b = wx.Button(self, wx.ID_ANY, "Nassau/Cliff",   pos=(1790, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(NaCl), b)
			totalw = 2560+20
			centeroffset = 0

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

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect", pos=(centeroffset+100, 15))
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", pos=(centeroffset+100, 45))
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		self.bConfig = wx.Button(self, wx.ID_ANY, "Config", pos=(centeroffset+100, 75))
		self.Bind(wx.EVT_BUTTON, self.OnConfig, self.bConfig)
		self.bConfig.Enable(False)
		
		if not self.IsDispatcher() or self.settings.hideconfigbutton:
			self.bConfig.Hide()

		self.bLoadTrains = wx.Button(self, wx.ID_ANY, "Load Trains", pos=(centeroffset+250, 25))
		self.bLoadTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBLoadTrains, self.bLoadTrains)
		self.bLoadLocos = wx.Button(self, wx.ID_ANY, "Load Locos", pos=(centeroffset+250, 65))
		self.Bind(wx.EVT_BUTTON, self.OnBLoadLocos, self.bLoadLocos)
		self.bLoadLocos.Enable(False)
		
		self.bSaveTrains = wx.Button(self, wx.ID_ANY, "Save Trains", pos=(centeroffset+350, 25))
		self.bSaveTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBSaveTrains, self.bSaveTrains)
		self.bSaveLocos = wx.Button(self, wx.ID_ANY, "Save Locos", pos=(centeroffset+350, 65))
		self.Bind(wx.EVT_BUTTON, self.OnBSaveLocos, self.bSaveLocos)
		self.bSaveLocos.Enable(False)
		
		if not self.IsDispatcher():
			self.bLoadTrains.Hide()
			self.bLoadLocos.Hide()
			self.bSaveTrains.Hide()
			self.bSaveLocos.Hide()

		self.scrn = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), pos=(centeroffset+2200, 25), style=wx.TE_READONLY)
		self.xpos = wx.TextCtrl(self, wx.ID_ANY, "", size=(40, -1), pos=(centeroffset+2300, 25), style=wx.TE_READONLY)
		self.ypos = wx.TextCtrl(self, wx.ID_ANY, "", size=(40, -1), pos=(centeroffset+2360, 25), style=wx.TE_READONLY)
		
		self.bResetScreen = wx.Button(self, wx.ID_ANY, "Reset Screen", pos=(centeroffset+2200, 75))
		self.Bind(wx.EVT_BUTTON, self.OnResetScreen, self.bResetScreen)

		self.breakerDisplay = BreakerDisplay(self, pos=(int(totalw/2-400/2), 50), size=(400, 40))
		
		if self.IsDispatcher():
			f = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
			self.lblATC = wx.StaticText(self, wx.ID_ANY, "ATC:", pos=(centeroffset+1700, 2))
			self.lblATC.SetFont(f)
			self.atcList = ATCListCtrl(self, (centeroffset+1580, 25))
			
			self.cbAutoRouter = wx.CheckBox(self, wx.ID_ANY, "Auto-Router", pos=(centeroffset+600, 25))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBAutoRouter, self.cbAutoRouter)
			self.cbAutoRouter.Enable(False)
			
		self.totalw = totalw
		self.totalh = 1080
		self.ResetScreen()
		
	def OnResetScreen(self, _):
		self.ResetScreen()
		
	def ResetScreen(self):
		self.SetMaxSize((self.totalw, self.totalh))
		self.SetSize((self.totalw, self.totalh))
		self.SetPosition((0, 0))

		wx.CallAfter(self.Initialize)

	def DefineWidgets(self, voffset):
		if not self.IsDispatcher():
			return

		self.rbNassauControl = wx.RadioBox(self, wx.ID_ANY, "Nassau", (150, voffset), wx.DefaultSize,
				["Nassau", "Dispatcher: Main", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBNassau, self.rbNassauControl)
		self.rbNassauControl.Hide()
		self.widgetMap[NaCl].append(self.rbNassauControl)

		self.rbCliffControl = wx.RadioBox(self, wx.ID_ANY, "Cliff", (1550, voffset), wx.DefaultSize,
				["Cliff", "Dispatcher: Bank/Cliveden", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBCliff, self.rbCliffControl)
		self.rbCliffControl.Hide()
		self.widgetMap[NaCl].append(self.rbCliffControl)

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

		self.cbKrulishFleet = wx.CheckBox(self, -1, "Krulish Fleeting", (2200, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBKrulishFleet, self.cbKrulishFleet)
		self.cbKrulishFleet.Hide()
		self.widgetMap[LaKr].append(self.cbKrulishFleet)
		self.KrulishFleetSignals = ["K8R", "K4R", "K2R", "K8LA", "K8LB", "K2L"]

		self.cbNassauFleet = wx.CheckBox(self, -1, "Nassau Fleeting", (300, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBNassauFleet, self.cbNassauFleet)
		self.cbNassauFleet.Hide()
		self.widgetMap[NaCl].append(self.cbNassauFleet)
		self.NassauFleetSignals = ["N18R", "N16R", "N14R",
						"N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD",
						"N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD",
						"N28L", "N26L", "N24L"]

		self.cbBankFleet = wx.CheckBox(self, -1, "Martinsville Fleeting", (900, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBBankFleet, self.cbBankFleet)
		self.cbBankFleet.Hide()
		self.widgetMap[NaCl].append(self.cbBankFleet)
		self.BankFleetSignals = ["C22R", "C24R", "C22L", "C24L"]

		self.cbClivedenFleet = wx.CheckBox(self, -1, "Cliveden Fleeting", (1400, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBClivedenFleet, self.cbClivedenFleet)
		self.cbClivedenFleet.Hide()
		self.widgetMap[NaCl].append(self.cbClivedenFleet)
		self.ClivedenFleetSignals = ["C10R", "C12R", "C10L", "C12L"]

		self.cbYardFleet = wx.CheckBox(self, -1, "Yard Fleeting", (1650, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBYardFleet, self.cbYardFleet)
		self.cbYardFleet.Hide()
		self.widgetMap[HyYdPt].append(self.cbYardFleet)

		self.cbPortFleet = wx.CheckBox(self, -1, "Port Fleeting", (1650, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBPortFleet, self.cbPortFleet)
		self.cbPortFleet.Hide()
		self.widgetMap[HyYdPt].append(self.cbPortFleet)

		self.cbCliffFleet = wx.CheckBox(self, -1, "Cliff Fleeting", (2100, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBCliffFleet, self.cbCliffFleet)
		self.cbCliffFleet.Hide()
		self.widgetMap[NaCl].append(self.cbCliffFleet)
		self.CliffFleetSignals = [ "C2RA", "C2RB", "C2RC", "C2RD", "C2L",
					"C4R", "C4LA", "C4LB", "C4LC", "C4LD",
					"C6RA", "C6RB", "C6RC", "C6RD", "C6RE", "C6RF", "C6RG", "C6RH", "C6RJ", "C6RK", "C6RL", "C6L",
					"C8R", "C8LA", "C8LB", "C8LC", "C8LD", "C8LE", "C8LF", "C8LG", "C8LH", "C8LJ", "C8LK", "C8LL" ]

		self.cbHydeFleet = wx.CheckBox(self, -1, "Hyde Fleeting", (250, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBHydeFleet, self.cbHydeFleet)
		self.cbHydeFleet.Hide()
		self.widgetMap[HyYdPt].append(self.cbHydeFleet)

		self.fleetMaps = [
			[ self.LathamFleetSignals,    self.cbLathamFleet ],
			[ self.CarltonFleetSignals,   self.cbCarltonFleet ],
			[ self.ValleyJctFleetSignals, self.cbValleyJctFleet ],
			[ self.FossFleetSignals,      self.cbFossFleet ],
			[ self.NassauFleetSignals,    self.cbNassauFleet ],
			[ self.ShoreFleetSignals,     self.cbShoreFleet ],
			[ self.HydeJctFleetSignals,   self.cbHydeJctFleet ],
			[ self.KrulishFleetSignals,   self.cbKrulishFleet ],
			[ self.BankFleetSignals,      self.cbBankFleet ],
			[ self.ClivedenFleetSignals,  self.cbClivedenFleet ],
		]

	def UpdateControlWidget(self, name, value):
		if not self.IsDispatcher():
			return
		if name == "nassau":
			self.rbNassauControl.SetSelection(value)
		elif name == "cliff":
			self.rbCliffControl.SetSelection(value)
		elif name == "yard":
			self.rbYardControl.SetSelection(value)
		elif name == "signal4":
			self.rbS4Control.SetSelection(value)
		elif name == "cliff.fleet":
			self.cbCliffFleet.SetValue(value != 0)
		elif name == "port.fleet":
			self.cbPortFleet.SetValue(value != 0)
		elif name == "hyde.fleet":
			self.cbHydeFleet.SetValue(value != 0)
		elif name == "yard.fleet":
			self.cbYardFleet.SetValue(value != 0)
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

	def OnCBAutoRouter(self, evt):
		if self.cbAutoRouter.IsChecked():
			rqStatus = "on"
		else:
			rqStatus = "off"
		self.Request({"autorouter": { "status": rqStatus}})
		
	def OnRBNassau(self, evt):
		self.Request({"control": { "name": "nassau", "value": evt.GetInt()}})

	def OnRBCliff(self, evt):
		self.Request({"control": { "name": "cliff", "value": evt.GetInt()}})

	def OnRBYard(self, evt):
		self.Request({"control": { "name": "yard", "value": evt.GetInt()}})

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
		self.Request({"control": {"name": "yard.fleet", "value": f}})

	def OnCBPortFleet(self, _):
		f = 1 if self.cbPortFleet.IsChecked() else 0
		self.Request({"control": {"name": "port.fleet", "value": f}})

	def OnCBHydeFleet(self, _):
		f = 1 if self.cbHydeFleet.IsChecked() else 0
		self.Request({"control": {"name": "hyde.fleet", "value": f}})

	def FleetCheckBoxes(self, signm):
		if not self.IsDispatcher():
			return
		for siglist, checkbox in self.fleetMaps:
			if signm in siglist:
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

		self.districts.Initialize()

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
		self.ticker.Start(1000)

		print("finished initialize")

	def AddSignalLever(self, slname, district):
		self.signalLeverMap[slname] = district

	def GetSignalLeverDistrict(self, slname):
		if slname not in self.signalLeverMap:
			return None

		return self.signalLeverMap[slname]

	def IsDispatcher(self):
		return self.settings.dispatch

	def resolveObjects(self):
		for bknm, bk in self.blocks.items():
			sgWest, sgEast = bk.GetSignals()
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
			bk.SetSignals((sgWest, sgEast))

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
		if bname not in self.pendingFleets:
			return

		sig = self.pendingFleets[bname]
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
		self.ClearExpiredButtons()
		self.breakerDisplay.ticker()

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

	def ProcessClick(self, screen, pos):
		logging.debug("click %s %d, %d" % (screen, pos[0], pos[1]))
		try:
			to = self.turnoutMap[(screen, pos)]
		except KeyError:
			to = None

		if to:
			if to.IsDisabled():
				return

			to.GetDistrict().PerformTurnoutAction(to)
			return

		try:
			btn = self.buttonMap[(screen, pos)]
		except KeyError:
			btn = None

		if btn:
			btn.GetDistrict().PerformButtonAction(btn)
			return

		try:
			sig = self.signalMap[(screen, pos)]
		except KeyError:
			sig = None

		if sig:
			if sig.IsDisabled():
				return

			sig.GetDistrict().PerformSignalAction(sig)

		try:
			hs = self.handswitchMap[(screen, pos)]
		except KeyError:
			hs = None

		if hs:
			if hs.IsDisabled():
				return
			
			hs.GetDistrict().PerformHandSwitchAction(hs)

		try:
			ln = self.blockMap[(screen, pos[1])]
		except KeyError:
			ln = None

		if ln:
			for col, blk in ln:
				if col <= pos[0] <= col+3:
					break
			else:
				blk = None

			if blk:
				if blk.IsOccupied():
					tr = blk.GetTrain()
					oldName, oldLoco = tr.GetNameAndLoco()
					oldATC = tr.IsOnATC() if self.IsDispatcher() else None
					dlg = EditTrainDlg(self, tr, self.IsDispatcher())
					rc = dlg.ShowModal()
					if rc == wx.ID_OK:
						trainid, locoid, atc = dlg.GetResults()
					dlg.Destroy()
					if rc != wx.ID_OK:
						return

					self.Request({"renametrain": { "oldname": oldName, "newname": trainid, "oldloco": oldLoco, "newloco": locoid, "atc": atc}})
					if self.IsDispatcher() and atc != oldATC:
						tr.SetATC(atc)
						if atc:
							self.atcList.AddTrain(tr)
							self.Request({"atc": {"action": "add", "train": trainid, "loco": locoid}})
						else:
							self.atcList.DelTrain(tr)
							self.Request({"atc": {"action": "delete", "train": trainid, "loco": locoid}})					

					tr.Draw()

	def DrawTile(self, screen, pos, bmp):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawTile(pos[0], pos[1], offset, bmp)

	def DrawText(self, screen, pos, text):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawText(pos[0], pos[1], offset, text)

	def ClearText(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearText(pos[0], pos[1], offset)

	def DrawTrain(self, screen, pos, trainID, locoID, stopRelay, atc):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawTrain(pos[0], pos[1], offset, trainID, locoID, stopRelay, atc)

	def ClearTrain(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearTrain(pos[0], pos[1], offset)

	def SwapToScreen(self, screen):
		if screen not in screensList:
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
				print("Unknown screen: %d in widgeMap" % scr)
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
		name, loco = tr.GetNameAndLoco()
		self.trains[name] = tr
		return tr

	def ToasterSetup(self):
		self.toaster = Toaster()
		self.toaster.SetPositionByCorner(TB_CENTER)
		self.toaster.SetFont(wx.Font(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial")))
		self.toaster.SetBackgroundColour(wx.Colour(255, 179, 154))
		self.toaster.SetTextColour(wx.Colour(0, 0, 0))

	def Popup(self, message):
		self.toaster.Append(message)

	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			self.bConfig.Enable(False)
			self.bLoadTrains.Enable(False)
			self.bLoadLocos.Enable(False)
			self.bSaveTrains.Enable(False)
			self.bSaveLocos.Enable(False)
			if self.IsDispatcher():
				self.cbAutoRouter.Enable(False)
			
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
			self.bConfig.Enable(True)
			self.bLoadTrains.Enable(True)
			self.bLoadLocos.Enable(True)
			self.bSaveTrains.Enable(True)
			self.bSaveLocos.Enable(True)
			if self.IsDispatcher():
				self.cbAutoRouter.Enable(True)

		self.breakerDisplay.UpdateDisplay()
		self.ShowTitle()

	def OnRefresh(self, _):
		self.rrServer.SendRequest({"refresh": {"SID": self.sessionid}})
		
	def OnConfig(self, _):		
		self.rrServer.SendRequest({"refresh": {"type": "subblocks", "SID": self.sessionid}})

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
			logging.info("Dispatch: %s: %s" % (cmd, parms))
			# print("Incoming socket message: %s: %s" % (cmd, parms), flush=True)
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					to = self.turnouts[turnout]
					try:
						to = self.turnouts[turnout]
					except KeyError:
						to = None

					if to is not None and state != to.GetStatus():
						district = to.GetDistrict()
						st = REVERSE if state == "R" else NORMAL
						district.DoTurnoutAction(to, st)

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
					sigName = p["name"]
					aspect = p["aspect"]
					try:
						sig = self.signals[sigName]
					except:
						sig = None

					if sig is not None and aspect != sig.GetAspect():
						district = sig.GetDistrict()
						district.DoSignalAction(sig, aspect)

			elif cmd == "siglever":
				if self.IsDispatcher():
					for p in parms:
						signame = p["name"]
						state = p["state"]

						district = self.GetSignalLeverDistrict(signame)
						if district is None:
							print("unable to find district for signal lever %s" % signame)
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
					logging.debug("Set Breaker %s to %s" % (name, "TRIPPED" if val != 0 else "CLEAR"))
					if val == 0:
						self.Popup("Breaker: %s" % BreakerName(name))
						self.breakerDisplay.AddBreaker(name)
					else:
						self.breakerDisplay.DelBreaker(name)

					if name in self.indicators:
						ind = self.indicators[name]
						if val != ind.GetValue():
							ind.SetValue(val)

			elif cmd == "settrain":
				for p in parms:
					block = p["block"]
					name = p["name"]
					loco = p["loco"]
					atc = p["atc"]
					print(str(parms))

					try:
						blk = self.blocks[block]
					except:
						logging.warning("unable to identify block (%s)" % block)
						blk = None

					if blk:
						print("has block")
						tr = blk.GetTrain()
						if name is None:
							if tr:
								tr.RemoveFromBlock(blk)

							delList = []
							for trid, tr in self.trains.items():
								if tr.IsInBlock(blk):
									tr.RemoveFromBlock(blk)
									if tr.IsInNoBlocks():
										delList.append(trid)

							for trid in delList:
								try:
									del(self.trains[trid])
									self.atcList.DelTrainByName(trid)
								except:
									logging.warning("can't delete train %s from train list" % trid)

							return

						if not blk.IsOccupied():
							logging.warning("Set train for block %s, but that block is unoccupied" % block)
							return

						if tr:
							oldName = tr.GetName()
							print("block has train %s"  % oldName)
							if oldName and oldName != name:
								if name in self.trains:
									# merge the two trains under the new "name"
									try:
										bl = self.trains[oldName].GetBlockList()
									except:
										bl = {}
									for blk in bl.values():
										self.trains[name].AddToBlock(blk)
								else:
									tr.SetName(name)
									tr.SetATC(atc)
									self.trains[name] = tr
									if tr.IsOnATC():
										self.atcList.UpdateTrainName(tr, oldName)

								try:
									del(self.trains[oldName])
									self.atcList.DelTrainByName(oldName)
								except:
									logging.warning("can't delete train %s from train list" % oldName)
						
						try:
							print("trying to find train in existing list")
							tr = self.trains[name]
						except:
							print("nopt - createing a new one")
							tr = Train(name)
							self.trains[name] = tr
							
						print("set ATC to %s" % str(atc))
						tr.SetATC(atc)
						tr.AddToBlock(blk)
						if loco:
							tr.SetLoco(loco)

						self.atcList.RefreshTrain(tr)

						blk.SetTrain(tr)
						blk.EvaluateStoppingSections()
						if tr:
							tr.Draw()
						else:
							blk.DrawTrain()

			elif cmd == "control":
				for p in parms:
					name = p["name"]
					value = int(p["value"])
					self.UpdateControlWidget(name, value)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("connected to railroad server with session ID %d" % self.sessionid)
				self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "DISPATCH" if self.settings.dispatch else "DISPLAY"}})
				self.districts.OnConnect()
				self.ShowTitle()

			elif cmd == "end":
				if parms["type"] == "layout":
					if self.settings.dispatch:
						self.SendBlockDirRequests()
						self.SendOSRoutes()
					self.rrServer.SendRequest({"refresh": {"SID": self.sessionid, "type": "trains"}})
				elif parms["type"] == "trains":
					pass
				
			elif cmd == "subblocks":
				# parms contains subblocks information
				if self.settings.dispatch:
					self.districts.GenerateLayoutInformation(parms)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def Request(self, req):
		command = list(req.keys())[0]
		if self.settings.dispatch or command in allowedCommands:
			if self.subscribed:
				logging.debug(json.dumps(req))
				# print("Outgoing HTTP request: %s" % json.dumps(req))
				self.rrServer.SendRequest(req)

	def SendBlockDirRequests(self):
		for b in self.blocks.values():
			self.Request({"blockdir": { "block": b.GetName(), "dir": "E" if b.GetEast() else "W"}})
			sbw, sbe = b.GetStoppingSections()
			for sb in [sbw, sbe]:
				if sb:
					self.Request({"blockdir": { "block": sb.GetName(), "dir": "E" if b.GetEast() else "W"}})

	def SendOSRoutes(self):
		for b in self.blocks.values():
			if b.GetBlockType() == OVERSWITCH:
				b.SendRouteRequest()
		self.districts.SendRouteDefinitions()

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		self.bConfig.Enable(False)
		self.bLoadTrains.Enable(False)
		self.bLoadLocos.Enable(False)
		self.bSaveTrains.Enable(False)
		self.bSaveLocos.Enable(False)
		if self.IsDispatcher():
			self.cbAutoRouter.Enable(False)
		logging.info("Server socket closed")
		self.breakerDisplay.UpdateDisplay()
		self.ShowTitle()

	def OnBSaveTrains(self, _):
		dlg = wx.FileDialog(self, message="Save Trains", defaultDir=self.settings.traindir,
			defaultFile="", wildcard=wildcardTrain, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False

		path = dlg.GetPath()
		dlg.Destroy()

		trDict = {}
		for trid, tr in self.trains.items():
			if not trid.startswith("??"):
				trDict[trid] = tr.GetBlockNameList()
		print(path)
		with open(path, "w") as fp:
			json.dump(trDict, fp, indent=4, sort_keys=True)

		self.settings.SetTrainDir(os.path.split(path)[0])
		self.settings.save()

	def OnBLoadTrains(self, _):
		dlg = wx.FileDialog(self, message="Load Trains", defaultDir=self.settings.traindir,
			defaultFile="", wildcard=wildcardTrain, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_NO_FOLLOW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False

		path = dlg.GetPath()
		dlg.Destroy()

		with open(path, "r") as fp:
			trDict = json.load(fp)

		self.settings.SetTrainDir(os.path.split(path)[0])
		self.settings.save()

		for tid, blist in trDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk:
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, oldLoco = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": tid}})
					else:
						print("block %s not occupied or not known - ignoring" % bname)

	def OnBSaveLocos(self, _):
		dlg = wx.FileDialog(self, message="Save Locomotives", defaultDir=self.settings.locodir,
			defaultFile="", wildcard=wildcardLoco, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False

		path = dlg.GetPath()
		dlg.Destroy()

		locoDict = {}
		for trid, tr in self.trains.items():
			loco = tr.GetLoco()
			if loco is not None and not loco.startswith("??"):
				locoDict[loco] = tr.GetBlockNameList()
		print(path)
		with open(path, "w") as fp:
			json.dump(locoDict, fp, indent=4, sort_keys=True)

		self.settings.SetLocoDir(os.path.split(path)[0])
		self.settings.save()

	def OnBLoadLocos(self, _):
		dlg = wx.FileDialog(self, message="Load Locomotives", defaultDir=self.settings.locodir,
			defaultFile="", wildcard=wildcardLoco, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_NO_FOLLOW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False

		path = dlg.GetPath()
		dlg.Destroy()

		with open(path, "r") as fp:
			locoDict = json.load(fp)

		self.settings.SetLocoDir(os.path.split(path)[0])
		self.settings.save()

		for lid, blist in locoDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk:
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, oldLoco = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": oldName, "oldloco": oldLoco, "newloco": lid}})
					else:
						print("block %s not occupied or not known - ignoring" % bname)

	def OnClose(self, _):
		self.KillWindow()
		
	def KillWindow(self):
		self.toaster.Close()
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		self.Destroy()
		logging.info("Display process ending")

