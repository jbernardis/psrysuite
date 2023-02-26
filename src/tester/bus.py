import serial
import time

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
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=19200,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			print("Unable to Connect to serial port %s" % tty)
			return

		self.initialized = True
		
	def isOpen(self):
		return self.port is not None

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
			pass #print("expected %d byte(s) written, got %d" % (nbytes+1, nb))

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
			# print("incomplete read.  Expecting %d characters, got %d" % (nbytes, len(inbuf)))
			return [], 0

		return inbuf, nbytes
