import HTML
import wx
import os
import webbrowser

BTNSZ = (120, 46)

class Report:
	def __init__(self, parent, settings):
		self.initialized = False
		self.parent = parent
		self.settings = settings
		
		browserCmd = self.settings.browser + " --app=%s"

		try:
			self.browser = webbrowser.get(browserCmd)
		except webbrowser.Error:
			dlg = wx.MessageDialog(self.parent, "Unable to find an available browser at\n%s" % self.settings.browser,
					"Report Initialization failed",
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.initialized = True
		
	def Initialized(self):
		return self.initialized
	
	def openBrowser(self, title, html):
		htmlFileName = "report.html"
		with open(htmlFileName, "w") as fp:
			fp.write(html)
		
		path = os.path.join(os.getcwd(), htmlFileName)
		
		fileURL = 'file:///'+path

		self.browser.open_new(fileURL)


	def OpWorksheetReport(self, roster, order, schedule, locos):
		orderTrains = order.getOrder()
		extraTrains = order.getExtras()
		extras = [t for t in extraTrains if t not in schedule]
		if len(schedule) == 0:
			schedule = orderTrains

		if len(extraTrains) > 0:	
			dlg = ChooseExtrasDlg(self.parent, schedule, extras)
			rc = dlg.ShowModal()
			
			if rc == wx.ID_OK:
				schedule = dlg.getValues()
				
			dlg.Destroy()
			if rc != wx.ID_OK:
				return

		css = HTML.StyleSheet()
		css.addElement("div.page", {"page-break-inside": "avoid"})
		css.addElement("table.schedule", {'width': '700px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table.extra", {'width': '700px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td, th", {'text-align': 'center', 'width': '80px', 'overflow': 'hidden'})
		css.addElement("td.seq", {'text-align': 'center', 'width': '40px', 'overflow': 'hidden'})
		css.addElement("td.description", {'text-align': 'left', 'width': '300px', 'overflow': 'hidden'})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
	
	
		html += HTML.h1({'align': 'center'}, "Operating Worksheet")	
		html += "<br><br>"
		

		cardNumbers = {}
		seq = 1
		for tid in orderTrains:
			cardNumbers[tid] = "%2d" % seq
			seq += 1

		seq = 0
		for tid in extraTrains:
			cardNumbers[tid] = chr(ord('A') + seq)
			seq += 1
		
		header = HTML.tr({},
			HTML.th({}, "Card"),
			HTML.th({}, "Start"),
			HTML.th({}, "Track"),
			HTML.th({}, "Dir"),
			HTML.th({}, "Train"),
			HTML.th({}, "Loco"),
			HTML.th({}, "Description"),
			HTML.th({}, "End"),
			HTML.th({}, "Track"))
		
		rows = []
	
		for tid in schedule:
			tInfo = roster.getTrain(tid)

			if tInfo is not None:
				rows.append(self.generateOpWorksheetRow(tid, tInfo, locos, cardNumbers))

		html += HTML.div({"class": "page"}, 
			HTML.h2({'align': 'center'}, "Train Sequence"),
			HTML.table({"class": "schedule"}, header, "".join(rows))
		)

		html += HTML.endbody()
		html += HTML.endhtml()
		
		self.openBrowser("Operating Worksheet", html)

	def generateOpWorksheetRow(self, tid, tInfo, locos, cardNumbers, extra=False):
		rowColor = "#cdffb9"  if tInfo["dir"].lower() == "east" else "#ffaeae"
		cardColor = "#ff0000" if extra else "#000000"

		lid = tInfo["loco"]
		if lid is None:
			lid = ""
			desc = ""
		else:
			desc = locos.getLoco(lid)
			if desc is None:
				desc = ""

		if tInfo["origin"]["loc"] is None:
			start = ""
		else:
			start = tInfo["origin"]["loc"]
		if tInfo["origin"]["track"] is None:
			startTrack = ""
		else:
			startTrack = tInfo["origin"]["track"]

		if tInfo["terminus"]["loc"] is None:
			terminus = ""
		else:
			terminus = tInfo["terminus"]["loc"]
		if tInfo["terminus"]["track"] is None:
			terminusTrack = ""
		else:
			terminusTrack = tInfo["terminus"]["track"]


		return HTML.tr({},
			HTML.td({"class": "seq"}, "<font color=\"%s\">%s</font>" % (cardColor, cardNumbers[tid])),
			HTML.td({}, start),
			HTML.td({}, startTrack),
			HTML.td({}, tInfo["dir"]),
			HTML.td({"bgcolor": rowColor}, tid),
			HTML.td({"bgcolor": rowColor}, lid),
			HTML.td({'class': 'description', "bgcolor": rowColor}, HTML.nbsp(2), desc),
			HTML.td({}, terminus),
			HTML.td({}, terminusTrack))


	def TrainCards(self, roster, extra, order):	
		dlg = ChooseCardsDlg(self.parent, list(order), extra)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			scheduledToPrint, extraToPrint = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		ct = 0
		for flag in scheduledToPrint:
			if flag:
				ct += 1
				
		ctx = 0
		for flag in extraToPrint:
			if flag:
				ctx += 1
				
		if ct+ctx == 0:
			dlg = wx.MessageDialog(self.parent, "No Train Cards chosen - skipping report", 
						"Nothing to print",
						wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		css = HTML.StyleSheet()
		css.addElement("div.page", {"page-break-inside": "avoid"})
		css.addElement("*", {"box-sizing": "border-box"})
		css.addElement(".row", {"margin-left": "-5px", "margin-right": "-5px", "height": "107mm"})
		css.addElement(".column", {"float": "left", "width": "136mm", "padding": "1px"})
		css.addElement(".row::after", {"content": '""', "clear": "both", "display": "table"})
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "100%", "height": "106mm", "font-family": '"Times New Roman", Times, serif', "font-size": "16px"})
		css.addElement("td.trainid", {"width": "36.4%", "padding-left": "50px", "padding-top": "10px", "font-size": "28px", "font-weight": "bold"})
		css.addElement("td.firstcol", {"width": "36.4%", "padding-left": "50px"})
		css.addElement("td.secondcol", {"width": "10%"})
		css.addElement("tr.datarow", {"height": "5mm"})
		css.addElement("td", {"text-align": "left", "padding-left": "6px"})
		css.addElement("td.cardnumber", {"text-align": "right", "padding-right": "50px"})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
		
		cards = []

		for tx in range(len(order)):
			tid = order.getTid(tx)
			if scheduledToPrint[tx]:
				cards.append(self.formatTrainCard(tid, roster.getTrain(tid), "%d" % (tx+1)))
		for tx in range(len(extra)):
			tid = extra[tx]
			if extraToPrint[tx]:
				cn = chr(ord('A') + tx)
				cards.append(self.formatTrainCard(tid, roster.getTrain(tid), cn))
				
		nCards = len(cards)
		
		divs = []
		for i in range(0, nCards-1, 2):
			divs.append(HTML.div({"class": "row"}, cards[i], cards[i+1]))
			
		if nCards%2 != 0:
			divs.append(HTML.div({"class": "row"}, cards[-1]))

		dx = 0		
		while dx < len(divs):
			if dx == len(divs)-1:
				html += HTML.div({"class": "page"}, divs[dx])
			else:
				html += HTML.div({"class": "page"}, divs[dx], divs[dx+1])
				
			dx += 2

		html += HTML.endbody()
		html += HTML.endhtml()

		self.openBrowser("Train Cards", html)

	def formatTrainCard(self, tid, tinfo, tx):
		trainIdRow = HTML.tr({}, HTML.td({"class": "trainid"}, tid), HTML.td())
		emptyRow = HTML.tr({"class": "datarow"}, HTML.td({}, HTML.nbsp()))
		descr = "%sbound %s" % (tinfo["dir"], tinfo["desc"])
		if tinfo["cutoff"]:
			descr += " (via cutoff)"
		descRow = HTML.tr({}, HTML.td({"class": "firstcol", "colspan": "3"}, descr))
		cardNumberRow = HTML.tr({}, HTML.td({}, ""), HTML.td({}, ""), HTML.td({"class": "cardnumber"}, tx))

		stepRows = []
		for stp in tinfo["steps"]:
			row = HTML.tr({"class": "datarow"},
						HTML.td({"class": "firstcol"}, stp[0]),
						HTML.td({"class": "secondcol"}, "" if stp[2] == 0 else ("(%2d)" % stp[2])),
						HTML.td({}, stp[1])
			)
			stepRows.append(row)
			
		nRows = len(stepRows)
		nEmpty = 10 - nRows
		
		table = HTML.table({},
			trainIdRow,
			descRow,
			emptyRow,
			" ".join(stepRows),
			nEmpty * emptyRow,
			cardNumberRow
		)
		
		return HTML.div({"class": "column"}, table)
			
	def StatusReport(self, active, completed):
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '650px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td, th", {'text-align': 'center', 'width': '80px', 'overflow': 'hidden'})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
		
		html += HTML.h1({'align': 'center'}, "Active Trains")
		
		header = HTML.tr({},
			HTML.th({}, "Train"),
			HTML.th({}, "Engineer"),
			HTML.th({}, "Loco"),
			HTML.th({}, "Block"))
		
		rows = []
		for tid in active.getTrains():
			at = active.getTrainByTid(tid)
			rows.append(HTML.tr({},
					HTML.td({}, at.tid),
					HTML.td({}, at.engineer),
					HTML.td({}, at.loco),
					HTML.td({}, at.block))
			)
		html += HTML.table({}, header, "".join(rows))

		
		html += HTML.h1({'align': 'center'}, "Completed Trains")
		
		header = HTML.tr({},
			HTML.th({}, "Train"),
			HTML.th({}, "Engineer"),
			HTML.th({}, "Loco"))
		
		rows = []
		for tr, ti in completed:
			rows.append(HTML.tr({},
					HTML.td({}, tr),
					HTML.td({}, ti[0]),
					HTML.td({}, ti[1]))
			)
			
		html += HTML.table({}, header, "".join(rows))
			
		html += HTML.endbody()
		html += HTML.endhtml()
		
		self.openBrowser("Train Status Report", html)
					
	def LocosReport(self, locos):
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '650px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td.loco", {"text-align": "right", "width": "90px", "padding-right": "40px"})
		css.addElement("td.desc", {"text-align": "left", "width": "500px", "padding-left": "20px"})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
		
		html += HTML.h1({'align': 'center'}, "Locomotives")
		
		header = HTML.tr({},
			HTML.th({}, "Loco Number"),
			HTML.th({}, "Description"))
		
		rows = []
		for loco in locos.getLocoList():
			desc = locos.getLoco(loco)
			rows.append(HTML.tr({},
					HTML.td({"class": "loco"}, loco),
					HTML.td({"class": "desc"}, desc))
			)
		html += HTML.table({}, header, "".join(rows))

			
		html += HTML.endbody()
		html += HTML.endhtml()
		
		self.openBrowser("Locomotives Report", html)

class ChooseExtrasDlg(wx.Dialog):
	def __init__(self, parent, order, extra):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Extra Trains")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.order = order
		self.extra = extra

		self.schedule = [x for x in self.order]
		self.selectedTrain = None

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)

		self.cbList = {}
		self.chList = {}

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Select extra trains to include:")
		st.SetFont(textFont)
		hsz.Add(st)
		hsz.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "And their position in the schedule:")
		st.SetFont(textFont)
		hsz.Add(st)
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)

		self.clb = wx.CheckListBox(self, wx.ID_ANY, choices=self.extra, size=(100, 300))
		self.clb.SetFont(textFontBold)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onCheckExtra, self.clb)

		self.sch = wx.ListBox(self, wx.ID_ANY, choices = self.schedule, size=(100, 300), style=wx.LB_SINGLE)
		self.sch.SetFont(textFontBold)
		self.Bind(wx.EVT_LISTBOX, self.onClickSchedule, self.sch)

		self.bUp = wx.Button(self, wx.ID_ANY, "Up", size=(80, 30))
		self.bUp.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp);
		self.bUp.Enable(False)

		self.bDown = wx.Button(self, wx.ID_ANY, "Down", size=(80, 30))
		self.bDown.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown);
		self.bDown.Enable(False)

		bsz = wx.BoxSizer(wx.VERTICAL)
		bsz.Add(self.bUp)
		bsz.AddSpacer(20)
		bsz.Add(self.bDown)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(50)
		hsz.Add(self.clb)
		hsz.AddSpacer(80)
		hsz.Add(self.sch)
		hsz.AddSpacer(10)
		hsz.Add(bsz, 0, wx.ALIGN_CENTER_VERTICAL)

		vsizer.Add(hsz)

		vsizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bCancel)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()

	def onCheckExtra(self, evt):
		tx = evt.GetSelection()
		train = self.extra[tx]
		if self.clb.IsChecked(tx):
			self.schedule.append(train)
		else:
			self.schedule.remove(train)
		
		self.sch.SetItems(self.schedule)

	def onClickSchedule(self, evt):
		self.selectedTrain = evt.GetString()
		if self.selectedTrain in self.order:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
		else:
			try:
				ix = self.schedule.index(self.selectedTrain)
			except:
				ix = None
			if ix is None:
				self.bUp.Enable(False)
				self.bDown.Enable(False)
			elif ix <= 0:
				self.bUp.Enable(False)
				self.bDown.Enable(True)
			elif ix >= (len(self.schedule)-1):
				self.bUp.Enable(True)
				self.bDown.Enable(False)
			else:
				self.bUp.Enable(True)
				self.bDown.Enable(True)

	def bUpPressed(self, evt):
		try:
			ix = self.schedule.index(self.selectedTrain)
		except:
			return

		e1 = self.schedule[ix-1]
		e2 = self.schedule[ix]

		if ix == 1:
			nl = [e2, e1] + self.schedule[2:]
		elif ix == len(self.schedule)-1:
			nl = self.schedule[:-2] + [e2, e1]
		else:
			nl = self.schedule[:ix-1] + [e2, e1] +  self.schedule[ix+1:]

		self.schedule = [x for x in nl]
		self.sch.SetItems(self.schedule)
		self.sch.SetSelection(ix-1)

		if ix-1 == 0:
			self.bUp.Enable(False)
		self.bDown.Enable(True)

	def bDownPressed(self, evt):
		try:
			ix = self.schedule.index(self.selectedTrain)
		except:
			return

		e1 = self.schedule[ix]
		e2 = self.schedule[ix+1]
		
		if ix == 0:
			nl = [e2, e1] + self.schedule[2:]
		elif ix == len(self.schedule)-2:
			nl = self.schedule[:-2] + [e2, e1]
		else:
			nl = self.schedule[:ix] + [e2, e1] +  self.schedule[ix+2:]
			
		self.schedule = [x for x in nl]
		self.sch.SetItems(self.schedule)
		self.sch.SetSelection(ix+1)
		if ix+1 >= len(self.schedule)-1:
			self.bDown.Enable(False)
		self.bUp.Enable(True)

	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)

	def getValues(self):
		return self.schedule
		

