import threading
import serial
import time
import logging

MAXTRIES = 5
THRESHOLD = 2

def setBit(obyte, obit, val):
	if val != 0:
		return (obyte | (1 << obit)) & 0xff
	else:
		return obyte


def getBit(ibyte, ibit):
	if ibit < 0 or ibit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-ibit)
	b = int(ibyte.hex(), 16)
	return 1 if b & mask != 0 else 0

def getBitInverted(ibyte, ibit):
	if ibit < 0 or ibit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-ibit)
	b = int(ibyte.hex(), 16)
	return 0 if b & mask != 0 else 1


class Bus:
	def __init__(self, tty):
		self.initialized = False
		self.tty = tty
		self.byteTally = {}
		self.lastUsed = {}
		logging.info("Attempting to connect to serial port %s" % tty)
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=19200,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			logging.error("Unable to Connect to serial port %s" % tty)
			return

		self.initialized = True
		logging.info("successfully connected")

	def close(self):
		self.port.close()

	def sendRecv(self, address, outbuf, nbytes, threshold=1):
		if not self.initialized:
			return None
		
		try:
			lastused = self.lastUsed[address]
		except:
			lastused = [None for _ in range(nbytes)]
			self.lastUsed[address] = lastused

		sendBuffer = []
		sendBuffer.append(address)

		outbuf = list(reversed(outbuf))

		sendBuffer.extend(outbuf)
		
		nb = self.port.write(sendBuffer)
		if nb != (nbytes+1):
			logging.error("expected %d byte(s) written, got %d for address %x" % (nbytes+1, nb, address))

		tries = 0
		inbuf = []
		remaining = nbytes
		while tries < MAXTRIES and remaining > 0:
			b = self.port.read(remaining)
			if len(b) == 0:
				tries += 1
				time.sleep(0.0001)
			else:
				tries = 0
				inbuf.extend([bytes([b[i]]) for i in range(len(b))])
				remaining = nbytes-len(inbuf)
				
		if len(inbuf) != nbytes:
			logging.error("incomplete read for address %x.  Expecting %d characters, got %d" % (address, nbytes, len(inbuf)))
			return None #[b'\x00']*nbytes
		else:
			# make sure that if a byte is different, that it is at least different for "threshold" cycles before we accept it
			for i in range(nbytes):
				if lastused[i] is None:
					lastused[i] = inbuf[i]
				elif inbuf[i] == lastused[i]:
					self.byteTally[(address, i)] = 0
				elif self.verifyChange(address, i, threshold):
					lastused[i] = inbuf[i]
				else:
					inbuf[i] = lastused[i]
										
			return inbuf
		
	def verifyChange(self, address, bx, threshold):
		try:
			self.byteTally[(address, bx)] += 1
		except KeyError:
			self.byteTally[(address, bx)] = 1
			
		if self.byteTally[(address, bx)] > threshold:
			self.byteTally[(address, bx)] = 0
			return True
		
		return False


class RailroadMonitor(threading.Thread):
	def __init__(self, ttyDevice, rr, settings):
		threading.Thread.__init__(self)
		self.simulation = settings.simulation
		self.initialized = False
		self.tty = ttyDevice
		self.rr = rr
		if self.simulation:
			self.rrBus = None
		else:
			self.rrbus = Bus(self.tty)
			if not self.rrbus.initialized:
				return
			self.rr.setBus(self.rrbus)

		self.pollInterval = settings.busInterval * 1000000000  # convert s to ns

		self.isRunning = False
		self.initialized = True

	def kill(self):
		self.isRunning = False

	def run(self):
		self.isRunning = True
		lastPoll = time.monotonic_ns() - self.pollInterval
		while self.isRunning:
			current = time.monotonic_ns()
			elapsed = current - lastPoll
			if self.isRunning and elapsed > self.pollInterval:
				#logging.debug("Starting all io")
				self.rr.allIO()
				#logging.debug("all io finished")
				lastPoll = current
			else:
				time.sleep(0.0001) # yield to other threads
