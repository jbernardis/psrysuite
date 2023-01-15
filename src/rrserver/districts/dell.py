import logging

from district import District, DELL, FOSS, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, BlockInput, TurnoutInput
from bus import setBit, getBit

class Dell(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		self.D1W = self.D1E = self.D2W = self.D2E = False
		self.RXW = self.RXE = False

		sigNames =  [ "D4RA", "D4RB", "D4L",
						"D6RA", "D6RB", "D6L",
						"DXO", 
						"D10R", "D10L",
						"D12R", "D12L",
						"RXO", "R10W"
						]
		toNames = [ "DSw1", "DSw3", "DSw5", "DSw7", "DSw11" ]
		hsNames = [ "DSw9" ]
		handswitchNames = [ "DSw9.hand" ]
		relayNames = [ "H23.srel", "D11.srel", "D20.srel", "D21.srel", "S10.srel", "R10.srel" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		ix = 0
		ix = self.AddInputs(["D20", "D20.E", "H23", "H23.E", "DOSVJW", "DOSVJE", "D11.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("D11", ["D11A", "D11B"], ix)
		ix = self.AddInputs(["D11.E", "D21.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("D21", ["D21A", "D21B"], ix)
		ix = self.AddInputs(["D21.E", "DOSFOW", "DOSFOE", "S10.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("S10", ["S10A", "S10B", "S10C"], ix)
		ix = self.AddInputs(["S10.E"], BlockInput, District.block, ix)
		#ix = self.AddSubBlocks("R10", ["R10A", "R10B", "R10C"], ix)
		ix = self.AddInputs(["R11", "R12"], BlockInput, District.block, ix)

		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)

	def OutIn(self):
		# determine the state of the crossing gate at laporte
		dos1 = self.rr.GetInput("DOSVJW").GetValue() != 0
		d11w = self.rr.GetInput("D11.W").GetValue() != 0
		d11a = self.rr.GetInput("D11A").GetValue() != 0
		if dos1 and not self.D1W:
			self.D1E = True
		if (d11w or d11a) and not self.D1E:
			self.D1W = True
		if not dos1 and not (d11w or d11a):
			self.D1E = self.D1W = False

		dos2 = self.rr.GetInput("DOSVJE").GetValue() != 0
		d21w = self.rr.GetInput("D21.W").GetValue() != 0
		d21a = self.rr.GetInput("D21A").GetValue() != 0
		if dos2 and not self.D2W:
			self.D2E = True
		if (d21w or d21a) and not self.D2E:
			self.D2W = True
		if not dos2 and not (d21w or d21a):
			self.D2E = self.D2W = False

		DXO = (self.D1E and dos1) or (self.D1W and (d11w or d11a)) or (self.D2E and dos2) or (self.D2W and (d21w or d21a))

		# determine the state of the crossing gate at rocky hill
		r10b = self.rr.GetInput("R10B").GetValue() != 0
		r10c = self.rr.GetInput("R10C").GetValue() != 0
		if r10b and not self.RXW:
			self.RXE = True
		if r10c and not self.RXE:
			self.RXW = True
		if not r10b and not r10c:
			self.RXE = self.RXW = False

		RXO = (r10b and self.RXE) or (r10c and self.RXW)

		#Dell
		outb = [0 for _ in range(4)]
		asp = self.rr.GetOutput("D4RA").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # eastbound signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("D4RB").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("D6RA").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("D6RB").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp != 0 else 0)

		asp = self.rr.GetOutput("D4L").GetAspect()
		outb[1] = setBit(outb[1], 0, 1 if asp in [1, 3, 5, 7] else 0)  # westbound signals
		outb[1] = setBit(outb[1], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("D6L").GetAspect()
		outb[1] = setBit(outb[1], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [4, 5, 6, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if DXO else 0) # laporte crossing signal
		outb[1] = setBit(outb[1], 7, self.rr.GetInput("H13").GetValue())  #block indicators

		outb[2] = setBit(outb[2], 0, self.rr.GetInput("D10").GetValue())
		outb[2] = setBit(outb[2], 1, self.rr.GetInput("S20").GetValue())
		outb[2] = setBit(outb[2], 2, 0 if self.rr.GetOutput("DSw9.hand").GetStatus() != 0 else 1) 
		op = self.rr.GetOutput("DSw1").GetOutPulse()
		outb[2] = setBit(outb[2], 3, 1 if op > 0 else 0)                   # switches
		outb[2] = setBit(outb[2], 4, 1 if op < 0 else 0)
		op = self.rr.GetOutput("DSw3").GetOutPulse()
		outb[2] = setBit(outb[2], 5, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 6, 1 if op < 0 else 0)
		op = self.rr.GetOutput("DSw5").GetOutPulse()
		outb[2] = setBit(outb[2], 7, 1 if op > 0 else 0) 

		outb[3] = setBit(outb[3], 0, 1 if op < 0 else 0)
		op = self.rr.GetOutput("DSw7").GetOutPulse()
		outb[3] = setBit(outb[3], 1, 1 if op > 0 else 0)
		outb[3] = setBit(outb[3], 2, 1 if op < 0 else 0)
		op = self.rr.GetOutput("DSw11").GetOutPulse()
		outb[3] = setBit(outb[3], 3, 1 if op > 0 else 0)
		outb[3] = setBit(outb[3], 4, 1 if op < 0 else 0)
		outb[3] = setBit(outb[3], 5, self.rr.GetOutput("D20.srel").GetStatus())	# Stop relays
		outb[3] = setBit(outb[3], 6, self.rr.GetOutput("H23.srel").GetStatus())
		outb[3] = setBit(outb[3], 7, self.rr.GetOutput("D11.srel").GetStatus())

		otext = formatOText(outb, 4)
		logging.debug("Dell: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(DELL, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 2)
		else:
			itext = formatIText(inb, 3)
			logging.debug("Dell: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 2)

			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("DSw1").SetState(nb, rb)
			nb = getBit(inb[0], 2) 
			rb = getBit(inb[0], 3)
			self.rr.GetInput("DSw3").SetState(nb, rb)
			nb = getBit(inb[0], 4) 
			rb = getBit(inb[0], 5)
			self.rr.GetInput("DSw5").SetState(nb, rb)
			nb = getBit(inb[0], 6) 
			rb = getBit(inb[0], 7)
			self.rr.GetInput("DSw7").SetState(nb, rb)

			nb = getBit(inb[1], 0)  
			rb = getBit(inb[1], 1)
			self.rr.GetInput("DSw9").SetState(nb, rb)
			nb = getBit(inb[1], 2)  
			rb = getBit(inb[1], 3)
			self.rr.GetInput("DSw11").SetState(nb, rb)
			self.rr.GetInput("D20").SetValue(getBit(inb[1], 4))  # Detection
			self.rr.GetInput("D20.E").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("H23").SetValue(getBit(inb[1], 6)) 
			self.rr.GetInput("H23.E").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("DOSVJW").SetValue(getBit(inb[2], 0)) #DOS1
			self.rr.GetInput("DOSVJE").SetValue(getBit(inb[2], 1)) #DOS2
			self.rr.GetInput("D11.W").SetValue(getBit(inb[2], 2))
			self.rr.GetInput("D11A").SetValue(getBit(inb[2], 3))
			self.rr.GetInput("D11B").SetValue(getBit(inb[2], 4))
			self.rr.GetInput("D11.E").SetValue(getBit(inb[2], 5))

		# Foss
		outb = [0 for _ in range(3)]
		asp = self.rr.GetOutput("D10R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # eastbound signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("D12R").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)

		asp = self.rr.GetOutput("D10L").GetAspect()
		outb[1] = setBit(outb[1], 0, 1 if asp in [1, 3, 5, 7] else 0)  # westbound signals
		outb[1] = setBit(outb[1], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("D12L").GetAspect()
		outb[1] = setBit(outb[1], 3, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[1] = setBit(outb[1], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [4, 5, 6, 7] else 0)
		outb[1] = setBit(outb[1], 6, self.rr.GetOutput("D21.srel").GetStatus())	# Stop relays
		outb[1] = setBit(outb[1], 7, self.rr.GetOutput("S10.srel").GetStatus())

		# bit 2:0 is bad
		outb[2] = setBit(outb[2], 1, self.rr.GetOutput("R10.srel").GetStatus())
		outb[2] = setBit(outb[2], 2, 1 if RXO else 0)  # rocky hill crossing signal
		asp = self.rr.GetOutput("R10W").GetAspect()
		outb[2] = setBit(outb[2], 3, 1 if asp in [1, 3, 5, 7] else 0)  # rocky hill distant for nassau
		outb[2] = setBit(outb[2], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 5, 1 if asp in [4, 5, 6, 7] else 0)

		otext = formatOText(outb, 3)
		logging.debug("Foss: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(FOSS, outb, 3, swap=False)

		if inbc != 3:
			if self.sendIO:
				self.rr.ShowText(otext, "", 1, 2)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("FOSS: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 1, 2)

			self.rr.GetInput("D21.W").SetValue(getBit(inb[0], 0))  # Detection
			self.rr.GetInput("D21A").SetValue(getBit(inb[0], 1))
			self.rr.GetInput("D21B").SetValue(getBit(inb[0], 2))
			self.rr.GetInput("D21.E").SetValue(getBit(inb[0], 3))
			self.rr.GetInput("DOSFOW").SetValue(getBit(inb[0], 4)) #MFOS1
			self.rr.GetInput("DOSFOE").SetValue(getBit(inb[0], 5)) #MFOS2
			self.rr.GetInput("S10.W").SetValue(getBit(inb[0], 6))
			self.rr.GetInput("S10A").SetValue(getBit(inb[0], 7))

			self.rr.GetInput("S10B").SetValue(getBit(inb[1], 0))
			self.rr.GetInput("S10C").SetValue(getBit(inb[1], 1))
			self.rr.GetInput("S10.E").SetValue(getBit(inb[1], 2))
			self.rr.GetInput("R10.W").SetValue(getBit(inb[1], 3))
			self.rr.GetInput("R10A").SetValue(getBit(inb[1], 4)) 
			self.rr.GetInput("R10B").SetValue(getBit(inb[1], 5)) 
			self.rr.GetInput("R10C").SetValue(getBit(inb[1], 6))
			self.rr.GetInput("R11").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("R12").SetValue(getBit(inb[2], 0))

