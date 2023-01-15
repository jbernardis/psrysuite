import logging

from district import District, CLIVEDEN, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, SignalLeverInput, BreakerInput, BlockInput, TurnoutInput
from bus import setBit, getBit


class Cliveden(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames = [ "C14R", "C14LA", "C14LB",
						"C12R", "C12L",
						"C10R", "C10L" ]
		toNames = [ "CSw9", "CSw13" ]
		handswitchNames = [ "CSw15.hand", "CSw11.hand" ]
		hsNames = [ "CSw15", "CSw11" ]
		relayNames = [ "C13.srel", "C23.srel", "C12.srel" ]
		# indNames = [ "CBBank" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		# ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		brkrNames = sorted(["CBGreenMtnStn", "CBSheffieldA", "CBGreenMtnYd", "CBHydeJct",
					"CBHydeWest", "CBHydeEast", "CBSouthportJct", "CBCarlton", "CBSheffieldB" ])
		blockNames = [ "C13.W", "C13", "C13.E", "COSCLW", "C23.W", "C23", "C12.W", "C12", "COSCLEW", "COSCLEE", "C22", "C11" ]
		leverNames = [ "C10.lvr", "C12.lvr", "C14.lvr" ]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(leverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(brkrNames, BreakerInput, District.breaker, ix)

	def OutIn(self):
		outb = [0 for _ in range(4)]

		asp = self.rr.GetOutput("C14R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C14LA").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C14LB").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 7, 1 if asp in [2, 3, 6, 7] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C12R").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C10R").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if asp in [4, 5, 6, 7] else 0)
		# bit 7 unused

		asp = self.rr.GetOutput("C12L").GetAspect()
		outb[2] = setBit(outb[2], 0, 1 if asp in [1, 3, 5, 7] else 0)
		outb[2] = setBit(outb[2], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C10L").GetAspect()
		outb[2] = setBit(outb[2], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[2] = setBit(outb[2], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 5, 1 if asp in [4, 5, 6, 7] else 0)
		outb[2] = setBit(outb[2], 6, 0 if self.rr.GetOutput("CSw11.hand").GetStatus() != 0 else 1) # hand switch unlocks
		op = self.rr.GetOutput("CSw13").GetOutPulse()
		outb[2] = setBit(outb[2], 7, 1 if op > 0 else 0)     # switches
		
		outb[3] = setBit(outb[3], 0, 1 if op < 0 else 0)
		op = self.rr.GetOutput("CSw9").GetOutPulse()
		outb[3] = setBit(outb[3], 1, 1 if op > 0 else 0)    	
		outb[3] = setBit(outb[3], 6, 1 if op < 0 else 0) # bit 2 is bad - use bit 6
		outb[3] = setBit(outb[3], 3, self.rr.GetOutput("C13.srel").GetStatus())	# Stop relays
		outb[3] = setBit(outb[3], 4, self.rr.GetOutput("C23.srel").GetStatus())
		outb[3] = setBit(outb[3], 5, self.rr.GetOutput("C12.srel").GetStatus())

		otext = formatOText(outb, 4)
		logging.debug("Cliveden: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(CLIVEDEN, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 1)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("CLIVEDEN: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 1)

			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("CSw13").SetState(nb, rb)
			nb = getBit(inb[0], 2) 
			rb = getBit(inb[0], 3)
			self.rr.GetInput("CSw11").SetState(nb, rb)
			nb = getBit(inb[0], 4) 
			rb = getBit(inb[0], 5)
			self.rr.GetInput("CSw9").SetState(nb, rb)

			self.rr.GetInput("C13.W").SetValue(getBit(inb[1], 0))  # Detection
			self.rr.GetInput("C13").SetValue(getBit(inb[1], 1))
			self.rr.GetInput("C13.E").SetValue(getBit(inb[1], 2))
			self.rr.GetInput("COSCLW").SetValue(getBit(inb[1], 3))
			self.rr.GetInput("C12.W").SetValue(getBit(inb[1], 4)) 
			self.rr.GetInput("C12").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("C23.W").SetValue(getBit(inb[1], 6)) 
			self.rr.GetInput("C23").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("COSCLEW").SetValue(getBit(inb[2], 0)) 
			self.rr.GetInput("COSCLEE").SetValue(getBit(inb[2], 1))
			self.rr.GetInput("C22").SetValue(getBit(inb[2], 2))
			self.rr.GetInput("CBGreenMtnStn").SetValue(getBit(inb[2], 4))  # Breakers
			self.rr.GetInput("CBSheffieldA").SetValue(getBit(inb[2], 5))
			self.rr.GetInput("CBGreenMtnYd").SetValue(getBit(inb[2], 6))
			self.rr.GetInput("CBHydeJct").SetValue(getBit(inb[2], 7))

			self.rr.GetInput("CBHydeWest").SetValue(getBit(inb[3], 0))
			self.rr.GetInput("CBHydeEast").SetValue(getBit(inb[3], 1))
			self.rr.GetInput("CBSouthportJct").SetValue(getBit(inb[3], 2))
			self.rr.GetInput("CBCarlton").SetValue(getBit(inb[3], 3))
			self.rr.GetInput("CBSheffieldB").SetValue(getBit(inb[3], 4))
