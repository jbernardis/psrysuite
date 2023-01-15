import logging

from district import District, SHORE, HYDEJCT, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, BlockInput, TurnoutInput
from bus import setBit, getBit


class Shore(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		self.S1E = self.S1W = False
		self.S2E = self.S2W = False

		sigNames =  [ "S4LA", "S4LB", "S4LC", "S4R",
						"S8L", "S8R",
						"S12LA", "S12LB", "S12LC", "S12R",
						"S16L", "S16R",
						"S18LA", "S18LB", "S18R",
						"S20L", "S20R" ]
		toNames = [ "SSw3", "SSw5", "SSw7", "SSw9", "SSw11", "SSw13", "SSw15", "SSw17", "SSw19" ]
		hsNames = [ "SSw1" ]
		handswitchNames = [ "SSw1.hand" ]
		relayNames = [ "S20.srel", "S11.srel", "H30.srel", "H10.srel", "F10.srel", "F11.srel", "H20.srel", "H11.srel" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		ix = 0
		ix = self.AddInputs(["S20.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("S20", ["S20A", "S20B", "S20C"], ix)
		ix = self.AddInputs(["S20.E", "SOSW", "SOSE", "S11.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("S11", ["S11A", "S11B"], ix)
		ix = self.AddInputs(["S11.E", "S21", "H30.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("H30", ["H30A", "H30B"], ix)
		ix = self.AddInputs(["H10.W"], BlockInput, District.block, ix)
		ix = self.AddSubBlocks("H10", ["H10A", "H10B"], ix)
		ix = self.AddInputs(["F10", "F10.E", "SOSHF", "F11.W", "F11", "H20", "H20.E", "SOSHJW", "SOSHJM", "SOSHJE", "H11", "H11.W"], BlockInput, District.block, ix)

		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)

	def OutIn(self):
		S10B = self.rr.GetInput("S10B").GetValue() != 0
		S10C = self.rr.GetInput("S10C").GetValue() != 0
		S20B = self.rr.GetInput("S20B").GetValue() != 0
		S20C = self.rr.GetInput("S20C").GetValue() != 0
		if S10B and  not self.S1W:
			self.S1E = True
		if S10C and not self.S1E:
			self.S1W = True
		if not S10B and not S10C:
			self.S1E = self.S1W = False
		if S20B and not self.S2W:
			self.S2E = True
		if S20C and not self.S2E:
			self.S2W = True
		if not S20B and not S20C:
			self.S2E = self.S2W = False

		SXG = (self.S1E and S10B) or (self.S1W and S10C) or (self.S2E and S20B) or (self.S2W and S20C)
		BX = 0

		asp8l = self.rr.GetOutput("S8L").GetAspect()
		asp8r = self.rr.GetOutput("S8R").GetAspect()
		f10occ = self.rr.GetInput("F10").GetValue()
		F10H = asp8l == 0 and f10occ == 0
		F10D = F10H and (asp8r != 0)

		outb = [0 for _ in range(7)]
		asp = self.rr.GetOutput("S4R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # Main Signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S12R").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0)
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S4LA").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S4LB").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3, 5, 7] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S4LC").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 4, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S12LA").GetAspect()
		outb[1] = setBit(outb[1], 5, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 7, 1 if asp in [4, 5, 6, 7] else 0)

		asp = self.rr.GetOutput("S12LB").GetAspect()
		outb[2] = setBit(outb[2], 0, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S12LC").GetAspect()
		outb[2] = setBit(outb[2], 1, 1 if asp in [1, 3, 5, 7] else 0)
		outb[2] = setBit(outb[2], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 3, 1 if asp in [4, 5, 6, 7] else 0)
		outb[2] = setBit(outb[2], 4, 1 if F10H else 0)  # Branch signals
		outb[2] = setBit(outb[2], 5, 1 if F10D else 0)
		asp = self.rr.GetOutput("S8R").GetAspect()
		BX += asp
		outb[2] = setBit(outb[2], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S8L").GetAspect()
		BX += asp
		outb[2] = setBit(outb[2], 7, 1 if asp != 0 else 0)

		# bortell crossing animation being managed by local circuit - these 2 outputs are unnecessary
		# outb[3] = setBit(outb[3], 0, 1 if SXL1 else 0)  # bortelll crossing signal
		# outb[3] = setBit(outb[3], 1, 1 if SXL2 else 0) 
		outb[3] = setBit(outb[3], 2, self.rr.GetInput("S10").GetValue())  #block occupancy indicators
		outb[3] = setBit(outb[3], 3, self.rr.GetInput("H20").GetValue())
		outb[3] = setBit(outb[3], 4, self.rr.GetInput("S21").GetValue())
		outb[3] = setBit(outb[3], 5, self.rr.GetInput("P32").GetValue())
		outb[3] = setBit(outb[3], 6, self.rr.GetInput("CBShore").GetValue())
		outb[3] = setBit(outb[3], 7, self.rr.GetInput("CBHarpersFerry").GetValue())

		outb[4] = setBit(outb[4], 0, 0 if self.rr.GetOutput("SSw1.hand").GetStatus() != 0 else 1) # hand switch unlocks
		op = self.rr.GetOutput("SSw3").GetOutPulse()
		outb[4] = setBit(outb[4], 1, 1 if op > 0 else 0)   # Switch outputs
		outb[4] = setBit(outb[4], 2, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw5").GetOutPulse()
		outb[4] = setBit(outb[4], 3, 1 if op > 0 else 0) 
		outb[4] = setBit(outb[4], 4, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw7").GetOutPulse()
		outb[4] = setBit(outb[4], 5, 1 if op > 0 else 0) 
		outb[4] = setBit(outb[4], 6, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw9").GetOutPulse()
		outb[4] = setBit(outb[4], 7, 1 if op > 0 else 0) 

		outb[5] = setBit(outb[5], 0, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw11").GetOutPulse()
		outb[5] = setBit(outb[5], 1, 1 if op > 0 else 0) 
		outb[5] = setBit(outb[5], 2, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw13").GetOutPulse()
		outb[5] = setBit(outb[5], 3, 1 if op > 0 else 0) 
		outb[5] = setBit(outb[5], 4, 1 if op < 0 else 0)
		outb[5] = setBit(outb[5], 5, 1 if BX != 0 else 0)  # Diamond crossing power relay - power if EITHER S8L or S8L is not STOP
		outb[5] = setBit(outb[5], 6, self.rr.GetOutput("S20.srel").GetStatus())	# Stop relays
		outb[5] = setBit(outb[5], 7, self.rr.GetOutput("S11.srel").GetStatus())

		outb[6] = setBit(outb[6], 0, self.rr.GetOutput("H30.srel").GetStatus())
		outb[6] = setBit(outb[6], 1, self.rr.GetOutput("H10.srel").GetStatus())
		outb[6] = setBit(outb[6], 2, self.rr.GetOutput("F10.srel").GetStatus())
		outb[6] = setBit(outb[6], 3, self.rr.GetOutput("F11.srel").GetStatus())
		outb[6] = setBit(outb[6], 4, 0 if self.rr.GetOutput("CSw15.hand").GetStatus() != 0 else 1) # spikes peak hand switch
		outb[6] = setBit(outb[6], 5, 1 if SXG else 0)  # Bortell crossing gates

		otext = formatOText(outb, 7)
		logging.debug("Shore: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(SHORE, outb, 7, swap=False)

		if inbc != 7:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 2)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Shore: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 2)

			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("SSw1").SetState(nb, rb)
			nb = getBit(inb[0], 2) 
			rb = getBit(inb[0], 3)
			self.rr.GetInput("SSw3").SetState(nb, rb)
			nb = getBit(inb[0], 4) 
			rb = getBit(inb[0], 5)
			self.rr.GetInput("SSw5").SetState(nb, rb)
			nb = getBit(inb[0], 6) 
			rb = getBit(inb[0], 7)
			self.rr.GetInput("SSw7").SetState(nb, rb)

			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			self.rr.GetInput("SSw9").SetState(nb, rb)
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			self.rr.GetInput("SSw11").SetState(nb, rb)
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			self.rr.GetInput("SSw13").SetState(nb, rb)
			self.rr.GetInput("S20.W").SetValue(getBit(inb[1], 6))  # Shore Detection
			self.rr.GetInput("S20A").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("S20B").SetValue(getBit(inb[2], 0))
			self.rr.GetInput("S20C").SetValue(getBit(inb[2], 1))
			self.rr.GetInput("S20.E").SetValue(getBit(inb[2], 2))
			self.rr.GetInput("SOSW").SetValue(getBit(inb[2], 3))
			self.rr.GetInput("SOSE").SetValue(getBit(inb[2], 4))
			self.rr.GetInput("S11.W").SetValue(getBit(inb[2], 5))
			self.rr.GetInput("S11B").SetValue(getBit(inb[2], 6))
			self.rr.GetInput("S11.E").SetValue(getBit(inb[2], 7))

			self.rr.GetInput("H30.W").SetValue(getBit(inb[3], 0))
			self.rr.GetInput("H30B").SetValue(getBit(inb[3], 1))
			self.rr.GetInput("H10.W").SetValue(getBit(inb[3], 2))
			self.rr.GetInput("H10B").SetValue(getBit(inb[3], 3))
			self.rr.GetInput("F10").SetValue(getBit(inb[3], 4))  # Harpers detection
			self.rr.GetInput("F10.E").SetValue(getBit(inb[3], 5))
			self.rr.GetInput("SOSHF").SetValue(getBit(inb[3], 6))
			self.rr.GetInput("F11.W").SetValue(getBit(inb[3], 7))

			self.rr.GetInput("F11").SetValue(getBit(inb[4], 0))
			# 		SXON  = SIn[4].bit.b1;	//Crossing gate off normal - no londer needed
			nb = getBit(inb[4], 2) 
			rb = getBit(inb[4], 3)
			self.rr.GetInput("CSw15").SetState(nb, rb)
			self.rr.GetInput("S11A").SetValue(getBit(inb[4], 4))
			self.rr.GetInput("H30A").SetValue(getBit(inb[4], 5))
			self.rr.GetInput("H10A").SetValue(getBit(inb[4], 6))

		#  Hyde Junction
		outb = [0 for _ in range(3)]
		asp = self.rr.GetOutput("S16R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S18R").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0)
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S20R").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S16L").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3, 5, 7] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("S18LB").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S18LA").GetAspect()
		outb[1] = setBit(outb[1], 3, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("S20L").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if asp in [4, 5, 6, 7] else 0)
		op = self.rr.GetOutput("SSw15").GetOutPulse()  # switches
		outb[1] = setBit(outb[1], 7, 1 if op > 0 else 0)

		outb[2] = setBit(outb[2], 0, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw17").GetOutPulse()
		outb[2] = setBit(outb[2], 1, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 2, 1 if op < 0 else 0)
		op = self.rr.GetOutput("SSw19").GetOutPulse()
		outb[2] = setBit(outb[2], 3, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 4, 1 if op < 0 else 0)
		outb[2] = setBit(outb[2], 5, self.rr.GetOutput("H20.srel").GetStatus())	# Stop relays
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("P42.srel").GetStatus())
		outb[2] = setBit(outb[2], 7, self.rr.GetOutput("H11.srel").GetStatus())	

		otext = formatOText(outb, 3)
		logging.debug("Hyde Jct: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(HYDEJCT, outb, 3, swap=False)

		if inbc != 3:
			if self.sendIO:
				self.rr.ShowText(otext, "", 1, 2)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Hyde Jct: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 1, 2)

			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("SSw15").SetState(nb, rb)
			nb = getBit(inb[0], 2) 
			rb = getBit(inb[0], 3)
			self.rr.GetInput("SSw17").SetState(nb, rb)
			nb = getBit(inb[0], 4) 
			rb = getBit(inb[0], 5)
			self.rr.GetInput("SSw19").SetState(nb, rb)
			self.rr.GetInput("H20").SetValue(getBit(inb[0], 6))  # Detection
			self.rr.GetInput("H20.E").SetValue(getBit(inb[0], 7)) 

			self.rr.GetInput("P42.W").SetValue(getBit(inb[1], 0)) 
			self.rr.GetInput("P42").SetValue(getBit(inb[1], 1)) 
			self.rr.GetInput("P42.E").SetValue(getBit(inb[1], 2)) 
			self.rr.GetInput("SOSHJW").SetValue(getBit(inb[1], 3)) # HOS1
			self.rr.GetInput("SOSHJM").SetValue(getBit(inb[1], 4)) # HOS2
			self.rr.GetInput("SOSHJE").SetValue(getBit(inb[1], 5)) # HOS3
			self.rr.GetInput("H11.W").SetValue(getBit(inb[1], 6)) 
			self.rr.GetInput("H11").SetValue(getBit(inb[1], 7)) 
