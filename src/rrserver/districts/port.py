import logging

from district import District, leverState, PORTA, PORTB, PARSONS, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, HandSwitchOutput, RelayOutput, ToggleInput, SignalLeverInput, BlockInput, TurnoutInput, HandswitchLeverInput
from bus import setBit, getBit


class Port(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)
		self.PBE = False
		self.PBW = False

		sigNames = [ "PA12R", "PA12LA", "PA12LB", "PA12LC", "PA10RA", "PA10RB", "PA10L",
					"PA8R", "PA8L", "PA6R", "PA6LA", "PA6LB", "PA6LC", "PA4RA", "PA4RB", "PA4L",
					"PA34RA", "PA34RB", "PA34RC", "PA34RD", "PA34LA", "PA34LB", "PA32RA", "PA32RB", "PA32L",
					"PB2R", "PB2L", "PB4R", "PB4L", "PB12R", "PB12L", "PB14R", "PB14L" ]
		toNames = [ "PBSw1", "PBSw3", "PBSw11", "PBSw13",
					"PASw1", "PASw3", "PASw5", "PASw7", "PASw9", "PASw11", "PASw13",
					"PASw15", "PASw17", "PASw19", "PASw21", "PASw23",
					"PASw27", "PASw29", "PASw31", "PASw33", "PASw35", "PASw37"]
		hsNames = [ "PBSw5", "PBSw15a", "PBSw15b" ]
		handswitchNames = [ "PBSw5.hand", "PBSw15a.hand", "PBSw15b.hand" ]
		relayNames = [ "P10.srel", "P11.srel", "P20.srel", "P21.srel",
					"P30.srel", "P31.srel", "P32.srel", "P40.srel", "P41.srel", "P42.srel" ]

		ix = 0
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen)

		blockNames = [ "P1", "P2", "P3", "P4", "P5", "P6", "P7",
						"P10", "P10.E", "P11.W", "P11", "P11.E", "P20", "P20.E", "P21", "P21.E",
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
		outb = [0 for _ in range(9)]
		asp = self.rr.GetOutput("PA12R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3] else 0)  # signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA10RA").GetAspect()
		outb[0] = setBit(outb[0], 2, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 3, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA12LA").GetAspect()
		outb[0] = setBit(outb[0], 4, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA10RB").GetAspect()
		outb[0] = setBit(outb[0], 5, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 6, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA8R").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA12LB").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA6R").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA4RA").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA12LC").GetAspect()
		outb[1] = setBit(outb[1], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA4RB").GetAspect()
		outb[1] = setBit(outb[1], 7, 1 if asp in [1, 3] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("PA8L").GetAspect()
		outb[2] = setBit(outb[2], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA6LA").GetAspect()
		outb[2] = setBit(outb[2], 2, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA6LB").GetAspect()
		outb[2] = setBit(outb[2], 3, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA6LC").GetAspect()
		outb[2] = setBit(outb[2], 4, 1 if asp != 0 else 0)
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
		outb[6] = setBit(outb[6], 1, self.rr.GetInput("CBParsonsJct").GetValue())  # Circuit breakers
		outb[6] = setBit(outb[6], 2, self.rr.GetInput("CBSouthport").GetValue())
		outb[6] = setBit(outb[6], 3, self.rr.GetInput("CBLavinYard").GetValue())
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

		otext = formatOText(outb, 9)
		logging.debug("Port A: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(PORTA, outb, 9, swap=False)

		if inbc != 9:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Port A: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 3)

			ip = self.rr.GetInput("PASw1")  # Switch positions
			nb = getBit(inb[0], 0)
			rb = getBit(inb[0], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw3")
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw5")
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw7")
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			ip.SetState(nb, rb)

			ip = self.rr.GetInput("PASw9")
			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw11")
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw13")
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw15")
			nb = getBit(inb[1], 6)
			rb = getBit(inb[1], 7)
			ip.SetState(nb, rb)

			ip = self.rr.GetInput("PASw17")
			nb = getBit(inb[2], 0)
			rb = getBit(inb[2], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw19")
			nb = getBit(inb[2], 2)
			rb = getBit(inb[2], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw21")
			nb = getBit(inb[2], 4)
			rb = getBit(inb[2], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw23")
			nb = getBit(inb[2], 6)
			rb = getBit(inb[2], 7)
			ip.SetState(nb, rb)

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

		# Parsons Junction
		outb = [0 for _ in range(4)]
		asp = self.rr.GetOutput("PA34LB").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # westward signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PA32L").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("PA34LA").GetAspect()
		outb[0] = setBit(outb[0], 4, 1 if asp in [1, 3, 5, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 6, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PA34RD").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3, 5, 7] else 0)  # eastward signals

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PA34RC").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp != 0 else 0)  # eastward signals
		asp = self.rr.GetOutput("PA32RA").GetAspect()
		outb[1] = setBit(outb[1], 3, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PA34RB").GetAspect()
		outb[1] = setBit(outb[1], 6, 1 if asp != 0 else 0)  # eastward signals
		asp = self.rr.GetOutput("PA32RB").GetAspect()
		outb[1] = setBit(outb[1], 7, 1 if asp in [1, 3, 5, 7] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PA34RA").GetAspect()
		outb[2] = setBit(outb[2], 2, 1 if asp != 0 else 0)  # eastward signals
		outb[2] = setBit(outb[2], 3, self.rr.GetOutput("P20.srel").GetStatus())	      # Stop relays
		outb[2] = setBit(outb[2], 4, self.rr.GetOutput("P30.srel").GetStatus())
		outb[2] = setBit(outb[2], 5, self.rr.GetOutput("P50.srel").GetStatus())
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("P11.srel").GetStatus())

		otext = formatOText(outb, 4)
		logging.debug("Parsons: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(PARSONS, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 1, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Parsons: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 1, 3)

			ip = self.rr.GetInput("PASw27")  # Switch positions
			nb = getBit(inb[0], 0)
			rb = getBit(inb[0], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw29")
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw31")
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw33")
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			ip.SetState(nb, rb)

			ip = self.rr.GetInput("PASw35")
			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("PASw37")
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			ip.SetState(nb, rb)
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

		#  Port B
		outb = [0 for _ in range(7)]
		asp = self.rr.GetOutput("PB2R").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # South Jct Eastward signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB4R").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp in [1, 3, 5, 7] else 0)
		outb[0] = setBit(outb[0], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB2L").GetAspect()
		outb[0] = setBit(outb[0], 6, 1 if asp in [1, 3, 5, 7] else 0)  # South Jct Westward signals
		outb[0] = setBit(outb[0], 7, 1 if asp in [2, 3, 6, 7] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB4L").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB12L").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3, 5, 7] else 0)  # Circus Jct Eastward signals
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 6, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB14L").GetAspect()
		outb[1] = setBit(outb[1], 7, 1 if asp in [1, 3, 5, 7] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 1, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB12R").GetAspect()
		outb[2] = setBit(outb[2], 2, 1 if asp in [1, 3, 5, 7] else 0)  # Circus Jct Westward signals
		outb[2] = setBit(outb[2], 3, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 4, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("PB14R").GetAspect()
		outb[2] = setBit(outb[2], 5, 1 if asp in [1, 3, 5, 7] else 0)
		outb[2] = setBit(outb[2], 6, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 7, 1 if asp in [4, 5, 6, 7] else 0)

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
		outb[5] = setBit(outb[5], 4, self.rr.GetInput("CBSouthJct").GetValue())  # Circuit breakers
		outb[5] = setBit(outb[5], 5, self.rr.GetInput("CBCircusJct").GetValue())
		outb[5] = setBit(outb[5], 6, 1 if self.rr.GetSwitchLock("PBSw1") else 0)  # Switch Locks
		outb[5] = setBit(outb[5], 7, 1 if self.rr.GetSwitchLock("PBSw3") else 0)

		outb[6] = setBit(outb[6], 0, 1 if self.rr.GetSwitchLock("PBSw5") else 0)
		outb[6] = setBit(outb[6], 1, 1 if self.rr.GetSwitchLock("PBSw11") else 0)
		outb[6] = setBit(outb[6], 2, 1 if self.rr.GetSwitchLock("PBSw13") else 0)
		outb[6] = setBit(outb[6], 3, 1 if self.rr.GetSwitchLock("PBSw15") else 0)
		outb[6] = setBit(outb[6], 4, self.rr.GetOutput("P32.srel").GetStatus())	      # Stop relays
		outb[6] = setBit(outb[6], 5, self.rr.GetOutput("P41.srel").GetStatus())
		outb[6] = setBit(outb[6], 6, 1 if PBXO else 0)  # Crossing signal

		otext = formatOText(outb, 7)
		logging.debug("Port  B: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(PORTB, outb, 7, swap=False)

		if inbc != 7:
			if self.sendIO:
				self.rr.ShowText(otext, "", 2, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Port B: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 2, 3)

			nb = getBit(inb[0], 0)  # Switch Positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("PBSw1").SetState(nb, rb)
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			self.rr.GetInput("PBSw3").SetState(nb, rb)
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			self.rr.GetInput("PBSw11").SetState(nb, rb)
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			self.rr.GetInput("PBSw13").SetState(nb, rb)

			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			self.rr.GetInput("PBSw5").SetState(nb, rb)
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			self.rr.GetInput("PBSw15a").SetState(nb, rb)
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			self.rr.GetInput("PBSw15b").SetState(nb, rb)
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
