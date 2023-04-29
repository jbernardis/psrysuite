import wx
import os
import winshell
import sys
import glob

from config.cleandlg import CleanDlg

GENBTNSZ = (170, 40)

class GenerateDlg(wx.Dialog):
    def __init__(self, parent, generator):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Generate Shortcuts/Start Menu")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.generator = generator
    
        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        genBox = wx.StaticBox(self, wx.ID_ANY, "Generate Shortcuts")
        topBorder = genBox.GetBordersForSizer()[0]
        boxsizer = wx.BoxSizer(wx.VERTICAL)
        boxsizer.AddSpacer(topBorder)
        
        self.bGenDispatch = wx.Button(genBox, wx.ID_ANY, "Dispatcher", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenDispatch, self.bGenDispatch)
        boxsizer.Add(self.bGenDispatch, 0, wx.ALL, 10)
                
        self.bGenRemoteDispatch = wx.Button(genBox, wx.ID_ANY, "Remote Dispatcher", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenRemoteDispatch, self.bGenRemoteDispatch)
        boxsizer.Add(self.bGenRemoteDispatch, 0, wx.ALL, 10)
                    
        self.bGenSimulation = wx.Button(genBox, wx.ID_ANY, "Simulation", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenSimulation, self.bGenSimulation)
        boxsizer.Add(self.bGenSimulation, 0, wx.ALL, 10)
                    
        self.bGenDisplay = wx.Button(genBox, wx.ID_ANY, "Display", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenDisplay, self.bGenDisplay)
        boxsizer.Add(self.bGenDisplay, 0, wx.ALL, 10)
        
        boxsizer.AddSpacer(20)
                    
        self.bGenThrottle = wx.Button(genBox, wx.ID_ANY, "Throttle", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenThrottle, self.bGenThrottle)
        boxsizer.Add(self.bGenThrottle, 0, wx.ALL, 10)
                    
        self.bGenTracker = wx.Button(genBox, wx.ID_ANY, "Tracker", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenTracker, self.bGenTracker)
        boxsizer.Add(self.bGenTracker, 0, wx.ALL, 10)
                    
        self.bGenEditor = wx.Button(genBox, wx.ID_ANY, "Train Editor", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenEditor, self.bGenEditor)
        boxsizer.Add(self.bGenEditor, 0, wx.ALL, 10)
        
        boxsizer.AddSpacer(20)
                    
        self.bGenServerOnly = wx.Button(genBox, wx.ID_ANY, "Server Only", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenServerOnly, self.bGenServerOnly)
        boxsizer.Add(self.bGenServerOnly, 0, wx.ALL, 10)
                    
        self.bGenDispatcherOnly = wx.Button(genBox, wx.ID_ANY, "Dispatcher Only", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenDispatcherOnly, self.bGenDispatcherOnly)
        boxsizer.Add(self.bGenDispatcherOnly, 0, wx.ALL, 10)
                    
        self.bGenTester = wx.Button(genBox, wx.ID_ANY, "Tester", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBGenTester, self.bGenTester)
        boxsizer.Add(self.bGenTester, 0, wx.ALL, 10)
        
        genBox.SetSizer(boxsizer)
        
        vszr.Add(genBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)
        
        self.cbStartMenu = wx.CheckBox(self, wx.ID_ANY, "Also add to Start menu")
        vszr.Add(self.cbStartMenu, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.cbStartMenu.SetValue(False)
        vszr.AddSpacer(10)
        
        
        self.bClean = wx.Button(self, wx.ID_ANY, "Clean up Shortcuts", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBClean, self.bClean)
        vszr.Add(self.bClean, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(20)

        self.bCleanMenu = wx.Button(self, wx.ID_ANY, "Clean up Start Menu", size=GENBTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBCleanMenu, self.bCleanMenu)
        vszr.Add(self.bCleanMenu, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(10)
        hszr.Add(vszr)
        hszr.AddSpacer(10)
        
        self.SetSizer(hszr)
        self.Fit()
        self.Layout()
        
    def OnBGenDispatch(self, _):
        module = {
            "name": "PSRY Dispatcher",
            "dir":  "launcher",
            "main": "main.py",
            "desc": "Launcher for Local Dispatcher",
            "icon": "dispatch.ico",
            "parameter": "dispatcher"
        }
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenRemoteDispatch(self, _):
        module = {
            "name": "PSRY Remote Dispatcher",
            "dir":  "launcher",
            "main": "main.py",
            "desc": "Launcher for Remote Dispatcher",
            "icon": "dispatch.ico",
            "parameter": "remotedispatcher"
        }
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenSimulation(self, _):
        module = {
            "name": "PSRY Simulation",
            "dir":  "launcher",
            "main": "main.py",
            "desc": "Launcher for Simulation",
            "icon": "dispatch.ico",
            "parameter": "simulation"
        }
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenDisplay(self, _):
        module = {
            "name": "PSRY Display",
            "dir":  "launcher",
            "main": "main.py",
            "desc": "Launcher for Display",
            "icon": "dispatch.ico",
            "parameter": "display"
        }
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenServerOnly(self, _):
        module = {
            "name": "PSRY Server Only",
            "dir":  "rrserver",
            "main": "main.py",
            "desc": "Railroad Server",
            "icon": "server.ico"
        }    
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenDispatcherOnly(self, _):
        module = {
            "name": "PSRY Dispatcher Only",
            "dir":  "dispatcher",
            "main": "main.py",
            "desc": "Dispatcher Only",
            "icon": "dispatch.ico"
        }    
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenThrottle(self, _):
        module = {
            "name": "PSRY Throttle",
            "dir":  "throttle",
            "main": "main.py",
            "desc": "Throttle",
            "icon": "throttle.ico"
        }    
        self.generator(module, self.cbStartMenu.IsChecked())
        
    def OnBGenEditor(self, _):
        module = {
            "name": "PSRY Train Editor",
            "dir":  "traineditor",
            "main": "main.py",
            "desc": "Train Editor",
            "icon": "editor.ico"
        }
        self.generator(module, self.cbStartMenu.IsChecked())

    def OnBGenTester(self, _):
        module = {
            "name": "PSRY Tester Utility",
            "dir":  "tester",
            "main": "main.py",
            "desc": "Tester",
            "icon": "tester.ico"
        }
        self.generator(module, self.cbStartMenu.IsChecked())

    def OnBGenTracker(self, _):
        module = {
            "name": "PSRY Train Tracker",
            "dir":  "tracker",
            "main": "traintracker.py",
            "desc": "Tracker",
            "icon": "tracker.ico"
        }
        self.generator(module, self.cbStartMenu.IsChecked())
        
            
    def OnBClean(self, _):
        desktop = winshell.desktop()
        pathname = os.path.join(desktop, "PSRY*.lnk")
        scList = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(pathname)]
        if len(scList) == 0:
            dlg = wx.MessageDialog(self, "No shortcut files found",
                    'No Shortcuts', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        
        dlg = CleanDlg(self, scList, "shortcuts")
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            rv = dlg.GetResults()

        dlg.Destroy()            
        if rc != wx.ID_OK:
            return 
        
        for p in rv:
            path = os.path.join(desktop, p+".lnk")
            os.unlink(path)
            
    def OnBCleanMenu(self, _):
        pathname = os.path.join(winshell.start_menu(), "Programs", "PSRY", "PSRY*.lnk")
        scList = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(pathname)]
        if len(scList) == 0:
            dlg = wx.MessageDialog(self, "No start menu items found",
                    'No Menu Items', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return 
        
        dlg = CleanDlg(self, scList, "start menu")
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            rv = dlg.GetResults()

        dlg.Destroy()            
        if rc != wx.ID_OK:
            return 
        
        for p in rv:
            path = os.path.join(winshell.start_menu(), "Programs", "PSRY", p+".lnk")
            os.unlink(path)
        
    def OnClose(self, _):
        self.doExit()
        
    def doExit(self):
        self.Destroy()