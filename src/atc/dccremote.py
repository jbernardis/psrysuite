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
	
	def Profiler(self, loco, aspect, speed):
		if aspect == 0:
			return 0, -5
		
		if aspect == 51:
			return 100, 5
			
		return 50, 5
		
	def SelectLoco(self, loco, assertValues=False):
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
		if assertValues:			
			self.SetSpeedAndDirection(nspeed=l.GetSpeed(), ndir=l.GetDirection(), assertValues=True)
			self.SetFunction(headlight=l.GetHeadlight(), horn=l.GetHorn(), bell=l.GetBell(), assertValues=True)
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
		
	def SetSpeed(self, nspeed, assertValues=False):
		self.SetSpeedAndDirection(nspeed=nspeed, assertValues=assertValues)
		
	def SetDirection(self, ndir, assertValues = False):
		self.SetSpeedAndDirection(ndir=ndir, assertValues=assertValues)
						
	def SetSpeedAndDirection(self, nspeed=None, ndir=None, assertValues=False):
		if self.selectedLoco is None:
			return 

		ospeed = self.selectedLoco.GetSpeed()		
		if nspeed is not None:
			if nspeed < 0 or nspeed > 128:
				print("speed value is out of range: %d" % nspeed)
				return
			
			self.selectedLoco.SetSpeed(nspeed)

		odirection = self.selectedLoco.GetDirection()			
		if ndir is not None:
			if ndir not in [FORWARD, REVERSE]:
				print("invalid value for direction: %s" % ndir)
				return 
			
			self.selectedLoco.SetDirection(ndir)
		
		loco = self.selectedLoco.GetLoco()
		speed = self.selectedLoco.GetSpeed()
		direction = self.selectedLoco.GetDirection()
		
		if (speed != ospeed or direction != odirection) or assertValues:
			self.server.SendRequest({"throttle": {"loco": loco, "speed": speed, "direction": direction}})
		
	def SetFunction(self, headlight=None, horn=None, bell=None, assertValues=False):
		if self.selectedLoco is None:
			return 

		oheadlight = self.selectedLoco.GetHeadlight()		
		if headlight is not None:
			self.selectedLoco.SetHeadlight(headlight)
		
		ohorn = self.selectedLoco.GetHorn()
		if horn is not None:
			self.selectedLoco.SetHorn(horn)
			
		obell = self.selectedLoco.GetBell()
		if bell is not None:
			self.selectedLoco.SetBell(bell)
			
		bell = self.selectedLoco.GetBell()
		horn = self.selectedLoco.GetHorn()
		light = self.selectedLoco.GetHeadlight()
		
		loco = self.selectedLoco.GetLoco()

		if (oheadlight != headlight or ohorn != horn or obell != bell) or assertValues:
			self.server.SendRequest({"function": {"loco": loco, "bell": bell, "horn": horn, "light": light}})
		
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

