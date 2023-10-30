import wx
import os
from glob import glob

         
def GetSnapshotFiles():
    fxp = os.path.join(os.getcwd(), "data", "trackersnapshots", "*.json")
    return [os.path.splitext(os.path.split(x)[1])[0] for x in glob(fxp)]

class ChooseSnapshotDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose snapshot")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        style = wx.CB_DROPDOWN | wx.CB_READONLY    
            
        self.files = GetSnapshotFiles()                
        
        cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=self.files, style=style)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        if len(self.files) > 0:
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
        
    def GetFile(self):
        fn = self.cbItems.GetValue()
        if fn is None or fn == "":
            return None
        
        fn = os.path.join(os.getcwd(), "data", "trackersnapshots", fn+".json")
            
        return fn

        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)

class ChooseSnapshotsDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose snapshot(s) to delete")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        files = GetSnapshotFiles()        
        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=files)
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
            
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        
    def GetFiles(self):
        return self.cbItems.GetCheckedStrings()
