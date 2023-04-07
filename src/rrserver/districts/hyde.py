import logging

from rrserver.district import District, HYDE, formatIText, formatOText
from rrserver.rrobjects import SignalOutput, TurnoutOutput, RelayOutput, IndicatorOutput, RouteInput, BlockInput, \
	FleetLeverInput, TurnoutInput
from rrserver.bus import setBit, getBit

class Hyde(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		# OUTPUTS
		sigNames = [
				["H4LA", 1], ["H4LB", 1], ["H4LC", 1], ["H4LD", 1], ["H4R", 1], 
				["H6LA", 1], ["H6LB", 1], ["H6LC", 1], ["H6LD", 1], ["H6R", 1],  
				["H8L", 1], ["H8R", 1],  
				["H10L", 1], ["H10RA", 1], ["H10RB", 1], ["H10RC", 1], ["H10RD", 1], ["H10RE", 1], 
				["H12RA", 1], ["H12RB", 1], ["H12RC", 1], ["H12RD", 1], ["H12RE", 1], ["H12L", 1] ]
		toNames =[ "HSw1", "HSw3", "HSw5", "HSw7", "HSw9", "HSw11", "HSw13", "HSw15", "HSw17", "HSw19", "HSw21", "HSw23", "HSw25", "HSw27", "HSw29" ]
		indNames = [ "CBHydeJct", "CBHydeEast", "CBHydeWest", "HydeEastPower", "HydeWestPower", ]
		relayNames = [ "H13.srel", "H21.srel" ]

		ix = 0
		ix = self.AddOutputs([s[0] for s in sigNames], SignalOutput, District.signal, ix)
		for sig, bits in sigNames:
			self.rr.GetOutput(sig).SetBits(bits)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen, settings.topulsect)

		# INPUTS
		routeNames = [ "H30E",
				"H31E", "H32E", "H33E", "H34E", "H12E", "H22E", "H43E", "H42E", "H41E", "H40E",
				"H31W", "H32W", "H33W", "H34W", "H12W", "H22W", "H43W", "H42W", "H41W"	]
		self.routeMap = {
				"H12W": [ ["HSw1", "N"], ["HSw3","N"], ["HSw5", "N"] ], 
				"H34W": [ ["HSw1", "N"], ["HSw3", "R"], ["HSw5", "R"] ],
				"H33W": [ ["HSw1", "R"], ["HSw3", "N"], ["HSw5", "N"] ], 
				"H32W": [ ["HSw1", "R"], ["HSw3", "R"], ["HSw5", "R"], ["HSw7","N"] ], 
				"H31W": [ ["HSw1", "R"], ["HSw3", "R"], ["HSw5", "R"], ["HSw7","R"] ], 

				"H12E": [ ["HSw15", "N"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H34E": [ ["HSw15", "R"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H33E": [ ["HSw15", "N"], ["HSw17", "R"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H32E": [ ["HSw15", "N"], ["HSw17", "N"], ["HSw19", "R"], ["HSw21", "N"] ], 
				"H31E": [ ["HSw15", "N"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "R"] ], 
				"H30E": [ ["HSw7", "N"] ],

				"H22W": [ ["HSw9", "N"], ["HSw11", "N"], ["HSw13", "N"] ], 
				"H43W": [ ["HSw9", "N"], ["HSw11", "R"], ["HSw13", "R"] ], 
				"H42W": [ ["HSw9", "R"], ["HSw11", "N"], ["HSw13", "N"] ], 
				"H41W": [ ["HSw9", "R"], ["HSw11", "R"], ["HSw13", "R"] ], 

				"H22E": [ ["HSw23", "N"], ["HSw25", "N"], ["HSw27", "N"], ["HSw29", "N"] ], 
				"H43E": [ ["HSw23", "N"], ["HSw25", "R"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H42E": [ ["HSw23", "R"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H41E": [ ["HSw23", "N"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H40E": [ ["HSw23", "N"], ["HSw25", "N"], ["HSw27", "N"], ["HSw29", "R"] ], 
		}

		blockNames = [ "H21", "H21.E",
				"HOSWW2", "HOSWW", "HOSWE",
				"H31", "H32", "H33", "H34", "H12", "H22", "H43", "H42", "H41", "H40",
				"HOSEW", "HOSEE",
				"H13.W", "H13" ]
		fleetlLeverNames = [ "hyde.fleet" ]

		ix = 0
		ix = self.AddInputs(routeNames, RouteInput, District.route, ix)
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(fleetlLeverNames, FleetLeverInput, District.flever, ix)

		# add "proxy" inputs for the turnouts.  These will not be addressed directly, but through the  route table
		for t in toNames:
			self.rr.AddInput(TurnoutInput(t, self), self, District.turnout)

	def OutIn(self):
		outbc = 5
		outb = [0 for _ in range(outbc)]
		op = self.rr.GetOutput("HSw1").GetOutPulse()
		outb[0] = setBit(outb[0], 0, 1 if op > 0 else 0)                   # switches
		outb[0] = setBit(outb[0], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw3").GetOutPulse()
		outb[0] = setBit(outb[0], 2, 1 if op > 0 else 0)           
		outb[0] = setBit(outb[0], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw7").GetOutPulse()
		outb[0] = setBit(outb[0], 4, 1 if op > 0 else 0)           
		outb[0] = setBit(outb[0], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw9").GetOutPulse()
		outb[0] = setBit(outb[0], 6, 1 if op > 0 else 0)           
		outb[0] = setBit(outb[0], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("HSw11").GetOutPulse()
		outb[1] = setBit(outb[1], 0, 1 if op > 0 else 0)
		outb[1] = setBit(outb[1], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw23").GetOutPulse()
		outb[1] = setBit(outb[1], 2, 1 if op > 0 else 0)           
		outb[1] = setBit(outb[1], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw25").GetOutPulse()
		outb[1] = setBit(outb[1], 4, 1 if op > 0 else 0)           
		outb[1] = setBit(outb[1], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw27").GetOutPulse()
		outb[1] = setBit(outb[1], 6, 1 if op > 0 else 0)           
		outb[1] = setBit(outb[1], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("HSw29").GetOutPulse()
		outb[2] = setBit(outb[2], 0, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw15").GetOutPulse()
		outb[2] = setBit(outb[2], 2, 1 if op > 0 else 0)           
		outb[2] = setBit(outb[2], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw17").GetOutPulse()
		outb[2] = setBit(outb[2], 4, 1 if op > 0 else 0)           
		outb[2] = setBit(outb[2], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("HSw19").GetOutPulse()
		outb[2] = setBit(outb[2], 6, 1 if op > 0 else 0)           
		outb[2] = setBit(outb[2], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("HSw21").GetOutPulse()
		outb[3] = setBit(outb[3], 0, 1 if op > 0 else 0)
		outb[3] = setBit(outb[3], 1, 1 if op < 0 else 0)
		
		outb[3] = setBit(outb[3], 2, self.rr.GetInput("H30").GetValue())    # block indicators
		outb[3] = setBit(outb[3], 3, self.rr.GetInput("H10").GetValue())
		outb[3] = setBit(outb[3], 4, self.rr.GetInput("H23").GetValue())
		N25occ = self.rr.GetInput("N25.W").GetValue() + self.rr.GetInput("N25").GetValue() + self.rr.GetInput("N25.E").GetValue()
		outb[3] = setBit(outb[3], 5, 1 if N25occ != 0 else 0) 
		outb[3] = setBit(outb[3], 6, self.rr.GetOutput("H21.srel").GetStatus())	      # Stop relays
		outb[3] = setBit(outb[3], 7, self.rr.GetOutput("H13.srel").GetStatus())

		outb[4] = setBit(outb[4], 0, self.rr.GetInput("CBHydeJct").GetInvertedValue())    # Circuit breakers
		outb[4] = setBit(outb[4], 1, self.rr.GetInput("CBHydeWest").GetInvertedValue()) 
		outb[4] = setBit(outb[4], 2, self.rr.GetInput("CBHydeEast").GetInvertedValue()) 
		outb[4] = setBit(outb[4], 3, self.rr.GetOutput("HydeWestPower").GetStatus())  # Power Control
		outb[4] = setBit(outb[4], 4, self.rr.GetOutput("HydeEastPower").GetStatus()) 

		otext = formatOText(outb, outbc)
		#logging.debug("Hyde: Output bytes: %s" % otext)
	
		inbc = outbc		
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(HYDE, outb, outbc)

			itext = formatIText(inb, inbc)
			#logging.debug("Hyde: Input Bytes: %s" % itext)

			self.rr.GetInput("H12W").SetValue(getBit(inb[0], 0))   # Routes
			self.rr.GetInput("H34W").SetValue(getBit(inb[0], 1))
			self.rr.GetInput("H33W").SetValue(getBit(inb[0], 2))
			self.rr.GetInput("H30E").SetValue(getBit(inb[0], 3))
			self.rr.GetInput("H31W").SetValue(getBit(inb[0], 4))
			self.rr.GetInput("H32W").SetValue(getBit(inb[0], 5))
			self.rr.GetInput("H22W").SetValue(getBit(inb[0], 6))
			self.rr.GetInput("H43W").SetValue(getBit(inb[0], 7))

			self.rr.GetInput("H42W").SetValue(getBit(inb[1], 0))  
			self.rr.GetInput("H41W").SetValue(getBit(inb[1], 1))
			self.rr.GetInput("H41E").SetValue(getBit(inb[1], 2))
			self.rr.GetInput("H42E").SetValue(getBit(inb[1], 3))
			self.rr.GetInput("H43E").SetValue(getBit(inb[1], 4))
			self.rr.GetInput("H22E").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("H40E").SetValue(getBit(inb[1], 6))
			self.rr.GetInput("H12E").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("H34E").SetValue(getBit(inb[2], 0))  
			self.rr.GetInput("H33E").SetValue(getBit(inb[2], 1))
			self.rr.GetInput("H32E").SetValue(getBit(inb[2], 2))
			self.rr.GetInput("H31E").SetValue(getBit(inb[2], 3))
			self.rr.GetInput("H21").SetValue(getBit(inb[2], 4))   # detection
			self.rr.GetInput("H21.E").SetValue(getBit(inb[2], 5))
			self.rr.GetInput("HOSWW2").SetValue(getBit(inb[2], 6)) # HOS4
			self.rr.GetInput("HOSWW").SetValue(getBit(inb[2], 7)) # HOS5

			self.rr.GetInput("HOSWE").SetValue(getBit(inb[3], 0))  # HOS6
			self.rr.GetInput("H31").SetValue(getBit(inb[3], 1))
			self.rr.GetInput("H32").SetValue(getBit(inb[3], 2))
			self.rr.GetInput("H33").SetValue(getBit(inb[3], 3))
			self.rr.GetInput("H34").SetValue(getBit(inb[3], 4))  
			self.rr.GetInput("H12").SetValue(getBit(inb[3], 5))
			self.rr.GetInput("H22").SetValue(getBit(inb[3], 6))
			self.rr.GetInput("H43").SetValue(getBit(inb[3], 7))

			self.rr.GetInput("H42").SetValue(getBit(inb[4], 0))
			self.rr.GetInput("H41").SetValue(getBit(inb[4], 1))
			self.rr.GetInput("H40").SetValue(getBit(inb[4], 2))
			self.rr.GetInput("HOSEW").SetValue(getBit(inb[4], 3))  # HOS7
			self.rr.GetInput("HOSEE").SetValue(getBit(inb[4], 4))  # HOS8
			self.rr.GetInput("H13.W").SetValue(getBit(inb[4], 5))
			self.rr.GetInput("H13").SetValue(getBit(inb[4], 6))
			
		if self.sendIO:
			self.rr.ShowText("Hyde", HYDE, otext, itext, 0, 1)

