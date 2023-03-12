import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import logging
logging.basicConfig(filename=os.path.join("logs", "dccserver.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from dccserver.settings import Settings
from dccserver.httpserver import HTTPServer

import serial
import socket
import time

FORWARD = 0x04
REVERSE = 0x03

MAXTRIES = 3

def formatLocoID(lid):
	lidhi = (lid >> 8) | 0xc0
	lidlo = lid % 256
	return [lidhi, lidlo]


class Loco:
	def __init__(self, lid):
		self.locoid = lid
		self.dpeed = 0
		self.direction = FORWARD
		self.headlight = False
		self.horn = False
		self.bell = False
		
	def GetID(self):
		return self.locoid
		
	def SetSpeed(self, speed):
		self.speed = speed
		
	def GetSpeed(self):
		return self.speed
	
	def SetDirection(self, dval):
		self.direction = dval
		
	def GetDirection(self):
		return self.direction
	
	def SetBell(self, bell):
		self.bell = bell
		
	def GetBell(self):
		return self.bell
	
	def SetHorn(self, horn):
		self.horn = horn
		
	def GetHorn(self):
		return self.horn
		
	def SetHeadlight(self, headlight):
		self.headlight = headlight
		
	def GetHeadlight(self):
		return self.headlight

		
		
class MainUnit:
	def __init__(self):
		logging.info("PSRY DCC Server starting...")
		
		self.locos = {}

		hostname = socket.gethostname()
		self.ip = socket.gethostbyname(hostname)

		self.settings = Settings()
		
		if self.settings.ipaddr is not None:
			if self.ip != self.settings.ipaddr:
				logging.info("Using configured IP Address (%s) instead of retrieved IP Address: (%s)" % (self.settings.ipaddr, self.ip))
				self.ip = self.settings.ipaddr
				
		logging.info("Opening serial port %s to DCC Command Station" % self.settings.tty)

		try:
			self.port = serial.Serial(port=self.settings.tty,
					baudrate=9600,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			logging.error("Unable to Connect to serial port %s" % self.settings.tty)
			# sys.exit()
			
		logging.info("Serial connection to DCC command station successful")
		logging.info("Creating HTTP server...")

		try:
			self.dccServer = HTTPServer(self.ip, self.settings.dccserverport, self.dccCommandReceipt)
		except Exception as e:
			logging.error("Unable to Create HTTP server for IP address %s (%s)" % (self.ip, str(e)))
			sys.exit()
			
		logging.info("HTTP Server created.  Awaiting commands...")
			
	def dccCommandReceipt(self, cmdString):
		print("DCC Command receipt: (%s)" % str(cmdString))
		logging.info("Command Receipt: %s" % str(cmdString))
		
		cmd = cmdString["cmd"][0].lower()

		if cmd == "throttle":
			try:
				locoid = int(cmdString["loco"][0])
			except:
				locoid = None
				
			if locoid is None:
				print("unable to parse locomotive ID: %s" % cmdString["loco"][0])
				return
				
			try:
				speed = int(cmdString["speed"][0])
			except:
				speed = None
				
			try:
				direction = cmdString["direction"][0]
			except:
				direction = None
				
			self.SetSpeedAndDirection(locoid, speed, direction)
		
		elif cmd == "function":
			try:
				locoid = int(cmdString["loco"][0])
			except:
				locoid = None
				
			if locoid is None:
				print("unable to parse locomotive ID: %s" % cmdString["loco"][0])
				return
				
			try:
				headlight = int(cmdString["light"][0])
			except:
				headlight = None
				
			try:
				horn = int(cmdString["horn"][0])
			except:
				horn = None
				
			try:
				bell = int(cmdString["bell"][0])
			except:
				bell = None
				
			self.SetFunction(locoid, headlight, horn, bell)
				
		elif cmd == "exit":
			logging.info("terminating DCC server normally")
			self.dccServer.close()
			
	def SetSpeedAndDirection(self, lid, speed=None, direction=None):
		try:
			loco = self.locos[lid]
		except KeyError:
			loco = Loco(lid)
			self.locos[lid] = loco
			
		if speed is not None:
			loco.SetSpeed(speed)
			
		if direction is not None:
			loco.SetDirection(REVERSE if direction == "R" else FORWARD)
	
		speed = loco.GetSpeed()
		direction = loco.GetDirection()
		
		outb = [ 0xa2 ] + formatLocoID(lid) + [ direction, speed if speed > 4 else 0 ]
		
		self.SendDCC(outb)
		
	def SetFunction(self, lid, headlight=None, horn=None, bell=None):
		print("set func %s %s %s %s" % (lid, headlight, horn, bell))
		try:
			loco = self.locos[lid]
		except KeyError:
			loco = Loco(lid)
			self.locos[lid] = loco
			
		if headlight is not None:
			loco.SetHeadlight(headlight == 1)
			
		if horn is not None:
			loco.SetHorn(horn == 1)
			
		if bell is not None:
			loco.SetBell(bell == 1)
			
		function = 0
		if loco.GetBell():
			function += 0x80
			
		if loco.GetHorn():
			function += 0x40
			
		if loco.GetHeadlight():
			function += 0x08

		outb = [ 0xa2 ] + formatLocoID(lid) + [ 0x07, function & 0xff ]

		self.SendDCC(outb)
		
	def SendDCC(self, outb):
		print("Trying to output: %s" % str(outb))
		if self.port is None:
			print("port not open")
			return False
		
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

		
	def run(self):
		self.dccServer.waitForFinish()
		logging.info("PSRY DCC Server exiting")
		try:
			self.port.close()
		except:
			pass


main = MainUnit()
main.run()