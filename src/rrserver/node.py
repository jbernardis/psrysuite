
import logging

def setBit(obyte, obit, val):
    if val != 0:
        return (obyte | (1 << obit)) & 0xff
    else:
        return (obyte & ~(1 << obit)) & 0xff


def getBit(ibyte, ibit):
    if ibit < 0 or ibit > 7:
        # bit index is out of range
        return 0
    mask = 1 << (7-ibit)
    b = int(bytes([ibyte]).hex(), 16)
    return 1 if b & mask != 0 else 0

class Node:
    def __init__(self, district, rr, address, bcount, settings):
        self.district = district
        self.rr = rr
        self.address = address
        self.bcount = bcount
        self.outb = [0 for _ in range(bcount)]
        self.inb = [0 for _ in range(bcount)]
        self.lastinb = [0 for _ in range(bcount)]
        self.topulselen = settings.topulselen
        self.topulsect = settings.topulsect
        self.nxbpulselen = settings.nxbpulselen
        self.nxbpulsect = settings.nxbpulsect
        self.first = True
        
        self.inputMap = {}
        
        self.rrBus = None
       
    def GetAllBits(self):
        return self.bcount, self.outb, self.inb
      
    def GetInputBit(self, vbyte, vbit):
        return getBit(self.inb[vbyte], vbit)
    
    def AddInputToMap(self, bytebit, o):
        self.inputMap[bytebit] = o
    
    def GetInputBits(self, bits):
        rv = []
        for bt in bits:
            if bt is None:
                rv.append(None)
            else:
                rv.append(getBit(self.inb[bt[0]], bt[1]))
        return rv
    
    def SetInputBit(self, vbyte, vbit, state):
        self.inb[vbyte] = setBit(self.inb[vbyte], 7-vbit, state) 
     
    def SetOutputBit(self, vbyte, vbit, state):
        self.outb[vbyte] = setBit(self.outb[vbyte], vbit, state)       
        
    def setBus(self, bus):
        self.rrBus = bus
        
    def OutIn(self):
        if self.rrBus is not None:     
            inb = self.rrBus.sendRecv(self.address, self.outb, self.bcount)
            if inb is not None:
                for i in range(self.bcount):
                    self.inb[i] = int.from_bytes(inb[i], "big")
            else:
                logging.error("Communications error on railroad serial port")
                    
    def GetChangedInputs(self):
        results = []
        for b in range(len(self.inb)):
            new = self.inb[b]
            old = self.lastinb[b]
            if self.first:
                mask = 0b11111111
            else:
                mask = new ^ old
  
            if mask != 0:
                for i in range(8):
                    if mask & (1 << (7-i)) != 0:
                        v = getBit(new, i)
                        try:
                            o = self.inputMap[(b, i)]
                        except KeyError:
                            if not self.first:
                                logging.warning("input for location %x:%d:%d not found" % (self.address, b, i))
                            o = None
                        if o:
                            results.append([self, b, i, o, v])
                            
        self.lastinb = [x for x in self.inb]
        self.first = False
        return results

                
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
