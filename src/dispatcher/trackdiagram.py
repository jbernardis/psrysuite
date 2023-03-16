import wx

class TrackDiagram(wx.Panel):
	def __init__(self, frame, dlist): #screen, id, diagramBmp, offset):
		wx.Panel.__init__(self, frame, size=(100, 100), pos=(0,0), style=0)
		self.frame = frame
		self.screens = [d.screen for d in dlist]
		self.bgbmps =  [d.bitmap for d in dlist]
		self.offsets = [d.offset for d in dlist]
		self.xoffset = [int(o/16) for o in self.offsets]
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
		self.xoffset.append(9999)

		self.showPosition = True

		self.tiles = {}
		self.text = {}
		self.trains = {}
		self.bitmaps = {}
		self.tx = 0
		self.ty = 0
		self.scr = -1
		self.shift_down = False

		self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

		w = 0;
			
		for b in self.bgbmps:
			w += b.GetWidth()
		h = self.bgbmps[0].GetHeight()  # assume all the same height

		self.SetSize((w, h))
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		self.Bind(wx.EVT_ENTER_WINDOW, lambda event: self.SetFocus())

	def DrawBackground(self, dc):
		for i in range(len(self.bgbmps)):
			dc.DrawBitmap(self.bgbmps[i], self.offsets[i], 0)

	def OnMotion(self, evt):
		pt = evt.GetPosition()
		ntx = int(pt.x/16)
		nty = int(pt.y/16)
		ox = self.DetermineScreen(ntx)
		if ox is None:
			# ignore if we can't determine position
			return

		ntx -= self.xoffset[ox]
		scr = self.screens[ox]

		if ntx != self.tx or nty != self.ty or self.scr != scr:
			self.tx = ntx
			self.ty = nty
			self.scr = scr
			if self.showPosition:
				self.frame.UpdatePositionDisplay(self.tx, self.ty, self.scr)

	def DetermineScreen(self, x):
		for ox in range(len(self.xoffset)-1):
			if self.xoffset[ox] <= x < self.xoffset[ox+1]:
				return ox

		return None 

	def OnKeyDown(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_SHIFT:
			self.shift_down = True
			print("shift down")

		event.Skip()

	def OnKeyUp(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_SHIFT:
			self.shift_down = False
			print("shift up")

		event.Skip()

	def OnLeftUp(self, evt):
		self.frame.ProcessClick(self.scr, (self.tx, self.ty), shift=self.shift_down)

	def DrawTile(self, x, y, offset, bmp):
		self.tiles[(x*16+offset, y*16)] = bmp;
		self.Refresh()

	def DrawText(self, x, y, offset, text):
		self.text[(x*16+offset, y*16)] = text;
		self.Refresh()

	def DrawFixedBitmap(self, x, y, offset, bmp):
		self.bitmaps[x+offset, y] = bmp
		self.Refresh()

	def ClearText(self, x, y, offset):
		textKey = (x*16+offset, y*16)
		if textKey not in self.text:
			return
		del(self.text[textKey])
		self.Refresh()

	def DrawTrain(self, x, y, offset, trainID, locoID, stopRelay, atc):
		self.trains[(x*16+offset, y*16)] = [trainID, locoID, stopRelay, atc];
		self.Refresh()

	def ClearTrain(self, x, y, offset):
		textKey = (x*16+offset, y*16)
		if textKey not in self.trains:
			return
		del(self.trains[textKey])
		self.Refresh()

	def OnPaint(self, evt):
		dc = wx.BufferedPaintDC(self)
		dc.SetTextForeground(wx.Colour(255, 0, 0))
		dc.SetTextBackground(wx.Colour(255, 255, 255))
		dc.SetBackgroundMode(wx.BRUSHSTYLE_SOLID)
		dc.SetFont(wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		self.DrawBackground(dc)
		for bx, bmp in self.tiles.items():
			dc.DrawBitmap(bmp, bx[0], bx[1])
		for bx, bmp in self.bitmaps.items():
			dc.DrawBitmap(bmp, bx[0], bx[1])
		for bx, txt in self.text.items():
			dc.DrawText(txt, bx[0], bx[1])
		for bx, tinfo in self.trains.items():
			x = bx[0]
			y = bx[1]
			if tinfo[2]:
				dc.SetTextForeground(wx.Colour(255, 255, 255))
				dc.SetTextBackground(wx.Colour(255, 0, 0))
				txt = "* "
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]
				
			if tinfo[3]:
				dc.SetTextForeground(wx.Colour(0, 192, 0))
				dc.SetTextBackground(wx.Colour(0, 0, 0))
				txt = "A "
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]

			dc.SetTextForeground(wx.Colour(255, 0, 0))
			dc.SetTextBackground(wx.Colour(255, 255, 255))
			dc.DrawText(tinfo[0]+" ", x, y)
			x += dc.GetTextExtent(tinfo[0])[0]+2

			dc.SetTextForeground(wx.Colour(255, 255, 255))
			dc.SetTextBackground(wx.Colour(255, 0, 0))
			dc.DrawText(tinfo[1], x, y)
