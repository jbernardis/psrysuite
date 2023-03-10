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
		self.governingSignal = None
		self.governingAspect = 0
		self.profiler = None
		self.movedBeyondOrigin = False
		self.headAtTerminus = False
		self.origin = None
		self.terminus = None
		self.completed = False
		self.inBlock = False
		
	def SetOriginTerminus(self, origin, terminus):
		self.origin = origin
		self.terminus = terminus
		
	def SetInBlock(self, flag):
		print("inblock set to %s" % str(flag))
		self.inBlock = flag		
		
	def HasMoved(self, moved=None):
		if moved is not None:
			self.movedBeyondOrigin = moved

		print("has moved: %s" % self.movedBeyondOrigin)			
		return self.movedBeyondOrigin
	
	def CheckHasMoved(self, blknm):
		if blknm != self.origin:
			self.movedBeyondOrigin = True
			print("check has moved: %s" % self.movedBeyondOrigin)			
			
	def AtTerminus(self, blknm):
		return blknm == self.terminus
	
	def HeadAtTerminus(self, flag=None):
		if flag is not None:
			self.headAtTerminus = flag
			
		print("head at terminus: %s" % str(self.headAtTerminus))
			
		return self.headAtTerminus
	
	def MarkCompleted(self):
		self.completed = True
		print("marked complete")
		
	def HasCompleted(self):
		print("check completed: %s" % self.completed)
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
		print("get speed step")
		if self.HasCompleted() and self.speed > 0:
			print("return -10")
			return -10
		
		if self.step == 0:
			print("return 0 A")
			return 0
		
		if self.step > 0:
			if self.speed < self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step > self.step:
					step = self.step
				print("returning %d B" % step)
				return step
			elif self.speed > self.targetSpeed:
				print("returning %d B" % (self.speed - self.targetSpeed))
				return self.speed - self.targetSpeed
			else:
				print("returning 0 C")
				return 0
			
		if self.step < 0:
			if self.speed > self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step < self.step:
					step = self.step
				print("returning %d D" % step)
				return step
			elif self.speed < self.targetSpeed:
				print("returning %d E" % (self.speed - self.targetSpeed))
				return self.speed - self.targetSpeed
			else:
				print("returning 0 F")
				return 0
			
		print("returning 0 G")
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
		print("returning %s %d as governing signal, aspect" % (self.governingSignal, self.governingAspect))
		return self.governingSignal, self.governingAspect
	
	def SetGoverningSignal(self, sig):
		self.governingSignal = sig
		print("governing signal set to %s" % str(sig))
		
	def SetGoverningAspect(self, aspect):
		print("set governing aspect to %d" % aspect)
		if self.inBlock:
			print("in block - just leave the aspect as %d" % self.governingAspect)
			# the signal aspect is "frozen" after we pass it so make no change here
			return 
		
		if self.completed:
			print("completed - just leave the aspect as %d" % self.governingAspect)
			# the train has completed - make no aspect change here
			self.targetSpeed = 0
			self.step = 0 
			return
		
		self.governingAspect = aspect	
		if self.profiler is None:
			self.targetSpeed = 0
			self.step = 0
		else:
			self.targetSpeed, self.step = self.profiler(self.loco, aspect, self.speed)
		print("aspect changed, target, step = %d %d" % (self.targetSpeed, self.step))
		
	def GetGoverningAspect(self):
		if self.completed:
			self.governingAspect = 0
			
		return self.governingAspect	
	