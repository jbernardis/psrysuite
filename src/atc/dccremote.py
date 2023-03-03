FORWARD = 'F'
REVERSE = 'R'

class DCCLoco:
	def __init__(self, loco):
		self.loco = loco
		self.direction = FORWARD;
		self.speed = 0;
		self.light = False;
		self.horn = False
		self.bell = False
		
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
	

class DCCRemote:
	def __init__(self, server):
		self.server = server
		self.initialized = False
		self.locos = []
		
	def PrintList(self):
		for l in self.locos:
			print("%s" % l.GetLoco(), flush=True)
		
	def LocoCount(self):
		return len(self.locos)
		
	def SelectLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco:
				self.selectedLoco = l
				break
			
		else:
			l = DCCLoco(loco)
			self.locos.append(l)
			self.selectedLoco = l

		l = self.selectedLoco			
		self.SetSpeedAndDirection(nspeed=l.GetSpeed(), ndir=l.GetDirection())
		self.SetFunction(headlight=l.GetHeadlight(), horn=l.GetHorn(), bell=l.GetBell())
		return l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()
		
	def ClearSelection(self):
		self.selectedLoco = None
		
	def DropLoco(self, loco):
		self.locos = [l for l in self.locos if l.GetLoco() != loco]
		
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
		
	def GetLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco:
				return {l.GetLoco(): [l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()]}
	
		return {}
		
	def GetLocos(self):
		return {l.GetLoco(): [l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()] for l in self.locos}

