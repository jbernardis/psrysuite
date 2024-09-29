import wx  
import os     
import logging

BSIZE = (120, 40)
skipBlocks = ["KOSN10S11", "KOSN20S21"]


class InspectDlg(wx.Dialog):
    def __init__(self, parent, closer, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.CenterOnScreen()
        self.parent = parent
        self.closer = closer
        self.settings = settings
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        self.SetTitle("Inspection Dialog")

        btnszr1 = wx.BoxSizer(wx.VERTICAL)
        btnszr1.AddSpacer(20)

        bLogLevel = wx.Button(self, wx.ID_ANY, "Logging Level", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLogLevel, bLogLevel)
        btnszr1.Add(bLogLevel)

        btnszr1.AddSpacer(10)

        bDebug = wx.Button(self, wx.ID_ANY, "Debugging Flags", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBDebug, bDebug)
        btnszr1.Add(bDebug)

        btnszr1.AddSpacer(20)

        btnszr2 = wx.BoxSizer(wx.VERTICAL)
        btnszr2.AddSpacer(20)

        bProxies = wx.Button(self, wx.ID_ANY, "OS Proxies", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBProxies, bProxies)
        btnszr2.Add(bProxies)

        btnszr2.AddSpacer(10)

        bRelays = wx.Button(self, wx.ID_ANY, "Stop Relays", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBRelays, bRelays)
        btnszr2.Add(bRelays)

        btnszr2.AddSpacer(10)

        bLevers = wx.Button(self, wx.ID_ANY, "Signal Levers", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLevers, bLevers)
        btnszr2.Add(bLevers)

        btnszr2.AddSpacer(20)

        btnszr3 = wx.BoxSizer(wx.VERTICAL)
        btnszr3.AddSpacer(20)

        bToLocks = wx.Button(self, wx.ID_ANY, "Turnout Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBTurnoutLocks, bToLocks)
        btnszr3.Add(bToLocks)

        btnszr3.AddSpacer(10)

        bHandSwitches = wx.Button(self, wx.ID_ANY, "Siding Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBHandSwitches, bHandSwitches)
        btnszr3.Add(bHandSwitches)

        btnszr3.AddSpacer(10)

        bResetBlks = wx.Button(self, wx.ID_ANY, "Reset Blocks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBResetBlks, bResetBlks)
        btnszr3.Add(bResetBlks)

        btnszr3.AddSpacer(20)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        btnszr.AddSpacer(20)
        btnszr.Add(btnszr1)
        btnszr.AddSpacer(10)
        btnszr.Add(btnszr2)
        btnszr.AddSpacer(10)
        btnszr.Add(btnszr3)
        btnszr.AddSpacer(20)

        self.SetSizer(btnszr)
        self.Layout()
        self.Fit()

    def OnBLogLevel(self, _):
        dlg = LogLevelDlg(self)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            dlg.ApplyResults()
        dlg.Destroy()

    def OnBDebug(self, _):
        dlg = DebugFlagsDlg(self, self.settings)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            dlg.ApplyResults()
        dlg.Destroy()

    def OnBProxies(self, _):
        pi = self.parent.GetOSProxyInfo()
        if pi is None:
            pi = []
        dlg = OSProxyDlg(self, pi, self.parent.GetOSProxyInfo)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBRelays(self, _):
        rl = self.GetRelayList()
        if len(rl) == 0:
            dlg = wx.MessageDialog(self, "No stopping relays are presently activated",
                "Stopping Relays",
                wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MultiChoiceDialog( self,
            "Choose stopping relay(s) to unlock",
            "Stopping Relays", rl)

        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            selections = dlg.GetSelections()
            rlNames = [rl[x] for x in selections]
        else:
            rlNames = []

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        if len(rlNames) == 0:
            return

        for bn in rlNames:
            self.parent.SetStoppingRelays(bn, False)

        dlg = wx.MessageDialog(self, "Deactivated Relays:\n%s" % ", ".join(rlNames),
            "Stopping Relays",
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GetRelayList(self):
        rl = self.parent.Get("stoprelays", {})
        if rl is None:
            return []
        relayList = [self.formatRelayName(rly) for rly in sorted(rl.keys()) if rl[rly]]
        return relayList

    def formatRelayName(self, rn):
        return rn.split(".")[0]

    def OnBLevers(self, _):
        slv = self.GetSignalLeverValues()
        dlg = ListDlg(self, slv, (200, 200), "Signal Levers", self.GetSignalLeverValues)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBTurnoutLocks(self, _):
        lks = self.parent.GetTurnoutLocks()
        toList = [x for x in lks if len(lks[x]) != 0]
        if len(toList) == 0:
            dlg = wx.MessageDialog(self, "No turnouts are presently locked",
                "Turnout Locks",
                wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MultiChoiceDialog( self,
            "Choose turnout(s) to unlock",
            "Turnout Locks", toList)

        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            selections = dlg.GetSelections()
            toNames = [toList[x] for x in selections]
        else:
            toNames = []

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        if len(toNames) == 0:
            return

        for tonm in toNames:
            self.parent.turnouts[tonm].ClearLocks()
            self.parent.turnouts[tonm].Draw()

        dlg = wx.MessageDialog(self, "Unlocked Turnouts:\n%s" % ", ".join(toNames),
            "Turnout Locks",
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GetSignalLeverValues(self):
        sl = self.parent.Get("signallevers", {})
        if sl is None:
            return []

        leverList = ["%-6.6s   %s" % (lvr, self.formatSigLvr(sl[lvr])) for lvr in sorted(sl.keys())]
        return leverList

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

    def OnBHandSwitches(self, _):
        hsv = self.GetHandswitchValues()
        dlg = ListDlg(self, hsv, (260, 200), "Siding Locks", self.GetHandswitchValues)
        dlg.ShowModal()
        dlg.Destroy()

    def GetHandswitchValues(self):
        hsinfo = self.parent.GetHandswitchInfo()
        if hsinfo is None:
            return []
        hsList = ["%-9.9s   %s" % (hs, str(hsinfo[hs])) for hs in sorted(hsinfo.keys())]
        return hsList

    def OnBResetBlks(self, _):
        resetList = []
        blks = sorted([bn for bn, blk in self.parent.blocks.items() if (blk.IsCleared() and bn not in skipBlocks)])
        dlg = CheckListDlg(self, blks, "Choose Block(s) to reset")
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            resetList = dlg.GetCheckedItems()

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        for bn in resetList:
            blk = self.parent.blocks[bn]
            blk.RemoveClearStatus()

    def OnCancel(self, _):
        self.closer()


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
    def __init__(self, parent, data, sz, title, cbRefresh=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.cbRefresh = cbRefresh

        vszr = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

        lb = wx.ListBox(self, wx.ID_ANY, choices=data, size=sz, style=wx.LC_REPORT)
        lb.SetFont(font)
        vszr.Add(lb, 1, wx.ALL, 20)
        self.lb = lb

        if callable(cbRefresh):
            vszr.AddSpacer(20)
            b = wx.Button(self, wx.ID_ANY, "Refresh")
            self.Bind(wx.EVT_BUTTON, self.onBRefresh, b)
            vszr.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
            vszr.AddSpacer(20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def onBRefresh(self, _):
        top = self.lb.GetTopItem()
        r = self.cbRefresh()
        if r is None:
            return

        self.lb.Clear()
        self.lb.SetItems(r)
        self.lb.SetFirstItem(top)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


class OSProxyDlg(wx.Dialog):
    def __init__(self, parent, data, cbRefresh=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "OS Proxies")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.cbRefresh = cbRefresh

        vszr = wx.BoxSizer(wx.VERTICAL)

        lb = OSProxyListCtrl(self, data)
        vszr.Add(lb, 1, wx.ALL, 20)
        self.lb = lb

        if callable(self.cbRefresh):
            vszr.AddSpacer(20)
            b = wx.Button(self, wx.ID_ANY, "Refresh")
            self.Bind(wx.EVT_BUTTON, self.onBRefresh, b)
            vszr.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
            vszr.AddSpacer(20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def onBRefresh(self, _):
        ospdict = self.cbRefresh()
        self.lb.SetData(ospdict)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


class OSProxyListCtrl(wx.ListCtrl):
    def __init__(self, parent, ospdict, cbRefresh=None):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(700, 160), style=wx.LC_REPORT + wx.LC_VIRTUAL)
        self.parent = parent
        self.cbRefresh=cbRefresh
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

    def SetData(self, ospdict):
        self.order = [rname for rname in sorted(ospdict.keys())]
        self.osp = ospdict
        self.SetItemCount(0)
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


class CheckListDlg(wx.Dialog):
    def __init__(self, parent, items, title):
        self.choices = items
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=items)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        bAll = wx.Button(self, wx.ID_ANY, "All")
        self.Bind(wx.EVT_BUTTON, self.OnBAll, bAll)

        bNone = wx.Button(self, wx.ID_ANY, "None")
        self.Bind(wx.EVT_BUTTON, self.OnBNone, bNone)

        btnszr.Add(bAll)
        btnszr.AddSpacer(20)
        btnszr.Add(bNone)

        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)

        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)

        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)

        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)

        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit()

    def OnBAll(self, evt):
        self.cbItems.SetCheckedItems(range(len(self.choices)))

    def OnBNone(self, evt):
        self.cbItems.SetCheckedItems([])

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)

    def GetCheckedItems(self):
        return self.cbItems.GetCheckedStrings()
