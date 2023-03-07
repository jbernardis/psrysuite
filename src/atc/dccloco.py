FORWARD = 'F'
REVERSE = 'R'


class DCCLoco:
	def __init__(self, train, loco):
		self.loco = loco
		self.train = train
		self.direction = FORWARD;
		self.speed = 0;
		self.light = False;
		self.horn = False
		self.bell = False
		self.governingSignal = {"signal": None, "os": None, "route": None}
		self.governingAspect = 0
		self.profiler = None
		
	def SetProfiler(self, prof):
		self.profiler = prof
		
	def GetTrain(self):
		return self.train
	
	def GetName(self):
		return self.GetTrain()
		
	def GetLoco(self):
		return self.loco
	
	def SetDirection(self, direction):
		self.direction = direction
		
	def GetDirection(self):
		return self.direction
	
	def SetSpeed(self, speed):
		self.speed = speed
		
	def GetSpeed(self):
		return self.speed
	
	def GetSpeedStep(self):
		if self.step == 0:
			return 0
		
		if self.step > 0:
			if self.speed < self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step > self.step:
					step = self.step
				return step
			elif self.speed > self.targetSpeed:
				return self.speed - self.targetSpeed
			else:
				return 0
			
		if self.step < 0:
			if self.speed > self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step < self.step:
					step = self.step
				return step
			elif self.speed < self.targetSpeed:
				return self.speed - self.targetSpeed
			else:
				return 0
			
		return 0
	
	def SetHeadlight(self, onoff):
		self.light = onoff
		
	def GetHeadlight(self):
		return self.light
	
	def SetHorn(self, onoff):
		self.horn = onoff
		
	def GetHorn(self):
		return self.horn
	
	def SetBell(self, onoff):
		self.bell = onoff
		
	def GetBell(self):
		return self.bell

	def GetGoverningSignal(self):
		return self.governingSignal, self.governingAspect
	
	def SetGoverningSignal(self, sig):
		print("set governing signal of %s to %s" % (self.train, str(sig)))
		self.governingSignal = sig
		
	def SetGoverningAspect(self, aspect):
		print("set governing aspect of %s to %d" % (self.train, aspect))
		self.governingAspect = aspect	
		if self.profiler is None:
			print("unable to determine acceleration profile for train/loco %s/%d" % (self.train, self.loco))
			self.targetSpeed = 0
			self.step = 0
		else:
			self.targetSpeed, self.step = self.profiler(aspect, self.loco, self.speed)
			print("based on aspect %d and loco %s, setting target speed/step to %d, %d" % (aspect, self.loco, self.targetSpeed, self.step))
		
	def GetGoverningAspect(self):
		return self.governingAspect	
	