import threading
import serial
import time
import logging

MAXTRIES = 3


def swapbyte(b):
	return int("0b"+"{0:08b}".format(b)[::-1], 2)


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


class Bus:
	def __init__(self, tty):
		self.initialized = False
		self.tty = tty
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

	def sendRecv(self, address, outbuf, nbytes, swap=False):
		if not self.initialized:
			return None, 0

		sendBuffer = []
		sendBuffer.append(address)

		if swap:
			outbuf = [swapbyte(x) for x in outbuf]

		sendBuffer.extend(outbuf)
		
		nb = self.port.write(sendBuffer)
		if nb != (nbytes+1):
			logging.error("expected %d byte(s) written, got %d" % (nbytes+1, nb))

		tries = 0
		inbuf = []
		remaining = nbytes
		while tries < MAXTRIES and remaining > 0:
			b = self.port.read(remaining)
			if len(b) == 0:
				tries += 1
				time.sleep(0.001)
			else:
				tries = 0
				inbuf.extend([bytes([b[i]]) for i in range(len(b))])
				remaining = nbytes-len(inbuf)
				
		if len(inbuf) != nbytes:
			logging.error("incomplete read.  Expecting %d characters, got %d" % (nbytes, len(inbuf)))
			return [], 0

		return inbuf, nbytes


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
				logging.debug("Starting all io")
				self.rr.allIO()
				logging.debug("all io finished")
				lastPoll = current
			else:
				time.sleep(0.0001) # yield to other threads
