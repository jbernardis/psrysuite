import wx
import time

from tester.settings import Settings
from tester.bus import Bus

from tester.nodes.dell import Dell
from tester.nodes.foss import Foss
from tester.nodes.cornell import Cornell
from tester.nodes.eastjct import EastJct
from tester.nodes.kale import Kale
from tester.nodes.yard import Yard
from tester.nodes.yardsw import YardSw

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
	"Yard" : ( YARD, Yard ),
	"Kale" : ( KALE, Kale ),
	"East Jct" : ( EASTJCT, EastJct ),
	"Cornell" : ( CORNELL, Cornell ),
	"Yard SW" : ( YARDSW, YardSw ),
	"Parsons Jct" : ( PARSONS, None ),
	"Port A" : ( PORTA, None ),
	"Port B" : ( PORTB, None ),
	"Latham" : ( LATHAM, None ),
	"Carlton" : ( CARLTON, None ),
	"Dell" : ( DELL, Dell ),
	"Foss" : ( FOSS, Foss ),
	"Hyde Jct" : ( HYDEJCT, None ),
	"Hyde" : ( HYDE, None ),
	"Shore" : ( SHORE, None ),
	"Krulish" : ( KRULISH, None ),
	"Nassau W" : ( NASSAUW, None ),
	"Nassau E" : ( NASSAUE, None ),
	"Nassau NX" : ( NASSAUNX, None ),
	"Bank" : ( BANK, None ),
	"Cliveden" : ( CLIVEDEN, None ),
	"Green Mtn" : ( GREENMTN, None ),
	"Cliff" : ( CLIFF, None ),
	"Sheffield" : ( SHEFFIELD, None )	
}

def formatInputBytes(inb):
	if inb is None or len(inb) == 0:
		return "No response"
	
	return " ".join(["%02x" % int.from_bytes(b, "little") for b in inb])


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.bus = None
		
		self.SetTitle("PSRY Tester")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)

		self.nodeNames = list(sorted(nodes.keys()))
		
		self.selectedName = self.nodeNames[0]
		self.selectedAddress = nodes[self.selectedName]
		self.nodeList = ["%s - 0x%x" % (n, nodes[n][0]) for n in self.nodeNames]
		
		self.cbNodes = wx.Choicebook(self, wx.ID_ANY)
		self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
	
		for node in self.nodeNames:
			if nodes[node][1] is None:
				win = wx.Panel(self.cbNodes, size=(300, 300))
				wx.StaticText(win, wx.ID_ANY, "%s not yet implemented" % node, (10,10))
			else:
				win = nodes[node][1](self.cbNodes, nodes[node][0])
			
			text = "%s - 0x%x" % (node, nodes[node][0])
			self.cbNodes.AddPage(win, text)
		
		vszr.Add(self.cbNodes, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.bSend = wx.Button(self, wx.ID_ANY, "Send")
		self.Bind(wx.EVT_BUTTON, self.OnBSend, self.bSend)
		
		self.scReps = wx.SpinCtrl(self, wx.ID_ANY, "1")
		self.scReps.SetRange(1,10)
		self.scReps.SetValue(1)
		
		self.bClear = wx.Button(self, wx.ID_ANY, "Clear")
		self.Bind(wx.EVT_BUTTON, self.OnBClear, self.bClear)
		
		vszr.AddSpacer(20)
		
		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		btnszr.AddSpacer(20)
		btnszr.Add(self.bSend)
		btnszr.AddSpacer(5)
		btnszr.Add(self.scReps)
		btnszr.AddSpacer(10)
		btnszr.Add(self.bClear)
		btnszr.AddSpacer(20)
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
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
		self.cbNodes.SetSelection(0)
		self.currentNode = self.cbNodes.GetPage(0)
		self.bus = Bus(self.settings.tty)
		if not self.bus.isOpen():
			self.bSend.Enable(False)
			
	def OnPageChanged(self, event):
		sel = self.cbNodes.GetSelection()
		self.currentNode = self.cbNodes.GetPage(sel)
		event.Skip()
		
	def OnBSend(self, _):
		addr = self.currentNode.GetAddress()
		outb, hasPulsed = self.currentNode.GetOBytes()
		outStr = " ".join(["%02x" % b for b in outb])
		if hasPulsed:
			outb2 = self.currentNode.GetOBytes(pulseZero=True)[0]
			outStr2 = " ".join(["%02x" % b for b in outb2])
			
		reps = self.scReps.GetValue()
		

		for _ in range(reps):
			t = round(time.time()*1000)
			print("%d: sending (%s)" % (t, outStr))
			inb, _ = self.bus.sendRecv(addr, outb, len(outb), swap=False)
			t = round(time.time()*1000)
			print("%d: %s" % (t, formatInputBytes(inb)))
			time.sleep(0.8)
			if hasPulsed:
				t = round(time.time()*1000)
				print("%d: sending (%s)" % (t, outStr2))
				inb, _ = self.bus.sendRecv(addr, outb2, len(outb2), swap=False)
				t = round(time.time()*1000)
				print("%d: %s" % (t, formatInputBytes(inb)))
				time.sleep(0.4)
				
		self.currentNode.PutIBytes(inb)
		
	def OnBClear(self, _):
		self.currentNode.ClearBits()
		
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
		
