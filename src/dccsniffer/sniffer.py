import serial
import logging

class Sniffer:
	def __init__(self):
		self.tty = None
		self.baud = None
		self.port = None
		self.isRunning = False

	def connect(self, tty):
		self.tty = tty
		try:
			self.port = serial.Serial(port=self.tty, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=1)
		except serial.SerialException:
			self.port = None
			raise
		
	def isConnected(self):
		return self.port is not None
	
	def kill(self):
		self.isRunning = False
		
	def run(self, rrserver):
		self.isRunning = True
		while self.isRunning:
			if self.port is None or not self.port.is_open:
				self.isRunning = False
			else:
				try:
					c = self.port.read_until()
				except serial.SerialException:
					self.port = None
					self.isRunning = True
				
				if len(c) != 0:
					try:
						s = str(c, 'UTF-8')
					except:
						logging.info("unable to convert DCC message to string: (" + s + ")")
					else:
						p = s.split()
						req = {
							"dccspeed": {
								"cmd": p[0],
								"loco": "%d" % int(p[1]), # strip off any leading zeroes
								"speed": p[2]
							}
						}
						rrserver.SendRequest(req)

		try:
			self.port.close()
		except:
			pass
				
		logging.info("DCC sniffer ended execution")


