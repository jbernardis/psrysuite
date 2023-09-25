import serial
import time
import logging

MAXTRIES = 5

class Bus:
	def __init__(self, tty):
		self.initialized = False
		self.tty = tty
		self.byteTally = {}
		self.lastUsed = {}
		self.open()
		
	def open(self):
		logging.info("Attempting to connect to serial port %s" % self.tty)
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=19200,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			logging.error("Unable to Connect to serial port %s: serial exception" % self.tty)
			return False

		self.initialized = True
		logging.info("successfully connected")
		return True

	def close(self):
		logging.info("closing serial port %s" % self.tty)
		self.port.close()
		
	def reopen(self):
		logging.info("attempting to re-open serial port")
		self.close()
		rc = self.open()
		if not rc:
			logging.error("Unable to re-open serial port")
			
		return rc

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
		
		retries = 3;
		while retries > 0:
			try:
				retries -= 1		
				nb = self.port.write(sendBuffer)
			except Exception as e:
				logging.error("Exception %s when trying to write to address %x" % (str(e), address))
				nb = 0
			else:
				if nb != (nbytes+1):
					logging.error("expected %d byte(s) written, got %d for address %x" % (nbytes+1, nb, address))
				else:
					break
					
			time.sleep(0.0001)

		if retries <= 0:
			# failed to write - don't even try to read
			return None

		tries = 0
		inbuf = []
		remaining = nbytes
		while tries < MAXTRIES and remaining > 0:
			try:
				b = self.port.read(remaining)
			except Exception as e:
				logging.error("Exception %s when trying to read from address %s" % (str(e), address))
				b = ""
				
			if len(b) == 0:
				tries += 1
				time.sleep(0.01) # an experiment to see if a larger wait period reduces the number of errors.  Was:  0.0001)
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
