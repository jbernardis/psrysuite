import wx
import json
import os

from traineditor.traindlg import TrainDlg
from traineditor.train import Trains
from traineditor.blocksequence import BlockSequenceListCtrl
from traineditor.layoutdata import LayoutData
from traineditor.simscriptdlg import SimScriptDlg
from traineditor.arscriptdlg import ARScriptDlg
from traineditor.arblockdlg import ARBlockDlg

SIMSCRIPTFN = "simscripts.json"
ARSCRIPTFN =  "arscripts.json"

def StoppingSection(blk):
	return blk.endswith(".W") or blk.endswith(".E")
		

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.title = "PSRY Train Editor"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.dataDir = os.path.join(os.getcwd(), "data")
		
		self.cbTrain = wx.ComboBox(self, wx.ID_ANY, "", size=(100, -1),
			 choices=[],
			 style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER | wx.CB_SORT)
		self.Bind(wx.EVT_COMBOBOX, self.OnCbTrain, self.cbTrain)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnCbTrainTextEnter, self.cbTrain)
				
		self.chbEast = wx.CheckBox(self, wx.ID_ANY, "EastBound: ")
		self.chbEast.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnChbEastbound, self.chbEast)

		self.teStartBlock = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), style=wx.TE_READONLY)	
		self.teStartBlockTime = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), style=wx.TE_READONLY)	
		
		self.blockSeq = BlockSequenceListCtrl(self, height=200, readonly=True)
		
		
		self.bEditSteps = wx.Button(self, wx.ID_ANY, "Edit\nRoute", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBEditSteps, self.bEditSteps)
		self.bDelTrain = wx.Button(self, wx.ID_ANY, "Delete\nTrain", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBDelTrain, self.bDelTrain)
		
		trsz = wx.BoxSizer(wx.HORIZONTAL)
		trsz.Add(wx.StaticText(self, wx.ID_ANY, "Train: "), 0, wx.TOP, 5)
		trsz.AddSpacer(5)
		trsz.Add(self.cbTrain)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
		self.bRevert = wx.Button(self, wx.ID_ANY, "Revert", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBRevert, self.bRevert)
		self.bGenSim = wx.Button(self, wx.ID_ANY, "Sim/ATC\nScript", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBGenSim, self.bGenSim)
		self.bGenSim.Enable(False)
		self.bGenAR = wx.Button(self, wx.ID_ANY, "AR/Advisor\nScript", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBGenAR, self.bGenAR)
		self.bGenAR.Enable(False)
		self.bGenSimAll = wx.Button(self, wx.ID_ANY, "Sim/ATC\nAll", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBGenSimAll, self.bGenSimAll)
		self.bGenARAll = wx.Button(self, wx.ID_ANY, "AR/Advisor\nAll", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBGenARAll, self.bGenARAll)
		
		buttonsz = wx.BoxSizer(wx.HORIZONTAL)
		buttonsz.AddSpacer(10)
		buttonsz.Add(self.bGenSim)
		buttonsz.AddSpacer(10)
		buttonsz.Add(self.bGenSimAll)
		buttonsz.AddSpacer(30)
		buttonsz.Add(self.bGenAR)
		buttonsz.AddSpacer(10)
		buttonsz.Add(self.bGenARAll)
		buttonsz.AddSpacer(30)
		buttonsz.Add(self.bSave)
		buttonsz.AddSpacer(20)
		buttonsz.Add(self.bRevert)
		buttonsz.AddSpacer(50)
		buttonsz.Add(self.bExit)
		buttonsz.AddSpacer(10)
		
		vszl = wx.BoxSizer(wx.VERTICAL)
		vszl.AddSpacer(20)
		vszl.Add(trsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszl.AddSpacer(20)
		vszl.Add(self.chbEast, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszl.AddSpacer(20)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(10)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Starting Block: "))
		hsz.AddSpacer(5)
		hsz.Add(self.teStartBlock)
		hsz.AddSpacer(10)
		hsz.Add(wx.StaticText(self, wx.ID_ANY, "Time: "))
		hsz.AddSpacer(5)
		hsz.Add(self.teStartBlockTime)
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(10)
		vszr.Add(self.blockSeq)
		vszr.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bEditSteps)
		hsz.AddSpacer(20)
		hsz.Add(self.bDelTrain)
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vszl)
		hsz.AddSpacer(20)
		hsz.Add(vszr)
		hsz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		vsz.Add(buttonsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		self.layout = LayoutData(self.dataDir)
		wx.CallAfter(self.Initialize)
		
	def Initialize(self):
		self.selectedTrain = None
		self.modified = False
		self.ShowTitle()
		self.EnableButtons(False)
		self.loadTrains()
		self.SetTrainChoices(self.trains.GetTrainList())
		
	def EnableButtons(self, flag=True):
		self.bEditSteps.Enable(flag)
		
	def loadTrains(self):
		self.trains = Trains(self.dataDir)
		
	def SetTrainChoices(self, trlist=None):
		if trlist is not None:
			self.trainChoices = sorted([x for x in trlist])
			
		self.cbTrain.SetItems(self.trainChoices)
		if self.selectedTrain is not None:
			try:
				tx = self.trainChoices.index(self.selectedTrain)
			except ValueError:
				self.selectedTrain = None
				
		if self.selectedTrain is None and len(self.trainChoices) > 0:
			tx = 0
			self.UpdateTrainSelection(self.trainChoices[0])
		elif self.selectedTrain is None:
			self.UpdateTrainSelection(None)
				
		if self.selectedTrain is not None:
			self.cbTrain.SetSelection(tx)
			
		self.bDelTrain.Enable(self.selectedTrain is not None)
		self.bGenAR.Enable(self.selectedTrain is not None)
		self.bGenSim.Enable(self.selectedTrain is not None)
				
	def AddTrainChoice(self, newtid):
		if newtid in self.trainChoices:
			return False
		
		dlg = wx.MessageDialog(self, "Train %s does not yet exist.\nDo you wish to add it?" % newtid, 'Train does not exist', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if rc != wx.ID_YES:
			self.SetTrainChoices()
			return False
		
		self.trainChoices.append(newtid)
		self.selectedTrain = newtid
		self.trainChoices = sorted(self.trainChoices)
		self.trains.AddTrain(newtid, self.chbEast.IsChecked())
		self.SetTrainChoices()
		
		self.SetModified()
		
		return True

	def ShowTitle(self):
		titleString = self.title
		if self.modified:
			titleString += " *"
		self.SetTitle(titleString)
		
	def OnCbTrain(self, evt):
		tx = self.cbTrain.GetSelection()
		if tx is None or tx == wx.NOT_FOUND:
			tid = None
		else:
			tid = self.cbTrain.GetString(tx)

		self.UpdateTrainSelection(tid)
	
	def OnCbTrainTextEnter(self, evt):
		tid = evt.GetString()
		self.UpdateTrainSelection(tid)
		
	def UpdateTrainSelection(self, tid):
		if tid is None:
			self.EnableButtons(False)
			self.currentTrain = None
			self.blockSeq.SetItems([])
			return
		if tid not in self.trainChoices:
			if not self.AddTrainChoice(tid):
				if self.currentTrain is None:
					self.EnableButtons(False)
					self.currentTrain = None
					self.blockSeq.SetItems([])
					return

				self.selectedTrain = self.currentTrain.GetTrainID()
			else:
				self.selectedTrain = tid
		else:
			self.selectedTrain = tid
			
		self.EnableButtons(True)

		tr = self.trains.GetTrainById(self.selectedTrain)
		self.currentTrain = tr
		
		self.chbEast.SetValue(tr.IsEast())
		
		self.blockSeq.SetItems(self.currentTrain.GetSteps())
		self.startBlock = self.currentTrain.GetStartBlock()
		self.startSubBlock = self.currentTrain.GetStartSubBlock()
		self.startBlockTime = self.currentTrain.GetStartBlockTime()

		self.ShowStartBlock()
		
	def ShowStartBlock(self):		
		if self.startBlock is not None:
			if self.startSubBlock is None:
				sbString = self.startBlock
			else:
				sbString = "%s(%s)" % (self.startBlock, self.startSubBlock)
				
			self.teStartBlock.SetValue(sbString)
		else:
			self.teStartBlock.SetValue("")
		self.teStartBlockTime.SetValue("%d" % self.startBlockTime)
			
	def OnChbEastbound(self, evt):
		self.currentTrain.SetDirection(self.chbEast.IsChecked())
		self.SetModified()

	def OnBEditSteps(self, _):
		dlg = TrainDlg(self, self.currentTrain, self.layout)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			results = dlg.GetResults()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.currentTrain.SetSteps(results["steps"])
		self.currentTrain.SetStartBlock(results["startblock"])
		self.currentTrain.SetStartSubBlock(results["startsubblock"])
		self.currentTrain.SetStartBlockTime(results["time"])
		self.blockSeq.SetItems(self.currentTrain.GetSteps())
		self.startBlock = self.currentTrain.GetStartBlock()
		self.startSubBlock = self.currentTrain.GetStartSubBlock()
		self.startBlockTime = self.currentTrain.GetStartBlockTime()
		self.ShowStartBlock()
		self.SetModified()
		
	def OnBDelTrain(self, _):
		if self.currentTrain is None:
			return
		
		tid = self.currentTrain.GetTrainID()
		dlg = wx.MessageDialog(self, "Are you sure you want to delete train %s?\nPress \"Yes\" to continue,\nor \"No\" to cancel." % tid,
				'Confirm train deletion', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		self.trainChoices.remove(tid)
		self.trains.DelTrainByTID(tid)
		self.SetTrainChoices()
		
		self.SetModified()

	def OnBGenSimAll(self, _):
		allSim = {}
		for tr in self.trains:
			if tr.GetNSteps() > 0:
				_, scr = self.GenSim(tr)
				allSim.update(scr)
		
		fn = os.path.join(os.getcwd(), "data", SIMSCRIPTFN)
		with open(fn, "w") as jfp:
			json.dump(allSim, jfp, indent=2)

	def OnBGenSim(self, _):
		# TODO; need to do sometning about loco number.  Do we put it here, or should it be put inmy the simulator?
		# TODO - train length
		trainid, scr = self.GenSim(self.currentTrain)
		scrString = json.dumps(scr, indent=2)
		dlg = SimScriptDlg(self, scrString, trainid)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			fn = os.path.join(os.getcwd(), "data", SIMSCRIPTFN)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				j = {}
			j.update(scr)
			
			with open(fn, "w") as jfp:
				json.dump(j, jfp, indent=2)
									
		dlg.Destroy()
		
	def GenSim(self, tr):
		locoid = 0
		trainid = tr.GetTrainID()
		east = tr.IsEast()
		segTimes, segString = self.determineSegmentsAndTimes(tr.GetStartBlock(), None, east, tr.GetStartBlockTime())
		sBlk = tr.GetStartBlock()
		subBlk = tr.GetStartSubBlock()
		#if subBlk is not None:
			#sBlk = subBlk
			
		# determine which segment is our starting position and ignore the seqments before it in the list
		for idx in range(len(segTimes)):
			if sBlk == segTimes[idx][0]:
				break
		else:
			idx = 0
			
		script = []
		placeTrainCmd = {"block": sBlk, "name": trainid, "loco": locoid, "time": segTimes[idx][1], "length": 3}
		if subBlk is not None:
			placeTrainCmd["subblock"] = segTimes[idx][0]
			
		script.append({"placetrain": placeTrainCmd})

		idx += 1
		while idx < len(segTimes):
			script.append({"movetrain": {"block": segTimes[idx][0], "time": segTimes[idx][1]}})
			idx += 1

		blkSeq = tr.GetSteps()
		nblocks = len(blkSeq)
		bx = 0
		for b in blkSeq:
			bx += 1
			terminus = bx == nblocks
			segTimes, segString = self.determineSegmentsAndTimes(b["block"], b["os"], east, b["time"], terminus=terminus)

			script.append({"waitfor": {"signal": b["signal"], "route": b["route"], "os": segTimes[0][0], "block": segString}})
			
			script.append({"movetrain": {"block": segTimes[0][0], "time": segTimes[0][1]}})
			for seg, tm in segTimes[1:]:
				script.append({"movetrain": {"block": seg, "time": tm}})

		scr = {"%s" % trainid: script}
		return trainid, scr
		
		
	def determineSegmentsAndTimes(self, block, os, east, blockTime, terminus=False):
		subBlocks = self.layout.GetSubBlocks(block)
		if len(subBlocks) == 0:
			subBlocks = [block]  # no sub-blocks - just use the block name itself
		stopBlocks = self.layout.GetStopBlocks(block)
		
		blks = []
		waitblks = []
		subCt = len(subBlocks)
		stopCt = 0
		if east:
			if stopBlocks[1]:
				stopCt += 1
				blks.append(stopBlocks[1])
				waitblks.append(stopBlocks[1])
			blks.extend(subBlocks) # TODO: one of these will need to be reversed
			waitblks.append(block)
			if stopBlocks[0] and not terminus: # Don't include stop block in terminus'
				stopCt += 1
				blks.append(stopBlocks[0])
				waitblks.append(stopBlocks[0])
		else:
			if stopBlocks[0]:
				stopCt += 1
				blks.append(stopBlocks[0])
				waitblks.append(stopBlocks[0])
			blks.extend(subBlocks) # one of these will need to be reversed
			waitblks.append(block)
			if stopBlocks[1] and not terminus: # Don't include stop block in terminus:
				stopCt += 1
				blks.append(stopBlocks[1])
				waitblks.append(stopBlocks[1])

		waitString = ",".join(waitblks) # segment string should NOT include the os
		if os is not None:
			blks.insert(0, os)
			subCt += 1
		stopTime = int(blockTime * 0.1)
		subTime = int((blockTime - stopTime * stopCt) / subCt)
		segTimes = [[blk, stopTime if StoppingSection(blk) else subTime] for blk in blks]
		
		return segTimes,waitString

	def OnBGenARAll(self, _):
		allAR = {}
		for tr in self.trains:
			if tr.GetNSteps() > 0:
				_, scr = self.GenAR(tr, None)
				allAR.update(scr)
		
		#print(json.dumps(allAR, indent=2))
		fn = os.path.join(os.getcwd(), "data", ARSCRIPTFN)
		with open(fn, "w") as jfp:
			json.dump(allAR, jfp, indent=2)
		
	def OnBGenAR(self, _):
		# TODO: we may not want to autproute at every OS - need a way to check the ones we do want
		blist = []
		lb = self.startBlock
		for b in self.blockSeq.GetBlocks():
			blist.append("%s => %s" % (lb, b["block"]))
			lb = b["block"]

		dlg = ARBlockDlg(self, blist)
		dlg.ShowModal()
		blist = dlg.GetResults()
		dlg.Destroy()
		
		blks = [self.blockSeq.GetBlocks()[b]["block"] for b in blist]
		
		trainid, scr = self.GenAR(self.currentTrain, blks)
		
		scrString = json.dumps(scr, indent=2)
		dlg = ARScriptDlg(self, scrString, trainid)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			fn = os.path.join(os.getcwd(), "data", ARSCRIPTFN)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				j = {}
			j.update(scr)
			
			with open(fn, "w") as jfp:
				json.dump(j, jfp, indent=2)
			
		dlg.Destroy()

	def GenAR(self, tr, blks):		
		trainid = tr.GetTrainID()
		lastBlock = tr.GetStartBlock()
		blkSeq = tr.GetSteps()
		script = {}
		for b in blkSeq:
			if len(script) == 0:
				script["origin"] = lastBlock
				
			if blks is None or b["block"] in blks:
				trigger = 'F' if b["trigger"] == "Front" else 'B'			
				script[lastBlock] = {"route": b["route"], "trigger": trigger}
			lastBlock = b["block"]
			
		script["terminus"] = lastBlock

		scr = {"%s" % trainid: script}
		return trainid, scr
		
	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()
		
	def OnBSave(self, _):
		self.trains.Save()
		self.SetModified(False)
		
	def OnBExit(self, _):
		self.doExit()
		
	def OnBRevert(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train(s) have been modified.\nAre you sure you want to revert without saving?\nPress "Yes" to revert and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
		
		self.Initialize()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train(s) have been modified.\nAre you sure you want to exit without saving?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
		self.Destroy()
		
