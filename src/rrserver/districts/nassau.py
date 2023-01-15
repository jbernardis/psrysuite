import logging

from district import District, leverState,  NASSAUE, NASSAUW, NASSAUNX, formatIText, formatOText
from rrobjects import SignalOutput, TurnoutOutput, NXButtonOutput, RelayOutput, BreakerInput, BlockInput, \
	TurnoutInput, SignalLeverInput, ToggleInput
from bus import setBit, getBit


class Nassau(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames =  [
			"N20R", "N20L",
			"N18R", "N18LA", "N18LB",
			"N16R", "N16L",
			"N14R", "N14LA", "N14LB", "N14LC", "N14LD",
			"N28R", "N28L",
			"N26RA", "N26RB", "N26RC", "N26L",
			"N24RA", "N24RB", "N24RC", "N24RD", "N24L",
			"N11W", "N21W", "B20E"
		]
		toONames = ["NSw13", "NSw15", "NSw17"]
		toNames = [ "NSw19", "NSw21", "NSw23", "NSw25", "NSw27", "NSw29", "NSw31", "NSw33", "NSw35",
					"NSw39", "NSw41", "NSw43", "NSw45", "NSw47", "NSw51", "NSw53", "NSw55", "NSw57"]
		relayNames = [ "N21.srel", "B10.srel" ]

		self.NXMap = {
			"NNXBtnT12": {
				"NNXBtnW10":  [ ["NSw25", "N"] ]
			},

			"NNXBtnN60": {
				"NNXBtnW10":  [ ["NSw21", "N"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"] ],
				"NNXBtnN32W": [ ["NSw21", "N"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"] ],
				"NNXBtnN31W": [ ["NSw21", "N"], ["NSw23", "N"], ["NSw27", "N"] ],
				"NNXBtnN12W": [ ["NSw21", "N"], ["NSw27", "R"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},

			"NNXBtnN11": {
				"NNXBtnW10":  [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN32W": [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN31W": [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN12W": [ ["NSw19", "N"], ["NSw21", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},

			"NNXBtnN21": {
				"NNXBtnW10":  [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN32W": [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN31W": [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN12W": [ ["NSw19", "R"], ["NSw21", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},
						"NNXBtnR10": {
				"NNXBtnW11":  [ ["NSw47", "N"], ["NSw55", "N"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ]
			}, 
			
			"NNXBtnB10": {
				"NNXBtnW11":  [ ["NSw55", "R"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"]],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ]
			}, 
			
			"NNXBtnB20": {
				"NNXBtnW11":  [ ["NSw55", "R"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"]],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"]],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ]
			}

		}
		ix = 0
		nxButtons = [
			"NNXBtnT12", "NNXBtnN60", "NNXBtnN11", "NNXBtnN21",
			"NNXBtnW10", "NNXBtnN32W",	"NNXBtnN31W", "NNXBtnN12W", "NNXBtnN22W", "NNXBtnN41W", "NNXBtnN42W", "NNXBtnW20W",
			"NNXBtnR10", "NNXBtnB10", "NNXBtnB20",
			"NNXBtnW11", "NNXBtnN32E", "NNXBtnN31E", "NNXBtnN12E", "NNXBtnN22E", "NNXBtnN41E", "NNXBtnN42E", "NNXBtnW20E"
		]
		ix = self.AddOutputs(sigNames, SignalOutput, District.signal, ix)
		ix = self.AddOutputs(toONames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(nxButtons, NXButtonOutput, District.nxbutton, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)

		for n in nxButtons:
			self.SetNXButtonPulseLen(n, settings.nxbpulselen)

		brkrNames = [ "CBKrulish", "CBKrulishYd", "CBNassauW", "CBNassauE", "CBSptJct", "CBWilson", "CBThomas", "CBFoss", "CBDell" ]
		blockNames = [ "N21.W", "N21", "N21.E", "NWOSTY", "NWOSCY", "NWOSW", "NWOSE",
						"N31", "N32", "N12", "N22", "N41", "N42",
						"NEOSW", "NEOSE", "NEOSRH", "B10.W", "B10",
						"N60", "T12", "W10", "W11", "W20", "R10.W" ]
		signalLeverNames = [ "N14.lvr", "N16.lvr", "N18.lvr", "N20.lvr", "N24.lvr", "N26.lvr", "N28.lvr" ]
		toggleNames = [ "nrelease" ]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddSubBlocks("R10", ["R10A", "R10B", "R10C"], ix)
		ix = self.AddInputs(toONames+toNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(brkrNames, BreakerInput, District.breaker, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(toggleNames, ToggleInput, District.toggle, ix)

	def EvaluateNXButtons(self, bEntry, bExit):
		try:
			tolist = self.NXMap[bEntry][bExit]
		except KeyError:
			try:
				tolist = self.NXMap[bExit][bEntry]
			except KeyError:
				return

		for toName, status in tolist:
			self.rr.GetInput(toName).SetState(status)

	def DetermineSignalLevers(self):
		self.sigLever["N14"] = self.DetermineSignalLever(["N14LA", "N14LB", "N14LC"], ["N14R"])
		self.sigLever["N16"] = self.DetermineSignalLever(["N16L"], ["N16R"])
		self.sigLever["N18"] = self.DetermineSignalLever(["N18LA", "N18LB"], ["N18R"])
		self.sigLever["N20"] = self.DetermineSignalLever(["N20L"], ["N20R"])
		self.sigLever["N24"] = self.DetermineSignalLever(["N24L"], ["N24RA", "N24RB", "N24RC", "N24RD"])
		self.sigLever["N26"] = self.DetermineSignalLever(["N26L"], ["N26RA", "N26RB", "N26RC"])
		self.sigLever["N28"] = self.DetermineSignalLever(["N28L"], ["N28R"])

	def OutIn(self):
		optControl = self.rr.GetControlOption("nassau")  # 0 => Nassau, 1 => Dispatcher Main, 2 => Dispatcher All
		optFleet = self.rr.GetControlOption("nassau.fleet")  # 0 => no fleeting, 1 => fleeting

		NESL = self.rr.GetDistrictLock("NESL")
		NWSL = self.rr.GetDistrictLock("NWSL")
		# Nassau West
		outb = [0 for _ in range(8)]

		asp = self.rr.GetOutput("N14LC").GetAspect()     # signals
		outb[0] = setBit(outb[0], 0, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N14LB").GetAspect()    
		outb[0] = setBit(outb[0], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N20R").GetAspect()    
		outb[0] = setBit(outb[0], 2, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N20L").GetAspect()    
		outb[0] = setBit(outb[0], 3, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N14LA").GetAspect()    
		outb[0] = setBit(outb[0], 4, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N16L").GetAspect()    
		outb[0] = setBit(outb[0], 6, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 7, 1 if asp in [2, 3] else 0)

		asp = self.rr.GetOutput("N18LB").GetAspect()    
		outb[1] = setBit(outb[1], 0, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 1, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N18LA").GetAspect()    
		outb[1] = setBit(outb[1], 2, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 3, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N16R").GetAspect()    
		outb[1] = setBit(outb[1], 4, 1 if asp in [1, 3] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N14R").GetAspect()    
		outb[1] = setBit(outb[1], 6, 1 if asp in [1, 3] else 0)
		outb[7] = setBit(outb[7], 3, 1 if asp in [2, 3] else 0)  # Transferred to byte 7:3 because of 1:7 being a Bad output?

		asp = self.rr.GetOutput("N18R").GetAspect()    
		outb[2] = setBit(outb[2], 0, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N11W").GetAspect()
		outb[2] = setBit(outb[2], 1, 1 if asp in [1, 3, 5, 7] else 0)  # Block signals
		outb[2] = setBit(outb[2], 2, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 3, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("N21W").GetAspect()
		outb[2] = setBit(outb[2], 4, 1 if asp in [1, 3, 5, 7] else 0) 
		outb[2] = setBit(outb[2], 5, 1 if asp in [2, 3, 6, 7] else 0)
		outb[2] = setBit(outb[2], 6, 1 if asp in [4, 5, 6, 7] else 0)
		outb[2] = setBit(outb[2], 6, self.rr.GetInput("S11").GetValue())  # Shore approach indicator

		v = self.rr.GetInput("R10").GetValue() + self.rr.GetInput("R10.W").GetValue() 
		outb[3] = setBit(outb[3], 0, 1 if v != 0 else 0 )  				# Rocky Hill approach indicator
		outb[3] = setBit(outb[3], 1, self.rr.GetInput("B20").GetValue())  # Bank approach indicator
		outb[3] = setBit(outb[3], 2, optFleet)                    # fleet indicator
		outb[3] = setBit(outb[3], 3, 1-optFleet)
		sigL = self.sigLever["N14"]
		outb[3] = setBit(outb[3], 4, 1 if sigL == "L" else 0)       # Signal Indicators
		outb[3] = setBit(outb[3], 5, 1 if sigL == "N" else 0)
		outb[3] = setBit(outb[3], 6, 1 if sigL == "R" else 0)
		sigL = self.sigLever["N16"]
		outb[3] = setBit(outb[3], 7, 1 if sigL == "L" else 0) 

		outb[4] = setBit(outb[4], 0, 1 if sigL == "N" else 0)
		outb[4] = setBit(outb[4], 1, 1 if sigL == "R" else 0)
		sigL = self.sigLever["N18"]
		outb[4] = setBit(outb[4], 2, 1 if sigL == "L" else 0)
		outb[4] = setBit(outb[4], 3, 1 if sigL == "N" else 0)
		outb[4] = setBit(outb[4], 4, 1 if sigL == "R" else 0)
		sigL = self.sigLever["N20"]
		outb[4] = setBit(outb[4], 5, 1 if sigL == "L" else 0) 
		outb[4] = setBit(outb[4], 6, 1 if sigL == "N" else 0)
		outb[4] = setBit(outb[4], 7, 1 if sigL == "R" else 0)

		op = self.rr.GetOutput("KSw1").GetOutPulse()
		outb[5] = setBit(outb[5], 0, 1 if op > 0 else 0)             # Krulish switches
		outb[5] = setBit(outb[5], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("KSw3").GetOutPulse()
		outb[5] = setBit(outb[5], 2, 1 if op > 0 else 0)  
		outb[5] = setBit(outb[5], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("KSw5").GetOutPulse()
		outb[5] = setBit(outb[5], 4, 1 if op > 0 else 0)  
		outb[5] = setBit(outb[5], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("KSw7").GetOutPulse()
		outb[5] = setBit(outb[5], 6, 1 if op > 0 else 0)  
		outb[5] = setBit(outb[5], 7, 1 if op < 0 else 0)

		outb[6] = setBit(outb[6], 0, self.rr.GetInput("CBKrulish").GetValue())   # Circuit breakers
		outb[6] = setBit(outb[6], 1, self.rr.GetInput("CBNassauW").GetValue()) 
		outb[6] = setBit(outb[6], 2, self.rr.GetInput("CBNassauE").GetValue())  
		outb[6] = setBit(outb[6], 3, self.rr.GetInput("CBSptJct").GetValue())  
		outb[6] = setBit(outb[6], 4, self.rr.GetInput("CBWilson").GetValue())   
		outb[6] = setBit(outb[6], 5, self.rr.GetInput("CBThomas").GetValue())
		outb[6] = setBit(outb[6], 6, NWSL[0])  # switch locks west
		outb[6] = setBit(outb[6], 7, NWSL[1])

		outb[7] = setBit(outb[7], 0, NWSL[2])
		outb[7] = setBit(outb[7], 1, NWSL[3])
		outb[7] = setBit(outb[7], 2, self.rr.GetOutput("N21.srel").GetStatus())	      # Stop relays
																					# Bit 3 used for signal N14R above
		asp = self.rr.GetOutput("N14LD").GetAspect()    							# dwarf signals for W20
		outb[7] = setBit(outb[7], 4, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N24RD").GetAspect()   
		outb[7] = setBit(outb[7], 5, 1 if asp != 0 else 0)

		otext = formatOText(outb, 8)
		logging.debug("Nassau West: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(NASSAUW, outb, 8, swap=False)

		if inbc != 8:
			if self.sendIO:
				self.rr.ShowText(otext, "", 0, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Nassau West: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 0, 3)

			ip = self.rr.GetInput("NSw19")  #Switch positions
			nb = getBit(inb[0], 0)
			rb = getBit(inb[0], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw21") 
			nb = getBit(inb[0], 2)
			rb = getBit(inb[0], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw23") 
			nb = getBit(inb[0], 4)
			rb = getBit(inb[0], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw25")
			nb = getBit(inb[0], 6)
			rb = getBit(inb[0], 7)
			ip.SetState(nb, rb)

			ip = self.rr.GetInput("NSw27") 
			nb = getBit(inb[1], 0)
			rb = getBit(inb[1], 1)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw29") 
			nb = getBit(inb[1], 2)
			rb = getBit(inb[1], 3)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw31") 
			nb = getBit(inb[1], 4)
			rb = getBit(inb[1], 5)
			ip.SetState(nb, rb)
			ip = self.rr.GetInput("NSw33")
			nb = getBit(inb[1], 6)
			rb = getBit(inb[1], 7)
			ip.SetState(nb, rb)

			ip = self.rr.GetInput("N21.W") 
			ip.SetValue(getBit(inb[2], 0))   #detection
			ip = self.rr.GetInput("N21") 
			ip.SetValue(getBit(inb[2], 1)) 
			ip = self.rr.GetInput("N21.E") 
			ip.SetValue(getBit(inb[2], 2)) 
			ip = self.rr.GetInput("NWOSTY")  # NWOS1
			ip.SetValue(getBit(inb[2], 3)) 
			ip = self.rr.GetInput("NWOSCY")  # NWOS2
			ip.SetValue(getBit(inb[2], 4)) 
			ip = self.rr.GetInput("NWOSW")  # NWOS3
			ip.SetValue(getBit(inb[2], 5)) 
			ip = self.rr.GetInput("NWOSE")  # NWOS4
			ip.SetValue(getBit(inb[2], 6)) 
			ip = self.rr.GetInput("N32") 
			ip.SetValue(getBit(inb[2], 7)) 

			ip = self.rr.GetInput("N31") 
			ip.SetValue(getBit(inb[3], 0)) 
			ip = self.rr.GetInput("N12") 
			ip.SetValue(getBit(inb[3], 1)) 

			if optControl == 0:  # Nassau local control
				release = getBit(inb[3], 2)
				self.rr.GetInput("nrelease").SetState(release)  # C Release switch
				fleet = getBit(inb[3], 3)
				self.rr.GetInput("nassau.fleet").SetState(fleet)  # fleet
				lvrL = getBit(inb[3], 4)  # signal levers
				lvrCallOn = getBit(inb[3], 5)
				lvrR = getBit(inb[3], 6)
				self.rr.GetInput("N14.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[3], 7)

				lvrCallOn = getBit(inb[4], 0)
				lvrR = getBit(inb[4], 1)
				self.rr.GetInput("N16.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[4], 2)
				lvrCallOn = getBit(inb[4], 3)
				lvrR = getBit(inb[4], 4)
				self.rr.GetInput("N18.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

				lvrL = getBit(inb[5], 0)
				lvrCallOn = getBit(inb[5], 1)
				lvrR = getBit(inb[5], 2)
				self.rr.GetInput("N24.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[5], 3)
				lvrCallOn = getBit(inb[5], 4)
				lvrR = getBit(inb[5], 5)
				self.rr.GetInput("N26.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

			if optControl != 2:  # NOT dispatcher ALL
				lvrL = getBit(inb[4], 5)
				lvrCallOn = getBit(inb[4], 6)
				lvrR = getBit(inb[4], 7)
				self.rr.GetInput("N20.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
				lvrL = getBit(inb[5], 6)
				lvrCallOn = getBit(inb[5], 7)
				lvrR = getBit(inb[6], 0)
				self.rr.GetInput("N28.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))

			self.rr.GetInput("CBKrulishYd").SetValue(getBit(inb[6], 1)) # Breakers
			self.rr.GetInput("CBThomas").SetValue(getBit(inb[6], 2))
			self.rr.GetInput("CBWilson").SetValue(getBit(inb[6], 3))
			self.rr.GetInput("CBKrulish").SetValue(getBit(inb[6], 4))
			self.rr.GetInput("CBNassauW").SetValue(getBit(inb[6], 5))
			self.rr.GetInput("CBNassauE").SetValue(getBit(inb[6], 6))
			self.rr.GetInput("CBFoss").SetValue(getBit(inb[6], 7))

			self.rr.GetInput("CBDell").SetValue(getBit(inb[7], 0))
			NSw60A = getBit(inb[7], 1)  # Switches in coach yard
			NSw60B = getBit(inb[7], 2)
			NSw60C = getBit(inb[7], 3)
			NSw60D = getBit(inb[7], 4)
			ip13 = self.rr.GetInput("NSw13") 
			ip15 = self.rr.GetInput("NSw15") 
			ip17 = self.rr.GetInput("NSw17") 
			if NSw60A != 0:
				ip13.SetState(0, 1)
				ip15.SetState(0, 1)
				ip17.SetState(0, 1)
			elif NSw60B != 0:
				ip13.SetState(1, 0)
				ip15.SetState(1, 0)
				ip17.SetState(0, 1)
			elif NSw60C != 0:
				ip13.SetState(0, 1)
				ip15.SetState(0, 1)
				ip17.SetState(1, 0)
			elif NSw60D != 0:
				ip13.SetState(1, 0)
				ip15.SetState(1, 0)
				ip17.SetState(1, 0)

			ip = self.rr.GetInput("NSw35")
			nb = getBit(inb[7], 5)
			rb = getBit(inb[7], 6)
			ip.SetState(nb, rb)

		# Nassau East
		outb = [0 for _ in range(4)]

		asp = self.rr.GetOutput("N24RB").GetAspect()             # Signals
		outb[0] = setBit(outb[0], 0, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 1, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N24RC").GetAspect()    
		outb[0] = setBit(outb[0], 2, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 3, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N26RC").GetAspect()    
		outb[0] = setBit(outb[0], 4, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 5, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N24RA").GetAspect()    
		outb[0] = setBit(outb[0], 6, 1 if asp in [1, 3] else 0)
		outb[0] = setBit(outb[0], 7, 1 if asp in [2, 3] else 0)

		asp = self.rr.GetOutput("N26RA").GetAspect()       
		outb[1] = setBit(outb[1], 0, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N26RB").GetAspect()       
		outb[1] = setBit(outb[1], 1, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N28R").GetAspect()       
		outb[1] = setBit(outb[1], 2, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("B20E").GetAspect()
		outb[1] = setBit(outb[1], 3, 1 if asp in [1, 3, 5, 7] else 0)  # block signal
		outb[1] = setBit(outb[1], 4, 1 if asp in [2, 3, 6, 7] else 0)
		outb[1] = setBit(outb[1], 5, 1 if asp in [4, 5, 6, 7] else 0)
		asp = self.rr.GetOutput("N24L").GetAspect()       
		outb[1] = setBit(outb[1], 6, 1 if asp != 0 else 0)
		asp = self.rr.GetOutput("N26L").GetAspect()       
		outb[1] = setBit(outb[1], 7, 1 if asp in [1, 3] else 0)

		outb[2] = setBit(outb[2], 0, 1 if asp in [2, 3] else 0)
		asp = self.rr.GetOutput("N28L").GetAspect()       
		outb[2] = setBit(outb[2], 1, 1 if asp in [1, 3] else 0)
		outb[2] = setBit(outb[2], 2, 1 if asp in [2, 3] else 0)
		outb[2] = setBit(outb[2], 3, NESL[0])  # switch locks east
		outb[2] = setBit(outb[2], 4, NESL[1])
		outb[2] = setBit(outb[2], 5, NESL[2])
		outb[2] = setBit(outb[2], 6, self.rr.GetOutput("B10.srel").GetStatus())	# Stop relay
		sigL = self.sigLever["N24"]
		outb[2] = setBit(outb[2], 7, 1 if sigL == "L" else 0)       # Signal Indicators

		outb[3] = setBit(outb[3], 0, 1 if sigL == "N" else 0)
		outb[3] = setBit(outb[3], 1, 1 if sigL == "R" else 0)
		sigL = self.sigLever["N26"]
		outb[3] = setBit(outb[3], 2, 1 if sigL == "L" else 0)  
		outb[3] = setBit(outb[3], 3, 1 if sigL == "N" else 0)
		outb[3] = setBit(outb[3], 4, 1 if sigL == "R" else 0)
		sigL = self.sigLever["N28"]
		outb[3] = setBit(outb[3], 5, 1 if sigL == "L" else 0)  
		outb[3] = setBit(outb[3], 6, 1 if sigL == "N" else 0)
		outb[3] = setBit(outb[3], 7, 1 if sigL == "R" else 0)

		otext = formatOText(outb, 4)
		logging.debug("Nassau East: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(NASSAUE, outb, 4, swap=False)

		if inbc != 4:
			if self.sendIO:
				self.rr.ShowText(otext, "", 1, 3)
		else:
			itext = formatIText(inb, inbc)
			logging.debug("Nassau East: Input Bytes: %s" % itext)
			if self.sendIO:
				self.rr.ShowText(otext, itext, 1, 3)
		
			nb = getBit(inb[0], 0)  # Switch positions
			rb = getBit(inb[0], 1)
			self.rr.GetInput("NSw41").SetState(nb, rb)
			nb = getBit(inb[0], 2) 
			rb = getBit(inb[0], 3)
			self.rr.GetInput("NSw43").SetState(nb, rb)
			nb = getBit(inb[0], 4) 
			rb = getBit(inb[0], 5)
			self.rr.GetInput("NSw5").SetState(nb, rb)
			nb = getBit(inb[0], 6) 
			rb = getBit(inb[0], 7)
			self.rr.GetInput("NSw47").SetState(nb, rb)

			nb = getBit(inb[1], 0) 
			rb = getBit(inb[1], 1)
			self.rr.GetInput("NSw51").SetState(nb, rb)
			nb = getBit(inb[1], 2) 
			rb = getBit(inb[1], 3)
			self.rr.GetInput("NSw53").SetState(nb, rb)
			nb = getBit(inb[1], 4) 
			rb = getBit(inb[1], 5)
			self.rr.GetInput("NSw55").SetState(nb, rb)
			nb = getBit(inb[1], 6) 
			rb = getBit(inb[1], 7)
			self.rr.GetInput("NSw57").SetState(nb, rb)

			self.rr.GetInput("N22").SetValue(getBit(inb[2], 0))  # Detection
			self.rr.GetInput("N41").SetValue(getBit(inb[2], 1))  
			self.rr.GetInput("N42").SetValue(getBit(inb[2], 2)) 
			self.rr.GetInput("NEOSRH").SetValue(getBit(inb[2], 3)) # NEOS1 
			self.rr.GetInput("NEOSW").SetValue(getBit(inb[2], 4))  # NEOS2
			self.rr.GetInput("NEOSE").SetValue(getBit(inb[2], 5))  # NEOS3 
			self.rr.GetInput("B10.W").SetValue(getBit(inb[2], 6))  
			self.rr.GetInput("B10").SetValue(getBit(inb[2], 7))  

			nb = getBit(inb[3], 0) 
			rb = getBit(inb[3], 1)
			self.rr.GetInput("NSw39").SetState(nb, rb)

		# NX Buttons Output only
		outb = [0 for _ in range(3)]

		op = self.rr.GetOutput("NNXBtnT12").GetOutPulse() # Nassau West
		outb[0] = setBit(outb[0], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN60").GetOutPulse()
		outb[0] = setBit(outb[0], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN11").GetOutPulse()
		outb[0] = setBit(outb[0], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN21").GetOutPulse()
		outb[0] = setBit(outb[0], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnW10").GetOutPulse()
		outb[0] = setBit(outb[0], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN32W").GetOutPulse()
		outb[0] = setBit(outb[0], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN31W").GetOutPulse()
		outb[0] = setBit(outb[0], 6, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN12W").GetOutPulse()
		outb[0] = setBit(outb[0], 7, 1 if op != 0 else 0)

		op = self.rr.GetOutput("NNXBtnN22W").GetOutPulse()
		outb[1] = setBit(outb[1], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN41W").GetOutPulse()
		outb[1] = setBit(outb[1], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN42W").GetOutPulse()
		outb[1] = setBit(outb[1], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnW20W").GetOutPulse()
		outb[1] = setBit(outb[1], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnW11").GetOutPulse()
		outb[1] = setBit(outb[1], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN32E").GetOutPulse()
		outb[1] = setBit(outb[1], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN31E").GetOutPulse()
		outb[1] = setBit(outb[1], 6, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN12E").GetOutPulse()
		outb[1] = setBit(outb[1], 7, 1 if op != 0 else 0)

		op = self.rr.GetOutput("NNXBtnN22E").GetOutPulse()
		outb[2] = setBit(outb[2], 0, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN41E").GetOutPulse()
		outb[2] = setBit(outb[2], 1, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnN42E").GetOutPulse()
		outb[2] = setBit(outb[2], 2, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnW20E").GetOutPulse()
		outb[2] = setBit(outb[2], 3, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnR10").GetOutPulse()
		outb[2] = setBit(outb[2], 4, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnB10").GetOutPulse()
		outb[2] = setBit(outb[2], 5, 1 if op != 0 else 0)
		op = self.rr.GetOutput("NNXBtnB20").GetOutPulse()
		outb[2] = setBit(outb[2], 6, 1 if op != 0 else 0)

		otext = formatOText(outb, 3)
		logging.debug("Nassau NX: Output bytes: %s" % otext)
			
		if self.settings.simulation:
			inb = []
			inbc = 0
		else:
			inb, inbc = self.rrbus.sendRecv(NASSAUNX, outb, 3, swap=False)
		if self.sendIO:
			self.rr.ShowText(otext, "", 2, 3)

# 	No inputs here
