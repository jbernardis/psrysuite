import logging

from rrserver.district import District, leverState,  NASSAUE, NASSAUW, NASSAUNX, formatIText, formatOText
from rrserver.rrobjects import SignalOutput, TurnoutOutput, NXButtonOutput, RelayOutput, BreakerInput, BlockInput, \
	TurnoutInput, SignalLeverInput, ToggleInput, FleetLeverInput, IndicatorOutput
from rrserver.bus import setBit, getBit


class Nassau(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)
		
		self.panelFleet = False

		sigNames =  [
			["N20R", 1], ["N20L", 1],
			["N18R", 1], ["N18LA", 2], ["N18LB", 2],
			["N16R", 2], ["N16L", 2],
			["N14R", 2], ["N14LA", 2], ["N14LB", 1], ["N14LC", 1], ["N14LD", 1],
			["N28R", 1], ["N28L", 2],
			["N26RA", 1], ["N26RB", 1], ["N26RC", 2], ["N26L", 2],
			["N24RA", 2], ["N24RB", 2], ["N24RC", 2], ["N24RD", 1], ["N24L", 1],
			["N11W", 3], ["N21W", 3], ["B20E", 3]
		]
		toONames = ["NSw13", "NSw15", "NSw17"]
		toNames = [ "NSw19", "NSw21", "NSw23", "NSw25", "NSw27", "NSw29", "NSw31", "NSw33", "NSw35",
					"NSw39", "NSw41", "NSw43", "NSw45", "NSw47", "NSw51", "NSw53", "NSw55", "NSw57"]
		relayNames = [ "N21.srel", "B10.srel" ]
		indNames =  [ "CBKrulish", "CBNassauW", "CBNassauE", "CBSptJct", "CBWilson", "CBThomas" ]

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
		ix = self.AddOutputs([s[0] for s in sigNames], SignalOutput, District.signal, ix)
		for sig, bits in sigNames:
			self.rr.GetOutput(sig).SetBits(bits)
		ix = self.AddOutputs(toONames+toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(nxButtons, NXButtonOutput, District.nxbutton, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in nxButtons:
			self.SetNXButtonPulseLen(n, settings.nxbpulselen, settings.nxbpulsect)

		brkrNames = [ "CBKrulish", "CBKrulishYd", "CBNassauW", "CBNassauE", "CBSptJct", "CBWilson", "CBThomas", "CBFoss", "CBDell" ]
		blockNames = [ "N21.W", "N21", "N21.E", "NWOSTY", "NWOSCY", "NWOSW", "NWOSE",
						"N31", "N32", "N12", "N22", "N41", "N42",
						"NEOSW", "NEOSE", "NEOSRH", "B10.W", "B10",
						"N60", "T12", "W10", "W11", "W20", "R10.W" ]
		signalLeverNames = [ "N14.lvr", "N16.lvr", "N18.lvr", "N20.lvr", "N24.lvr", "N26.lvr", "N28.lvr" ]
		toggleNames = [ "nrelease" ]
		fleetLeverNames = [ "nassau.fleet" ]

		ix = 0
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddSubBlocks("R10", ["R10A", "R10B", "R10C"], ix)
		ix = self.AddInputs(toONames+toNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(brkrNames, BreakerInput, District.breaker, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(fleetLeverNames, FleetLeverInput, District.flever, ix)
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
		if optControl == 0:
			optFleet = self.rr.GetInput("nassau.fleet").GetState() # get the state of the lever on the panel
		else:
			optFleet = self.rr.GetControlOption("nassau.fleet")  # otherwise get the fleeting state from the check box

		nRelease = self.rr.GetInput("nrelease").GetState()
		optOssLocks = self.rr.GetControlOption("osslocks")

		NESL = self.rr.GetDistrictLock("NESL")
		NWSL = self.rr.GetDistrictLock("NWSL")
		if nRelease == 1 or optOssLocks == 0:
			# don't set any switch locks if release button is being pressed
			NESL = [0 for _ in range(len(NESL))]
			NWSL = [0 for _ in range(len(NWSL))]
			if optControl == 1:  # Dispatcher Main only
				NESL[0] = 1
				NWSL[0] = 1
			
		# Nassau West
		outbc = 8
		outb = [0 for _ in range(outbc)]

		asp = self.rr.GetOutput("N14LC").GetAspectBits()     # signals
		outb[0] = setBit(outb[0], 0, asp[0])
		asp = self.rr.GetOutput("N14LB").GetAspectBits()    
		outb[0] = setBit(outb[0], 1, asp[0])
		asp = self.rr.GetOutput("N20R").GetAspectBits()    
		outb[0] = setBit(outb[0], 2, asp[0])
		asp = self.rr.GetOutput("N20L").GetAspectBits()    
		outb[0] = setBit(outb[0], 3, asp[0])
		asp = self.rr.GetOutput("N14LA").GetAspectBits()    
		outb[0] = setBit(outb[0], 4, asp[0])
		outb[0] = setBit(outb[0], 5, asp[1])
		asp = self.rr.GetOutput("N16L").GetAspectBits()    
		outb[0] = setBit(outb[0], 6, asp[0])
		outb[0] = setBit(outb[0], 7, asp[1])

		asp = self.rr.GetOutput("N18LB").GetAspectBits()    
		outb[1] = setBit(outb[1], 0, asp[0])
		outb[1] = setBit(outb[1], 1, asp[1])
		asp = self.rr.GetOutput("N18LA").GetAspectBits()    
		outb[1] = setBit(outb[1], 2, asp[0])
		outb[1] = setBit(outb[1], 3, asp[1])
		asp = self.rr.GetOutput("N16R").GetAspectBits()    
		outb[1] = setBit(outb[1], 4, asp[0])
		outb[1] = setBit(outb[1], 5, asp[1])
		asp = self.rr.GetOutput("N14R").GetAspectBits()    
		outb[1] = setBit(outb[1], 6, asp[0])
		outb[7] = setBit(outb[7], 3, asp[1])  # Transferred to byte 7:3 because of 1:7 being a Bad output?

		asp = self.rr.GetOutput("N18R").GetAspectBits()    
		outb[2] = setBit(outb[2], 0, asp[0])
		asp = self.rr.GetOutput("N11W").GetAspectBits()
		outb[2] = setBit(outb[2], 1, asp[0])  # Block signals
		outb[2] = setBit(outb[2], 2, asp[1])
		outb[2] = setBit(outb[2], 3, asp[2])
		asp = self.rr.GetOutput("N21W").GetAspectBits()
		outb[2] = setBit(outb[2], 4, asp[0]) 
		outb[2] = setBit(outb[2], 5, asp[1])
		outb[2] = setBit(outb[2], 6, asp[2])
		v = self.rr.GetInput("S11A").GetValue() + self.rr.GetInput("S11B").GetValue()
		outb[2] = setBit(outb[2], 6, 1 if v != 0 else 0)  # Shore approach indicator

		v = self.rr.GetInput("R10").GetValue() + self.rr.GetInput("R10.W").GetValue() 
		outb[3] = setBit(outb[3], 0, 1 if v != 0 else 0 )  				# Rocky Hill approach indicator
		outb[3] = setBit(outb[3], 1, self.rr.GetInput("B20").GetValue())  # Bank approach indicator
		outb[3] = setBit(outb[3], 2, 1-optFleet)                    # fleet indicator
		outb[3] = setBit(outb[3], 3, optFleet)
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

		outb[6] = setBit(outb[6], 0, self.rr.GetInput("CBKrulish").GetInvertedValue())   # Circuit breakers
		outb[6] = setBit(outb[6], 1, self.rr.GetInput("CBNassauW").GetInvertedValue()) 
		outb[6] = setBit(outb[6], 2, self.rr.GetInput("CBNassauE").GetInvertedValue())  
		outb[6] = setBit(outb[6], 3, self.rr.GetInput("CBSptJct").GetInvertedValue())  
		outb[6] = setBit(outb[6], 4, self.rr.GetInput("CBWilson").GetInvertedValue())   
		outb[6] = setBit(outb[6], 5, self.rr.GetInput("CBThomas").GetInvertedValue())
		outb[6] = setBit(outb[6], 6, NWSL[0])  # switch locks west
		outb[6] = setBit(outb[6], 7, NWSL[1])

		outb[7] = setBit(outb[7], 0, NWSL[2])
		outb[7] = setBit(outb[7], 1, NWSL[3])
		outb[7] = setBit(outb[7], 2, self.rr.GetOutput("N21.srel").GetStatus())	      # Stop relays
																					# Bit 3 used for signal N14R above
		asp = self.rr.GetOutput("N14LD").GetAspectBits()    							# dwarf signals for W20
		outb[7] = setBit(outb[7], 4, asp[0])
		asp = self.rr.GetOutput("N24RD").GetAspectBits()   
		outb[7] = setBit(outb[7], 5, asp[0])

		otext = formatOText(outb, outbc)
		#logging.debug("Nassau West: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(NASSAUW, outb, outbc)
			if inb is None:
				itext = "Read Error"
			else:
				itext = formatIText(inb, inbc)
				#logging.debug("Nassau West: Input Bytes: %s" % itext)
	
				ip = self.rr.GetInput("NSw19")  #Switch positions
				nb = getBit(inb[0], 0)
				rb = getBit(inb[0], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw21") 
				nb = getBit(inb[0], 2)
				rb = getBit(inb[0], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw23") 
				nb = getBit(inb[0], 4)
				rb = getBit(inb[0], 5)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw25")
				nb = getBit(inb[0], 6)
				rb = getBit(inb[0], 7)
				ip.SetTOState(nb, rb)
	
				ip = self.rr.GetInput("NSw27") 
				nb = getBit(inb[1], 0)
				rb = getBit(inb[1], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw29") 
				nb = getBit(inb[1], 2)
				rb = getBit(inb[1], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw31") 
				nb = getBit(inb[1], 4)
				rb = getBit(inb[1], 5)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("NSw33")
				nb = getBit(inb[1], 6)
				rb = getBit(inb[1], 7)
				ip.SetTOState(nb, rb)
	
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
					lvrR = getBit(inb[3], 4)  # signal levers
					lvrCallOn = getBit(inb[3], 5)
					lvrL = getBit(inb[3], 6)
					self.rr.GetInput("N14.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[3], 7)
	
					lvrCallOn = getBit(inb[4], 0)
					lvrL = getBit(inb[4], 1)
					self.rr.GetInput("N16.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[4], 2)
					lvrCallOn = getBit(inb[4], 3)
					lvrL = getBit(inb[4], 4)
					self.rr.GetInput("N18.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
	
					lvrR = getBit(inb[5], 0)
					lvrCallOn = getBit(inb[5], 1)
					lvrL = getBit(inb[5], 2)
					self.rr.GetInput("N24.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[5], 3)
					lvrCallOn = getBit(inb[5], 4)
					lvrL = getBit(inb[5], 5)
					self.rr.GetInput("N26.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
	
				if optControl != 2:  # NOT dispatcher ALL
					lvrR = getBit(inb[4], 5)
					lvrCallOn = getBit(inb[4], 6)
					lvrL = getBit(inb[4], 7)
					self.rr.GetInput("N20.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[5], 6)
					lvrCallOn = getBit(inb[5], 7)
					lvrL = getBit(inb[6], 0)
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
					ip13.SetTOState(0, 1)
					ip15.SetTOState(0, 1)
					ip17.SetTOState(0, 1)
				elif NSw60B != 0:
					ip13.SetTOState(1, 0)
					ip15.SetTOState(1, 0)
					ip17.SetTOState(0, 1)
				elif NSw60C != 0:
					ip13.SetTOState(0, 1)
					ip15.SetTOState(0, 1)
					ip17.SetTOState(1, 0)
				elif NSw60D != 0:
					ip13.SetTOState(1, 0)
					ip15.SetTOState(1, 0)
					ip17.SetTOState(1, 0)
	
				ip = self.rr.GetInput("NSw35")
				nb = getBit(inb[7], 5)
				rb = getBit(inb[7], 6)
				ip.SetTOState(nb, rb)

		if self.sendIO:
			self.rr.ShowText("NasW", NASSAUW, otext, itext, 0, 3)

		# Nassau East
		outbc = 4
		outb = [0 for _ in range(outbc)]

		asp = self.rr.GetOutput("N24RB").GetAspectBits()             # Signals
		outb[0] = setBit(outb[0], 0, asp[0])
		outb[0] = setBit(outb[0], 1, asp[1])
		asp = self.rr.GetOutput("N24RC").GetAspectBits()    
		outb[0] = setBit(outb[0], 2, asp[0])
		outb[0] = setBit(outb[0], 3, asp[1])
		asp = self.rr.GetOutput("N26RC").GetAspectBits()   
		outb[0] = setBit(outb[0], 4, asp[0])
		outb[0] = setBit(outb[0], 5, asp[1])
		asp = self.rr.GetOutput("N24RA").GetAspectBits()    
		outb[0] = setBit(outb[0], 6, asp[0])
		outb[0] = setBit(outb[0], 7, asp[1])

		asp = self.rr.GetOutput("N26RA").GetAspectBits()       
		outb[1] = setBit(outb[1], 0, asp[0])
		asp = self.rr.GetOutput("N26RB").GetAspectBits()       
		outb[1] = setBit(outb[1], 1, asp[0])
		asp = self.rr.GetOutput("N28R").GetAspectBits()       
		outb[1] = setBit(outb[1], 2, asp[0])
		asp = self.rr.GetOutput("B20E").GetAspectBits()
		outb[1] = setBit(outb[1], 3, asp[0])  # block signal
		outb[1] = setBit(outb[1], 4, asp[1])
		outb[1] = setBit(outb[1], 5, asp[2])
		asp = self.rr.GetOutput("N24L").GetAspectBits()       
		outb[1] = setBit(outb[1], 6, asp[0])
		asp = self.rr.GetOutput("N26L").GetAspectBits()       
		outb[1] = setBit(outb[1], 7, asp[0])

		outb[2] = setBit(outb[2], 0, asp[1])
		asp = self.rr.GetOutput("N28L").GetAspectBits()       
		outb[2] = setBit(outb[2], 1, asp[0])
		outb[2] = setBit(outb[2], 2, asp[1])
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

		otext = formatOText(outb, outbc)
		#logging.debug("Nassau East: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(NASSAUE, outb, outbc)
			if inb is None:
				itext = "Read Error"
			else:
				itext = formatIText(inb, inbc)
				#logging.debug("Nassau East: Input Bytes: %s" % itext)
			
				nb = getBit(inb[0], 0)  # Switch positions
				rb = getBit(inb[0], 1)
				self.rr.GetInput("NSw41").SetTOState(nb, rb)
				nb = getBit(inb[0], 2) 
				rb = getBit(inb[0], 3)
				self.rr.GetInput("NSw43").SetTOState(nb, rb)
				nb = getBit(inb[0], 4) 
				rb = getBit(inb[0], 5)
				self.rr.GetInput("NSw45").SetTOState(nb, rb)
				nb = getBit(inb[0], 6) 
				rb = getBit(inb[0], 7)
				self.rr.GetInput("NSw47").SetTOState(nb, rb)
	
				nb = getBit(inb[1], 0) 
				rb = getBit(inb[1], 1)
				self.rr.GetInput("NSw51").SetTOState(nb, rb)
				nb = getBit(inb[1], 2) 
				rb = getBit(inb[1], 3)
				self.rr.GetInput("NSw53").SetTOState(nb, rb)
				nb = getBit(inb[1], 4) 
				rb = getBit(inb[1], 5)
				self.rr.GetInput("NSw55").SetTOState(nb, rb)
				nb = getBit(inb[1], 6) 
				rb = getBit(inb[1], 7)
				self.rr.GetInput("NSw57").SetTOState(nb, rb)
	
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
				self.rr.GetInput("NSw39").SetTOState(nb, rb)
			
		if self.sendIO:
			self.rr.ShowText("NasE", NASSAUE, otext, itext, 1, 3)

		# NX Buttons Output only
		outbc = 3
		outb = [0 for _ in range(outbc)]

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

		otext = formatOText(outb, outbc)
		#logging.debug("Nassau NX: Output bytes: %s" % otext)

		if not self.settings.simulation:
			inb = self.rrBus.sendRecv(NASSAUNX, outb, outbc)
			
		if self.sendIO:
			self.rr.ShowText("NsNX", NASSAUNX, otext, "- no inputs from this node -", 2, 3)

# 	No inputs here
