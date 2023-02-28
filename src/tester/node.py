import wx
import wx.lib.scrolledpanel as scrolled

def getBit(ibyte, ibit):
	if ibit < 0 or ibit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-ibit)
	b = int(ibyte.hex(), 16)
	return 1 if b & mask != 0 else 0

class Node (scrolled.ScrolledPanel):
	pulsed = 1
	unused = 8
	disabled = 9
	
	def __init__(self, parent):
		scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY, size=(600, 600))
		self.parent = parent

		self.cboMap = []
		self.stoMap = []
		self.nobytes = 0
		
		self.cbiMap = []
		self.stiMap = []
		self.nibytes = 0

	def getWidth(self):
		return self.maxWidth

	def getHeight(self):
		return self.maxHeight

	def AddWidgets(self):
		self.nobytes = len(self.outputs)
		
		for byte in range(self.nobytes):
			cboMapRow = []
			stoMapRow = []
			for bit in range(8):
				try:
					oinfo = self.outputs[byte][bit]
				except IndexError:
					oinfo = None
				if oinfo is not None:
					if oinfo[2] == Node.disabled:
						cboMapRow.append(None)
						st = wx.StaticText(self, wx.ID_ANY, "- disabled -", size=(200, -1))
						stoMapRow.append(st)
					elif oinfo[2] == Node.unused:
						cboMapRow.append(None)
						st = wx.StaticText(self, wx.ID_ANY, "- unused -", size=(200, -1))
						stoMapRow.append(st)
					else:				
						cb = wx.CheckBox(self, wx.ID_ANY, oinfo[0], size=(100, -1))
						cboMapRow.append(cb)
						st = wx.StaticText(self, wx.ID_ANY, oinfo[1], size=(100, -1))
						stoMapRow.append(st)
				else:
					cboMapRow.append(None)
					stoMapRow.append(None)					
				
			self.cboMap.append(cboMapRow)
			self.stoMap.append(stoMapRow)
			
		self.nibytes = len(self.inputs)
		
		for byte in range(self.nibytes):
			cbiMapRow = []
			stiMapRow = []
			for bit in range(8):
				try:
					iinfo = self.inputs[byte][bit]
				except IndexError:
					iinfo = None
				if iinfo is not None:
					cb = wx.CheckBox(self, wx.ID_ANY, "", size=(15, -1))
					cb.Enable(False)
					cbiMapRow.append(cb)
					st1 = wx.StaticText(self, wx.ID_ANY, iinfo[0], size=(85, -1))
					st2 = wx.StaticText(self, wx.ID_ANY, iinfo[1], size=(100, -1))
					stiMapRow.append((st1, st2))
				else:
					cbiMapRow.append(None)
					stiMapRow.append(None)					
				
			self.cbiMap.append(cbiMapRow)
			self.stiMap.append(stiMapRow)
			
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		n = self.nobytes if self.nobytes >= self.nibytes else self.nibytes
		for byte in range(n):
			for bit in range(8):
				hsz = wx.BoxSizer(wx.HORIZONTAL)
				if bit == 0:
					st = wx.StaticText(self, wx.ID_ANY, "%d:" % byte, size=(20, -1))
				else:
					st = wx.StaticText(self, wx.ID_ANY, "", size=(20, -1))
				hsz.Add(st)
				hsz.Add(wx.StaticText(self, wx.ID_ANY, "%d:" % bit, size=(20, -1)))
				
				try:
					cb = self.cboMap[byte][bit]
				except IndexError:
					cb = None
					
				if cb is not None:
					hsz.Add(cb)
					hsz.Add(self.stoMap[byte][bit])
				else:
					try:
						st = self.stoMap[byte][bit]
					except IndexError:
						st = None
						
					if st is None:
						hsz.Add(wx.StaticText(self, wx.ID_ANY, "", size=(200, -1)))
					else:
						hsz.Add(st)
				
				hsz.AddSpacer(30)
				try:
					cb = self.cbiMap[byte][bit]
				except IndexError:
					cb = None
						
				if cb is not None:
					hsz.Add(cb)
					hsz.Add(self.stiMap[byte][bit][0])
					hsz.Add(self.stiMap[byte][bit][1])
					
				vsz.Add(hsz)
				
			vsz.Add(wx.StaticText(self, wx.ID_ANY, "----------------------------------------------------------------------------------------------------------"))		
			
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
			
		self.SetSizer(hsz)
		self.SetupScrolling(scroll_x=False)

	def ClearBits(self):
		for byte in range(self.nobytes):
			for bit in range(8):
				cb = self.cboMap[byte][bit]
				if cb is not None:
					cb.SetValue(False)
		for byte in range(self.nibytes):
			for bit in range(8):
				cb = self.cbiMap[byte][bit]
				if cb is not None:
					cb.SetValue(False)
						
	def GetAddress(self):
		return self.address
	
	def GetOBytes(self, pulseZero=False):
		byteVals = []
		hasPulsed = False
		for byte in range(self.nobytes):
			byteVal = 0
			for bit in range(8):
				cb = self.cboMap[byte][bit]
				if cb is None:
					rv = 0
				else:
					if not pulseZero:
						rv = 1 if cb.IsChecked() else 0
						if rv == 1 and self.outputs[byte][bit][2] == Node.pulsed:
							hasPulsed = True
					else:
						if self.outputs[byte][bit][2] == Node.pulsed:
							rv = 0
						else:
							rv = 1 if cb.IsChecked() else 0

				if rv == 1:
					byteVal += (1 << (7-bit))
					
			byteVals.append(byteVal)
					
		n = self.nobytes if self.nobytes >= self.nibytes else self.nibytes
		while len(byteVals) < n:
			byteVals.append(0)
			
		return bytes(byteVals), hasPulsed
	
	def PutIBytes(self, ibytes):
		for byte in range(self.nibytes):
			for bit in range(8):
				cb = self.cbiMap[byte][bit]
				if cb is not None:
					try:
						cb.SetValue(getBit(ibytes[byte], bit) == 1)
					except:
						cb.SetValue(False)
