import wx

class ListDlg(wx.Dialog):
    def __init__(self, parent, title, dataList):
        self.parent = parent
        
        wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
        self.SetTitle(title)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        font = wx.Font(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        data = "\n".join(dataList)
        tcList = wx.TextCtrl(self, wx.ID_ANY, data,
                size=(600, 460), style=wx.TE_MULTILINE)
        tcList.SetFont(font)
        tcList.ShowPosition(len(data))
        vsz.Add(tcList)
        vsz.AddSpacer(10)
        
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bExit = wx.Button(self, wx.ID_ANY, "Close")
        self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
        bsz.Add(self.bExit)
        
        vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vsz.AddSpacer(20)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        
        hsz.Add(vsz)
        hsz.AddSpacer(20)
        
        self.SetSizer(hsz)
        
        self.Fit()
        self.Layout()

    def OnClose(self, _):
        self.DoClose()
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        
    def OnBExit(self, _):
        self.DoClose()
        
    def DoClose(self):
        self.EndModal(wx.ID_CANCEL)
