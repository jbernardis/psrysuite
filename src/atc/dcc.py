import serial
import time

MAXTRIES = 3

FORWARD = 0x04
REVERSE = 0x03

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
	

class DCC:
	def __init__(self, tty):
		self.tty = tty
		self.initialized = False
		
	def Open(self):
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=9600,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			print("Unable to Connect to serial port %s" % self.tty)
			## REMOVE THIS STATEMENT
			self.Initialize()
			return

		self.Initialize()
		
	def Initialize(self, flag=True):
		print("initialized = %s" % str(flag))
		self.initialized = flag
		self.locos = []
		
	def IsInitialized(self):
		return self.initialized

	def Close(self):
		try:
			self.port.close()
		except:
			pass
		
		self.Initialize(False)
		
	def SelectLoco(self, loco):
		if not self.IsInitialized():
			return
		
		for l in self.locos:
			if l.GetLoco() == loco:
				self.selectedLoco = l
				break
			
		else:
			l = DCCLoco(loco)
			
		self.locos.append(l)
		self.selectedLoco = l
		self.SetSpeedAndDirection(nspeed=l.GetSpeed(), ndir=l.GetDirection())
		self.SetFunction(headlight=l.GetHeadlight(), horn=l.GetHorn(), bell=l.GetBell())
		return l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()
		
	def ClearSelection(self):
		if not self.IsInitialized():
			return
		
		self.selectedLoco = None
		
	def DropLoco(self, loco):
		if not self.IsInitialized():
			return
		
		self.locos = [l for l in self.locos if l.GetLoco() != loco]
		
	def SetSpeed(self, nspeed):
		if not self.IsInitialized():
			return
		
		self.SetSpeedAndDirection(nspeed=nspeed)
		
	def SetDirection(self, ndir):
		if not self.IsInitialized():
			return
		
		self.SetSpeedAndDirection(ndir=ndir)
						
	def SetSpeedAndDirection(self, nspeed=None, ndir=None):
		if not self.IsInitialized():
			return
		
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
		
		outb = [
			0xa2,
			loco >> 8,
			loco % 256,
			direction,
			speed if speed > 4 else 0]
		
		self.SendDCC(outb)
		
	def SetFunction(self, headlight=None, horn=None, bell=None):
		if not self.IsInitialized():
			return
		
		if self.selectedLoco is None:
			return 
		
		if headlight is not None:
			self.selectedLoco.SetHeadlight(headlight)
		if horn is not None:
			self.selectedLoco.SetHorn(horn)
		if bell is not None:
			self.selectedLoco.SetBell(bell)
			
		function = 0
		if self.selectedLoco.GetBell():
			function += 0x80
			
		if self.selectedLoco.GetHorn():
			function += 0x40
			
		if self.selectedLoco.GetHeadlight():
			function += 0x08
		
		loco = self.selectedLoco.GetLoco()

		outb = [
			0xa2,
			loco >> 8,
			loco % 256,
			0x07,
			function & 0xff]
		
		self.SendDCC(outb)
		
	def GetLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco:
				return {l.GetLoco(): [l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()]}
	
		return {}
		
	def GetLocos(self):
		return {l.GetLoco(): [l.GetSpeed(), l.GetDirection(), l.GetHeadlight(), l.GetHorn(), l.GetBell()] for l in self.locos}
		
	def SendDCC(self, outb):
		if self.port is None:
			print("Trying to output: %s" % str(outb))
			return True
		
		n = self.port.write(bytes(outb))
		if n != len(outb):
			print("incomplete write.  expected to send %d bytes, but sent %d" % (len(outb), n))
		
		tries = 0
		inbuf = []
		while tries < MAXTRIES and len(inbuf) < 1:
			b = self.port.read(1)
			if len(b) == 0:
				tries += 1
				time.sleep(0.001)
			else:
				tries = 0
				inbuf.append(b)
				
		if len(inbuf) != 1:
			return False

		return True


