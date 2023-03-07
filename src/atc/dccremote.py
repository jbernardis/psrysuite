from atc.dccloco import FORWARD, REVERSE


class DCCRemote:
	def __init__(self, server):
		self.server = server
		self.initialized = False
		self.locos = []
		
	def LocoCount(self):
		return len(self.locos)
	
	def HasTrain(self, trn):
		for l in self.locos:
			if l.GetTrain() == trn:
				return True
			
		return False
	
	def Profiler(self, aspect, loco, speed):
		if aspect == 0:
			return 0, -5
		
		if aspect == 1:
			return 100, 5
			
		return 50, 5
		
	def SelectLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco.GetLoco():
				self.selectedLoco = l
				break
			
		else:
			l = loco
			self.locos.append(l)
			l.SetProfiler(self.Profiler)
			self.selectedLoco = l

		l = self.selectedLoco			
		self.SetSpeedAndDirection(nspeed=l.GetSpeed(), ndir=l.GetDirection())
		self.SetFunction(headlight=l.GetHeadlight(), horn=l.GetHorn(), bell=l.GetBell())
		return l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()
		
	def ClearSelection(self):
		self.selectedLoco = None
		
	def DropLoco(self, loco):
		self.locos = [l for l in self.locos if l.GetLoco() != loco]
		
	def ApplySpeedStep(self, step):
		if self.selectedLoco is None:
			return 
		
		nspeed = self.selectedLoco.GetSpeed() + step
		self.SetSpeedAndDirection(nspeed)
		
	def SetSpeed(self, nspeed):
		self.SetSpeedAndDirection(nspeed=nspeed)
		
	def SetDirection(self, ndir):
		self.SetSpeedAndDirection(ndir=ndir)
						
	def SetSpeedAndDirection(self, nspeed=None, ndir=None):
		if self.selectedLoco is None:
			return 
		
		if nspeed is not None:
			if nspeed < 0 or nspeed > 128:
				print("speed value is out of range: %d" % nspeed)
				return
			
			self.selectedLoco.SetSpeed(nspeed)
			
		if ndir is not None:
			if ndir not in [FORWARD, REVERSE]:
				print("invalid value for direction: %s" % ndir)
				return 
			
			self.selectedLoco.SetDirection(ndir)
		
		loco = self.selectedLoco.GetLoco()
		speed = self.selectedLoco.GetSpeed()
		direction = self.selectedLoco.GetDirection()
		
		self.server.SendRequest("move", {"loco": loco, "speed": speed, "direction": direction})
		
	def SetFunction(self, headlight=None, horn=None, bell=None):
		if self.selectedLoco is None:
			return 
		
		if headlight is not None:
			self.selectedLoco.SetHeadlight(headlight)
		if horn is not None:
			self.selectedLoco.SetHorn(horn)
		if bell is not None:
			self.selectedLoco.SetBell(bell)
			
		bell = self.selectedLoco.GetBell()
		horn = self.selectedLoco.GetHorn()
		light = self.selectedLoco.GetHeadlight()
		
		loco = self.selectedLoco.GetLoco()

		self.server.SendRequest("function", {"loco": loco, "bell": bell, "horn": horn, "light": light})
		
	def GetDCCLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco:
				return l
	
		return None
	
	def GetDCCLocoByTrain(self, train):
		for l in self.locos:
			if l.GetTrain() == train:
				return l
			
		return None

		
	def GetDCCLocos(self):
		return self.locos
		#return {l.GetLoco(): [l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()] for l in self.locos}

