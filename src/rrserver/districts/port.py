import logging

from rrserver.district import District, leverState, PORTA, PORTB, PARSONS, formatIText, formatOText
from rrserver.rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, ToggleInput, SignalLeverInput, BlockInput, TurnoutInput, \
		IndicatorOutput, HandswitchLeverInput
from rrserver.bus import setBit, getBit


class Port(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)
		self.PBE = False
		self.PBW = False

		sigNames = [ ["PA12R", 2], ["PA12LA", 1], ["PA12LB", 1], ["PA12LC", 1], ["PA10RA", 2], ["PA10RB", 2], ["PA10L", 1],
					["PA8R", 2], ["PA8L", 1], ["PA6R", 2], ["PA6LA", 1], ["PA6LB", 1], ["PA6LC", 1], ["PA4RA", 2], ["PA4RB", 2], ["PA4L", 1],
					["PA34RA", 1], ["PA34RB", 1], ["PA34RC", 1], ["PA34RD", 3], ["PA34LA", 3], ["PA34LB", 3], ["PA32RA", 3], ["PA32RB", 3], ["PA32L", 1],
					["PB2R", 3], ["PB2L", 3], ["PB4R", 3], ["PB4L", 3], ["PB12R", 3], ["PB12L", 3], ["PB14R", 3], ["PB14L", 3] ]
		toNames = [ "PBSw1", "PBSw3", "PBSw11", "PBSw13",
					"PASw1", "PASw3", "PASw5", "PASw7", "PASw9", "PASw11", "PASw13",
					"PASw15", "PASw17", "PASw19", "PASw21", "PASw23",
					"PASw27", "PASw29", "PASw31", "PASw33", "PASw35", "PASw37"]
		hsNames = [ "PBSw5", "PBSw15a", "PBSw15b" ]
		handswitchNames = [ "PBSw5.hand", "PBSw15a.hand", "PBSw15b.hand" ]
		#relayNames = [ "P10.srel", "P11.srel", "P20.srel", "P21.srel",
		relayNames = [ "P10.srel", "P11.srel", "P20.srel",
					"P30.srel", "P31.srel", "P32.srel", "P40.srel", "P41.srel", "P42.srel" ]
		indNames = [ "CBParsonsJct", "CBSouthport", "CBLavinYard", "CBSouthJct", "CBCircusJct" ]

		ix = 0
		ix = self.AddOutputs([s[0] for s in sigNames], SignalOutput, District.signal, ix)
		for sig, bits in sigNames:
			self.rr.GetOutput(sig).SetBits(bits)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen, settings.topulsect)

		#				"P10", "P10.E", "P11.W", "P11", "P11.E", "P20", "P20.E", "P21", "P21.E",
		blockNames = [ "P1", "P2", "P3", "P4", "P5", "P6", "P7",
						"P10", "P10.E", "P11.W", "P11", "P11.E", "P20", "P20.E",
						"P30.W", "P30", "P30.E", "P31.W", "P31", "P31.E", "P32.W", "P32", "P32.E",
						"P40", "P40.E", "P41.W", "P41", "P41.E", "P42.W", "P42", "P42.E", "P50.W", "P50", "P50.E",
						"P60", "P61", "P62", "P63", "P64", "V10", "V11",
						"POSCJ1", "POSCJ2", "POSSJ1", "POSSJ2", "POSPJ1", "POSPJ2",
						"POSSP1", "POSSP2", "POSSP3", "POSSP4", "POSSP5" ]
		signalLeverNames = [ "PA4.lvr", "PA6.lvr", "PA8.lvr", "PA10.lvr", "PA12.lvr", "PA32.lvr", "PA34.lvr",
						"PB2.lvr", "PB4.lvr", "PB12.lvr", "PB14.lvr" ]
		hsLeverNames = [ "PBSw5.lvr", "PBSw15a.lvr", "PBSw15b.lvr" ]
		toggleNames = [ "parelease", "pbrelease" ]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(hsLeverNames, HandswitchLeverInput, District.hslever, ix)
		ix = self.AddInputs(toggleNames, ToggleInput, District.toggle, ix)

	def OutIn(self):
		P40M = self.rr.GetInput("P40").GetValue() != 0
		P40E = self.rr.GetInput("P40.E").GetValue() != 0
		if P40M and not self.PBE:
			self.PBW = True
		if P40E and not self.PBW:
			self.PBE = True
		if not P40M and not P40E:
			self.PBE = self.PBW = False
		PBXO = (P40E and self.PBE) or (P40M and self.PBW)

		# Port A
		#
		# Southport
		outbc = 9
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("PA12R").GetAspectBits(2)
		outb[0] = setBit(outb[0], 0, asp[0])  # signals
		outb[0] = setBit(outb[0], 1, asp[1])
		asp = self.rr.GetOutput("PA10RA").GetAspectBits(2)
		outb[0] = setBit(outb[0], 2, asp[0])
		outb[0] = setBit(outb[0], 3, asp[1])
		asp = self.rr.GetOutput("PA12LA").GetAspectBits(1)
		outb[0] = setBit(outb[0], 4, asp[0])
		asp = self.rr.GetOutput("PA10RB").GetAspectBits(2)
		outb[0] = setBit(outb[0], 5, asp[0])
		outb[0] = setBit(outb[0], 6, asp[1])
		asp = self.rr.GetOutput("PA8R").GetAspectBits(2)
		outb[0] = setBit(outb[0], 7, asp[0])

		outb[1] = setBit(outb[1], 0, asp[1])
		asp = self.rr.GetOutput("PA12LB").GetAspectBits(1)
		outb[1] = setBit(outb[1], 1, asp[0])
		asp = self.rr.GetOutput("PA6R").GetAspectBits(2)
		outb[1] = setBit(outb[1], 2, asp[0])
		outb[1] = setBit(outb[1], 3, asp[1])
		asp = self.rr.GetOutput("PA4RA").GetAspectBits(2)
		outb[1] = setBit(outb[1], 4, asp[0])
		outb[1] = setBit(outb[1], 5, asp[1])
		asp = self.rr.GetOutput("PA12LC").GetAspectBits(1)
		outb[1] = setBit(outb[1], 6, asp[0])
		asp = self.rr.GetOutput("PA4RB").GetAspectBits(2)
		outb[1] = setBit(outb[1], 7, asp[0])

		outb[2] = setBit(outb[2], 0, asp[1])
		asp = self.rr.GetOutput("PA8L").GetAspectBits(1)
		outb[2] = setBit(outb[2], 1, asp[0])
		asp = self.rr.GetOutput("PA6LA").GetAspectBits(1)
		outb[2] = setBit(outb[2], 2, asp[0])
		asp = self.rr.GetOutput("PA6LB").GetAspectBits(1)
		outb[2] = setBit(outb[2], 3, asp[0])
		asp = self.rr.GetOutput("PA6LC").GetAspectBits(1)
		outb[2] = setBit(outb[2], 4, asp[0])
		inp = self.rr.GetInput("P10")
		clr10w = inp.GetClear() and not inp.GetEast()
		outb[5] = setBit(outb[2], 5, 1 if clr10w else 0)  # semaphore signal
		outb[5] = setBit(outb[2], 6, 1 if clr10w else 0)  # should be using RstrW
		st = self.rr.GetInput("PA4.lvr")   # Signal indicators
		outb[2] = setBit(outb[2], 7, 1 if st == "L" else 0)

		outb[3] = setBit(outb[3], 0, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 1, 1 if st == "R" else 0)
		st = self.rr.GetInput("PA6.lvr")
		outb[3] = setBit(outb[3], 2, 1 if st == "L" else 0)
		outb[3] = setBit(outb[3], 3, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 4, 1 if st == "R" else 0)
		st = self.rr.GetInput("PA8.lvr")
		outb[3] = setBit(outb[3], 5, 1 if st == "L" else 0)
		outb[3] = setBit(outb[3], 6, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 7, 1 if st == "R" else 0)

		st = self.rr.GetInput("PA10.lvr")
		outb[4] = setBit(outb[4], 0, 1 if st == "L" else 0)
		outb[4] = setBit(outb[4], 1, 1 if st == "N" else 0)
		outb[4] = setBit(outb[4], 2, 1 if st == "R" else 0)
		st = self.rr.GetInput("PA12.lvr")
		outb[4] = setBit(outb[4], 3, 1 if st == "L" else 0)
		outb[4] = setBit(outb[4], 4, 1 if st == "N" else 0)
		outb[4] = setBit(outb[4], 5, 1 if st == "R" else 0)
		st = self.rr.GetInput("PA32.lvr")
		outb[4] = setBit(outb[4], 6, 1 if st == "L" else 0)
		outb[4] = setBit(outb[4], 7, 1 if st == "N" else 0)

		outb[5] = setBit(outb[5], 0, 1 if st == "R" else 0)
		st = self.rr.GetInput("PA34.lvr")
		outb[5] = setBit(outb[5], 1, 1 if st == "L" else 0)
		outb[5] = setBit(outb[5], 2, 1 if st == "N" else 0)
		outb[5] = setBit(outb[5], 3, 1 if st == "R" else 0)
		outb[5] = setBit(outb[5], 4, self.rr.GetInput("P21").GetValue())  # Block indicators
		outb[5] = setBit(outb[5], 5, self.rr.GetInput("P40").GetValue())
		inp = self.rr.GetInput("P50")
		clr50w = inp.GetClear() and not inp.GetEast()
		outb[5] = setBit(outb[5], 6, 1 if clr50w else 0)  # Yard signal
		inp = self.rr.GetInput("P11")
		clr11e = inp.GetClear() and inp.GetEast()
		outb[5] = setBit(outb[5], 7, 1 if clr11e else 0)  # latham signals

		inp = self.rr.GetInput("P21")
		clr21e = inp.GetClear() and inp.GetEast()
		outb[6] = setBit(outb[6], 0, 1 if clr21e else 0)
		outb[6] = setBit(outb[6], 1, self.rr.GetInput("CBParsonsJct").GetInvertedValue())  # Circuit breakers
		outb[6] = setBit(outb[6], 2, self.rr.GetInput("CBSouthport").GetInvertedValue())
		outb[6] = setBit(outb[6], 3, self.rr.GetInput("CBLavinYard").GetInvertedValue())
		outb[6] = setBit(outb[6], 4, 1 if self.rr.GetSwitchLock("PASw1") else 0)  # Switch Locks
		outb[6] = setBit(outb[6], 5, 1 if self.rr.GetSwitchLock("PASw3") else 0)
		outb[6] = setBit(outb[6], 6, 1 if self.rr.GetSwitchLock("PASw5") else 0)
		outb[6] = setBit(outb[6], 7, 1 if self.rr.GetSwitchLock("PASw7") else 0)

		outb[7] = setBit(outb[7], 0, 1 if self.rr.GetSwitchLock("PASw9") else 0)
		outb[7] = setBit(outb[7], 1, 1 if self.rr.GetSwitchLock("PASw11") else 0)  # also locks 13
		outb[7] = setBit(outb[7], 2, 1 if self.rr.GetSwitchLock("PASw15") else 0)  # also locks 17
		outb[7] = setBit(outb[7], 3, 1 if self.rr.GetSwitchLock("PASw19") else 0)
		outb[7] = setBit(outb[7], 4, 1 if self.rr.GetSwitchLock("PASw21") else 0)
		outb[7] = setBit(outb[7], 5, 1 if self.rr.GetSwitchLock("PASw23") else 0)
		outb[7] = setBit(outb[7], 6, 1 if self.rr.GetSwitchLock("PASw31") else 0)  # also locks 27 and 29
		outb[7] = setBit(outb[7], 7, 1 if self.rr.GetSwitchLock("PASw33") else 0)

		outb[8] = setBit(outb[8], 0, 1 if self.rr.GetSwitchLock("PASw35") else 0)
		outb[8] = setBit(outb[8], 1, 1 if self.rr.GetSwitchLock("PASw37") else 0)
		outb[8] = setBit(outb[8], 2, self.rr.GetOutput("P10.srel").GetStatus())	      # Stop relays
		outb[8] = setBit(outb[8], 2, self.rr.GetOutput("P40.srel").GetStatus())
		outb[8] = setBit(outb[8], 2, self.rr.GetOutput("P31.srel").GetStatus())
		inp = self.rr.GetInput("P40")
		clr40w = inp.GetClear() and not inp.GetEast()
		outb[8] = setBit(outb[2], 5, 1 if clr40w else 0)  # semaphore signal
		outb[8] = setBit(outb[2], 6, 1 if clr40w else 0)  # should be using RstrW

		otext = formatOText(outb, outbc)
		#logging.debug("Port A: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(PORTA, outb, outbc)

			itext = formatIText(inb, inbc)
			#logging.debug("Port A: Input Bytes: %s" % itext)

			ip = self.rr.GetInput("PASw1")  # Switch positions
			nb = getBit(inb[0], 0)
			rb = getBit(inb[0], 1)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw3")
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw5")
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw7")
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			ip.SetTOState(nb, rb)

			ip = self.rr.GetInput("PASw9")
			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw11")
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw13")
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw15")
			nb = getBit(inb[1], 6)
			rb = getBit(inb[1], 7)
			ip.SetTOState(nb, rb)

			ip = self.rr.GetInput("PASw17")
			nb = getBit(inb[2], 0)
			rb = getBit(inb[2], 1)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw19")
			nb = getBit(inb[2], 2)
			rb = getBit(inb[2], 3)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw21")
			nb = getBit(inb[2], 4)
			rb = getBit(inb[2], 5)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw23")
			nb = getBit(inb[2], 6)
			rb = getBit(inb[2], 7)
			ip.SetTOState(nb, rb)

			ip = self.rr.GetInput("P1")
			ip.SetValue(getBit(inb[3], 0))   # detection
			ip = self.rr.GetInput("P2")
			ip.SetValue(getBit(inb[3], 1))
			ip = self.rr.GetInput("P3")
			ip.SetValue(getBit(inb[3], 2))
			ip = self.rr.GetInput("P4")
			ip.SetValue(getBit(inb[3], 3))
			ip = self.rr.GetInput("P5")
			ip.SetValue(getBit(inb[3], 4))
			ip = self.rr.GetInput("P6")
			ip.SetValue(getBit(inb[3], 5))
			ip = self.rr.GetInput("P7")
			ip.SetValue(getBit(inb[3], 6))
			ip = self.rr.GetInput("POSSP1")
			ip.SetValue(getBit(inb[3], 7))  # PAOS1

			ip = self.rr.GetInput("POSSP2")
			ip.SetValue(getBit(inb[4], 0))  # PAOS2
			ip = self.rr.GetInput("POSSP3")
			ip.SetValue(getBit(inb[4], 1))  # PAOS3
			ip = self.rr.GetInput("POSSP4")
			ip.SetValue(getBit(inb[4], 2))  # PAOS4
			ip = self.rr.GetInput("POSSP5")
			ip.SetValue(getBit(inb[4], 3))  # PAOS5
			ip = self.rr.GetInput("P10")
			ip.SetValue(getBit(inb[4], 4))
			ip = self.rr.GetInput("P10.E")
			ip.SetValue(getBit(inb[4], 5))

			lvrL = getBit(inb[4], 6)       # signal levers
			lvrCallOn = getBit(inb[4], 7)

			lvrR = getBit(inb[5], 0)
			self.rr.GetInput("PA4.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[5], 1)
			lvrCallOn = getBit(inb[5], 2)
			lvrR = getBit(inb[5], 3)
			self.rr.GetInput("PA6.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[5], 4)
			lvrCallOn = getBit(inb[5], 5)
			lvrR = getBit(inb[5], 6)
			self.rr.GetInput("PA8.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[5], 7)

			lvrCallOn = getBit(inb[6], 0)
			lvrR = getBit(inb[6], 1)
			self.rr.GetInput("PA10.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[6], 2)
			lvrCallOn = getBit(inb[6], 3)
			lvrR = getBit(inb[6], 4)
			self.rr.GetInput("PA12.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[6], 5)
			lvrCallOn = getBit(inb[6], 6)
			lvrR = getBit(inb[6], 7)
			self.rr.GetInput("PA32.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

			lvrL = getBit(inb[7], 0)
			lvrCallOn = getBit(inb[7], 1)
			lvrR = getBit(inb[7], 2)
			self.rr.GetInput("PA34.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			release = getBit(inb[7], 3)
			self.rr.GetInput("parelease").SetState(release)  # Port A Release switch
	
		if self.sendIO:
			self.rr.ShowText("PrtA", PORTA, otext, itext, 0, 3)

		# Parsons Junction
		outbc = 4
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("PA34LB").GetAspectBits(3)
		outb[0] = setBit(outb[0], 0, asp[0])  # westward signals
		outb[0] = setBit(outb[0], 1, asp[1])
		outb[0] = setBit(outb[0], 2, asp[2])
		asp = self.rr.GetOutput("PA32L").GetAspectBits(1)
		outb[0] = setBit(outb[0], 3, asp[0])
		asp = self.rr.GetOutput("PA34LA").GetAspectBits(3)
		outb[0] = setBit(outb[0], 4, asp[0])
		outb[0] = setBit(outb[0], 5, asp[1])
		outb[0] = setBit(outb[0], 6, asp[2])
		asp = self.rr.GetOutput("PA34RD").GetAspectBits(3)
		outb[0] = setBit(outb[0], 7, asp[0])  # eastward signals

		outb[1] = setBit(outb[1], 0, asp[1])
		outb[1] = setBit(outb[1], 1, asp[2])
		asp = self.rr.GetOutput("PA34RC").GetAspectBits(1)
		outb[1] = setBit(outb[1], 2, asp[0])  # eastward signals
		asp = self.rr.GetOutput("PA32RA").GetAspectBits(3)
		outb[1] = setBit(outb[1], 3, asp[0])
		outb[1] = setBit(outb[1], 4, asp[1])
		outb[1] = setBit(outb[1], 5, asp[2])
		asp = self.rr.GetOutput("PA34RB").GetAspectBits(1)
		outb[1] = setBit(outb[1], 6, asp[0])  # eastward signals
		asp = self.rr.GetOutput("PA32RB").GetAspectBits(3)
		outb[1] = setBit(outb[1], 7, asp[0])

		outb[2] = setBit(outb[2], 0, asp[1])
		outb[2] = setBit(outb[2], 1, asp[2])
		asp = self.rr.GetOutput("PA34RA").GetAspectBits(1)
		outb[2] = setBit(outb[2], 2, asp[0])  # eastward signals
		outb[2] = setBit(outb[2], 3, self.rr.GetOutput("P20.srel").GetStatus())	      # Stop relays
		outb[2] = setBit(outb[2], 4, self.rr.GetOutput("P30.srel").GetStatus())
		outb[2] = setBit(outb[2], 5, self.rr.GetOutput("P50.srel").GetStatus())
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("P11.srel").GetStatus())

		otext = formatOText(outb, outbc)
		#logging.debug("Parsons: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(PARSONS, outb, outbc)

			itext = formatIText(inb, inbc)
			#logging.debug("Parsons: Input Bytes: %s" % itext)

			ip = self.rr.GetInput("PASw27")  # Switch positions
			nb = getBit(inb[0], 0)
			rb = getBit(inb[0], 1)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw29")
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw31")
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw33")
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			ip.SetTOState(nb, rb)

			ip = self.rr.GetInput("PASw35")
			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("PASw37")
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			ip.SetTOState(nb, rb)
			ip = self.rr.GetInput("P20")
			ip.SetValue(getBit(inb[1], 4))   # detection
			ip = self.rr.GetInput("P20.E")
			ip.SetValue(getBit(inb[1], 5))
			ip = self.rr.GetInput("P30.W")
			ip.SetValue(getBit(inb[1], 6))
			ip = self.rr.GetInput("P30")
			ip.SetValue(getBit(inb[1], 7))

			ip = self.rr.GetInput("P30.E")
			ip.SetValue(getBit(inb[2], 0))
			ip = self.rr.GetInput("POSPJ1")  # PJOS1
			ip.SetValue(getBit(inb[2], 1))
			ip = self.rr.GetInput("POSPJ2")  # PJOS2
			ip.SetValue(getBit(inb[2], 2))
			ip = self.rr.GetInput("P50.W")
			ip.SetValue(getBit(inb[2], 3))
			ip = self.rr.GetInput("P50")
			ip.SetValue(getBit(inb[2], 4))
			ip = self.rr.GetInput("P50.E")
			ip.SetValue(getBit(inb[2], 5))
			ip = self.rr.GetInput("P11.W")
			ip.SetValue(getBit(inb[2], 6))
			ip = self.rr.GetInput("P11")
			ip.SetValue(getBit(inb[2], 7))

			ip = self.rr.GetInput("P11.E")
			ip.SetValue(getBit(inb[3], 0))
				
		if self.sendIO:
			self.rr.ShowText("PJct", PARSONS, otext, itext, 1, 3)

		#  Port B
		outbc = 7
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("PB2R").GetAspectBits(3)
		outb[0] = setBit(outb[0], 0, asp[0])  # South Jct Eastward signals
		outb[0] = setBit(outb[0], 1, asp[1])
		outb[0] = setBit(outb[0], 2, asp[2])
		asp = self.rr.GetOutput("PB4R").GetAspectBits(3)
		outb[0] = setBit(outb[0], 3, asp[0])
		outb[0] = setBit(outb[0], 4, asp[1])
		outb[0] = setBit(outb[0], 5, asp[2])
		asp = self.rr.GetOutput("PB2L").GetAspectBits(3)
		outb[0] = setBit(outb[0], 6, asp[0])  # South Jct Westward signals
		outb[0] = setBit(outb[0], 7, asp[1])

		outb[1] = setBit(outb[1], 0, asp[2])
		asp = self.rr.GetOutput("PB4L").GetAspectBits(3)
		outb[1] = setBit(outb[1], 1, asp[0])
		outb[1] = setBit(outb[1], 2, asp[1])
		outb[1] = setBit(outb[1], 3, asp[2])
		asp = self.rr.GetOutput("PB12L").GetAspectBits(3)
		outb[1] = setBit(outb[1], 4, asp[0])  # Circus Jct Eastward signals
		outb[1] = setBit(outb[1], 5, asp[1])
		outb[1] = setBit(outb[1], 6, asp[2])
		asp = self.rr.GetOutput("PB14L").GetAspectBits(3)
		outb[1] = setBit(outb[1], 7, asp[0])

		outb[2] = setBit(outb[2], 0, asp[1])
		outb[2] = setBit(outb[2], 1, asp[2])
		asp = self.rr.GetOutput("PB12R").GetAspectBits(3)
		outb[2] = setBit(outb[2], 2, asp[0])  # Circus Jct Westward signals
		outb[2] = setBit(outb[2], 3, asp[1])
		outb[2] = setBit(outb[2], 4, asp[2])
		asp = self.rr.GetOutput("PB14R").GetAspectBits(3)
		outb[2] = setBit(outb[2], 5, asp[0])
		outb[2] = setBit(outb[2], 6, asp[1])
		outb[2] = setBit(outb[2], 7, asp[2])

		st = self.rr.GetInput("PB2.lvr")
		outb[3] = setBit(outb[3], 0, 1 if st == "L" else 0)  # Signal indicators
		outb[3] = setBit(outb[3], 1, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 2, 1 if st == "R" else 0)
		st = self.rr.GetInput("PB4.lvr")
		outb[3] = setBit(outb[3], 3, 1 if st == "L" else 0)
		outb[3] = setBit(outb[3], 4, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 5, 1 if st == "R" else 0)
		locked = self.rr.GetOutput("PBSw5.hand").GetStatus() != 0  # Hand switch unlock indicators
		outb[3] = setBit(outb[3], 6, 0 if locked else 1)
		outb[3] = setBit(outb[3], 7, 1 if locked else 0)

		st = self.rr.GetInput("PB12.lvr")
		outb[3] = setBit(outb[3], 0, 1 if st == "L" else 0)  # Signal indicators
		outb[3] = setBit(outb[3], 1, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 2, 1 if st == "R" else 0)
		st = self.rr.GetInput("PB14.lvr")
		outb[3] = setBit(outb[3], 3, 1 if st == "L" else 0)
		outb[3] = setBit(outb[3], 4, 1 if st == "N" else 0)
		outb[3] = setBit(outb[3], 5, 1 if st == "R" else 0)
		psw15 = self.rr.GetOutput("PBSw15a.hand").GetStatus() + self.rr.GetOutput("PBSw15b.hand").GetStatus()
		outb[3] = setBit(outb[3], 6, 0 if psw15 != 0 else 1)  # hand switch unlocks
		outb[3] = setBit(outb[3], 7, 0 if psw15 == 0 else 1)

		outb[5] = setBit(outb[5], 0, self.rr.GetInput("P30").GetValue())
		outb[5] = setBit(outb[5], 1, self.rr.GetInput("P42").GetValue())
		inp = self.rr.GetInput("P32")
		clr32w = inp.GetClear() and not inp.GetEast()
		outb[5] = setBit(outb[5], 2, 1 if clr32w else 0)  # Shore signal
		inp = self.rr.GetInput("P42")
		clr42e = inp.GetClear() and inp.GetEast()
		outb[5] = setBit(outb[5], 3, 1 if clr42e else 0)  # Hyde Jct signal
		outb[5] = setBit(outb[5], 4, self.rr.GetInput("CBSouthJct").GetInvertedValue())  # Circuit breakers
		outb[5] = setBit(outb[5], 5, self.rr.GetInput("CBCircusJct").GetInvertedValue())
		outb[5] = setBit(outb[5], 6, 1 if self.rr.GetSwitchLock("PBSw1") else 0)  # Switch Locks
		outb[5] = setBit(outb[5], 7, 1 if self.rr.GetSwitchLock("PBSw3") else 0)

		outb[6] = setBit(outb[6], 0, 1 if self.rr.GetSwitchLock("PBSw5") else 0)
		outb[6] = setBit(outb[6], 1, 1 if self.rr.GetSwitchLock("PBSw11") else 0)
		outb[6] = setBit(outb[6], 2, 1 if self.rr.GetSwitchLock("PBSw13") else 0)
		outb[6] = setBit(outb[6], 3, 1 if self.rr.GetSwitchLock("PBSw15") else 0)
		outb[6] = setBit(outb[6], 4, self.rr.GetOutput("P32.srel").GetStatus())	      # Stop relays
		outb[6] = setBit(outb[6], 5, self.rr.GetOutput("P41.srel").GetStatus())
		outb[6] = setBit(outb[6], 6, 1 if PBXO else 0)  # Crossing signal

		otext = formatOText(outb, outbc)
		#logging.debug("Port  B: Output bytes: %s" % otext)
	
		inbc = outbc		
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(PORTB, outb, outbc)

			itext = formatIText(inb, inbc)
			#logging.debug("Port B: Input Bytes: %s" % itext)

			nb = getBit(inb[0], 0)  # Switch Positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("PBSw1").SetTOState(nb, rb)
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			self.rr.GetInput("PBSw3").SetTOState(nb, rb)
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			self.rr.GetInput("PBSw11").SetTOState(nb, rb)
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			self.rr.GetInput("PBSw13").SetTOState(nb, rb)

			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			self.rr.GetInput("PBSw5").SetTOState(nb, rb)
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			self.rr.GetInput("PBSw15a").SetTOState(nb, rb)
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			self.rr.GetInput("PBSw15b").SetTOState(nb, rb)
			ip = self.rr.GetInput("P40")    # South Jct Detection
			ip.SetValue(getBit(inb[1], 6))
			ip = self.rr.GetInput("P40.E")
			ip.SetValue(getBit(inb[1], 7))

			ip = self.rr.GetInput("POSSJ2")  # PBOS1
			ip.SetValue(getBit(inb[2], 0))
			ip = self.rr.GetInput("POSSJ1")  # PBOS2
			ip.SetValue(getBit(inb[2], 1))
			ip = self.rr.GetInput("P31.W")
			ip.SetValue(getBit(inb[2], 2))
			ip = self.rr.GetInput("P31")
			ip.SetValue(getBit(inb[2], 3))
			ip = self.rr.GetInput("P31.E")
			ip.SetValue(getBit(inb[2], 4))
			ip = self.rr.GetInput("P32.W")  # Circus Jct Detection
			ip.SetValue(getBit(inb[2], 5))
			ip = self.rr.GetInput("P32")
			ip.SetValue(getBit(inb[2], 6))
			ip = self.rr.GetInput("P32.E")
			ip.SetValue(getBit(inb[2], 7))

			ip = self.rr.GetInput("POSCJ2")  # PBOS3
			ip.SetValue(getBit(inb[3], 0))
			ip = self.rr.GetInput("POSCJ1")  # PBOS4
			ip.SetValue(getBit(inb[3], 1))
			ip = self.rr.GetInput("P41.W")
			ip.SetValue(getBit(inb[3], 2))
			ip = self.rr.GetInput("P41")
			ip.SetValue(getBit(inb[3], 3))
			ip = self.rr.GetInput("P41.E")
			ip.SetValue(getBit(inb[3], 4))
			lvrL = getBit(inb[3], 5)       # signal levers
			lvrCallOn = getBit(inb[3], 6)
			lvrR = getBit(inb[3], 7)
			self.rr.GetInput("PB2.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

			lvrL = getBit(inb[4], 0)
			lvrCallOn = getBit(inb[4], 1)
			lvrR = getBit(inb[4], 2)
			self.rr.GetInput("PB4.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			self.rr.GetInput("PBSw5.lvr").SetState(getBit(inb[4], 3))  # handswitch unlocking
			lvrL = getBit(inb[4], 4)
			lvrCallOn = getBit(inb[4], 5)
			lvrR = getBit(inb[4], 6)
			self.rr.GetInput("PB12.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			lvrL = getBit(inb[4], 7)

			lvrCallOn = getBit(inb[5], 0)
			lvrR = getBit(inb[5], 1)
			self.rr.GetInput("PB14.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
			st = getBit(inb[5], 2)
			self.rr.GetInput("PBSw15a.lvr").SetState(st)
			self.rr.GetInput("PBSw15b.lvr").SetState(st)
			release = getBit(inb[5], 3)
			self.rr.GetInput("pbrelease").SetState(release)  # Port B Release switch
				
		if self.sendIO:
			self.rr.ShowText("PrtB", PORTB, otext, itext, 2, 3)


