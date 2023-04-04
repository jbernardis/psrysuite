import json

class Locomotives:
	def __init__(self, fn):
		self.filename = fn
		with open(fn, "r") as fp:	
			self.locos = json.load(fp)
			
	def buildSortKey(self, lid):
		return int(lid)
		
	def getLocoList(self):
		return sorted(list(self.locos.keys()), key=self.buildSortKey)
		
	def getLocoListFull(self):
		ll = sorted(list(self.locos.keys()), key=self.buildSortKey)
		return ["%s - %s" % (lid, "" if self.locos[lid]["desc"] is None else self.locos[lid]['desc']) for lid in ll]
		
	def getLoco(self, lId):
		if lId not in self.locos:
			return None
		
		return self.locos[lId]
	
	def delete(self, lId):
		if lId not in self.locos:
			return False
		
		del(self.locos[lId])
		return True
	
	def setDescription(self, lId, desc):
		self.locos[lId] = desc
