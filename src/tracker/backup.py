
import wx
import os
from zipfile import ZipFile, is_zipfile

TYPE_TRAIN = "train"
TYPE_ORDER = "order"
TYPE_ENGINEER = "engineer"
TYPE_LOCO = "loco"

BTNSZ = (120, 46)

def saveData(parent, settings):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			parent, message="Save data files to zip file ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			zipfile = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		dirs = { TYPE_TRAIN: settings.traindir,
				TYPE_ORDER: settings.orderdir,
				TYPE_ENGINEER: settings.engineerdir,
				TYPE_LOCO: settings.locodir }

		fc = 0
		msg2 = ""
		with ZipFile(zipfile, 'w') as zfp:
			for d in dirs.keys():
				fl = [ f for f in os.listdir(dirs[d]) if os.path.isfile(os.path.join(dirs[d], f)) ]
				for fn in fl:
					fc += 1
					msg2 += "%d: %s\n" % (fc, os.path.join(d, fn))
					zfp.write(os.path.join(dirs[d], fn), arcname=os.path.join(d, fn))
				
		msg1 = "%d files successfully written to\n%s\n\n" % (fc, zipfile)
				
		dlg = wx.MessageDialog(parent, msg1 + msg2, 'Data backup successfully written', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

def isValidBackupFile(fn):
	d, _ = os.path.split(fn)
	return d in [TYPE_TRAIN, TYPE_ORDER, TYPE_ENGINEER, TYPE_LOCO]

def fileExists(fn, settings):
	fqfn = formFileName(fn, settings)
	return os.path.isfile(fqfn)

def formFileName(fn, settings):
	d, f = os.path.split(fn)
	if d == TYPE_TRAIN:
		ddir = settings.traindir
	elif d == TYPE_ORDER:
		ddir = settings.orderdir
	elif d == TYPE_ENGINEER:
		ddir = settings.engineerdir
	elif d == TYPE_LOCO:
		ddir = settings.locodir
		
	return os.path.join(ddir, f)

		
def restoreData(parent, settings):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			parent, message="Restore data files from ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			zf = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		if not is_zipfile(zf):
			dlg = wx.MessageDialog(parent,
				"File %s is not a valid zip file" % zf,
				"Not a zip file",
				wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		fc = 0
		msg2 = ""
		with ZipFile(zf, 'r') as zfp:
			nl  = [n for n in zfp.namelist() if isValidBackupFile(n)]
			dlg = ChooseRestoreFiles(parent, nl)
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				nlFlags = dlg.getValues()
				
			dlg.Destroy()
			if rc != wx.ID_OK:
				return
			
			flct = 0
			for f in nlFlags:
				if f:
					flct += 1
					
			if flct == 0:
				dlg = wx.MessageDialog(parent,
					"No files were chosen for restoration",
					"No Files Chosen",
					wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				return

			exists = []
			for fx in range(len(nl)):
				exists.append(nlFlags[fx] and fileExists(nl[fx], settings))
				
			exct = 0
			for f in exists:
				if f:
					exct += 1
					
			if exct >0:
				exfl = []
				for fx in range(len(nl)):
					if exists[fx]:
						exfl.append(formFileName(nl[fx], settings))

				dlg = ChooseOverwriteFiles(parent, exfl)
				rc = dlg.ShowModal()
				if rc == wx.ID_OK:
					confirm = dlg.getValues()
					
				dlg.Destroy()
				
				if rc != wx.ID_OK:
					return
				
				cx = 0
				for fx in range(len(nl)):
					if exists[fx]:
						nlFlags[fx] = confirm[cx]
						cx += 1
			
			for fx in range(len(nl)):
				if nlFlags[fx]:
					fn = nl[fx]
					dfn = formFileName(fn, settings)
					f = os.path.basename(fn)
						
					data = zfp.read(fn)
					fc += 1
					msg2 += "%d: %s -> %s\n" % (fc, f, dfn)
					with open(dfn, "wb") as ofp:
						ofp.write(data)

		msg1 = "%d files restored from %s\n\n" % (fc, zf)
				
		dlg = wx.MessageDialog(parent, msg1 + msg2, 'Data restore successful', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

class ChooseRestoreFiles(wx.Dialog):
	def __init__(self, parent, files):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Files to Restore")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.files = files

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "Choose Files to restore:")
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		self.fchoices = [y for y in [self.formatName(x) for x in self.files] if y is not None]
		
		clb = wx.CheckListBox(self, wx.ID_ANY, choices=self.fchoices, size=(-1, 200))
		self.Bind(wx.EVT_CHECKLISTBOX, self.onClbFiles, clb)
		self.clbFiles = clb
		hsz.Add(clb)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bCheckAll = wx.Button(self, wx.ID_ANY, "Select\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCheckAllPressed, self.bCheckAll)
		
		self.bUncheckAll = wx.Button(self, wx.ID_ANY, "Unselect\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bUncheckAllPressed, self.bUncheckAll)
		
		vsz.Add(self.bCheckAll)
		vsz.AddSpacer(20)
		vsz.Add(self.bUncheckAll)
		
		hsz.AddSpacer(20)
		hsz.Add(vsz, 0, wx.ALIGN_CENTER_VERTICAL)
		
		vsizer.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(10)
		
		self.stCheckCount = wx.StaticText(self, wx.ID_ANY, " 0 Files Selected")
		vsizer.Add(self.stCheckCount, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bCancel)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()
		
	def formatName(self, fn):
		d, f = os.path.split(fn)
		if d == TYPE_TRAIN:
			fl = "TRAIN"
		elif d == TYPE_ORDER:
			fl = "ORDER"
		elif d == TYPE_ENGINEER:
			fl = "ENGINEER"
		elif d == TYPE_LOCO:
			fl = "LOCO"
		else:
			return None
			
		return "%s: %s" % (fl, f)

	def onClbFiles(self, _):
		self.reportCheckCount()
		
	def reportCheckCount(self):
		ct = 0
		for i in range(len(self.fchoices)):
			if self.clbFiles.IsChecked(i):
				ct += 1
				
		if ct == 1:
			text = " 1 File  Selected"
		else:
			text = "%2d Files Selected" % ct
			
		self.stCheckCount.SetLabel(text)
		
	def bCheckAllPressed(self, _):
		for i in range(len(self.fchoices)):
			self.clbFiles.Check(i, True)
			
		self.reportCheckCount()
		
	def bUncheckAllPressed(self, _):
		for i in range(len(self.fchoices)):
			self.clbFiles.Check(i, False)
			
		self.reportCheckCount()
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)

	def getValues(self):
		return [self.clbFiles.IsChecked(i) for i in range(len(self.fchoices))]
		
		

class ChooseOverwriteFiles(wx.Dialog):
	def __init__(self, parent, files):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Confirm file over-write")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.files = files

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "Confirm files to overwrite:")
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		clb = wx.CheckListBox(self, wx.ID_ANY, choices=self.files, size=(-1, 200))
		self.Bind(wx.EVT_CHECKLISTBOX, self.onClbFiles, clb)
		self.clbFiles = clb
		hsz.Add(clb)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bCheckAll = wx.Button(self, wx.ID_ANY, "Select\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCheckAllPressed, self.bCheckAll)
		
		self.bUncheckAll = wx.Button(self, wx.ID_ANY, "Unselect\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bUncheckAllPressed, self.bUncheckAll)
		
		vsz.Add(self.bCheckAll)
		vsz.AddSpacer(20)
		vsz.Add(self.bUncheckAll)
		
		hsz.AddSpacer(20)
		hsz.Add(vsz, 0, wx.ALIGN_CENTER_VERTICAL)
		
		vsizer.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(10)
		
		self.stCheckCount = wx.StaticText(self, wx.ID_ANY, " 0 Files Selected")
		vsizer.Add(self.stCheckCount, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bCancel)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()
		
		for i in range(len(self.files)):
			self.clbFiles.Check(i, check=True)
		self.reportCheckCount()
			
	def onClbFiles(self, _):
		self.reportCheckCount()
		
	def reportCheckCount(self):
		ct = 0
		for i in range(len(self.files)):
			if self.clbFiles.IsChecked(i):
				ct += 1
				
		if ct == 1:
			text = " 1 File  Selected"
		else:
			text = "%2d Files Selected" % ct
			
		self.stCheckCount.SetLabel(text)
		
	def bCheckAllPressed(self, _):
		for i in range(len(self.files)):
			self.clbFiles.Check(i, True)
			
		self.reportCheckCount()
		
	def bUncheckAllPressed(self, _):
		for i in range(len(self.files)):
			self.clbFiles.Check(i, False)
			
		self.reportCheckCount()
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)

	def getValues(self):
		return [self.clbFiles.IsChecked(i) for i in range(len(self.files))]
