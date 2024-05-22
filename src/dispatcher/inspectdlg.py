import wx  
import os     
import logging

BSIZE = (120, 40)
class InspectDlg(wx.Dialog):
    def __init__(self, parent, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.CenterOnScreen()
        self.parent = parent
        self.settings = settings
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        self.SetTitle("Inspection Dialog")

        btnszr = wx.BoxSizer(wx.VERTICAL)

        btnszr.AddSpacer(20)

        bLogLevel = wx.Button(self, wx.ID_ANY, "Logging Level", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLogLevel, bLogLevel)
        btnszr.Add(bLogLevel)

        btnszr.AddSpacer(20)

        bDebug = wx.Button(self, wx.ID_ANY, "Debugging Flags", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBDebug, bDebug)
        btnszr.Add(bDebug)

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

    def OnBLogLevel(self, _):
        dlg = LogLevelDlg(self)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            dlg.ApplyResults()
            dlg.Destroy()
            self.EndModal(wx.ID_EXIT)
        else:
            dlg.Destroy()

    def OnBDebug(self, _):
        dlg = DebugFlagsDlg(self, self.settings)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            dlg.ApplyResults()
            dlg.Destroy()
            self.EndModal(wx.ID_EXIT)
        else:
            dlg.Destroy()

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


class DebugFlagsDlg(wx.Dialog):
    def __init__(self, parent, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Debugging Flags")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.settings = settings

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        self.cbEvalAspect = wx.CheckBox(self, wx.ID_ANY, "Show aspect calculation")
        vszr.Add(self.cbEvalAspect)
        self.cbEvalAspect.SetValue(self.settings.debug.showaspectcalculation)

        vszr.AddSpacer(10)

        self.cbBlockOccupancy = wx.CheckBox(self, wx.ID_ANY, "Block Occupancy")
        vszr.Add(self.cbBlockOccupancy)
        self.cbBlockOccupancy.SetValue(self.settings.debug.blockoccupancy)

        vszr.AddSpacer(10)

        self.cbTrainID = wx.CheckBox(self, wx.ID_ANY, "Train Identification")
        vszr.Add(self.cbTrainID)
        self.cbTrainID.SetValue(self.settings.debug.identifytrain)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
        btnszr.Add(self.bOK)

        btnszr.AddSpacer(20)

        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)
        btnszr.Add(self.bCancel)

        vszr.AddSpacer(20)
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
        self.CenterOnScreen()

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def OnOK(self, _):
        self.EndModal(wx.ID_OK)

    def ApplyResults(self):
        messages = []
        nv = self.cbEvalAspect.GetValue()
        if nv != self.settings.debug.showaspectcalculation:
            self.settings.debug.showaspectcalculation = nv
            messages.append("Show Aspect Calculation => %s" % nv)

        nv = self.cbBlockOccupancy.GetValue()
        if nv != self.settings.debug.blockoccupancy:
            self.settings.debug.blockoccupancy = nv
            messages.append("Block Occupancy => %s" % nv)

        nv = self.cbTrainID.GetValue()
        if nv != self.settings.debug.identifytrain:
            self.settings.debug.identifytrain = nv
            messages.append("Train Identification => %s" % nv)

        if len(messages) == 0:
            dlg = wx.MessageDialog(self, "No Flags Changed",
                                   "No Changes",
                                   wx.OK | wx.ICON_INFORMATION
                                   )
        else:
            dlg = wx.MessageDialog(self, "\n".join(messages),
                                   "Flags Modified",
                                   wx.OK | wx.ICON_INFORMATION
                                   )
        dlg.ShowModal()
        dlg.Destroy()



class LogLevelDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Set Log Level")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.CenterOnScreen()

        vszr = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

        self.logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.logLevelValues = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        self.rbMode = wx.RadioBox(self, wx.ID_ANY, "Log Level", choices=self.logLevels,
                                  majorDimension=1, style=wx.RA_SPECIFY_COLS)
        vszr.AddSpacer(20)
        vszr.Add(self.rbMode, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        l = logging.getLogger().getEffectiveLevel()
        try:
            lvl = self.logLevelValues.index(l)
        except ValueError:
            lvl = 4
        self.rbMode.SetSelection(lvl)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
        btnszr.Add(self.bOK)

        btnszr.AddSpacer(20)

        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)
        btnszr.Add(self.bCancel)

        vszr.AddSpacer(20)
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit();

    def OnOK(self, _):
        self.EndModal(wx.ID_OK)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def ApplyResults(self):
        lvl = self.rbMode.GetSelection()
        logging.getLogger().setLevel(self.logLevelValues[lvl])

        dlg = wx.MessageDialog(self, "Logging Level has been set to %s" % self.logLevels[lvl],
                               "Logging Level Changed",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Destroy()


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