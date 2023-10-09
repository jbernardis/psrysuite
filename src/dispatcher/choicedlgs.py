import wx  
import os     
from glob import glob

class ChooseItemDlg(wx.Dialog):
    def __init__(self, parent, trains, allowentry):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.trains = trains
        self.allowentry = allowentry
        if trains:
            if allowentry:
                self.SetTitle("Choose/Enter train IDs file")
            else:
                self.SetTitle("Choose train IDs file")
        else:
            if allowentry:
                self.SetTitle("Choose/Enter loco #s file")
            else:
                self.SetTitle("Choose loco #s file")
        
        self.allowentry = allowentry

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        if allowentry:
            style = wx.CB_DROPDOWN
        else:
            style = wx.CB_DROPDOWN | wx.CB_READONLY    
            
        self.GetFiles()                
        
        cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=self.files, style=style)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        if not allowentry and len(self.files) > 0:
            self.cbItems.SetSelection(0)
        else:
            self.cbItems.SetSelection(wx.NOT_FOUND)
        
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        bOK.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        
        bDelete = wx.Button(self, wx.ID_ANY, "Delete")
        self.Bind(wx.EVT_BUTTON, self.OnDelete, bDelete)
        
        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)
        btnszr.AddSpacer(20)
        btnszr.Add(bDelete)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit();
        
    def GetFiles(self):
        if self.trains:
            fxp = os.path.join(os.getcwd(), "data", "trains", "*.trn")
        else:
            fxp = os.path.join(os.getcwd(), "data", "locos", "*.loco")
        self.files = [os.path.splitext(os.path.split(x)[1])[0] for x in glob(fxp)]
        
    def GetValue(self):
        fn = self.cbItems.GetValue()
        if fn is None or fn == "":
            return None
        
        if self.trains:
            return os.path.join(os.getcwd(), "data", "trains", fn+".trn")
        else:
            return os.path.join(os.getcwd(), "data", "locos", fn+".loco")
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        fn = self.cbItems.GetValue()
        if fn in self.files and self.allowentry:
            dlg = wx.MessageDialog(self, "File '%s' already exists.\n Are you sure you want to over-write it?" % fn,
                "File exists", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            rv = dlg.ShowModal()
            dlg.Destroy()
            if rv == wx.ID_NO:
                return

        self.EndModal(wx.ID_OK)
        
    def OnDelete(self, _):
        dlg = ChooseItemsDlg(self, self.files, self.trains)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            l = dlg.GetValue()
            
        dlg.Destroy()
        if rc != wx.ID_OK:
            return 

        if len(l) == 0:
            return 
                
        for fn in l:
            if self.trains:
                path = os.path.join(os.getcwd(), "data", "trains", fn+".trn")
            else:
                path = os.path.join(os.getcwd(), "data", "locos", fn+".loco")
            os.unlink(path)
            
        self.GetFiles()
        self.cbItems.SetItems(self.files)
        if not self.allowentry and len(self.files) > 0:
            self.cbItems.SetSelection(0)
        else:
            self.cbItems.SetSelection(wx.NOT_FOUND)

class ChooseItemsDlg(wx.Dialog):
    def __init__(self, parent, items, trains):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        if trains:
            self.SetTitle("Choose train file(s) to delete")
        else:
            self.SetTitle("Choose loco file(s) to delete")

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=items)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
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
        self.Fit();

class ChooseBlocksDlg(wx.Dialog):
    def __init__(self, parent, tid, blocklist):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.SetTitle("Sever from train %s" % tid)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        st = wx.StaticText(self, wx.ID_ANY, "Choose blocks to sever")
        vszr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)
        
        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=list(blocklist.keys()))
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
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
        self.Fit();
        
    def GetResults(self):
        return self.cbItems.GetCheckedStrings()
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        

class ChooseTrainDlg(wx.Dialog):
    def __init__(self, parent, tid, trainlist):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.SetTitle("Choose train")

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        st = wx.StaticText(self, wx.ID_ANY, "Choose train to merge with %s" % tid)
        vszr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)

        cb = wx.ListBox(self, wx.ID_ANY, size=(160, -1), choices=trainlist, style=wx.LB_SINGLE)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
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
        self.Fit();
        
    def GetResults(self):
        idx = self.cbItems.GetSelection()
        if idx == wx.NOT_FOUND:
            return None
        
        return self.cbItems.GetString(idx)
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        
BTNDIM = (80, 40)
   
class ChooseSnapshotActionDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose snapshot sction")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        
        vszr = wx.BoxSizer(wx.VERTICAL)
        
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        
        hszr.AddSpacer(20)
        
        bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnBSave, bSave)
        hszr.Add(bSave)
        
        hszr.AddSpacer(30)
        
        bRestore = wx.Button(self, wx.ID_ANY, "Restore", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnBRestore, bRestore)
        hszr.Add(bRestore)
        
        hszr.AddSpacer(20)
        
        vszr.AddSpacer(20)
        vszr.Add(hszr)
        vszr.AddSpacer(30)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        vszr.Add(bCancel, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
       
        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        
    def OnBSave(self, _):
        self.EndModal(wx.ID_SAVE)
        
    def OnBRestore(self, _):
        self.EndModal(wx.ID_OPEN)
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
       

