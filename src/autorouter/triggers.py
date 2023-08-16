import json
import os

from traineditor.generators import GenerateAR

TriggerPointFront = 'F'  # front of train
TriggerPointRear = 'R'  # rear of train


class Triggers:
	def __init__(self, trainSeq):
		self.trainSeq = trainSeq
		with open(os.path.join(os.getcwd(), "data", "arscripts.json"), "r") as jfp:
			self.triggerTable = json.load(jfp)	
			
	def AddTrain(self, trid):
		print("adding train %s to triggers" % trid)
		tr = self.trainSeq.GetTrainById(trid)
		blkseq = tr.GetSteps()
		print("derived sequence for train %s" % trid)
		for b in blkseq:
			print("   %s" % str(b))
		trid, script = GenerateAR(tr, None)
		print("-----------------------------------------------------------------")
		print("train: %s" % trid)
		print("%s" % json.dumps(script, indent=2))
		print("=================================================================")
		print("%s" % json.dumps(self.triggerTable[trid], indent=2))
		
	def RemoveTrain(self, trid):
		print("removing train %s from triggers" % trid)		

	def GetRoute(self, train, block):
		if train not in self.triggerTable:
			return None

		if block not in self.triggerTable[train]:
			return None

		return self.triggerTable[train][block]["route"]

	def GetTriggerPoint(self, train, block):
		if train not in self.triggerTable:
			return TriggerPointFront

		if block not in self.triggerTable[train]:
			return TriggerPointFront

		return self.triggerTable[train][block]["trigger"]
	
	def IsOrigin(self, train, block):
		if train not in self.triggerTable:
			return False
		
		return block == self.triggerTable[train]["origin"]
	
	def GetOrigin(self, train):
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["origin"]
	
	def IsTerminus(self, train, block):
		if train not in self.triggerTable:
			return False
		
		return block == self.triggerTable[train]["terminus"]
	
	def GetTerminus(self, train):
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["terminus"]
