import wx  
import os     

BSIZE = (120, 40)
class InspectDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.parent = parent
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        self.SetTitle("Inspection Dialog")

        btnszr = wx.BoxSizer(wx.VERTICAL)

        btnszr.AddSpacer(20)

        bProxies = wx.Button(self, wx.ID_ANY, "OS Proxies", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBProxies, bProxies)
        btnszr.Add(bProxies)

        btnszr.AddSpacer(10)

        bRelays = wx.Button(self, wx.ID_ANY, "Stop Relays", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBRelays, bRelays)
        btnszr.Add(bRelays)

        btnszr.AddSpacer(10)

        bLevers = wx.Button(self, wx.ID_ANY, "Signal Levers", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLevers, bLevers)
        btnszr.Add(bLevers)

        btnszr.AddSpacer(20)

        szr = wx.BoxSizer(wx.HORIZONTAL)
        szr.AddSpacer(40)
        szr.Add(btnszr)
        
        szr.AddSpacer(40)
        
        self.SetSizer(szr)
        self.Layout()
        self.Fit()

    def OnBProxies(self, _):
        pi = self.parent.GetOSProxyInfo()
        print(str(pi), flush=True)
        dlg = OSProxyDlg(self, pi)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBRelays(self, _):
        rl = self.parent.Get("stoprelays", {})
        relayList = ["%-6.6s   %s" % (self.formatRelayName(rly), str(rl[rly])) for rly in sorted(rl.keys())]
        dlg = ListDlg(self, "\n".join(relayList), (200, 200), "Stopping Relays")
        dlg.ShowModal()
        dlg.Destroy()

    def formatRelayName(self, rn):
        return rn.split(".")[0]

    def OnBLevers(self, _):
        sl = self.parent.Get("signallevers", {})
        leverList = ["%-6.6s   %s" % (lvr, self.formatSigLvr(sl[lvr])) for lvr in sorted(sl.keys())]
        dlg = ListDlg(self, "\n".join(leverList), (200, 200), "Signal Levers")
        dlg.ShowModal()
        dlg.Destroy()

    def formatSigLvr(self, data):
        dl = 0 if data[0] is None else data[0]
        dc = 0 if data[1] is None else data[1]
        dr = 0 if data[2] is None else data[2]

        callon = " C" if dc != 0 else "  "

        if dl != 0 and dr == 0:
            return "L  " + callon
        elif dl == 0 and dr != 0:
            return "  R" + callon
        elif dl == 0 and dr == 0:
            return " N " + callon
        else:
            return " ? " + callon

    def OnCancel(self, _):
        self.EndModal(wx.ID_EXIT)

class ListDlg(wx.Dialog):
    def __init__(self, parent, data, sz, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent

        vszr = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

        lb = wx.TextCtrl(self, wx.ID_ANY, value=data, size=sz, style=wx.TE_READONLY + wx.TE_MULTILINE)
        lb.SetFont(font)
        vszr.Add(lb, 1, wx.ALL, 20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

class OSProxyDlg(wx.Dialog):
    def __init__(self, parent, data):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "OS Proxies")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent

        vszr = wx.BoxSizer(wx.VERTICAL)

        lb = OSProxyListCtrl(self, data)
        vszr.Add(lb, 1, wx.ALL, 20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

class OSProxyListCtrl(wx.ListCtrl):
    def __init__(self, parent, ospdict):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(700, 160), style=wx.LC_REPORT + wx.LC_VIRTUAL)
        self.parent = parent
        self.order = [rname for rname in sorted(ospdict.keys())]
        self.osp = ospdict

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
        self.SetFont(font)

        self.normalA = wx.ItemAttr()
        self.normalB = wx.ItemAttr()
        self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
        self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

        self.InsertColumn(0, "Route")
        self.SetColumnWidth(0, 160)
        self.InsertColumn(1, "OS")
        self.SetColumnWidth(1, 160)
        self.InsertColumn(2, "Count")
        self.SetColumnWidth(2, 80)
        self.InsertColumn(3, "Segments")
        self.SetColumnWidth(3, 300)

        self.SetItemCount(len(self.order))

    def OnGetItemText(self, item, col):
        rte = self.order[item]

        if col == 0:
            return rte

        elif col == 1:
            return self.osp[rte]["os"]

        elif col == 2:
            return "%d" % self.osp[rte]["count"]

        elif col == 3:
            return ", ".join(self.osp[rte]["segments"])

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.normalB
        else:
            return self.normalA
