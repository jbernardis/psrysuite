import json
import os

class Train:
	def __init__(self, tid):
		self.tid = tid
		self.east = True
		self.steps = []
		self.startblock = None
		self.startsubblock = None
		self.startblocktime = 5000
		
	def SetDirection(self, direction):
		self.east = direction
		
	def GetTrainID(self):
		return self.tid
	
	def IsEast(self):
		return self.east

	def SetSteps(self, steps):
		self.steps = [x for x in steps]
		
	def GetSteps(self):
		return [x for x in self.steps]
	
	def SetStartBlockTime(self, time):
		self.startblocktime = time
		
	def GetStartBlockTime(self):
		return self.startblocktime
	
	def SetStartBlock(self, blk):
		self.startblock = blk
		
	def GetStartBlock(self):
		return self.startblock
	
	def SetStartSubBlock(self, blk):
		self.startsubblock = blk
		
	def GetStartSubBlock(self):
		return self.startsubblock
	
	def ToJSON(self):
		return {self.tid: {"eastbound": self.east, "startblock": self.startblock, "startsubblock": self.startsubblock, "time": self.startblocktime, "steps": self.steps}}
	
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
			tr = self.AddTrain(tid, trData["eastbound"])
			tr.SetStartBlock(trData["startblock"])
			tr.SetStartSubBlock(trData["startsubblock"])
			tr.SetStartBlockTime(trData["time"])
			tr.SetSteps(trData["steps"])
		
	def Save(self):
		TrainsJson = {}
		for tr in self.trainlist:
			TrainsJson.update(tr.ToJSON())
			
		with open(self.fn, "w") as jfp:
			json.dump(TrainsJson, jfp, sort_keys=True, indent=2)
		
	def GetTrainList(self):
		return [tr.GetTrainID() for tr in self.trainlist]
	
	def AddTrain(self, tid, east):
		tr = Train(tid)
		tr.SetDirection(east)
		self.trainlist.append(tr)
		self.trainmap[tid] = tr
		return tr
	
	def DelTrainByTID(self, tid):
		if tid not in self.trainmap:
			return False
		
		del self.trainmap[tid]
		
		newtr = [tr for tr in self.trainlist if tr.GetTrainID() != tid]
		self.trainlist = newtr
		
	def GetTrainById(self, tid):
		if tid not in self.trainmap:
			return None
		
		return self.trainmap[tid]
	