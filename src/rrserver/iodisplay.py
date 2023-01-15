import wx


class IODisplay(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(940, 240), style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_VIRTUAL)
		f = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace")
		self.SetFont(f)
		self.parent = parent
		self.olines = []
		self.ilines = []
		self.InsertColumn(0, "")
		self.SetColumnWidth(0, 940)
		self.SetItemCount(0)
		self.attrO = wx.ItemAttr()
		self.attrO.SetBackgroundColour("white")

		self.attrI = wx.ItemAttr()
		self.attrI.SetBackgroundColour("light blue")

	def OnGetItemText(self, item, col):
		if item % 2 == 0:
			ox = int(item/2)
			return ("%d: " % ox) + self.olines[ox]
		else:
			ix = int((item-1)/2)
			return "   " + self.ilines[ix]

	def OnGetItemAttr(self, item):
		if item % 2 == 0:
			return self.attrO
		else:
			return self.attrI

	def ClearIO(self):
		self.olines = []
		self.ilines = []
		self.SetItemCount(0)
		self.RefreshItems(0, 0)

	def ShowText(self, otext, itext, line, lines):
		if self.GetItemCount() == 0:
			self.olines = ["" for i in range(lines)]
			self.ilines = ["" for i in range(lines)]
			self.SetItemCount(lines*2)

		self.olines[line] = otext
		self.ilines[line] = itext
		self.RefreshItem(line*2)
		self.RefreshItem(line*2+1)
