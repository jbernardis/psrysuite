import os
import sys
import wx

from wx.lib import newevent
from serial import SerialException
import json
import logging
from dispatcher.breaker import BreakerName
logging.basicConfig(filename=os.path.join("logs", "tracker.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

ofp = open("tracker.out", "w")
efp = open("tracker.err", "w")

sys.stdout = ofp
sys.stderr = efp

from tracker.rrserver import RRServer
from tracker.trainroster import TrainRoster
from tracker.locomotives import Locomotives
from tracker.engineers import Engineers
from tracker.activetrain import ActiveTrain
from tracker.activetrainlist import ActiveTrainList, FWD_128, FWD_28, REV_128, REV_28, STOP 
from tracker.activetrainlistctrl import ActiveTrainListCtrl
from tracker.activetrainlistdlg import ActiveTrainListDlg
from tracker.completedtrainlist import CompletedTrainList
from tracker.manageengineers import ManageEngineersDlg
from tracker.manageschedule import ManageScheduleDlg
from tracker.assignlocos import AssignLocosDlg
from tracker.detailsdlg import DetailsDlg
from tracker.aboutdlg import AboutDlg
from tracker.settings import Settings
from tracker.reports import Report
from tracker.completedtrains import CompletedTrains
from tracker.listener import Listener
from tracker.backup import saveData, restoreData
from tracker.dccsniffer import DCCSniffer
from tracker.engqueuedlg import EngQueueDlg

# class dummyDCCEvt:
# 	def __init__(self, loco, spd):
# 		self.dcc = {"instr": "F", "param": spd, "loco": loco}
# self.onDCCMessage(dummyDCCEvt("2216", "10"))
# self.onDCCMessage(dummyDCCEvt("2216", "0"))

DEVELOPMODE = True
VERSIONDATE = "2-February-2023"

BTNSZ = (120, 46)

MENU_FILE_ABOUT = 120
MENU_FILE_BACKUP = 113
MENU_FILE_RESTORE = 114
MENU_FILE_EXIT = 199
MENU_MANAGE_ENGINEERS = 201
MENU_MANAGE_ASSIGN_LOCOS = 203
MENU_MANAGE_SCHEDULE = 205
MENU_MANAGE_RESET = 299
MENU_REPORT_OP_WORKSHEET = 301
MENU_REPORT_TRAIN_CARDS = 302
MENU_REPORT_LOCOS = 303
MENU_REPORT_STATUS = 304
MENU_DISPATCH_CONNECT = 401
MENU_DISPATCH_DISCONNECT = 402
MENU_DCC_CONNECT = 501
MENU_DCC_DISCONNECT = 502
MENU_VIEW_ENG_QUEUE = 601
MENU_VIEW_ACTIVE_TRAINS = 602
MENU_VIEW_LEGEND = 603
MENU_VIEW_SORT = 610
MENU_SORT_TID = 650
MENU_SORT_TIME = 651
MENU_SORT_GROUP = 652
MENU_SORT_ASCENDING = 653

MAX_STEPS = 9

wildcard = "JSON file (*.json)|*.json|"	 \
				"All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
				"All files (*.*)|*.*"

(DeliveryEvent, EVT_DELIVERY) = newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = newevent.NewEvent() 
(ConnectEvent, EVT_CONNECT) = newevent.NewEvent() 

(DCCMessageEvent, EVT_DCCMESSAGE) = newevent.NewEvent()  
(DCCClosedEvent,  EVT_DCCCLOSED)  = newevent.NewEvent()  

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleSched = None
		self.titleConnected = False
		self.titleDCC = False

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "tracker.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.CreateStatusBar()
		menuBar = wx.MenuBar()
		
		self.connection = None
		self.dcc = None

		self.menuFile = wx.Menu()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_BACKUP, "Backup", helpString="Backup data files to a ZIP file")
		self.menuFile.Append(i)
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_RESTORE, "Restore", helpString="Restore data files from a ZIP file")
		self.menuFile.Append(i)
		
		self.menuFile.AppendSeparator()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_ABOUT, "About", helpString="About")
		self.menuFile.Append(i)
		
		self.menuFile.AppendSeparator()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_EXIT, "Exit", helpString="Exit Program")
		self.menuFile.Append(i)
		
		self.menuSort = wx.Menu()
		
		i = wx.MenuItem(self.menuSort, MENU_SORT_TID, "Train ID", helpString="Sort Based on Train ID", kind=wx.ITEM_RADIO)
		self.menuSort.Append(i)
		
		i = wx.MenuItem(self.menuSort, MENU_SORT_TIME, "Time", helpString="Sort Based on Train running time", kind=wx.ITEM_RADIO)
		self.menuSort.Append(i)
		i.Check()
		
		self.menuSort.AppendSeparator()
				
		i = wx.MenuItem(self.menuSort, MENU_SORT_GROUP, "Group by Direction", helpString="Group East and West trains together", kind=wx.ITEM_CHECK)
		self.menuSort.Append(i)
		i.Check(False)
		
		self.menuSort.AppendSeparator()
				
		i = wx.MenuItem(self.menuSort, MENU_SORT_ASCENDING, "Ascending", helpString="Sort ascending", kind=wx.ITEM_CHECK)
		self.menuSort.Append(i)
		i.Check(False)

		self.menuView = wx.Menu()
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_SORT, "Sort Active Trains", helpString="Change sorting parameters", subMenu=self.menuSort)
		self.menuView.Append(i)
		
		self.menuView.AppendSeparator()
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_ENG_QUEUE, "Engineer Queue", helpString="Display Engineer Queue")
		self.menuView.Append(i)
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_ACTIVE_TRAINS, "Active Train List", helpString="Display Active Train List")
		self.menuView.Append(i)

		i = wx.MenuItem(self.menuView, MENU_VIEW_LEGEND, "Legend", helpString="Display a legend for icons")
		self.menuView.Append(i)
		
		self.menuManage = wx.Menu()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ENGINEERS, "Engineers", helpString="Manage the content and ordering of active engineers list")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_SCHEDULE, "Train Schedule", helpString="Add/remove/reorder trains to/from the schedule and extra train list")
		self.menuManage.Append(i)
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ASSIGN_LOCOS, "Assign Locomotives", helpString="Assign locomotives to trains")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_RESET, "Reset Session", helpString="Reset Operating Session")
		self.menuManage.Append(i)
		
		self.menuReports = wx.Menu()
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_OP_WORKSHEET, "Operating Worksheet", helpString="Print an Operating Worksheet")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_TRAIN_CARDS, "Train Cards", helpString="Print Train Cards")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_LOCOS, "Locomotives", helpString="Print Locomotive Roster")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_STATUS, "Train Status", helpString="List of all active and completed trains")
		self.menuReports.Append(i)
		
		self.menuDispatch = wx.Menu()
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_CONNECT, "Connect", helpString="Connect to dispatcher")
		self.menuDispatch.Append(i)
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_DISCONNECT, "Disconnect", helpString="Disconnect from dispatcher")
		self.menuDispatch.Append(i)
		self.menuDispatch.Enable(MENU_DISPATCH_DISCONNECT, False)
		
		self.menuDCC = wx.Menu()
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_CONNECT, "Connect", helpString="Connect to DCC Sniffer")
		self.menuDCC.Append(i)
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_DISCONNECT, "Disconnect", helpString="Disconnect from DCC Sniffer")
		self.menuDCC.Append(i)
		self.menuDCC.Enable(MENU_DCC_DISCONNECT, False)

		menuBar.Append(self.menuFile, "File")
		menuBar.Append(self.menuView, "View")
		menuBar.Append(self.menuManage, "Manage")
		menuBar.Append(self.menuReports, "Reports")
		menuBar.Append(self.menuDispatch, "Dispatch")
		menuBar.Append(self.menuDCC, "DCC")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainTrackerPanel(self)
		sizer.Add(self.panel)
		
		self.Bind(wx.EVT_MENU, self.panel.onAbout, id=MENU_FILE_ABOUT)
		self.Bind(wx.EVT_MENU, self.panel.onSaveData, id=MENU_FILE_BACKUP)
		self.Bind(wx.EVT_MENU, self.panel.onRestoreData, id=MENU_FILE_RESTORE)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		
		self.Bind(wx.EVT_MENU, self.panel.onViewEngQueue, id=MENU_VIEW_ENG_QUEUE)
		self.Bind(wx.EVT_MENU, self.panel.onViewActiveTrains, id=MENU_VIEW_ACTIVE_TRAINS)
		self.Bind(wx.EVT_MENU, self.panel.onViewLegend, id=MENU_VIEW_LEGEND)
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_TID)	
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_TIME)		
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_GROUP)		
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_ASCENDING)
		
		self.Bind(wx.EVT_MENU, self.panel.onManageEngineers, id=MENU_MANAGE_ENGINEERS)
		self.Bind(wx.EVT_MENU, self.panel.onManageSchedule, id=MENU_MANAGE_SCHEDULE)
		self.Bind(wx.EVT_MENU, self.panel.onAssignLocos, id=MENU_MANAGE_ASSIGN_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onResetSession, id=MENU_MANAGE_RESET)
		
		self.Bind(wx.EVT_MENU, self.panel.onReportOpWorksheet, id=MENU_REPORT_OP_WORKSHEET)
		self.Bind(wx.EVT_MENU, self.panel.onReportTrainCards, id=MENU_REPORT_TRAIN_CARDS)
		self.Bind(wx.EVT_MENU, self.panel.onReportLocos, id=MENU_REPORT_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onReportStatus, id=MENU_REPORT_STATUS)
		
		self.Bind(wx.EVT_MENU, self.panel.connectToDispatch, id=MENU_DISPATCH_CONNECT)
		self.Bind(wx.EVT_MENU, self.panel.disconnectFromDispatch, id=MENU_DISPATCH_DISCONNECT)
		
		self.Bind(wx.EVT_MENU, self.panel.onConnectSnifferPressed, id=MENU_DCC_CONNECT)
		self.Bind(wx.EVT_MENU, self.panel.onDisconnectSnifferPressed, id=MENU_DCC_DISCONNECT)
		
		sizer.AddSpacer(100)
		self.SetSizer(sizer)
		self.Layout()
		self.Fit()
		
		self.enableForConnection(False)
		
	def setTitle(self, schedule=None, connected=None, dcc=None):
		if schedule is not None:
			self.titleSched = schedule
			
		if connected is not None:
			self.titleConnected = connected
			
		if dcc is not None:
			self.titleDCC = dcc
			
		title = "Train Tracker"
		if self.titleSched is not None:
			title += ("   Schedule: %s" % schedule)
			
		if self.titleConnected:
			title += "    Connected to server"
		else:
			title += "    Not Connected to server"
			
		if self.titleDCC:
			title += "    Connected to DCC"
		else:
			title += "    Not Connected to DCC"
			
		self.SetTitle(title)
		
	def disableReports(self):
		for r in [ MENU_REPORT_OP_WORKSHEET, MENU_REPORT_TRAIN_CARDS, MENU_REPORT_LOCOS, MENU_REPORT_STATUS ]:
			self.menuReports.Enable(r, False)
			
	def enableForConnection(self, connected):
		self.menuDispatch.Enable(MENU_DISPATCH_DISCONNECT, connected)
		self.menuManage.Enable(MENU_MANAGE_SCHEDULE, connected)
		self.menuManage.Enable(MENU_MANAGE_ASSIGN_LOCOS, connected)
		
		self.menuDispatch.Enable(MENU_DISPATCH_CONNECT, not connected)
	
	def onClose(self, _):
		self.panel.onClose(None)
		self.Destroy()

class TrainTrackerPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.SetBackgroundColour(wx.Colour(250, 250, 250))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.parent = parent
		
		self.parent.setTitle()
		self.setConnected(False)
		self.completedTrains = CompletedTrains()
		self.breakers = {}
		
		self.sessionid = None
		
		self.listener = None
		self.sniffer = None
		self.dlgEngQueue = None
		self.dlgActiveTrains = None

		self.trainRoster = None
		self.pendingTrains = []
		self.selectedEngineers = [] 
		self.idleEngineers = []
		self.speeds = {}
		self.schedName = None
		self.trainSchedule = None
		
		self.dlgSplash = None
		self.splashTimer = 0;

		self.dlgLegend = None

		self.atl = ActiveTrainList()
		self.atl.setSortKey("time")

		labelFontBold = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		textFont = wx.Font(wx.Font(9, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(9, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.AddSpacer(20)

		boxTrain = wx.StaticBox(self, wx.ID_ANY, "Train")
		topBorder = boxTrain.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxTrain, wx.ID_ANY, "", size=(240, -1)))
		
		self.chTrain = wx.Choice(boxTrain, wx.ID_ANY, choices=self.pendingTrains, size=(120, -1))
		self.chTrain.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.chTrain)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Scheduled: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chTrain)
		
		self.bSkip = wx.Button(boxTrain, wx.ID_ANY, "-", size=(30, -1))
		self.Bind(wx.EVT_BUTTON, self.bSkipPressed, self.bSkip)
		self.bSkip.SetToolTip("Remove train from schedule")
		sz.AddSpacer(5)
		sz.Add(self.bSkip)
		bsizer.Add(sz)

		bsizer.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbExtra = wx.CheckBox(boxTrain, wx.ID_ANY, "Run Extra")
		self.Bind(wx.EVT_CHECKBOX, self.onCbExtra, self.cbExtra)
		sz.AddSpacer(100)
		sz.Add(self.cbExtra)
		self.cbExtra.Enable(False)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)

		self.chExtra = wx.Choice(boxTrain, wx.ID_ANY, choices=[], size=(120, -1))
		self.chExtra.Enable(False)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Extra: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chExtra)
		bsizer.Add(sz)
		bsizer.AddSpacer(20)
		self.Bind(wx.EVT_CHOICE, self.onChExtra, self.chExtra)
		
		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxTrain.SetSizer(bhsizer)
		
		vsizerl.Add(boxTrain)
		
		vsizerl.AddSpacer(20)

		boxEng = wx.StaticBox(self, wx.ID_ANY, "Engineer")
		topBorder = boxEng.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxEng, wx.ID_ANY, "", size=(240, -1)))

		self.chEngineer = wx.Choice(boxEng, wx.ID_ANY, choices=self.idleEngineers, size=(120, -1))
		self.chEngineer.SetSelection(wx.NOT_FOUND)
		self.selectedEngineer = None
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.chEngineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxEng, wx.ID_ANY, "Engineer: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chEngineer)
		
		self.bRmEng = wx.Button(boxEng, wx.ID_ANY, "-", size=(30, -1))
		self.Bind(wx.EVT_BUTTON, self.onRmEngineer, self.bRmEng)
		self.bRmEng.SetToolTip("Remove engineer from active list")
		sz.AddSpacer(5)
		sz.Add(self.bRmEng)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbATC = wx.CheckBox(boxEng, wx.ID_ANY, "ATC")
		self.Bind(wx.EVT_CHECKBOX, self.onCbATC, self.cbATC)
		sz.AddSpacer(100)
		sz.Add(self.cbATC)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(20)

		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxEng.SetSizer(bhsizer)
		
		vsizerl.Add(boxEng)

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bAssign = wx.Button(self, wx.ID_ANY, "Assign\nTrain/Engineer", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bAssignPressed, self.bAssign)
		btnsizer.Add(self.bAssign)
		self.bAssign.Enable(len(self.idleEngineers) != 0 and len(self.pendingTrains) != 0)

		vsizerl.AddSpacer(20)
		vsizerl.Add(btnsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

		vsizerr = wx.BoxSizer(wx.VERTICAL)
		vsizerr.AddSpacer(10)
		
		self.teBreaker = wx.TextCtrl(self, wx.ID_ANY, "", size=(240, -1), style=wx.TE_CENTER)
		self.ShowBreakers()
		breakerFont = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		self.teBreaker.SetFont(breakerFont)
		self.teBreaker.SetForegroundColour(wx.Colour(255, 255, 255))
		
		self.pngPSRY = wx.Image(os.path.join(os.getcwd(), "images", "PSLogo_large.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(self.pngPSRY, wx.BLUE)
		self.pngPSRY.SetMask(mask)
		b = wx.StaticBitmap(self, wx.ID_ANY, self.pngPSRY)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBreaker, 1, wx.TOP, 40)
		hsz.AddSpacer(40)
		hsz.Add(b)
		
		vsizerr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizerr.AddSpacer(10)

		boxDetails = wx.StaticBox(self, wx.ID_ANY, "Train Details")
		topBorder = boxDetails.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)

		self.stDescription = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(400, -1))
		self.stDescription.SetFont(labelFontBold)
		bsizer.Add(self.stDescription)
		bsizer.AddSpacer(5)
		self.stStepTowers = []
		self.stStepLocs = []
		self.stStepStops = []
		for i in range(MAX_STEPS):
			tower = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(100, -1))
			loc = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(60, -1))
			stop = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(300, -1))
			if i % 2 == 0:
				tower.SetBackgroundColour(wx.Colour(225, 255, 240))
				loc.SetBackgroundColour(wx.Colour(225, 255, 240))
				stop.SetBackgroundColour(wx.Colour(225, 255, 240))
			else:
				tower.SetBackgroundColour(wx.Colour(138, 255, 197))
				loc.SetBackgroundColour(wx.Colour(138, 255, 197))
				stop.SetBackgroundColour(wx.Colour(138, 255, 197))
			tower.SetFont(textFontBold)
			loc.SetFont(textFont)
			stop.SetFont(textFont)
			sz = wx.BoxSizer(wx.HORIZONTAL)
			sz.Add(tower)
			sz.Add(loc)
			sz.Add(stop)
			self.stStepTowers.append(tower)
			self.stStepLocs.append(loc)
			self.stStepStops.append(stop)
			bsizer.Add(sz)
		
		self.stLocoInfo = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(600, -1))
		self.stLocoInfo.SetFont(labelFontBold)
		bsizer.AddSpacer(5)
		bsizer.Add(self.stLocoInfo)
		bsizer.AddSpacer(5)
		
		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxDetails.SetSizer(bhsizer)
		
		vsizerr.Add(boxDetails)
		vsizerr.AddSpacer(5)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizerl)
		hsizer.AddSpacer(40)
		hsizer.Add(vsizerr)
		hsizer.AddSpacer(20)
		
		wsizerl = wx.BoxSizer(wx.VERTICAL)
		wsizerl.Add(hsizer)
		wsizerl.AddSpacer(5)
		st = wx.StaticText(self, wx.ID_ANY, "Active Trains:")
		st.SetFont(labelFontBold)
		wsizerl.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.lcActiveTrains = ActiveTrainListCtrl(self)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.lcActiveTrains)
		sz.AddSpacer(20)
		
		wsizerl.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		wsizerl.AddSpacer(20)
		
		wsizerr = wx.BoxSizer(wx.VERTICAL)
		
		wsizerr.AddSpacer(50)

		st = wx.StaticText(self, wx.ID_ANY, "Completed Trains:")
		st.SetFont(labelFontBold)
		wsizerr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.completedTrainList = CompletedTrainList(self, self.completedTrains)
		wsizerr.Add(self.completedTrainList)
		
		wsizer = wx.BoxSizer(wx.HORIZONTAL)
		wsizer.Add(wsizerl)
		wsizer.Add(wsizerr)
		wsizer.AddSpacer(10)

		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()
		
		# events from rr server
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)
		self.Bind(EVT_CONNECT, self.onConnectEvent)

		# events from DCC tracker
		self.Bind(EVT_DCCMESSAGE, self.onDCCMessage)
		self.Bind(EVT_DCCCLOSED,  self.onDCCClosed)
		
		wx.CallAfter(self.initialize)
		
	def initialize(self):
		self.splash()
		
		self.settings = Settings(self)
		
		self.completedTrains.clear()
		self.completedTrainList.update()

		self.loadEngineerFile(os.path.join(os.getcwd(), "data", "engineers.txt"))
		
		self.report = Report(self, self.settings)
		if not self.report.Initialized():
			self.parent.disableReports()

		self.setExtraTrains()
		
		self.atl.addDisplay("main", self.lcActiveTrains)
		
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)
		self.ticker.Start(1000)
		logging.info("Tracker initialization completed")
		
	def ShowBreakers(self):
		self.tripped = [name for name in self.breakers if self.breakers[name] == 0]
		if len(self.tripped) == 0:
			self.breakerx = 0
		
	def onTicker(self, _):
		if self.splashTimer > 0:
			self.splashTimer -= 1
			if self.splashTimer == 0:
				try:
					self.dlgSplash.Destroy()
				except:
					pass

		if not self.connected:
			self.teBreaker.SetBackgroundColour(wx.Colour(128, 128, 128))
			self.teBreaker.SetValue("Not Connected")
			
		elif len(self.tripped) == 0:
			self.teBreaker.SetBackgroundColour(wx.Colour(10, 158, 32))
			self.teBreaker.SetValue("All OK")
			
		else:
			bn = BreakerName(self.tripped[self.breakerx])
			self.teBreaker.SetValue(bn)
			self.teBreaker.SetBackgroundColour(wx.Colour(241, 41, 47))
			self.breakerx += 1
			if self.breakerx >= len(self.tripped):
				self.breakerx = 0
							
		self.atl.ticker()
		
	def onResetSession(self, _):
		dlg = wx.MessageDialog(self, 'This will reload all data files and will delete all active trains\nAre you sure you want to proceed?\n\nPress "Yes" to proceed, or "No" to cancel.',
							'Reset Session', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		logging.info("resetting session")
		self.completedTrains.clear()
		self.completedTrainList.update()
		
		self.idleEngineers = [x for x in self.selectedEngineers]
		
		self.pendingTrains = [t for t in self.scheduledTrains]
		self.extraTrains = sorted([t for t in self.extraScheduleTrains])
		self.setTrainSchedule(preserveActive=False)
		self.setExtraTrains()

		self.updateEngQueue()
		
	def connectToDispatch(self, _):
		self.setConnected(False)
		logging.info("connecting to server")

		self.RRServer = RRServer()
		self.RRServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		self.listener.connect()
		
	def onConnectEvent(self, evt):
		self.setConnected(True)
		
	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.QueueEvent(self, evt)

	def onDisconnectEvent(self, evt):
		self.setConnected(False)
		
	def raiseDeliveryEvent(self, msg): # thread context
		jdata = json.loads(msg)
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if  cmd == "breaker":
				logging.info("breaker: %s" % parms)
				for p in parms:
					brkName = p["name"]
					brkVal = p["value"]
					self.breakers[brkName] = brkVal
				self.ShowBreakers()
				
			elif cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("connected to railroad server with session ID %d" % self.sessionid)
				self.Request({"identify": {"SID": self.sessionid, "function": "TRACKER"}})
				self.trainRoster = TrainRoster(self.RRServer)
				self.locos = Locomotives(self.RRServer)
				self.DoRefresh()
				
			elif cmd == "end":
				if parms["type"] == "layout":
					self.DoRefresh(rtype="trains")
				elif parms["type"] == "trains":
					evt = ConnectEvent()
					wx.QueueEvent(self, evt)
			
			elif cmd == "settrain":
				logging.info("settrain: %s" % parms)
				for p in parms:
					try:
						train = p["name"]
					except:
						train = None
					try:
						loco = p["loco"]
					except:
						loco = None
					try:
						block = p["block"]
					except:
						block = None
						
					if train is None or "??" in train:
						continue
						
					if block is None:
						continue

					if loco is None or "??" in loco:
						loco = ""
					
					tr = self.trainRoster.getTrain(train)					
					tr["block"] = block
					tr["loco"] = loco
					
				self.updateActiveListLocos()
								
			elif cmd == "trainsignal":
				logging.info("trainsignal: %s" % parms)
				try:
					train = parms["train"]
				except:
					train = None
				try:
					aspect = int(parms["aspect"])
				except:
					aspect = 0  # default is to stop

				tr = self.trainRoster.getTrain(train)					
				lid = tr["loco"]
				if lid is not None and "??" not in lid:
					loco = self.locos.getLoco(lid)
					if loco is not None:
						self.locos.setLimit(lid, aspect)
						self.atl.setLimit(lid, self.locos.getLimit(lid))

	def DoRefresh(self, rtype=None):
		req = {"refresh": {"SID": self.sessionid}}
		if rtype is not None:
			req["refresh"]["type"] = rtype
		self.Request(req)
		
	def Request(self, req):
		self.RRServer.SendRequest(req)
	
	def setConnected(self, flag=True):
		self.connected = flag
		logging.info("Server connection: %s" % str(flag))
		self.parent.enableForConnection(flag)
		self.parent.setTitle(connected=flag)
		
	def disconnectFromDispatch(self, _):
		self.listener.kill()
		self.setConnected(False)

	def onViewEngQueue(self, _):
		if self.dlgEngQueue is None:
			self.dlgEngQueue = EngQueueDlg(self, self.idleEngineers, self.onCloseEngQueue)
			self.dlgEngQueue.Show()
		else:
			self.dlgEngQueue.Raise()
			
	def onCloseEngQueue(self):
		if self.dlgEngQueue is None:
			return
		
		self.dlgEngQueue.Destroy()
		self.dlgEngQueue = None
		
	def updateEngQueue(self):
		if self.dlgEngQueue is None:
			return
		
		self.dlgEngQueue.updateEngQueue(self.idleEngineers)
		
	def onViewActiveTrains(self, _):
		if self.dlgActiveTrains is None:
			self.dlgActiveTrains = ActiveTrainListDlg(self, self.atl, self.onCloseActiveTrains)
			self.dlgActiveTrains.Show()
		else:
			self.dlgActiveTrains.Raise()
			
	def onCloseActiveTrains(self):
		if self.dlgActiveTrains is None:
			return
		
		self.dlgActiveTrains.Destroy()
		self.dlgActiveTrains = None

	def onViewLegend(self, _):
		if self.dlgLegend is None:
			self.dlgLegend = LegendDlg(self, self.onLegendDlgClose)
			self.dlgLegend.Show();
		else:
			self.dlgLegend.Raise()

	def onLegendDlgClose(self):
		self.dlgLegend = None
	
	def setExtraTrains(self):
		if self.trainSchedule is None:
			self.extraTrains = []
		else:
			self.extraTrains = [t for t in self.trainSchedule.getExtras() if not self.atl.hasTrain(t)]

		self.chExtra.SetItems(self.extraTrains)
		if len(self.extraTrains) > 0:
			self.chExtra.SetSelection(0)
			
		self.cbExtra.SetValue(False)			
		self.cbExtra.Enable(len(self.extraTrains) > 0)
		self.chExtra.Enable(False)
		
	def onCbExtra(self, _):
		self.enableExtraMode(self.cbExtra.IsChecked())
			
	def enableExtraMode(self, flag=True):
		if flag:
			self.chExtra.Enable(True)
			tx = self.chExtra.GetSelection()
			tid = self.chExtra.GetString(tx)
			self.setSelectedTrain(tid)
			self.chTrain.Enable(False)
			self.bSkip.Enable(False)
			self.bAssign.Enable(len(self.idleEngineers) > 0 or self.cbATC.IsChecked())
		else:
			self.chExtra.Enable(False)
			self.chTrain.Enable(True)
			tx = self.chTrain.GetSelection()
			tid = self.chTrain.GetString(tx)
			self.setSelectedTrain(tid)
			self.bSkip.Enable(len(self.pendingTrains) > 0)
			self.cbExtra.SetValue(False)
			if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
				self.bAssign.Enable(True)
			else:
				self.bAssign.Enable(False)
					
	def updateActiveListLocos(self):
		if self.locos is None:
			return
		
		actTrains = self.atl.getTrains()
		locos = self.locos.getLocoList()
		for tid in actTrains:
			at = self.atl.getTrainByTid(tid)
			tInfo = self.trainRoster.getTrain(tid)
			if at is not None:
				rloco = tInfo["loco"]
				if rloco not in locos:
					ndesc = ""
				else:
					ndesc = self.locos.getLoco(rloco)

				self.atl.updateTrain(tid, rloco, ndesc, tInfo["block"])

	def loadEngineerFile(self, fn, preserveActive=False):
		try:
			self.engineers = Engineers(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Engineer file %s' % fn,
					'File Not Found',
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.engineers = None
			
		if not preserveActive:
			self.idleEngineers = []
			self.updateEngQueue()
			
		self.selectedEngineers = [x for x in self.idleEngineers]
		self.chEngineer.SetItems(self.idleEngineers)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)

		self.atl.clear()

		self.cbATC.SetValue(False)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		
		if len(self.idleEngineers) > 0:
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
		else:
			self.chEngineer.SetSelection(wx.NOT_FOUND)
			self.selectedEngineer = None
				
	def setTrainSchedule(self, preserveActive=False):
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) > 0:
			self.setSelectedTrain(self.chTrain.GetString(0))

		if not preserveActive:
			engRunning = [x for x in self.atl.getEngineers() if x not in self.idleEngineers]
			self.idleEngineers += engRunning 
		self.chEngineer.SetItems(self.idleEngineers)
		if len(self.idleEngineers) > 0:
			self.chEngineer.SetSelection(0)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		self.bSkip.Enable(len(self.pendingTrains) > 0)

		if not preserveActive:
			self.atl.clear()
			
		self.cbATC.SetValue(False)
		
		if len(self.pendingTrains) > 0:
			self.chTrain.SetSelection(0)
			tid = self.chTrain.GetString(0)
		else:
			self.chTrain.SetSelection(wx.NOT_FOUND)
			tid = None
			
		self.setSelectedTrain(tid)
		
	def onCbATC(self, _):
		if self.cbATC.IsChecked():
			self.bAssign.Enable(len(self.pendingTrains) > 0 or self.cbExtra.IsChecked())
		else:
			self.bAssign.Enable(len(self.idleEngineers) > 0 and (len(self.pendingTrains) > 0 or self.cbExtra.IsChecked()))
		
	def onRmEngineer(self, _):
		dlg = wx.MessageDialog(self, "This will remove engineer '%s' from the active list.\nPress \"Yes\" to proceed, or \"No\" to cancel." % self.selectedEngineer,
							'Remove Engineer',
							wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
			
		if rc != wx.ID_YES:
			return
		
		logging.info("removing engineer: %s" % self.selectedEngineer)
		
		self.idleEngineers.remove(self.selectedEngineer)
		self.updateEngQueue()
		self.selectedEngineers.remove(self.selectedEngineer)
		self.chEngineer.SetItems(self.idleEngineers)
		if len(self.idleEngineers) == 0:
			self.chEngineer.Enable(False)
			self.bRmEng.Enable(False)
			self.bAssign.Enable(False)
		else:
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			self.bRmEng.Enable(True)
		
	def bAssignPressed(self, _):
		if self.cbExtra.IsChecked():
			tx = self.chExtra.GetSelection()
			tid = self.chExtra.GetString(tx)
			tInfo = self.trainRoster.getTrain(tid)
			runningExtra = True
		else:
			tid = self.selectedTrain
			tInfo = self.trainRoster.getTrain(self.selectedTrain)
			runningExtra = False
			
		if tInfo is None:
			return
		
		if self.cbATC.IsChecked():
			eng = "ATC"
		else:
			eng = self.selectedEngineer
			
		dlg = wx.MessageDialog(self, "This will assign engineer %s to train %s.\nPress \"Yes\" to proceed, or \"No\" to cancel." % (eng, tid),
							'Train/Engineer Assign',
							wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
			
		if rc != wx.ID_YES:
			return

		logging.info("Train %s assigned to %s" % (tid, eng))
		req = {"advice": {"msg": "Train %s assigned to %s" % (tid, eng)}}
		self.Request(req)
		
		if tInfo["loco"] is None:
			loco = ""
			ldesc = ""
			llimit = 0
		else:
			loco = tInfo["loco"]
			ldesc = self.locos.getLocoDesc(loco)
			if ldesc is None:
				ldesc = ""
			try:
				llimit = self.locos.getLimit(loco)
			except:
				llimit = 0
				
		if "block" in tInfo:
			block = tInfo["block"]
		else:
			block = ""	

		self.atl.addTrain(ActiveTrain(tid, tInfo, loco, ldesc, llimit, eng, block))

		if loco in self.speeds:
			self.atl.setThrottle(loco, self.speeds[loco][0], self.speeds[loco][1])

		if not runningExtra:		
			self.pendingTrains.remove(tid)
			self.chTrain.SetItems(self.pendingTrains)
			if len(self.pendingTrains) == 0:
				self.chTrain.Enable(False)
				self.bAssign.Enable(False)
				self.bSkip.Enable(False)
				self.showInfo(None)
				self.setSelectedTrain(None)
			else:
				self.chTrain.SetSelection(0)
				self.setSelectedTrain(self.chTrain.GetString(0))
		else:
			self.setExtraTrains()
			self.enableExtraMode(False)
		
		if not self.cbATC.IsChecked():
			self.idleEngineers.remove(self.selectedEngineer)
			self.updateEngQueue()
			self.chEngineer.SetItems(self.idleEngineers)
			if len(self.idleEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bRmEng.Enable(False)
				self.bAssign.Enable(False)
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				self.bRmEng.Enable(True)
				
		else:
			self.cbATC.SetValue(False)
			self.bAssign.Enable(len(self.pendingTrains) != 0 and len(self.idleEngineers) != 0)
		
	def reassignTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return

		engActive = self.atl.getEngineers()	
		if at.engineer != "ATC":
			eng = ["ATC"]
		else:
			eng = []	
			
		eng += sorted([x for x in self.engineers if x not in engActive])
		
		dlg = wx.SingleChoiceDialog(self, 'Choose New Engineer', 'Reassign Engineer',
				eng,
				wx.CHOICEDLG_STYLE
				)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			neng = dlg.GetStringSelection()

		dlg.Destroy()	
		
		if rc != wx.ID_OK:
			dlg.Destroy()
			return
				
		if at.engineer in self.selectedEngineers:
			if at.engineer not in self.idleEngineers:
				self.idleEngineers.append(at.engineer)
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)

		if neng in self.idleEngineers:
			self.idleEngineers.remove(neng)
			self.updateEngQueue()
			self.chEngineer.SetItems(self.idleEngineers)
			if len(self.idleEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bRmEng.Enable(False)
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				self.chEngineer.Enable(True)
				self.bRmEng.Enable(True)

		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)

		oeng = at.engineer	
		tid = at.tid	
		logging.info("Reassigning train %s from %s to %s" % (tid, oeng, neng))
		
		self.atl.setNewEngineer(tid, neng)
		
	def onAbout(self, _):
		dlg = AboutDlg(self, self.pngPSRY, VERSIONDATE)
		dlg.ShowModal()
		dlg.Destroy()
		
	def splash(self):
		self.dlgSplash = AboutDlg(self, self.pngPSRY, VERSIONDATE)
		self.dlgSplash.CenterOnScreen()
		self.dlgSplash.Show()
		self.splashTimer = 5;
		
	def showDetails(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		
		tinfo = self.trainRoster.getTrain(at.tid)
		
		lid = at.loco
		if lid is None or lid == "":
			desc = ""
		else:
			desc = self.locos.getLocoDesc(lid)
			
		dlg = DetailsDlg(self, at.tid, tinfo, desc, at.engineer)
		dlg.Show()
		
	def bSkipPressed(self, _):	
		tInfo = self.trainRoster.getTrain(self.selectedTrain)
		if tInfo is None:
			return

		dlg = wx.MessageDialog(self, "This removes train %s from the schedule\nPress OK to continue, or Cancel" % self.selectedTrain,
							'Skip Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return
		
		logging.info("Removing train %s from schedule" % self.selectedTrain)
		
		self.pendingTrains.remove(self.selectedTrain)
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) == 0:
			self.chTrain.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))

	def onChangeSort(self, evt):
		self.assertSortOrder()
		
	def assertSortOrder(self):
		if self.parent.menuSort.FindItemById(MENU_SORT_TID).IsChecked():
			sortKey = "tid"
		else:
			sortKey = "time"

		grp = self.parent.menuSort.FindItemById(MENU_SORT_GROUP).IsChecked()
		asc = self.parent.menuSort.FindItemById(MENU_SORT_ASCENDING).IsChecked()
		
		self.atl.setSortKey(sortKey, groupDir=grp, ascending=asc)

	def returnActiveTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		if self.trainSchedule.isExtraTrain(at.tid):
			phrase  = "list of extra trains."	
		else:
			phrase = "top of the schedule."
			
		dlg = wx.MessageDialog(self, "This removes train %s (and its engineer) from the\nactive list, and places it back on the %s\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % (at.tid, phrase),
							'Return Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return

		self.atl.delTrain(tx)

		if self.trainSchedule.isExtraTrain(at.tid):
			self.setExtraTrains()
		else:
			self.pendingTrains = [at.tid] + self.pendingTrains
			self.chTrain.SetItems(self.pendingTrains)

			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))

		if at.engineer in self.selectedEngineers:
			if at.engineer not in self.idleEngineers:
				self.idleEngineers = [at.engineer] + self.idleEngineers
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
			
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		
	def removeActiveTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		
		dlg = wx.MessageDialog(self, "This indicates that train %s has reached its destination.\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % at.tid,
							'Remove Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return
		
		req = {"advice": {"msg": "Train %s has completed" % at.tid}}
		self.Request(req)


		mins = int(at.time / 60)
		secs = at.time % 60
		runtime = "%2d:%02d" % (mins, secs)
		self.completedTrains.append(at.tid, at.engineer, at.loco)
		self.completedTrainList.update()
		self.atl.delTrain(tx)
		
		logging.log("Train %s has completed" % at.tid)
		
		if self.trainSchedule.isExtraTrain(at.tid):
			self.setExtraTrains()
		
		if at.engineer in self.selectedEngineers:
			if at.engineer not in self.idleEngineers:
				self.idleEngineers.append(at.engineer)
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		
	def changeLoco(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return

		dlg = wx.SingleChoiceDialog(
				self, 'Choose a Locomotive', 'Change Locomotive',
				self.locos.getLocoListFull(),
				wx.CHOICEDLG_STYLE
				)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			loco = dlg.GetStringSelection()
			lid = loco.split(" ")[0]

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		logging.info("changing locomotive for train %s to %s" % (at.tid, lid))
		
		desc = self.locos.getLoco(lid)
		self.atl.updateTrain(at.tid, lid, desc, None)
		
		if lid in self.speeds:
			self.atl.setThrottle(lid, self.speeds[lid][0], self.speeds[lid][1])
		
		tinfo = self.trainRoster.getTrain(at.tid)
		if tinfo is not None:
			tinfo["loco"] = lid
		
	def onChoiceTID(self, _):
		tx = self.chTrain.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.chTrain.GetString(tx)
		self.setSelectedTrain(tid)
		
	def onChExtra(self, _):
		tx = self.chExtra.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.chExtra.GetString(tx)
		self.setSelectedTrain(tid)
		
	def reportSelection(self, tx):
		pass
		
	def reportDoubleClick(self, tx):
		self.reportSelection(tx)
		self.showDetails(tx)
		
	def onChoiceEngineer(self, _):
		ex = self.chEngineer.GetSelection()
		if ex == wx.NOT_FOUND:
			return
		
		self.selectedEngineer = self.chEngineer.GetString(ex)
		
	def setSelectedTrain(self, tid):
		self.selectedTrain = tid
		self.showInfo(tid)
		
	def showInfo(self, tid):
		if tid is None or tid == "":
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			self.stDescription.SetLabel("")
			return
		
		if self.trainRoster is None:
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			self.stDescription.SetLabel("Train Roster is empty")
			return
		else:
			tInfo = self.trainRoster.getTrain(tid)
			
		if tInfo is None:
			self.stDescription.SetLabel("Train %s is not in Train Roster" % tid)
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			return

		descr = "%s   %sbound %s" % (tid, "East" if tInfo["eastbound"] else "West", tInfo["desc"])	
		if tInfo["cutoff"]:
			descr += " (via cutoff)"	
		self.stDescription.SetLabel(descr)
		i = 0
		for step in tInfo["tracker"]:
			self.stStepTowers[i].SetLabel("" if step[0] is None else step[0])
			self.stStepStops[i].SetLabel("" if step[1] is None else step[1])
			if step[2] == 0:
				self.stStepLocs[i].SetLabel("")
			else:
				self.stStepLocs[i].SetLabel("(%2d)" % step[2])
			i += 1
			
		while i < MAX_STEPS:
			self.stStepTowers[i].SetLabel("")
			self.stStepLocs[i].SetLabel("")
			self.stStepStops[i].SetLabel("")
			i += 1
		
		if tInfo["loco"] is None:
			locoString = ""
		else:
			lId = tInfo["loco"]
			lInfo = self.locos.getLoco(lId)
			if lInfo is not None:
				lDesc = lInfo["desc"]
				if lDesc is None:
					locoString = "Loco: %s" % lId
				else:
					locoString = "Loco: %s - %s" % (lId, lDesc.replace('&', '&&'))
			else:
				locoString = ""

		if tInfo["block"] is None or tInfo["block"] == "":
			self.stLocoInfo.SetLabel("%-50.50s" % locoString)
		else:
			blockString = "Block: %s" % tInfo["block"]	
			self.stLocoInfo.SetLabel("%-40.40s %s" % (locoString, blockString))
						
				
	def onManageSchedule(self, _):
		dlg = ManageScheduleDlg(self, self.schedName, self.trainSchedule, self.trainRoster.getTrainList(), self.settings)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			self.schedName, self.trainSchedule = dlg.getResults()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return

		self.scheduledTrains = self.trainSchedule.getSchedule()
		self.extraScheduleTrains = self.trainSchedule.getExtras()
		
		self.pendingTrains = [t for t in self.scheduledTrains if not self.atl.hasTrain(t) and t not in self.completedTrains]
		self.extraTrains = sorted([t for t in self.extraScheduleTrains])
		self.setTrainSchedule(preserveActive=True)
		self.setExtraTrains()
		
		self.parent.setTitle(schedule=self.schedName)
		
	def onManageEngineers(self, _):
		busyEngineers = [x for x in self.atl.getEngineers() if x in self.selectedEngineers]
		availableEngineers = [x for x in list(self.engineers) if x not in busyEngineers]
		dlg = ManageEngineersDlg(self, availableEngineers, self.idleEngineers, busyEngineers, self.settings)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newSelEngs = dlg.getValues()
			
		if dlg.IsReloadNeeded():
			self.loadEngineerFile(os.path.join(os.getcwd(), "data", "engineers.txt"), preserveActive=True)

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.idleEngineers = newSelEngs	
		self.updateEngQueue()	
		self.chEngineer.SetItems(self.idleEngineers)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		
		self.selectedEngineers = [x for x in self.idleEngineers] + [x for x in busyEngineers if x in availableEngineers]

	def onAssignLocos(self, _):
		order = [x for x in self.trainSchedule]
		dlg = AssignLocosDlg(self, self.trainRoster, order, self.extraTrains, self.locos)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			result = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		for tid in list(self.trainSchedule) + self.extraTrains:
			tinfo = self.trainRoster.getTrain(tid)
			if tinfo["loco"] != result[tid]:
				tinfo["loco"] = result[tid]
					
		self.showInfo(self.selectedTrain)
		self.updateActiveListLocos()
		self.trainRoster.save()

	def onReportOpWorksheet(self, _):
		self.report.OpWorksheetReport(self.trainRoster, self.trainSchedule, self.locos)
		
	def onReportLocos(self, _):
		self.report.LocosReport(self.locos)
		
	def onReportStatus(self, _):
		self.report.StatusReport(self.atl, self.completedTrains)
			
	def onReportTrainCards(self, _):
		self.report.TrainCards(self.trainRoster, self.extraTrains, self.trainSchedule)
		
	def onSaveData(self, _):
		saveData(self, self.settings)
		
	def onRestoreData(self, _):
		restoreData(self, self.settings)
		
	def onConnectSnifferPressed(self, _):
		self.connectSniffer()

	def connectSniffer(self):	
		print("connect to sniffer")	
		self.sniffer = DCCSniffer()
		self.sniffer.bind(self.DCCMessage, self.DCCClosed)

		try:
			self.sniffer.connect(self.settings.dccsnifferport, self.settings.dccsnifferbaud, 1)
		except SerialException:
			dlg = wx.MessageDialog(self, 'Connection to DCC Sniffer on port ' + self.settings.dccsnifferport + ' failed',
					'Connection Failed',
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			self.sniffer = None
			
		self.enableDCCDisconnect(self.sniffer is not None)
		if self.sniffer:
			self.parent.setTitle(dcc="DCC Connected(%s)" % self.settings.dccsnifferport)
		else:
			self.parent.setTitle(dcc=True)

	def onDisconnectSnifferPressed(self, _):
		self.disconnectSniffer()
		
	def disconnectSniffer(self):
		if self.sniffer is None:
			return
		
		try:
			self.sniffer.kill()
			self.sniffer.join()	
		except:
			pass
		
		self.sniffer = None
		self.enableDCCDisconnect(False)
		self.parent.setTitle(dcc=False)
		
	def enableDCCDisconnect(self, flag=True):
		self.parent.menuDCC.Enable(MENU_DCC_DISCONNECT, flag)
		self.parent.menuDCC.Enable(MENU_DCC_CONNECT, not flag)

			
	def DCCMessage(self, txt): # thread context
		dccMsg = {
			"instr": txt[0],
			"loco": "%d" % int(txt[1]), # strip off any leading zeroes
			"param": txt[2]
		}
		evt = DCCMessageEvent(dcc=dccMsg)
		wx.PostEvent(self, evt)
		
	def onDCCMessage(self, evt):
		dccMsg = evt.dcc
		cmd = dccMsg["instr"]
		if cmd in ["F", "f", "R", "r", "s", "e"]:
			if cmd == "F":
				speedType = FWD_128
			elif cmd == "f":
				speedType = FWD_28
			elif cmd == "R":
				speedType = REV_128
			elif cmd == "r":
				speedType = REV_28
			else:
				speedType = STOP

			try:
				speed = int(dccMsg["param"])
			except:
				speed = None
				
			if speed is not None:
				self.speeds[dccMsg["loco"]] = [speed, speedType]
				self.atl.setThrottle(dccMsg["loco"], speed, speedType)
		
	def DCCClosed(self): # thread context
		evt = DCCClosedEvent()
		wx.PostEvent(self, evt)
		
	def onDCCClosed(self, evt):
		self.disconnectSniffer()
			
	def onClose(self, _):
		if self.atl.count() > 0:
			dlg = wx.MessageDialog(self, 'Trains are still active.\nPress "Yes" to exit program, or "No" to cancel.',
						'Active Trains',
						wx.YES_NO | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.ticker.Stop()
			
		if self.dlgEngQueue is not None:
			self.dlgEngQueue.Destroy()
			
		if self.dlgActiveTrains is not None:
			self.dlgActiveTrains.Destroy()
			
		if self.listener is not None:
			self.listener.kill()
			
		self.disconnectSniffer()
			
		self.Destroy()

class LegendDlg(wx.Dialog):
	def __init__(self, parent, cbClose):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Legend", style=wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT |wx.STAY_ON_TOP)

		self.cbClose = cbClose
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.loadImages()		
		self.il = wx.ImageList(16, 16)
		empty = self.makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxRed = self.il.Add(self.imageRed)
		self.idxGreen = self.il.Add(self.imageGreen)
		self.idxRedGreen = self.il.Add(self.imageRedGreen)
		self.idxYellow = self.il.Add(self.imageYellow)
		text = [
			[ self.idxGreen,      "Train is operating at correct speed or lower" ],
			[ self.idxYellow,     "Train is moving, Signal speed limit is unknown" ],
			[ self.idxRedGreen,   "Train is traveling too fast for current signal" ],
			[ self.idxRed,        "Train is stopped" ],
			[ self.idxEmpty,      "Train has not started since being assigned" ]
		]

		textFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		self.lcLegend = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.BORDER_NONE)
		self.lcLegend.SetFont(textFont)
		self.lcLegend.InsertColumn(0, "")

		self.lcLegend.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		for i in range(5):
			self.lcLegend.InsertItem(i*2, text[i][1], text[i][0])

		self.lcLegend.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		
		vsz = wx.BoxSizer(wx.VERTICAL)	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(300)
		vsz.Add(hsz)	
		vsz.AddSpacer(20)

		vsz.Add(self.lcLegend, 0, wx.EXPAND)
		
		vsz.AddSpacer(20)		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit();

	def onClose(self, _):
		if callable(self.cbClose):
			self.cbClose()	
		self.Destroy()	

	def loadImages(self):
		fn = os.path.join(os.getcwd(), "images", "atlRed.png")
		png = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageRed = png
		
		fn = os.path.join(os.getcwd(), "images", "atlGreen.png")
		png = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageGreen = png
		
		fn = os.path.join(os.getcwd(), "images", "atlRedGreen.png")
		png = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageRedGreen = png
		
		fn = os.path.join(os.getcwd(), "images", "atlYellow.png")
		png = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageYellow = png

	def makeBlank(self):
		empty = wx.Bitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		if not DEVELOPMODE:
			self.frame.Maximize(True)
			
		self.SetTopWindow(self.frame)
		return True

import sys

ofp = open("tracker.out", "w")
efp = open("tracker.err", "w")

if not DEVELOPMODE:
	sys.stdout = ofp
	sys.stderr = efp

app = App(False)
app.MainLoop()

ofp.close()
efp.close()
