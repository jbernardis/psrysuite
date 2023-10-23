
ST_FWD    = "f"
ST_FWD128 = "F"
ST_REV    = "r"
ST_REV128 = "R"
ST_STOP   = "s"
ST_ESTOP  = "e"

class ActiveTrainList:
	def __init__(self):
		self.trains = {}
		self.order = []
		self.displays = {}
		
	def addDisplay(self, tag, lc):
		self.displays[tag] = lc
		lc.setAtl(self)
		lc.setSortHeaders(self.sortKey, self.sortGroupDir, self.sortAscending)
		
	def removeDisplay(self, tag):
		try:
			del(self.displays[tag])
		except:
			pass
		
	def count(self):
		return len(self.order)
	
	def clear(self):
		self.trains = {}
		self.order = []
		self.refreshDisplays()
		
	def addTrain(self, at):

		self.trains[at.tid] = at
		self.order.append(at.tid)
		self.sortTrains()
		
	def delTrain(self, tx):
		if tx < 0 or tx >= len(self.order):
			return
		
		tid = self.order[tx]
		del(self.order[tx])
		del(self.trains[tid])
		self.refreshDisplays()
		
	def updateTrain(self, tid, loco, desc, block, ndir):
		if tid not in self.order:
			return
		
		if tid not in self.trains.keys():
			return
		
		at = self.trains[tid]
		
		if loco is not None:
			if at.loco != loco:
				at.loco = loco
				at.speed = 0
				at.limit = None
				at.throttle = None

		if block is not None:
			if at.block != block:
				at.highlight = 5 # 5 second highlight time
				at.block = block
				
		if ndir:
			at.SetEast(ndir)
				
		if desc is not None:
			at.ldesc = desc
			
		try:
			tx = self.order.index(tid)
		except:
			tx = None
			
		if tx is not None:
			self.refreshDisplays(tx)
			
	def setNewEngineer(self, tid, neng):
		if tid not in self.order:
			return
		
		if tid not in self.trains.keys():
			return
	
		at = self.trains[tid]
		at.engineer = neng
		
		try:
			tx = self.order.index(tid)
		except:
			tx = None
			
		if tx is not None:
			self.refreshDisplays(tx)
			
	def setThrottle(self, loco, throttle, speedType):
		for at in self.trains.values():
			if at.loco == loco:
				at.throttle = self.formatThrottle(throttle, speedType)
				at.speed = throttle
				if at.speed != 0:
					at.hasStarted = True
					at.stopTime = None
				else:
					if at.hasStarted:
						if at.stopTime is None:
							at.stopTime = 0

				try:
					tx = self.order.index(at.tid)
				except:
					tx = None
					
				if tx is not None:
					self.refreshDisplays(tx)
				return
			
	def formatThrottle(self, speed, speedType):
		speedStr = "%3d" % int(speed)
	
		if speedType == ST_FWD128:
			return speedStr
		elif speedType == ST_FWD:
			return "%s/28" % speedStr
		elif speedType == ST_REV128:
			return "(%s)" % speedStr
		elif speedType == ST_REV:
			return "(%s/28)" % speedStr
		else:
			return speedStr
	
	def setLimit(self, loco, limit):
		for at in self.trains.values():
			if at.loco == loco:
				at.limit = limit
				tx = self.order.index(at.tid)
				try:
					tx = self.order.index(at.tid)
				except:
					tx = None
					
				if tx is not None:
					self.refreshDisplays(tx)
				return

	def hasTrain(self, tid):
		return tid in self.order
	
	def getTrainByTid(self, tid):
		if tid not in self.trains.keys():
			return None
		
		return self.trains[tid]
	
	def getTrains(self):
		return [t for t in self.order]
		
	def getTrainByPosition(self, tx):
		if tx < 0 or tx >= len(self.order):
			return None
		
		return self.trains[self.order[tx]]

	def setSortKey(self, sortKey, groupDir=False, ascending=False):
		self.sortAscending = ascending
		self.sortGroupDir = groupDir
		self.sortKey = sortKey
		for lc in self.displays.values():
			lc.setSortHeaders(self.sortKey, self.sortGroupDir, self.sortAscending)
		self.sortTrains()
		
	def buildSortKey(self, tid):
		at = self.trains[tid]
		if self.sortKey == "time":
			kf = "%06d" % at.time
		else:
			kf = at.tid
			
		if self.sortGroupDir:
			return at.dir + kf
		else:
			return kf
		
	def sortTrains(self):
		a = sorted(self.order, key=self.buildSortKey, reverse=not self.sortAscending)
		self.order = a
		self.refreshDisplays()
		
	def refreshDisplays(self, tx=None):
		for lc in self.displays.values():
			lc.ticker()
			if tx is None:
				lc.refreshAll()
			else:
				lc.RefreshItem(tx)
		
	def getEngineers(self):
		return [at.engineer for at in self.trains.values() if at.engineer != "ATC"]
	
	def ticker(self):
		if len(self.order) <= 0:
			return
	
		for at in self.trains.values():
			at.time += 1
			if at.highlight > 0:
				at.highlight -= 1

			if at.stopTime is not None:
				at.stopTime += 1
				
		self.refreshDisplays()
