import logging

from district import District, KRULISH, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, RelayOutput, IndicatorOutput, BlockInput, TurnoutInput
from bus import setBit, getBit

class Krulish(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames =  [ "K8R", "K4R", "K2R", "K8LA", "K8LB", "K2L" ]
		toNames = [ "KSw1", "KSw3", "KSw5", "KSw7" ]
		relayNames = [ "N10.srel", "N11.srel", "N20.srel" ]
		indNames = [ "CBKrulishYd" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		blockNames = ["N10.W", "N10", "N10.E", "N20.W", "N20", "N20.E", "KOSW", "KOSM", "KOSE", "N11.W", "N11", "N11.E"]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames, TurnoutInput, District.turnout, ix)

	def OutIn(self):
		outb = [0 for _ in range(3)]
		asp = self.rr.GetOutput("K8R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # eastbound signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("K4R").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("K2R").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 7, 1 if asp in [2, 3, 6, 7] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("K2L").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp in [1, 3, 5, 7] else 0)  # westbound signals
		outb[1] = setBit(outb[1], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("K8LA").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp != 0 else 0) 
		asp = self.rr.GetOutput("K8LB").GetAspect()
		outb[1] = setBit(outb[1], 5, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 7, 1 if asp in [4, 5, 6, 7] else 0)

		outb[2] = setBit(outb[2], 4, self.rr.GetInput("CBKrulishYd").GetValue())
		outb[2] = setBit(outb[2], 5, self.rr.GetOutput("N10.srel").GetStatus())	# Stop relays
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("N20.srel").GetStatus())	# Stop relays
		outb[2] = setBit(outb[2], 7, self.rr.GetOutput("N11.srel").GetStatus())	# Stop relays

		otext = formatOText(outb, 3)
		logging.debug("Krulish: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(KRULISH, outb, 3, swap=False)

		if inbc != 3:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 1)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Krulish: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 1)

			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("KSw1").SetState(nb, rb)
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			self.rr.GetInput("KSw3").SetState(nb, rb)
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			self.rr.GetInput("KSw5").SetState(nb, rb)
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			self.rr.GetInput("KSw7").SetState(nb, rb)

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
