
class Locomotives:
	def __init__(self, rrserver):
		self.locos = rrserver.Get("getlocos", {})
		for lid in self.locos:
			self.locos[lid]["limit"] = 0
			
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

	def setLimit(self, lId, aspect):
		if lId not in self.locos:
			return
		

		self.locos[lId]["limit"] = self.aspectToLimit(aspect, self.locos[lId]["prof"])	
		
	def getLimit(self, lId):
		if lId not in self.locos:
			return 0	

		return self.locos[lId]["limit"]
			
	def aspectToLimit(self, aspect, prof):
		if aspect == 0:
			return 0
		elif aspect == 0b011: #clear
			return prof["fast"]
		elif aspect in [ 0b100, 0b110 ]: # Restricting or Approach Slow
			return prof["slow"]
		else:
			return prof["medium"]
		
	def getLocoDesc(self, lId):
		if lId not in self.locos:
			return None
		
		try:
			return self.locos[lId]["desc"]
		except:
			return None

