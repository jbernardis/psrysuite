import logging

from rrserver.district import District, KRULISH, formatIText, formatOText
from rrserver.rrobjects import SignalOutput, TurnoutOutput, RelayOutput, IndicatorOutput, BlockInput, TurnoutInput
from rrserver.bus import setBit, getBit

class Krulish(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames =  [ ["K8R", 3], ["K4R", 3], ["K2R", 3], ["K8LA", 1], ["K8LB", 3], ["K2L", 3] ]
		toNames = [ "KSw1", "KSw3", "KSw5", "KSw7" ]
		relayNames = [ "N10.srel", "N11.srel", "N20.srel" ]
		indNames = [ "CBKrulishYd" ]

		ix = 0
		ix = self.AddOutputs([s[0] for s in sigNames], SignalOutput, District.signal, ix)
		for sig, bits in sigNames:
			self.rr.GetOutput(sig).SetBits(bits)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen, settings.topulsect)

		blockNames = ["N10.W", "N10", "N10.E", "N20.W", "N20", "N20.E", "KOSW", "KOSM", "KOSE", "N11.W", "N11", "N11.E"]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames, TurnoutInput, District.turnout, ix)

	def OutIn(self):
		outbc = 3
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("K8R").GetAspectBits()
		outb[0] = setBit(outb[0], 0, asp[0])  # eastbound signals
		outb[0] = setBit(outb[0], 1, asp[1])
		outb[0] = setBit(outb[0], 2, asp[2])
		asp = self.rr.GetOutput("K4R").GetAspectBits()
		outb[0] = setBit(outb[0], 3, asp[0]) 
		outb[0] = setBit(outb[0], 4, asp[1])
		outb[0] = setBit(outb[0], 5, asp[2])
		asp = self.rr.GetOutput("K2R").GetAspectBits()
		outb[0] = setBit(outb[0], 6, asp[0]) 
		outb[0] = setBit(outb[0], 7, asp[1])

		outb[1] = setBit(outb[1], 0, asp[2])
		asp = self.rr.GetOutput("K2L").GetAspectBits()
		outb[1] = setBit(outb[1], 1, asp[0])  # westbound signals
		outb[1] = setBit(outb[1], 2, asp[1])
		outb[1] = setBit(outb[1], 3, asp[2])
		asp = self.rr.GetOutput("K8LA").GetAspectBits()
		outb[1] = setBit(outb[1], 4, asp[0]) 
		asp = self.rr.GetOutput("K8LB").GetAspectBits()
		outb[1] = setBit(outb[1], 5, asp[0])
		outb[1] = setBit(outb[1], 6, asp[1])
		outb[1] = setBit(outb[1], 7, asp[2])

		outb[2] = setBit(outb[2], 4, self.rr.GetInput("CBKrulishYd").GetInvertedValue())
		outb[2] = setBit(outb[2], 5, self.rr.GetOutput("N10.srel").GetStatus())	# Stop relays
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("N20.srel").GetStatus())	# Stop relays
		outb[2] = setBit(outb[2], 7, self.rr.GetOutput("N11.srel").GetStatus())	# Stop relays

		otext = formatOText(outb, outbc)
		#logging.debug("Krulish: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(KRULISH, outb, outbc)
			if inb is None:
				itext = "Read Error"
			else:
				itext = formatIText(inb, inbc)
				#logging.debug("Krulish: Input Bytes: %s" % itext)
	
				nb = getBit(inb[0], 0)  # Switch positions
				rb = getBit(inb[0], 1)
				self.rr.GetInput("KSw1").SetTOState(nb, rb)
				nb = getBit(inb[0], 2)
				rb = getBit(inb[0], 3)
				self.rr.GetInput("KSw3").SetTOState(nb, rb)
				nb = getBit(inb[0], 4)
				rb = getBit(inb[0], 5)
				self.rr.GetInput("KSw5").SetTOState(nb, rb)
				nb = getBit(inb[0], 6)
				rb = getBit(inb[0], 7)
				self.rr.GetInput("KSw7").SetTOState(nb, rb)
	
				self.rr.GetInput("N10.W").SetValue(getBit(inb[1], 2))  # Detection
				self.rr.GetInput("N10").SetValue(getBit(inb[1], 3))
				self.rr.GetInput("N10.E").SetValue(getBit(inb[1], 4)) 
				self.rr.GetInput("N20.W").SetValue(getBit(inb[1], 5))
				self.rr.GetInput("N20").SetValue(getBit(inb[1], 6))
				self.rr.GetInput("N20.E").SetValue(getBit(inb[1], 7)) 
	
				self.rr.GetInput("KOSW").SetValue(getBit(inb[2], 0))  #KOS1
				self.rr.GetInput("KOSM").SetValue(getBit(inb[2], 1))  #KOS2
				self.rr.GetInput("KOSE").SetValue(getBit(inb[2], 2))  #KOS3
				self.rr.GetInput("N11.W").SetValue(getBit(inb[2], 3))
				self.rr.GetInput("N11").SetValue(getBit(inb[2], 4))
				self.rr.GetInput("N11.E").SetValue(getBit(inb[2], 5)) 
		
				
		if self.sendIO:
			self.rr.ShowText("Krul", KRULISH, otext, itext, 0, 1)

