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


class MainUnit:
	def __init__(self):
		logging.info("PSRY DCC Server starting...")

		hostname = socket.gethostname()
		self.ip = socket.gethostbyname(hostname)

		self.settings = Settings()
		
		if self.settings.ipaddr is not None:
			if self.ip != self.settings.ipaddr:
				logging.info("Using configured IP Address (%s) instead of retrieved IP Address: (%s)" % (self.settings.ipaddr, self.ip))
				self.ip = self.settings.ipaddr
				
		logging.info("Opening serial port to DCC Command Station")

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
			
	def dccCommandReceipt(self, cmd):
		print("DCC Command receipt: (%s)" % str(cmd))
		logging.info("Command Receipt: %s" % str(cmd))
		
		if cmd["cmd"][0].lower() == "exit":
			logging.info("terminating DCC server normally")
			self.dccServer.close()
			
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

		
	def run(self):
		self.dccServer.waitForFinish()
		logging.info("PSRY DCC Server exiting")
		try:
			self.port.close()
		except:
			pass


main = MainUnit()
main.run()