class ChooseCardsDlg(wx.Dialog):
	def __init__(self, parent, order, extra):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Train Cards")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.order = order
		self.extra = extra

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		clb = wx.CheckListBox(self, wx.ID_ANY, choices=order)
		clb.SetFont(textFont)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onClbOrder, clb)
		self.clbOrder = clb
		hsz.Add(clb)
		
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bCheckAll = wx.Button(self, wx.ID_ANY, "Select\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCheckAllPressed, self.bCheckAll)
		self.bCheckAll.SetFont(btnFont)
		
		self.bUncheckAll = wx.Button(self, wx.ID_ANY, "Unselect\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bUncheckAllPressed, self.bUncheckAll)
		self.bUncheckAll.SetFont(btnFont)
		
		vsz.Add(self.bCheckAll)
		vsz.AddSpacer(20)
		vsz.Add(self.bUncheckAll)
		
		hsz.Add(vsz, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(50)
		
		
		
		clb = wx.CheckListBox(self, wx.ID_ANY, choices=self.extra)
		clb.SetFont(textFont)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onClbExtra, clb)
		self.clbExtra = clb
		hsz.Add(clb)
		
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bCheckAllExtra = wx.Button(self, wx.ID_ANY, "Select\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCheckAllExtraPressed, self.bCheckAllExtra)
		self.bCheckAllExtra.SetFont(btnFont)
		
		self.bUncheckAllExtra = wx.Button(self, wx.ID_ANY, "Unselect\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bUncheckAllExtraPressed, self.bUncheckAllExtra)
		self.bUncheckAllExtra.SetFont(btnFont)
		
		vsz.Add(self.bCheckAllExtra)
		vsz.AddSpacer(20)
		vsz.Add(self.bUncheckAllExtra)
		
		hsz.Add(vsz, 0, wx.ALIGN_CENTER_VERTICAL)
		
		
		
		labelsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Select Scheduled Train Cards:")
		st.SetFont(textFontBold)
		labelsz.Add(st)
		
		labelsz.AddSpacer(50)
		
		st = wx.StaticText(self, wx.ID_ANY, "Select Extra Train Cards:")
		st.SetFont(textFontBold)
		labelsz.Add(st)
		
		vsizer.Add(labelsz)
		vsizer.AddSpacer(5)
				
		vsizer.Add(hsz)
		
		vsizer.AddSpacer(10)
		
		self.stCheckCount = wx.StaticText(self, wx.ID_ANY, " 0 Trains Selected")
		self.stCheckCount.SetFont(textFontBold)
		vsizer.Add(self.stCheckCount, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bCancel)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()
		
	def bCheckAllPressed(self, _):
		for i in range(len(self.order)):
			self.clbOrder.Check(i, True)
			
		self.reportCheckCount()
		
	def bUncheckAllPressed(self, _):
		for i in range(len(self.order)):
			self.clbOrder.Check(i, False)
			
		self.reportCheckCount()
		
	def bCheckAllExtraPressed(self, _):
		for i in range(len(self.extra)):
			self.clbExtra.Check(i, True)
			
		self.reportCheckCount()
		
	def bUncheckAllExtraPressed(self, _):
		for i in range(len(self.extra)):
			self.clbExtra.Check(i, False)
			
		self.reportCheckCount()
		
	def onClbOrder(self, _):
		self.reportCheckCount()
		
	def onClbExtra(self, _):
		self.reportCheckCount()
		
	def reportCheckCount(self):
		ct = 0
		for i in range(len(self.order)):
			if self.clbOrder.IsChecked(i):
				ct += 1
		for i in range(len(self.extra)):
			if self.clbExtra.IsChecked(i):
				ct += 1
				
		if ct == 1:
			text = " 1 Train  Selected"
		else:
			text = "%2d Trains Selected" % ct
			
		self.stCheckCount.SetLabel(text)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)
		
	def getValues(self):
		return [self.clbOrder.IsChecked(i) for i in range(len(self.order))], [self.clbExtra.IsChecked(i) for i in range(len(self.extra))]
	