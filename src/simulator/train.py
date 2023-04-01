import json
import os

class Train:
	def __init__(self, tid):
		self.tid = tid
		self.normalLoco = None
		
	def GetTrainID(self):
		return self.tid
	
	def SetNormalLoco(self, loco):
		self.normalLoco = loco
		
	def GetNormalLoco(self):
		return self.normalLoco
	
class Trains:
	def __init__(self, ddir):
		self.fn = os.path.join(ddir, "trains.json") 
		try:
			with open(self.fn, "r") as jfp:
				TrainsJson = json.load(jfp)
		except:
			TrainsJson = {}
			
		self.trainlist = []
		self.trainmap = {}
		for tid, trData in TrainsJson.items():
			tr = self.AddTrain(tid)
			tr.SetNormalLoco(trData["normalloco"])
			
	def __iter__(self):
		self._nx_ = 0
		return self
	
	def __next__(self):
		if self._nx_ >= len(self.trainlist):
			raise StopIteration
		
		nx = self._nx_
		self._nx_ += 1
		return self.trainlist[nx]
		
	def GetTrainList(self):
		return [tr.GetTrainID() for tr in self.trainlist]
	
	def AddTrain(self, tid):
		tr = Train(tid)
		self.trainlist.append(tr)
		self.trainmap[tid] = tr
		return tr
		
	def GetTrainById(self, tid):
		if tid not in self.trainmap:
			return None
		
		return self.trainmap[tid]
	