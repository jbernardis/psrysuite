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
		self.movedBeyondOrigin = False
		self.headAtTerminus = False
		self.origin = None
		self.terminus = None
		self.completed = False
		
	def SetOriginTerminus(self, origin, terminus):
		self.origin = origin
		self.terminus = terminus		
		
	def HasMoved(self, moved=None):
		if moved is not None:
			self.movedBeyondOrigin = moved
			
		return self.movedBeyondOrigin
	
	def CheckHasMoved(self, blknm):
		if blknm != self.origin:
			self.movedBeyondOrigin = True
			
	def AtTerminus(self, blknm):
		return blknm == self.terminus
	
	def HeadAtTerminus(self, flag=None):
		if flag is not None:
			self.headAtTerminus = flag
			
		return self.headAtTerminus
	
	def MarkCompleted(self):
		self.completed = True
		
	def HasCompleted(self):
		return self.completed
		
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
		self.governingSignal = sig
		
	def SetGoverningAspect(self, aspect):
		if self.completed:
			self.targetSpeed = 0
			self.step = 0
			return
		self.governingAspect = aspect	
		if self.profiler is None:
			self.targetSpeed = 0
			self.step = 0
		else:
			self.targetSpeed, self.step = self.profiler(self.loco, aspect, self.speed)
		
	def GetGoverningAspect(self):
		if self.completed:
			self.governingAspect = 0
			
		return self.governingAspect	
	