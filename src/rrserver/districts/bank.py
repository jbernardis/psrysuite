import logging

from district import District, BANK, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, IndicatorOutput, BreakerInput, \
	SignalLeverInput, BlockInput, TurnoutInput
from bus import setBit, getBit


class Bank(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames =  [ "C18RA", "C18RB", "C18L",
						"C22R", "C22L",
						"C24R", "C24L" ]
		toNames = [ "CSw17", "CSw23" ]
		hsNames = [ "CSw19", "CSw21a", "CSw21b" ]
		handswitchNames = [ "CSw19.hand", "CSw21a.hand", "CSw21b.hand" ]
		relayNames = [ "B20.srel", "B11.srel", "B21.srel" ]
		indNames = [ "CBBank" ]
		signalLeverNames = [ "C18.lvr", "C22.lvr", "C24.lvr" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		brkrNames = sorted([ "CBBank", "CBKale",  "CBWaterman", "CBEngineYard", "CBEastEndJct",
						"CBShore", "CBRockyHill", "CBHarpersFerry", "CBBlockY30", "CBBlockY81" ])
		blockNames = [ "B20", "B20.E", "BOSWW", "BOSWE", "B11.W", "B11", "B21.W", "B21", "B21.E", "BOSE" ]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(brkrNames, BreakerInput, District.breaker, ix)

	def OutIn(self):
		outb = [0 for _ in range(4)]
		asp = self.rr.GetOutput("C22R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp != 0 else 0)   # Bank West eastbound signals
		asp = self.rr.GetOutput("C24R").GetAspect()
		outb[0] = setBit(outb[0], 1, 1 if asp in [1, 3, 5, 7] else 0)  
		outb[0] = setBit(outb[0], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 3, 1 if asp in [4, 5, 6, 7] else 0)
		asp24l = self.rr.GetOutput("C24L").GetAspect()          # westbound signals
		outb[0] = setBit(outb[0], 4, 1 if asp24l in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 5, 1 if asp24l in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 6, 1 if asp24l in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C22L").GetAspect() 
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3, 5, 7] else 0) 

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C18RA").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp != 0 else 0)   # Bank East eastbound signals
		asp = self.rr.GetOutput("C18RB").GetAspect() 
		outb[1] = setBit(outb[1], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C18L").GetAspect()         #@ westbound signal
		outb[1] = setBit(outb[1], 6, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 7, 1 if asp in [2, 3, 6, 7] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [4, 5, 6, 7] else 0)
		outb[2] = setBit(outb[2], 1, self.rr.GetInput("B10").GetValue())  #block indicators
		outb[2] = setBit(outb[2], 2, self.rr.GetInput("C13").GetValue())
		csw21 = self.rr.GetOutput("CSw21a.hand").GetStatus() + self.rr.GetOutput("CSw21b.hand").GetStatus()
		outb[2] = setBit(outb[2], 3, 0 if csw21 != 0 else 1) # hand switch unlocks
		outb[2] = setBit(outb[2], 4, 0 if self.rr.GetOutput("CSw19.hand").GetStatus() != 0 else 1) 
		op = self.rr.GetOutput("CSw23").GetOutPulse()        # switch outputs
		outb[2] = setBit(outb[2], 5, 1 if op > 0 else 0) 
		outb[2] = setBit(outb[2], 6, 1 if op < 0 else 0)
		op = self.rr.GetOutput("CSw17").GetOutPulse()
		outb[2] = setBit(outb[2], 7, 1 if op > 0 else 0) 

		outb[3] = setBit(outb[3], 0, 1 if op < 0 else 0)
		outb[3] = setBit(outb[3], 1, self.rr.GetOutput("B20.srel").GetStatus())	 # stop relays
		outb[3] = setBit(outb[3], 2, self.rr.GetOutput("B11.srel").GetStatus())
		outb[3] = setBit(outb[3], 3, self.rr.GetOutput("B21.srel").GetStatus())
		outb[3] = setBit(outb[3], 4, self.rr.GetInput("CBBank").GetValue())  #Circuit breaker
		outb[3] = setBit(outb[3], 5, 1 if asp24l != 0 else 0)  #Signal 24L indicator

		otext = formatOText(outb, 4)
		logging.debug("Bank: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(BANK, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 1)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Bank: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 1)
			
			nb = getBit(inb[0], 0)  # Switch Positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("CSw23").SetState(nb, rb)
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			self.rr.GetInput("CSw21a").SetState(nb, rb)
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			self.rr.GetInput("CSw21b").SetState(nb, rb)
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			self.rr.GetInput("CSw19").SetState(nb, rb)

			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			self.rr.GetInput("CSw17").SetState(nb, rb)
			ip = self.rr.GetInput("B20")    # block detection
			ip.SetValue(getBit(inb[1], 2))
			ip = self.rr.GetInput("B20.E") 
			ip.SetValue(getBit(inb[1], 3))
			ip = self.rr.GetInput("BOSWW")  # BKOS1
			ip.SetValue(getBit(inb[1], 4))
			ip = self.rr.GetInput("BOSWE")  #BKOS2
			ip.SetValue(getBit(inb[1], 5))
			ip = self.rr.GetInput("B11.W") 
			ip.SetValue(getBit(inb[1], 6))
			ip = self.rr.GetInput("B11") 
			ip.SetValue(getBit(inb[1], 7))

			ip = self.rr.GetInput("B21.W") 
			ip.SetValue(getBit(inb[2], 0))
			ip = self.rr.GetInput("B21") 
			ip.SetValue(getBit(inb[2], 1))
			ip = self.rr.GetInput("B21.E") 
			ip.SetValue(getBit(inb[2], 2))
			ip = self.rr.GetInput("BOSE")  #BKOS3
			ip.SetValue(getBit(inb[2], 3))
			self.rr.GetInput("CBBank").SetValue(getBit(inb[2], 4)) # Breakers
			self.rr.GetInput("CBKale").SetValue(getBit(inb[2], 5))
			self.rr.GetInput("CBWaterman").SetValue(getBit(inb[2], 6))
			self.rr.GetInput("CBEngineYard").SetValue(getBit(inb[2], 7))

			self.rr.GetInput("CBEastEndJct").SetValue(getBit(inb[3], 0))
			self.rr.GetInput("CBShore").SetValue(getBit(inb[3], 1))
			self.rr.GetInput("CBRockyHill").SetValue(getBit(inb[3], 2))
			self.rr.GetInput("CBHarpersFerry").SetValue(getBit(inb[3], 3))
			self.rr.GetInput("CBBlockY30").SetValue(getBit(inb[3], 4))
			self.rr.GetInput("CBBlockY81").SetValue(getBit(inb[3], 5))
