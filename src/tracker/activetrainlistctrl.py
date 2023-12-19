import wx
import os

MENU_REMOVE_TRAIN    = 1100
MENU_CHANGE_ENGINEER = 1101
MENU_SHOW_DETAILS    = 1103
MENU_RETURN_TRAIN    = 1104

TIMECOL = 10
TIDCOL = 0
DIRCOL = 2		


class ActiveTrainListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(1070, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)
		
		self.atl = None
		self.altFlag = False
		
		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Origin")
		self.InsertColumn(2, "Dir")
		self.InsertColumn(3, "Terminus")
		self.InsertColumn(4, "Engineer")
		self.InsertColumn(5, "Loco #")
		self.InsertColumn(6, "Train Description")
		self.InsertColumn(7, "Block")
		self.InsertColumn(8, "Speed")
		self.InsertColumn(9, "Limit")
		self.InsertColumn(10, "Time")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 120)
		self.SetColumnWidth(4, 90)
		self.SetColumnWidth(5, 80)
		self.SetColumnWidth(6, 230)
		self.SetColumnWidth(7, 60)
		self.SetColumnWidth(8, 70)
		self.SetColumnWidth(9, 60)
		self.SetColumnWidth(10, 80)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.atcA = wx.ItemAttr()
		self.atcB = wx.ItemAttr()
		self.atcA.SetBackgroundColour(wx.Colour(255, 175, 159))
		self.atcB.SetBackgroundColour(wx.Colour(255, 135, 88)) # red
		
		self.hilite = wx.ItemAttr()
		self.hilite.SetBackgroundColour(wx.Colour(0, 116, 232))
		self.hilite.SetTextColour(wx.Colour(255, 255, 255))

		self.loadImages()		
		self.il = wx.ImageList(16, 16)
		empty = self.makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxRed = self.il.Add(self.imageRed)
		self.idxGreen = self.il.Add(self.imageGreen)
		self.idxYellow = self.il.Add(self.imageYellow)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self)
		
	def setAtl(self, atl):
		self.atl = atl
		self.refreshItemCount()
		
	def refreshItemCount(self):
		self.SetItemCount(self.atl.count())	

	def ticker(self):
		self.altFlag = not self.altFlag
		
	def refreshAll(self):
		self.refreshItemCount()
		if self.GetItemCount() > 0:
			self.RefreshItems(0, self.GetItemCount()-1)

	def makeBlank(self):
		empty = wx.Bitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty
	
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
		
		fn = os.path.join(os.getcwd(), "images", "atlYellow.png")
		png = wx.Image(fn, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageYellow = png
		
	def onRightClick(self, evt):
		self.itemSelected = self.GetFirstSelected()
		if self.itemSelected == wx.NOT_FOUND:
			return

		menu = wx.Menu()
		menu.Append( MENU_REMOVE_TRAIN, "Train at Destination" )
		menu.Append( MENU_CHANGE_ENGINEER, "Change Engineer" )
		menu.Append( MENU_SHOW_DETAILS, "Show Train Details" )
		menu.Append( MENU_RETURN_TRAIN, "Return Train to Schedule" )
		self.Bind(wx.EVT_MENU, self.onRemoveTrain, id=MENU_REMOVE_TRAIN)
		self.Bind(wx.EVT_MENU, self.onChangeEngineer, id=MENU_CHANGE_ENGINEER)
		self.Bind(wx.EVT_MENU, self.onShowDetails, id=MENU_SHOW_DETAILS)
		self.Bind(wx.EVT_MENU, self.onReturnTrain, id=MENU_RETURN_TRAIN)
		self.PopupMenu( menu, evt.GetPoint() )
		menu.Destroy()
		
	def onRemoveTrain(self, evt):
		self.parent.removeActiveTrain(self.itemSelected)
		
	def onChangeEngineer(self, evt):
		self.parent.reassignTrain(self.itemSelected)
		
	def onShowDetails(self, evt):
		self.parent.showDetails(self.itemSelected)
		
	def onReturnTrain(self, evt):
		self.parent.returnActiveTrain(self.itemSelected)
			
	def setSelection(self, tx, dclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		if dclick:
			self.parent.reportDoubleClick(tx)
		else:
			self.parent.reportSelection(tx)
		
	def setSortHeaders(self, sortkey, groupDir=False, ascending=False):				
		col = self.GetColumn(TIMECOL)
		if sortkey == "time":
			if ascending:
				hText = u"Time  \u21D1"
			else:
				hText = u"Time  \u21D3"
		else:
			hText = "Time"
		col.SetText(hText)
		self.SetColumn(TIMECOL, col)
		
		col = self.GetColumn(TIDCOL)
		if sortkey == "tid":
			if ascending:
				hText = u"Train  \u21D1"
			else:
				hText = u"Train  \u21D3"
		else:
			hText = "Train"
		col.SetText(hText)
		self.SetColumn(TIDCOL, col)
		
		col = self.GetColumn(DIRCOL)
		if groupDir:
			hText = u"Dir  \u21D4"
		else:
			hText = "Dir"
		col.SetText(hText)
		self.SetColumn(DIRCOL, col)
		
	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)
			
	def OnGetItemImage(self, item):
		at = self.atl.getTrainByPosition(item)
		if at is None:
			return self.idxEmpty

		if not at.hasStarted:
			return self.idxEmpty
		
		if at.throttle is None:
			return self.idxEmpty

		if at.speed == 0:
			return self.idxRed
		
		if at.limit is None:
			if self.altFlag:
				return self.idxRed
			else:
				return self.idxGreen
		
		if at.speed > at.limit:
			return self.idxRed
		
		return self.idxGreen

	def OnGetItemText(self, item, col):
		at = self.atl.getTrainByPosition(item)
		if at is None:
			return "??"

		if col == 0:
			return at.tid
		elif col == 1:
			if at.origin is None:
				return ""
			else:
				return at.origin
		elif col == 2:
			return at.dir
		elif col == 3:
			if at.terminus is None:
				return ""
			else:
				return at.terminus
		elif col == 4:
			return at.engineer
		elif col == 5:
			if at.loco is None:
				return ""
			else:
				return at.loco
		elif col == 6:
			if at.ldesc is None:
				return ""
			else:
				try:
					if at.ldesc["desc"] is None:
						return ""
					else:
						return at.ldesc["desc"]
				except:
					return ""
		elif col == 7:
			if at.block is None:
				return ""
			else:
				return at.block
		elif col == 8:
			if at.throttle is None:
				return ""
			else:
				try:
					return "%d" % at.throttle
				except TypeError:
					return "TE"
		elif col == 9:
			if at.limit is None:
				return ""
			else:
				try:
					return "%d" % at.limit
				except TypeError:
					return "TE"
		elif col == 10:
			mins = int(at.time / 60)
			secs = at.time % 60
			return "%2d:%02d" % (mins, secs)

	def OnGetItemAttr(self, item):	
		at = self.atl.getTrainByPosition(item)
		if at is None:
			return "??"

		hilite = at.highlight > 0
		if hilite:
			return self.hilite

		if at.engineer == "ATC":
			if item % 2 == 1:
				return self.atcB
			else:
				return self.atcA
		else:
			if item % 2 == 1:
				return self.normalB
			else:
				return self.normalA
