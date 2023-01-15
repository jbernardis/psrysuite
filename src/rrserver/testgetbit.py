def getBit(ibyte, ibit):
	if ibit < 0 or ibit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-ibit)
	b = int(ibyte.hex(), 16)
	return 1 if b & mask != 0 else 0

def swapbyte(b):
	return int("0b"+"{0:08b}".format(b)[::-1], 2)

a = b'\xa0'
print("{0:08b}".format(int(a.hex(), 16)))

for i in range(8):
	print("%d: %s" % (i, getBit(a, i)))
	
b = swapbyte(int(a.hex(), 16))
print("{0:08b}".format(b))
