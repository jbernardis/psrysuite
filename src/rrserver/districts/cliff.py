import logging

from district import District, leverState, formatIText, formatOText, GREENMTN, CLIFF, SHEFFIELD
from rrobjects import SignalOutput, NXButtonOutput, HandSwitchOutput, BlockInput, TurnoutInput, RouteInput, \
	FleetLeverInput, SignalLeverInput, HandswitchLeverInput, ToggleInput
from bus import setBit, getBit


class Cliff(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames =  [
			"C2RA", "C2RB", "C2RC", "C2RD", "C2L",
			"C4R", "C4LA", "C4LB", "C4LC", "C4LD",
			"C6RA", "C6RB", "C6RC", "C6RD", "C6RE", "C6RF", "C6RG", "C6RH", "C6GJ", "C6RK", "C6RL", "C6L",
			"C8R", "C8LA", "C8LB", "C8LC", "C8LD", "C8LE", "C8LF", "C8LG", "C8LH", "C8LJ", "C8LK", "C8LL",
		]
		toNames = [ "CSw31", "CSw33", "CSw35", "CSw37", "CSw39",
					"CSw41", "CSw43", "CSw45", "CSw47", "CSw49",
					"CSw51", "CSw53", "CSw55", "CSw57", "CSw59",
					"CSw61", "CSw63", "CSw65", "CSw67", "CSw69",
					"CSw71", "CSw73", "CSw75", "CSw77", "CSw79",
					"CSw81"]
		hsNames = [ "CSw3" ]
		handswitchNames = [ "CSw3.hand" ]

		self.routeMap = {
			"CG21W":  [ ["CSw41", "R"] ],
			"CC10W":  [ ["CSw41", "N"], ["CSw39", "N"] ],
			"CC30W":  [ ["CSw41", "N"], ["CSw39", "R"], ["CSw37", "R"] ],
			"CC31W":  [ ["CSw41", "N"], ["CSw39", "R"], ["CSw37", "N"] ],

			"CG12E":  [ ["CSw31", "R"], ["CSw35", "N"] ],
			"CG10E":  [ ["CSw31", "R"], ["CSw35", "R"] ],
			"CC10E":  [ ["CSw31", "N"], ["CSw33", "N"] ],
			"CC30E":  [ ["CSw31", "N"], ["CSw33", "R"] ],

			"CC44E":  [ ["CSw43", "N"], ["CSw49", "N"] ],
			"CC43E":  [ ["CSw43", "N"], ["CSw49", "R"] ],
			"CC42E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw51", "N"] ],
			"CC41E":  [ ["CSw43", "R"], ["CSw45", "R"], ["CSw51", "R"] ],
			"CC40E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "R"] ],
			"CC21E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "R"] ],
			"CC50E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "N"], ["CSw65", "R"] ],
			"CC51E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "R"], ["CSw69", "N"] ],
			"CC52E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "R"], ["CSw69", "R"] ],
			"CC53E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "N"], ["CSw71", "R"] ],
			"CC54E":  [ ["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw63", "N"], ["CSw65", "N"], ["CSw67", "N"], ["CSw71", "N"] ],

			"CC44W":  [ ["CSw57", "N"], ["CSw59", "N"], ["CSw61", "R"] ],
			"CC43W":  [ ["CSw57", "R"], ["CSw59", "N"], ["CSw61", "R"] ],
			"CC42W":  [ ["CSw53", "R"], ["CSw59", "R"], ["CSw61", "R"] ],
			"CC41W":  [ ["CSw53", "N"], ["CSw59", "R"], ["CSw61", "R"] ],
			"CC40W":  [ ["CSw55", "R"], ["CSw61", "N"] ],
			"CC21W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "N"] ],
			"CC50W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "R"], ["CSw75", "R"] ],

			"CC51W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"], ["CSw79", "N"] ],
			"CC52W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"], ["CSw79", "R"] ],
			"CC53W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"], ["CSw81", "R"] ],
			"CC54W":  [ ["CSw55", "N"], ["CSw61", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"], ["CSw81", "N"] ],
		}
		ix = 0
		nxButtons = [
			"CG21W", "CC10W", "CC30W", "CC31W",
			"CG12E", "CG10E", "CC10E", "CC30E",
			"CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E",
			"CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W",
		]
		signalLeverNames = [ "C2.lvr", "C4.lvr", "C6.lvr", "C8.lvr"]
		fleetlLeverNames = [ "cliff.fleet" ]
		hsLeverNames = [ "CSw3.lvr", "CSw11.lvr", "CSw15.lvr", "CSw19.lvr", "CSw21.lvr", "CSw21a.lvr", "CSw21b.lvr"]
		toggleNames = [ "crelease" ]

		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(nxButtons, NXButtonOutput, District.nxbutton, ix)
		ix = self.AddOutputs(handswitchNames, HandSwitchOutput, District.handswitch, ix)

		for n in nxButtons:
			self.SetNXButtonPulseLen(n, settings.nxbpulselen)

		blockNames = [ "G21", "C10", "C30", "C31", "COSGMW", "G10", "G12", "C20", "COSGME",
					"C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54", "COSSHE", "COSSHW"]

		ix = 0
		# each NX button corresponds to a route
		ix = self.AddInputs(nxButtons, RouteInput, District.route, ix)
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames+hsNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(fleetlLeverNames, FleetLeverInput, District.flever, ix)
		ix = self.AddInputs(hsLeverNames, HandswitchLeverInput, District.hslever, ix)
		ix = self.AddInputs(toggleNames, ToggleInput, District.toggle, ix)

	def EvaluateNXButton(self, btn):
		if btn not in self.routeMap:
			return

		tolist = self.routeMap[btn]

		for toName, status in tolist:
			self.rr.GetInput(toName).SetState(status)

	def DetermineSignalLevers(self):
		self.sigLever["C2"] = self.DetermineSignalLever(["C2L"], ["C2RA", "C2RB", "C2RC", "C2RD"])  # signal indicators
		self.sigLever["C4"] = self.DetermineSignalLever(["C4LA", "C4LB", "C4LC", "C4LD"], ["C4R"])
		self.sigLever["C6"] = self.DetermineSignalLever(["C6L"], ["C6RA", "C6RB", "C6RC", "C6RD", "C6RE", "C6RF", "C6RG", "C6RH", "C6GJ", "C6RK", "C6RL"])
		self.sigLever["C8"] = self.DetermineSignalLever(["C8LA", "C8LB", "C8LC", "C8LD", "C8LE", "C8LF", "C8LG", "C8LH", "C8LJ", "C8LK", "C8LL"], ["C8R"])
		self.sigLever["C10"] = self.DetermineSignalLever(["C10L"], ["C10R"])
		self.sigLever["C12"] = self.DetermineSignalLever(["C12L"], ["C12R"])
		self.sigLever["C14"] = self.DetermineSignalLever(["C14LA", "C14LB"], ["C14R"])
		self.sigLever["C18"] = self.DetermineSignalLever(["C18L"], ["C18RA", "C18RB"])
		self.sigLever["C22"] = self.DetermineSignalLever(["C22L"], ["C22R"])
		self.sigLever["C24"] = self.DetermineSignalLever(["C24L"], ["C24R"])

	def OutIn(self):
		optControl = self.rr.GetControlOption("cliff")  # 0 => Cliff, 1 => Dispatcher bank/cliveden, 2 => Dispatcher All
		optBank = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
		optCliveden = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
		optFleet = optBank or optCliveden
		# Green Mountain
		outb = [0 for _ in range(3)]
		asp = self.rr.GetOutput("C2RB").GetAspect()
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3, 5, 7] else 0)  # east end signals
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 2, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C2RD").GetAspect()
		outb[0] = setBit(outb[0], 3, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("C2L").GetAspect()
		outb[0] = setBit(outb[0], 4, 1 if asp in [1, 3, 5, 7] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[0] = setBit(outb[0], 6, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C2RA").GetAspect()
		outb[0] = setBit(outb[0], 7, 1 if asp in [1, 3] else 0)

		outb[1] = setBit(outb[1], 0, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("C2RC").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("C4LA").GetAspect()
		outb[1] = setBit(outb[1], 2, 1 if asp in [1, 3] else 0)	  # west end signals
		outb[1] = setBit(outb[1], 3, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("C4LB").GetAspect()
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("C4LC").GetAspect()
		outb[1] = setBit(outb[1], 6, 1 if asp in [1, 3, 5, 7] else 0)
		outb[1] = setBit(outb[1], 7, 1 if asp in [2, 3, 6, 7] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("C4LD").GetAspect()
		outb[2] = setBit(outb[2], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("C4R").GetAspect()
		outb[2] = setBit(outb[2], 2, 1 if asp in [1, 3, 5, 7] else 0)
		outb[2] = setBit(outb[2], 3, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 4, 1 if asp in [4, 5, 6, 7] else 0)
		outb[2] = setBit(outb[2], 5, 0 if self.rr.GetOutput("CSw3.hand").GetStatus() != 0 else 1)  # hand switch 3

		otext = formatOText(outb, 3)
		logging.debug("Green Mountain: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(GREENMTN, outb, 3, swap=False)

		if inbc != 3:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Green Mountain: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 3)

			self.rr.GetInput("CC30E").SetValue(getBit(inb[0], 0))   # Routes
			self.rr.GetInput("CC10E").SetValue(getBit(inb[0], 1))
			self.rr.GetInput("CG10E").SetValue(getBit(inb[0], 2))
			self.rr.GetInput("CG12E").SetValue(getBit(inb[0], 3))
			self.rr.GetInput("CC31W").SetValue(getBit(inb[0], 4))
			self.rr.GetInput("CC30W").SetValue(getBit(inb[0], 5))
			self.rr.GetInput("CC10W").SetValue(getBit(inb[0], 6))
			self.rr.GetInput("CG21W").SetValue(getBit(inb[0], 7))

			nb = getBit(inb[1], 0)  # Switch positions
			rb = getBit(inb[1], 1)
			self.rr.GetInput("CSw3").SetState(nb, rb)
			self.rr.GetInput("C11").SetValue(getBit(inb[1], 2))  # Detection
			self.rr.GetInput("COSGMW").SetValue(getBit(inb[1], 3))  # COS1
			self.rr.GetInput("C10").SetValue(getBit(inb[1], 4))
			self.rr.GetInput("C30").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("C31").SetValue(getBit(inb[1], 6))
			self.rr.GetInput("COSGME").SetValue(getBit(inb[1], 7))  # COS2

			self.rr.GetInput("C20").SetValue(getBit(inb[2], 0))

		# Cliff
		outb = [0 for _ in range(8)]
		sigl = self.sigLever["C2"]  # signal indicators
		outb[0] = setBit(outb[0], 0, 1 if sigl == "L" else 0)
		outb[0] = setBit(outb[0], 1, 1 if sigl == "N" else 0)
		outb[0] = setBit(outb[0], 2, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C4"]
		outb[0] = setBit(outb[0], 3, 1 if sigl == "L" else 0)
		outb[0] = setBit(outb[0], 4, 1 if sigl == "N" else 0)
		outb[0] = setBit(outb[0], 5, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C6"]
		outb[0] = setBit(outb[0], 6, 1 if sigl == "L" else 0)
		outb[0] = setBit(outb[0], 7, 1 if sigl == "N" else 0)

		outb[1] = setBit(outb[1], 0, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C8"]
		outb[1] = setBit(outb[1], 1, 1 if sigl == "L" else 0)
		outb[1] = setBit(outb[1], 2, 1 if sigl == "N" else 0)
		outb[1] = setBit(outb[1], 3, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C10"]
		outb[1] = setBit(outb[1], 4, 1 if sigl == "L" else 0)
		outb[1] = setBit(outb[1], 5, 1 if sigl == "N" else 0)
		outb[1] = setBit(outb[1], 6, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C12"]
		outb[1] = setBit(outb[1], 7, 1 if sigl == "L" else 0)

		outb[2] = setBit(outb[2], 0, 1 if sigl == "N" else 0)
		outb[2] = setBit(outb[2], 1, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C14"]
		outb[2] = setBit(outb[2], 2, 1 if sigl == "L" else 0)
		outb[2] = setBit(outb[2], 3, 1 if sigl == "N" else 0)
		outb[2] = setBit(outb[2], 4, 1 if sigl == "R" else 0)
		outb[2] = setBit(outb[2], 5, optFleet)                    # fleet indicator
		outb[2] = setBit(outb[2], 6, 1-optFleet)
		sigl = self.sigLever["C18"]
		outb[2] = setBit(outb[2], 7, 1 if sigl == "L" else 0)

		outb[3] = setBit(outb[3], 0, 1 if sigl == "N" else 0)
		outb[3] = setBit(outb[3], 1, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C22"]
		outb[3] = setBit(outb[3], 2, 1 if sigl == "L" else 0)
		outb[3] = setBit(outb[3], 3, 1 if sigl == "N" else 0)
		outb[3] = setBit(outb[3], 4, 1 if sigl == "R" else 0)
		sigl = self.sigLever["C24"]
		outb[3] = setBit(outb[3], 5, 1 if sigl == "L" else 0)
		outb[3] = setBit(outb[3], 6, 1 if sigl == "N" else 0)
		outb[3] = setBit(outb[3], 7, 1 if sigl == "R" else 0)

		locked = self.rr.GetOutput("CSw3.hand").GetStatus() != 0  # Hand switch unlock indicators
		outb[4] = setBit(outb[4], 0, 0 if locked else 1)
		outb[4] = setBit(outb[4], 1, 1 if locked else 0)
		locked = self.rr.GetOutput("CSw11.hand").GetStatus() != 0
		outb[4] = setBit(outb[4], 2, 0 if locked else 1)
		outb[4] = setBit(outb[4], 3, 1 if locked else 0)
		locked = self.rr.GetOutput("CSw15.hand").GetStatus() != 0
		outb[4] = setBit(outb[4], 4, 0 if locked else 1)
		outb[4] = setBit(outb[4], 5, 1 if locked else 0)
		locked = self.rr.GetOutput("CSw19.hand").GetStatus() != 0
		outb[4] = setBit(outb[4], 6, 0 if locked else 1)
		outb[4] = setBit(outb[4], 7, 1 if locked else 0)

		lockeda = self.rr.GetOutput("CSw21a.hand").GetStatus() != 0
		lockedb = self.rr.GetOutput("CSw21b.hand").GetStatus() != 0
		locked = lockeda or lockedb
		outb[5] = setBit(outb[5], 0, 0 if locked else 1)
		outb[5] = setBit(outb[5], 1, 1 if locked else 0)
		outb[5] = setBit(outb[5], 2, self.rr.GetInput("B10").GetValue())    # block indicators
		CBGM = self.rr.GetInput("CBGreenMtnStn").GetValue() + self.rr.GetInput("CBGreenMtnYd").GetValue()  # Circuit Breakers
		outb[5] = setBit(outb[5], 3, 1 if CBGM != 0 else 0)
		CBSheffield = self.rr.GetInput("CBSheffieldA").GetValue() + self.rr.GetInput("CBSheffieldB").GetValue()  # Circuit Breakers
		outb[5] = setBit(outb[5], 4, 1 if CBSheffield != 0 else 0)
		outb[5] = setBit(outb[5], 5, self.rr.GetInput("CBCliveden").GetValue())
		outb[5] = setBit(outb[5], 6, self.rr.GetInput("CBReverserC22C23").GetValue())
		outb[5] = setBit(outb[5], 6, self.rr.GetInput("CBBank").GetValue())

		outb[6] = setBit(outb[6], 0, 1 if self.rr.GetSwitchLock("CSw31") else 0)
		outb[6] = setBit(outb[6], 1, 1 if self.rr.GetSwitchLock("CSw41") else 0)
		outb[6] = setBit(outb[6], 2, 1 if self.rr.GetSwitchLock("CSw43") else 0)
		outb[6] = setBit(outb[6], 3, 1 if self.rr.GetSwitchLock("CSw61") else 0)
		outb[6] = setBit(outb[6], 4, 1 if self.rr.GetSwitchLock("CSw9") else 0)
		outb[6] = setBit(outb[6], 5, 1 if self.rr.GetSwitchLock("CSw13") else 0)
		outb[6] = setBit(outb[6], 6, 1 if self.rr.GetSwitchLock("CSw17") else 0)
		outb[6] = setBit(outb[6], 7, 1 if self.rr.GetSwitchLock("CSw23") else 0)

		outb[7] - setBit(outb[7], 0, 1 if self.rr.GetInput("CSw21a").GetValue() == "R" else 0)  # remote hand switch indications
		outb[7] - setBit(outb[7], 1, 1 if self.rr.GetInput("CSw21b").GetValue() == "R" else 0)
		outb[7] - setBit(outb[7], 2, 1 if self.rr.GetInput("CSw19").GetValue() == "R" else 0)
		outb[7] - setBit(outb[7], 3, 1 if self.rr.GetInput("CSw15").GetValue() == "R" else 0)
		outb[7] - setBit(outb[7], 4, 1 if self.rr.GetInput("CSw11").GetValue() == "R" else 0)

		otext = formatOText(outb, 8)
		logging.debug("Cliff: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(CLIFF, outb, 8, swap=False)

		if inbc != 8:
			if self.sendIO:
				self.rr.ShowText(otext, "", 1, 3)
		else:
			itext = formatIText(inb, 7)
			logging.debug("Cliff: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 1, 3)

			self.rr.GetInput("CC21W").SetValue(getBit(inb[0], 0))  # Routes
			self.rr.GetInput("CC40W").SetValue(getBit(inb[0], 1))
			self.rr.GetInput("CC44W").SetValue(getBit(inb[0], 2))
			self.rr.GetInput("CC43W").SetValue(getBit(inb[0], 3))
			self.rr.GetInput("CC42W").SetValue(getBit(inb[0], 4))
			self.rr.GetInput("CC41W").SetValue(getBit(inb[0], 5))
			self.rr.GetInput("CC41E").SetValue(getBit(inb[0], 6))
			self.rr.GetInput("CC42E").SetValue(getBit(inb[0], 7))

			self.rr.GetInput("CC21E").SetValue(getBit(inb[1], 0))
			self.rr.GetInput("CC40E").SetValue(getBit(inb[1], 1))
			self.rr.GetInput("CC44E").SetValue(getBit(inb[1], 2))
			self.rr.GetInput("CC43E").SetValue(getBit(inb[1], 3))
			self.rr.GetInput("COSSHE").SetValue(getBit(inb[1], 4))  # Detection (COS3)
			self.rr.GetInput("C21").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("C41").SetValue(getBit(inb[1], 6))
			self.rr.GetInput("C41").SetValue(getBit(inb[1], 7))

			self.rr.GetInput("C42").SetValue(getBit(inb[2], 0))
			self.rr.GetInput("C43").SetValue(getBit(inb[2], 1))
			self.rr.GetInput("C44").SetValue(getBit(inb[2], 2))
			self.rr.GetInput("COSSHW").SetValue(getBit(inb[2], 3))  # COS4
			if optControl != 2:  # NOT Dispatcher: ALL
				lvrL = getBit(inb[2], 4)       # signal levers
				lvrCallOn = getBit(inb[2], 5)
				lvrR = getBit(inb[2], 6)
				self.rr.GetInput("C2.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[2], 7)

				lvrCallOn = getBit(inb[3], 0)
				lvrR = getBit(inb[3], 1)
				self.rr.GetInput("C4.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[3], 2)
				lvrCallOn = getBit(inb[3], 3)
				lvrR = getBit(inb[3], 4)
				self.rr.GetInput("C6.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[3], 5)
				lvrCallOn = getBit(inb[3], 6)
				lvrR = getBit(inb[3], 7)
				self.rr.GetInput("C8.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

			if optControl == 0:  # Cliff local control
				lvrL = getBit(inb[4], 0)
				lvrCallOn = getBit(inb[4], 1)
				lvrR = getBit(inb[4], 2)
				self.rr.GetInput("C10.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[4], 3)
				lvrCallOn = getBit(inb[4], 4)
				lvrR = getBit(inb[4], 5)
				self.rr.GetInput("C12.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[4], 6)
				lvrCallOn = getBit(inb[4], 7)

				lvrR = getBit(inb[5], 0)
				self.rr.GetInput("C14.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				fleet = getBit(inb[5], 1)
				self.rr.GetInput("cliff.fleet").SetState(fleet)  # fleet
				lvrL = getBit(inb[5], 2)
				lvrCallOn = getBit(inb[5], 3)
				lvrR = getBit(inb[5], 4)
				self.rr.GetInput("C18.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[5], 5)
				lvrCallOn = getBit(inb[5], 6)
				lvrR = getBit(inb[5], 7)
				self.rr.GetInput("C22.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

				lvrL = getBit(inb[6], 0)
				lvrCallOn = getBit(inb[6], 1)
				lvrR = getBit(inb[6], 2)
				self.rr.GetInput("C24.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				release = getBit(inb[6], 3)
				self.rr.GetInput("crelease").SetState(release)  # C Release switch
				self.rr.GetInput("CSw3.lvr").SetState(getBit(inb[6], 4))  # handswitch unlocking
				self.rr.GetInput("CSw11.lvr").SetState(getBit(inb[6], 5))
				self.rr.GetInput("CSw15.lvr").SetState(getBit(inb[6], 6))
				self.rr.GetInput("CSw19.lvr").SetState(getBit(inb[6], 7))

				st = getBit(inb[6], 7)
				self.rr.GetInput("CSw21a.lvr").SetState(st)
				self.rr.GetInput("CSw21b.lvr").SetState(st)

		# Sheffield
		outb = [0 for _ in range(4)]
		op = self.rr.GetOutput("CC54E").GetOutPulse()  # Switch button outputs - Sheffield
		outb[0] = setBit(outb[0], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC53E").GetOutPulse()
		outb[0] = setBit(outb[0], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC52E").GetOutPulse()
		outb[0] = setBit(outb[0], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC51E").GetOutPulse()
		outb[0] = setBit(outb[0], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC50E").GetOutPulse()
		outb[0] = setBit(outb[0], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC21E").GetOutPulse()
		outb[0] = setBit(outb[0], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC40E").GetOutPulse()
		outb[0] = setBit(outb[0], 6, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC41E").GetOutPulse()
		outb[0] = setBit(outb[0], 7, 1 if op != 0 else 0)

		op = self.rr.GetOutput("CC42E").GetOutPulse()
		outb[1] = setBit(outb[1], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC43E").GetOutPulse()
		outb[1] = setBit(outb[1], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC44E").GetOutPulse()
		outb[1] = setBit(outb[1], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC54W").GetOutPulse()
		outb[1] = setBit(outb[1], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC53W").GetOutPulse()
		outb[1] = setBit(outb[1], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC52W").GetOutPulse()
		outb[1] = setBit(outb[1], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC51W").GetOutPulse()
		outb[1] = setBit(outb[1], 6, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC50W").GetOutPulse()
		outb[1] = setBit(outb[1], 7, 1 if op != 0 else 0)

		op = self.rr.GetOutput("CC21W").GetOutPulse()
		outb[2] = setBit(outb[2], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC40W").GetOutPulse()
		outb[2] = setBit(outb[2], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC41W").GetOutPulse()
		outb[2] = setBit(outb[2], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC42W").GetOutPulse()
		outb[2] = setBit(outb[2], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC43W").GetOutPulse()
		outb[2] = setBit(outb[2], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC44W").GetOutPulse()
		outb[2] = setBit(outb[2], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC30E").GetOutPulse()  # Switch buttons - green mountain
		outb[2] = setBit(outb[2], 6, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC10E").GetOutPulse()
		outb[2] = setBit(outb[2], 7, 1 if op != 0 else 0)

		op = self.rr.GetOutput("CG10E").GetOutPulse()
		outb[3] = setBit(outb[3], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CG12E").GetOutPulse()
		outb[3] = setBit(outb[3], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC30W").GetOutPulse()
		outb[3] = setBit(outb[3], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC31W").GetOutPulse()
		outb[3] = setBit(outb[3], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CC10W").GetOutPulse()
		outb[3] = setBit(outb[3], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("CG21W").GetOutPulse()
		outb[3] = setBit(outb[3], 5, 1 if op != 0 else 0)

		otext = formatOText(outb, 4)
		logging.debug("Sheffield: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(SHEFFIELD, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 2, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Sheffield: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 2, 3)

			self.rr.GetInput("CC50W").SetValue(getBit(inb[0], 0))  # Routes
			self.rr.GetInput("CC51W").SetValue(getBit(inb[0], 1))
			self.rr.GetInput("CC52W").SetValue(getBit(inb[0], 2))
			self.rr.GetInput("CC53W").SetValue(getBit(inb[0], 3))
			self.rr.GetInput("CC54W").SetValue(getBit(inb[0], 4))
			self.rr.GetInput("CC50E").SetValue(getBit(inb[0], 5))
			self.rr.GetInput("CC51E").SetValue(getBit(inb[0], 6))
			self.rr.GetInput("CC52E").SetValue(getBit(inb[0], 7))

			self.rr.GetInput("CC53E").SetValue(getBit(inb[1], 0))
			self.rr.GetInput("CC54E").SetValue(getBit(inb[1], 1))
			self.rr.GetInput("C50").SetValue(getBit(inb[1], 2))  # Detection
			self.rr.GetInput("C51").SetValue(getBit(inb[1], 3))
			self.rr.GetInput("C52").SetValue(getBit(inb[1], 4))
			self.rr.GetInput("C53").SetValue(getBit(inb[1], 5))
			self.rr.GetInput("C54").SetValue(getBit(inb[1], 6))

