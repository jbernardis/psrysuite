import json
import os

TriggerPointFront = 'F'  # front of train
TriggerPointRear = 'R'  # rear of train


class Triggers:
	def __init__(self):
		with open(os.path.join(os.getcwd(), "data", "arscripts.json"), "r") as jfp:
			self.triggerTable = json.load(jfp)			

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
