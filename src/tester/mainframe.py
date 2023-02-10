import wx
import os

from tester.hexctrl import HexCtrl

from tester.settings import Settings
from tester.bus import Bus

# district node addresses
YARD      = 0x11
KALE      = 0x12
EASTJCT   = 0x13
CORNELL   = 0x14
YARDSW    = 0x15
PARSONS   = 0x21
PORTA     = 0x22
PORTB     = 0x23
LATHAM    = 0x31
CARLTON   = 0x32
DELL      = 0x41
FOSS      = 0x42
HYDEJCT   = 0x51
HYDE      = 0x52
SHORE     = 0x61
KRULISH   = 0x71
NASSAUW   = 0x72
NASSAUE   = 0x73
NASSAUNX  = 0x74
BANK      = 0x81
CLIVEDEN  = 0x91
GREENMTN  = 0x92
CLIFF     = 0x93
SHEFFIELD = 0x95

nodes = {
	"Yard" : YARD,
	"Kale" : KALE,
	"East Jct" : EASTJCT,
	"Cornell" : CORNELL,
	"Yard SW" : YARDSW,
	"Parsons Jct" : PARSONS,
	"Port A" : PORTA,
	"Port B" : PORTB,
	"Latham" : LATHAM,
	"Carlton" : CARLTON,
	"Dell" : DELL,
	"Foss" : FOSS,
	"Hyde Jct" : HYDEJCT,
	"Hyde" : HYDE,
	"Shore" : SHORE,
	"Krulish" : KRULISH,
	"Nassau W" : NASSAUW,
	"Nassau E" : NASSAUE,
	"Nassau NX" : NASSAUNX,
	"Bank" : BANK,
	"Cliveden" : CLIVEDEN,
	"Green Mtn" : GREENMTN,
	"Cliff" : CLIFF,
	"Sheffield" : SHEFFIELD	
}

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.bus = None
		
		self.title = "PSRY Tester"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.sendZeroTimer = wx.Timer()
		self.Bind(wx.EVT_TIMER, self.SendZeros)
		
		self.dataDir = os.path.join(os.getcwd(), "data")
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)

		self.nodeNames = list(sorted(nodes.keys()))
		
		self.selectedName = self.nodeNames[0]
		self.selectedAddress = nodes[self.selectedName]
		self.nodeList = ["0x%x - %s" % (nodes[n], n) for n in self.nodeNames]
		
		self.cbNode = wx.ComboBox(self, wx.ID_ANY, self.nodeList[0],
						 size=(100, -1), choices=self.nodeList,
						 style=wx.CB_DROPDOWN | wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.cbNode)

		vszr.Add(wx.StaticText(self, wx.ID_ANY, "Node Address:"), 0, wx.ALIGN_CENTER_HORIZONTAL)		
		vszr.Add(self.cbNode, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)
		
		vszr.Add(wx.StaticText(self, wx.ID_ANY, "Data to send:"), 0, wx.ALIGN_CENTER_HORIZONTAL)		
		self.tcSend = HexCtrl(self, wx.ID_ANY, "", size=(100, -1))
		vszr.Add(self.tcSend, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)
		
		vszr.Add(wx.StaticText(self, wx.ID_ANY, "Data received:"), 0, wx.ALIGN_CENTER_HORIZONTAL)		
		self.tcRecv = wx.TextCtrl(self, wx.ID_ANY, "", size=(100, -1), style=wx.CB_READONLY)
		vszr.Add(self.tcRecv, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbSendZero = wx.CheckBox(self, wx.ID_ANY, "Send zeros after ")
		self.scMillis = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scMillis.SetRange(1,5000)
		self.scMillis.SetValue(500)

		hsz.Add(self.cbSendZero)
		hsz.Add(self.scMillis)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "milliseconds"))
		
		vszr.AddSpacer(20)
		vszr.Add(hsz)

		vszr.AddSpacer(20)
		self.bSend = wx.Button(self, wx.ID_ANY, "Send")
		self.Bind(wx.EVT_BUTTON, self.OnBSend, self.bSend)
		vszr.Add(self.bSend, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(40)
		hszr.Add(vszr)
		hszr.AddSpacer(40)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)
		
	def Initialize(self):
		self.settings = Settings()
		self.bus = Bus(self.settings.tty)
		if not self.bus.isOpen():
			self.bSend.Enable(False)
		
	def EvtComboBox(self, _):
		nx = self.cbNode.GetSelection()
		if nx == wx.NOT_FOUND:
			return
		
		self.selectedName = self.nodeNames[nx]
		self.selectedAddress = nodes[self.selectedName]
		
	def OnBSend(self, _):
		if self.Validate() and self.TransferDataFromWindow():
			dstr = self.tcSend.GetValue()
			
			nbytes = int(len(dstr)/2)
			outb = []
			for b in range(nbytes):
				byteStr = dstr[b*2:b*2+2]
				outb.append(int(byteStr, 16))
				
			inb, inbc = self.bus.sendRecv(self.selectedAddress, outb, nbytes, swap=False)
	
			inbstr = []			
			for b in inb:
				inbstr.append("%02x" % b)
				
			self.tcRecv.SetValue("".join(inbstr))
			
			if self.cbSendZero.IsChecked():
				self.zeroCount = nbytes
				msec = self.scMillis.GetValue()
				self.sendZeroTimer.StartOnce(msec)
			
	def SendZeros(self, _):
		outb = [0 for _ in range(self.zeroCount)]
		inb, inbc = self.bus.sendRecv(self.selectedAddress, outb, self.zeroCount, swap=False)
		inbstr = []			
		for b in inb:
			inbstr.append("%02x" % b)
			
		dlg = wx.MessageDialog(self, "Response = (%s)" % "".join(inbstr),
							'Zeros sent', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBExit(self, _):
		self.doExit()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		if self.bus is not None:
			try:
				self.bus.close()
			except:
				pass
		
		self.Destroy()
		
