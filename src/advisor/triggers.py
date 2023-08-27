import json
import os

from traineditor.generators import GenerateAR

TriggerPointFront = 'F'  # front of train
TriggerPointRear = 'R'  # rear of train


class Triggers:
	def __init__(self, trainSeq):
		self.trainSeq = trainSeq
		self.triggerTable = {}
		for tr in self.trainSeq:
			trid = tr.GetTrainID()
			trid, script = GenerateAR(tr, None)
			self.triggerTable[trid] = script
			
	def GetOrigin(self, train):			
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["origin"]
			
	def GetTerminus(self, train):			
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["terminus"]

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
