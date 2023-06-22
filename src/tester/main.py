import wx
#import os

import json

from tester.bus import Bus
from tester.outbyte import OutByte, EVT_OUTPUTCHANGE
from tester.inbyte import InByte
from tester.choosenode import ChooseNodeDlg

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "", size=(300, 300))
        
        dlg = ChooseNodeDlg(self)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            fn = dlg.GetValue()
            
        dlg.Destroy()
        if rc != wx.ID_OK:
            self.shutdown()
            return
        
        self.ShowMainWindow(fn)

        
    def ShowMainWindow(self, fn):      
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(EVT_OUTPUTCHANGE, self.onOutputChange)
        
        self.obytes = []
        self.ibytes = []
        
        self.tty = "COM4"
        
        self.bus = Bus(self.tty)
        
        with open(fn, "r") as jfp:
            node = json.load(jfp)
        
        self.nobytes = len(node["obytes"])
        self.nibytes = len(node["ibytes"])
        self.outb = [0 for _ in range(self.nobytes)]
        self.inb =  [0 for _ in range(self.nibytes)]
        
        self.address = node["address"]
         
        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.AddSpacer(20)
        
        st = wx.StaticText(self, wx.ID_ANY, "I/O Tester for address 0x%02x (%s)" % (node["address"], node["description"]))
        st.SetFont(font)
        sz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sz.AddSpacer(10)
       
        st = wx.StaticText(self, wx.ID_ANY, "Outputs:")
        st.SetFont(font)
        sz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sz.AddSpacer(10)
        
        osz = wx.BoxSizer(wx.HORIZONTAL)
        for obx in range(self.nobytes):
            ob = OutByte(self, "%d" % obx, obx, node["obytes"][obx])
            self.obytes.append(ob)  
            
            osz.Add(ob, 0, wx.ALL, 10)

        sz.Add(osz) 
                     
        sz.AddSpacer(10)
       
        st = wx.StaticText(self, wx.ID_ANY, "Inputs:")
        st.SetFont(font)
        sz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sz.AddSpacer(10)
        
        isz = wx.BoxSizer(wx.HORIZONTAL)
        for ibx in range(self.nibytes):
            ib = InByte(self, "%d" % ibx, ibx, node["ibytes"][ibx])
            self.ibytes.append(ib)  
            
            isz.Add(ib, 0, wx.ALL, 10)

        sz.Add(isz)        
        sz.AddSpacer(20)
        
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        bsz.AddSpacer(20)
        
        self.bSend = wx.Button(self, wx.ID_ANY, "Send", size=(100, 46))
        self.Bind(wx.EVT_BUTTON, self.onSend, self.bSend)
        
        bsz.Add(self.bSend)
        
        bsz.AddSpacer(30)
        
        self.scCount = wx.SpinCtrl(self, wx.ID_ANY, "")
        self.scCount.SetRange(1,50)
        self.scCount.SetValue(1)
        
        bsz.Add(self.scCount, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        st = wx.StaticText(self, wx.ID_ANY, "Count")
        st.SetFont(font)
        bsz.AddSpacer(10)
        bsz.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        bsz.AddSpacer(20)

        self.cbContinuous = wx.CheckBox(self, wx.ID_ANY, "Continuous")
        self.cbContinuous.SetFont(font)
        bsz.Add(self.cbContinuous, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        bsz.AddSpacer(100)
        st = wx.StaticText(self, wx.ID_ANY, "Successful:")
        st.SetFont(font)
        bsz.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        self.stSuccess = wx.StaticText(self, wx.ID_ANY, "000")
        self.stSuccess.SetFont(font)
        bsz.Add(self.stSuccess, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        self.stSuccess.SetLabel("  0")
        
        bsz.AddSpacer(20)
        st = wx.StaticText(self, wx.ID_ANY, "Failed:")
        st.SetFont(font)
        bsz.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        self.stFailed = wx.StaticText(self, wx.ID_ANY, "000")
        self.stFailed.SetFont(font)
        bsz.Add(self.stFailed, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        self.stFailed.SetLabel("  0")

        bsz.AddSpacer(20)
        sz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        sz.AddSpacer(20)
        
        self.SetSizer(sz)
        self.Fit()
        
        self.Show()
 
        self.Bind(wx.EVT_TIMER, self.onTicker)
        self.ticker = wx.Timer(self)
        
        if not self.bus.isOpen():
            dlg = wx.MessageDialog(self, "Unable to open serial port %s to railroad" % self.tty,
                                   "Serial Port Exception",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
        
    def onOutputChange(self, evt):
        nv = self.obytes[evt.index].GetValue()
        self.outb[evt.index] = nv
        
    def onSend(self, _):
        self.failedReads = 0
        self.successfulReads = 0
        self.stFailed.SetLabel("%3d" % self.failedReads)
        self.stSuccess.SetLabel("%3d" % self.successfulReads)
        self.runContinuous = self.cbContinuous.IsChecked()
        self.sendCount = self.scCount.GetValue()
        
        if self.sendCount > 1 or self.runContinuous:
            self.ticker.Start(400)
            self.bSend.Enable(False)
            
        self.SendOnce()
        
    def onTicker(self, _):
        self.SendOnce()
        
    def SendOnce(self):
        inbytes = self.bus.sendRecv(self.address, self.outb, self.nobytes)
        if inbytes is None:
            self.failedReads += 1
            self.stFailed.SetLabel("%3d" % self.failedReads)
        else:        
            self.successfulReads += 1
            self.stSuccess.SetLabel("%3d" % self.successfulReads)
            for ibx in range(self.nibytes):
                self.ibytes[ibx].SetValue(inbytes[ibx])
                
        if self.runContinuous:
            if not self.cbContinuous.IsChecked():
                self.ticker.Stop()
                self.bSend.Enable(True)
        else:
            self.sendCount -= 1
            if self.sendCount <= 0:
                self.ticker.Stop()
                self.bSend.Enable(True)
        
    def onClose(self, evt):
        self.shutdown()
        
    def shutdown(self):
        try:
            self.bus.close()
        except:
            pass
        
        try:
            self.Destroy()
        except:
            pass
            

app = wx.App()
frame = MyFrame()
frame.Show(True)
app.MainLoop()
