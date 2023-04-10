import json

class Locomotives:
	def __init__(self, rrserver):
		self.locos = rrserver.Get("getlocos", {})
			
	def buildSortKey(self, lid):
		return int(lid)
		
	def getLocoList(self):
		return sorted(list(self.locos.keys()), key=self.buildSortKey)
		
	def getLocoListFull(self):
		ll = sorted(list(self.locos.keys()), key=self.buildSortKey)
		rv = []
		for lid in ll:
			d = self.locos[lid]["desc"]
			if d is None:
				rv.append(lid)
			else:
				rv.append("%s - %s" % (lid, d))
		return rv
		
	def getLoco(self, lId):
		if lId not in self.locos:
			return None
		
		return self.locos[lId]
		
	def getLocoDesc(self, lId):
		if lId not in self.locos:
			return None
		
		try:
			return self.locos[lId]["desc"]
		except:
			return None

