import logging

from rrserver.district import District, leverState, CORNELL, EASTJCT, KALE, YARD, YARDSW, formatIText, formatOText
from rrserver.rrobjects import TurnoutInput, BlockInput, RouteInput, SignalOutput, TurnoutOutput, RelayOutput, \
	FleetLeverInput, IndicatorOutput, SignalLeverInput, ToggleInput, NXButtonOutput
from rrserver.bus import setBit, getBit


class Yard(District):
	def __init__(self, parent, name, settings):
		District.__init__(self, parent, name, settings)

		sigNames = [
				["Y2R", 1], ["Y2L", 3],
				["Y4R", 3], ["Y4LA", 3], ["Y4LB", 1],
				["Y8RA", 1], ["Y8RB", 1], ["Y8RC", 1], ["Y8L", 3],
				["Y10R", 3], ["Y10L", 1],
				["Y22R", 1], ["Y22L", 3],
				["Y24RA", 1], ["Y24RB", 1],
				["Y26RA", 1], ["Y26RB", 1], ["Y26RC", 1], ["Y26L", 1],
				["Y34R", 3], ["Y34LA", 1], ["Y34LB", 1] ]
		toNames = [ "YSw1", "YSw3",
				"YSw7", "YSw9", "YSw11",
				"YSw17", "YSw19", "YSw21", "YSw23", "YSw25", "YSw27", "YSw29", "YSw33"]
		relayNames = [ "Y11.srel", "Y20.srel", "Y21.srel", "L10.srel" ]
		indNames = [ "Y20H", "Y20D","CBKale", "CBEastEndJct", "CBCornellJct", "CBEngineYard", "CBWaterman" ]
		nxButtons = ["YWEB1", "YWEB2", "YWEB3", "YWEB4", "YWWB1", "YWWB2", "YWWB3", "YWWB4"]

		ix = 0
		ix = self.AddOutputs([s[0] for s in sigNames], SignalOutput, District.signal, ix)
		for sig, bits in sigNames:
			self.rr.GetOutput(sig).SetBits(bits)
		ix = self.AddOutputs(toNames, TurnoutOutput, District.turnout, ix)
		ix = self.AddOutputs(nxButtons, NXButtonOutput, District.nxbutton, ix)
		ix = self.AddOutputs(relayNames, RelayOutput, District.relay, ix)
		ix = self.AddOutputs(indNames, IndicatorOutput, District.indicator, ix)

		for n in nxButtons:
			self.SetNXButtonPulseLen(n, settings.nxbpulselen, settings.nxbpulsect)

		for n in toNames:
			self.SetTurnoutPulseLen(n, settings.topulselen, settings.topulsect)

		# INPUTS (also using toNames from above)
		blockNames = [
			"Y21.W", "Y21", "Y21.E", "YOSCJW", "YOSCJE", "L10.W", "L10",
			"Y20", "Y20.E", "YOSEJW", "YOSEJE", "Y11.W", "Y11",
			"Y30", "YOSKL4", "Y53", "Y52", "Y51", "Y50", "YOSKL3", "YOSKL1", "YOSKL2", "Y10",
			"Y70", "Y87", "Y81", "Y82", "Y83", "Y84", "YOSWYE", "YOSWYW",
		]
		
		routeNames = ["Y81W", "Y82W", "Y83W", "Y84W", "Y81E", "Y82E", "Y83E", "Y84E" ]
		self.routeMap = {
				"Y81W": [ ["YSw113", "N"], ["YSw115","N"], ["YSw116", "N"] ], 
				"Y82W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "R"] ],
				"Y83W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "N"] ],
				"Y84W": [ ["YSw113", "R"], ["YSw115","N"], ["YSw116", "N"] ],
				"Y81E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "N"] ], 
				"Y82E": [ ["YSw131", "R"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y83E": [ ["YSw131", "N"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y84E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "R"] ],
		}
		fleetlLeverNames = [ "yard.fleet" ]
		signalLeverNames = [ "Y2.lvr", "Y4.lvr", "Y8.lvr", "Y10.lvr",
							"Y22.lvr", "Y24.lvr", "Y26.lvr", "Y34.lvr"]
		toggleNames = ["yrelease", "wos1norm"]

		ix = 0
		ix = self.AddInputs(routeNames, RouteInput, District.route, ix)
		ix = self.AddInputs(blockNames, BlockInput, District.block, ix)
		ix = self.AddInputs(toNames, TurnoutInput, District.turnout, ix)
		ix = self.AddInputs(signalLeverNames, SignalLeverInput, District.slever, ix)
		ix = self.AddInputs(fleetlLeverNames, FleetLeverInput, District.flever, ix)
		ix = self.AddInputs(toggleNames, ToggleInput, District.toggle, ix)

		# add "proxy" inputs for the waterman turnouts.  These will not be addressed directly, but through the  route table
		hiddenToNames = sorted([ "YSw113", "YSw115", "YSw116", "YSw131", "YSw132", "YSw134" ])
		for t in hiddenToNames:
			self.rr.AddInput(TurnoutInput(t, self), self, District.turnout)

	def DetermineSignalLevers(self):
		self.sigLever["Y2"] = self.DetermineSignalLever(["Y2L"], ["Y2R"])
		self.sigLever["Y4"] = self.DetermineSignalLever(["Y4LA", "Y4LB"], ["Y4R"])
		self.sigLever["Y8"] = self.DetermineSignalLever(["Y8L"], ["Y8RA", "Y8RB", "Y8RC"])
		self.sigLever["Y10"] = self.DetermineSignalLever(["Y10L"], ["Y10R"])
		self.sigLever["Y22"] = self.DetermineSignalLever(["Y22L"], ["Y22R"])
		self.sigLever["Y24"] = self.DetermineSignalLever([], ["Y24RA", "Y24RB"])
		self.sigLever["Y26"] = self.DetermineSignalLever(["Y26L"], ["Y26RA", "Y26RB", "Y26RC"])
		self.sigLever["Y34"] = self.DetermineSignalLever(["Y34LA", "Y34LB"], ["Y34R"])

	def OutIn(self):
		optControl = self.rr.GetControlOption("yard")  # 0 => Yard, 1 => Dispatcher
		optFleet = self.rr.GetControlOption("yard.fleet")  # 0 => no fleeting, 1 => fleeting
		#Cornell Jct
		outbc = 2
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("Y4R").GetAspectBits()
		outb[0] = setBit(outb[0], 0, asp[0])
		outb[0] = setBit(outb[0], 1, asp[1])
		outb[0] = setBit(outb[0], 2, asp[2])
		asp = self.rr.GetOutput("Y2R").GetAspectBits()
		outb[0] = setBit(outb[0], 3, asp[0])
		asp = self.rr.GetOutput("Y2L").GetAspectBits()
		outb[0] = setBit(outb[0], 4, asp[0])
		outb[0] = setBit(outb[0], 5, asp[1])
		outb[0] = setBit(outb[0], 6, asp[2])
		asp = self.rr.GetOutput("Y4LA").GetAspectBits()
		outb[0] = setBit(outb[0], 7, asp[0])

		outb[1] = setBit(outb[1], 0, asp[1])
		outb[1] = setBit(outb[1], 1, asp[2])
		asp = self.rr.GetOutput("Y4LB").GetAspectBits()
		outb[1] = setBit(outb[1], 2, asp[0])
		outb[1] = setBit(outb[1], 3, self.rr.GetOutput("Y21.srel").GetStatus())	      # Stop relays
		outb[1] = setBit(outb[1], 4, self.rr.GetOutput("L10.srel").GetStatus())

		otext = formatOText(outb, outbc)
		logging.debug("Cornell: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(CORNELL, outb, outbc)

			if self.AcceptResponse(inb, inbc, CORNELL):
				itext = formatIText(inb, inbc)
				logging.debug("Cornell: Input Bytes: %s" % itext)
	
				ip = self.rr.GetInput("YSw1")  #Switches
				nb = getBit(inb[0], 0)
				rb = getBit(inb[0], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw3")
				nb = getBit(inb[0], 2)
				rb = getBit(inb[0], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("Y21.W")  # Block detection
				ip.SetValue(getBit(inb[0], 4))
				ip = self.rr.GetInput("Y21")
				ip.SetValue(getBit(inb[0], 5))
				ip = self.rr.GetInput("Y21.E")
				ip.SetValue(getBit(inb[0], 6))
				ip = self.rr.GetInput("YOSCJW") # CJOS1
				ip.SetValue(getBit(inb[0], 7))
	
				ip = self.rr.GetInput("YOSCJE") # CJOS2
				ip.SetValue(getBit(inb[1], 0))
				ip = self.rr.GetInput("L10.W")
				ip.SetValue(getBit(inb[1], 1))
				ip = self.rr.GetInput("L10")
				ip.SetValue(getBit(inb[1], 2))
				
			else:
				logging.error("Cornell: Failed read")
				itext = None
				
		if self.sendIO:
			self.rr.ShowText("Crnl", CORNELL, otext, itext, 0, 5)

		# East Junction-----------------------------------------------------------------
		outbc = 2
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("Y10R").GetAspectBits()
		outb[0] = setBit(outb[0], 0, asp[0])
		outb[0] = setBit(outb[0], 1, asp[1])
		outb[0] = setBit(outb[0], 2, asp[2])
		asp = self.rr.GetOutput("Y8RA").GetAspectBits()
		outb[0] = setBit(outb[0], 3, asp[0])
		asp = self.rr.GetOutput("Y8RB").GetAspectBits()
		outb[0] = setBit(outb[0], 4, asp[0])
		asp = self.rr.GetOutput("Y8RC").GetAspectBits()
		outb[0] = setBit(outb[0], 5, asp[0])
		asp = self.rr.GetOutput("Y8L").GetAspectBits()
		outb[0] = setBit(outb[0], 6, asp[0])
		outb[0] = setBit(outb[0], 7, asp[1])

		outb[1] = setBit(outb[1], 0, asp[2])
		asp = self.rr.GetOutput("Y10L").GetAspectBits()
		outb[1] = setBit(outb[1], 1, asp[0])
		outb[1] = setBit(outb[1], 2, self.rr.GetOutput("Y20.srel").GetStatus())	      # Stop relays
		outb[1] = setBit(outb[1], 3, self.rr.GetOutput("Y11.srel").GetStatus())

		otext = formatOText(outb, outbc)
		logging.debug("East Jct: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(EASTJCT, outb, outbc)

			if self.AcceptResponse(inb, inbc, EASTJCT):
				itext = formatIText(inb, inbc)
				logging.debug("East Jct: Input Bytes: %s" % itext)
	
				ip = self.rr.GetInput("YSw7")  #Switch positions
				nb = getBit(inb[0], 0)
				rb = getBit(inb[0], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw9") 
				nb = getBit(inb[0], 2)
				rb = getBit(inb[0], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw11")  
				nb = getBit(inb[0], 4)
				rb = getBit(inb[0], 5)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("Y20")  # Detection
				ip.SetValue(getBit(inb[0], 6))
				ip = self.rr.GetInput("Y20.E") 
				ip.SetValue(getBit(inb[0], 7))
	
				ip = self.rr.GetInput("YOSEJW")  # EJOS1
				ip.SetValue(getBit(inb[1], 0))
				ip = self.rr.GetInput("YOSEJE")  # EJOS2
				ip.SetValue(getBit(inb[1], 1))
				ip = self.rr.GetInput("Y11.W")
				ip.SetValue(getBit(inb[1], 2))
				ip = self.rr.GetInput("Y11") 
				ip.SetValue(getBit(inb[1], 3))
				
			else:
				logging.error("East Jct: Failed read")
				itext = None
				
		if self.sendIO:
			self.rr.ShowText("EJct", EASTJCT, otext, itext, 1, 5)

		# Kale-----------------------------------------------------------------------
		outbc = 4
		outb = [0 for _ in range(outbc)]
		asp = self.rr.GetOutput("Y22R").GetAspectBits()
		outb[0] = setBit(outb[0], 0, asp[0])
		asp = self.rr.GetOutput("Y26RA").GetAspectBits()
		outb[0] = setBit(outb[0], 1, asp[0])
		asp = self.rr.GetOutput("Y26RB").GetAspectBits()
		outb[0] = setBit(outb[0], 2, asp[0])
		asp = self.rr.GetOutput("Y26RC").GetAspectBits()
		outb[0] = setBit(outb[0], 3, asp[0])
		asp = self.rr.GetOutput("Y24RA").GetAspectBits()
		outb[0] = setBit(outb[0], 4, asp[0])
		asp = self.rr.GetOutput("Y24RB").GetAspectBits()
		outb[0] = setBit(outb[0], 5, asp[0])
		ind = self.rr.GetOutput("Y20H").GetStatus()
		outb[0] = setBit(outb[0], 6, 1 if ind != 0 else 0)
		ind = self.rr.GetOutput("Y20D").GetStatus()
		outb[0] = setBit(outb[0], 7, 1 if ind != 0 else 0)

		asp = self.rr.GetOutput("Y26L").GetAspectBits()
		outb[1] = setBit(outb[1], 0, asp[0])
		asp = self.rr.GetOutput("Y22L").GetAspect()
		outb[1] = setBit(outb[1], 1, 1 if asp == 0b101 else 0)  # Approach
		outb[1] = setBit(outb[1], 2, 1 if asp == 0b001 else 0)  # Restricting

		otext = formatOText(outb, outbc)
		logging.debug("Kale: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(KALE, outb, outbc)

			if self.AcceptResponse(inb, inbc, KALE):
				itext = formatIText(inb, inbc)
				logging.debug("Kale: Input Bytes: %s" % itext)
	
				ip = self.rr.GetInput("YSw17")  #Switch positions
				nb = getBit(inb[0], 0)
				rb = getBit(inb[0], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw19") 
				nb = getBit(inb[0], 2)
				rb = getBit(inb[0], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw21") 
				nb = getBit(inb[0], 4)
				rb = getBit(inb[0], 5)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw23") 
				nb = getBit(inb[0], 6)
				rb = getBit(inb[0], 7)
				ip.SetTOState(nb, rb)
	
				ip = self.rr.GetInput("YSw25") 
				nb = getBit(inb[1], 0)
				rb = getBit(inb[1], 1)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw27") 
				nb = getBit(inb[1], 2)
				rb = getBit(inb[1], 3)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("YSw29") 
				nb = getBit(inb[1], 4)
				rb = getBit(inb[1], 5)
				ip.SetTOState(nb, rb)
				ip = self.rr.GetInput("Y30") 
				ip.SetValue(getBit(inb[1], 6))   #detection
				ip = self.rr.GetInput("YOSKL4")  # KAOS1
				ip.SetValue(getBit(inb[1], 7)) 
	
				ip = self.rr.GetInput("Y53") 
				ip.SetValue(getBit(inb[2], 0))
				ip = self.rr.GetInput("Y52") 
				ip.SetValue(getBit(inb[2], 1))
				ip = self.rr.GetInput("Y51") 
				ip.SetValue(getBit(inb[2], 2))
				ip = self.rr.GetInput("Y50") 
				ip.SetValue(getBit(inb[2], 3))
				ip = self.rr.GetInput("YOSKL2")   #KAOS3
				ip.SetValue(getBit(inb[2], 4))
				ip = self.rr.GetInput("YOSKL1")   #KAOS4
				ip.SetValue(getBit(inb[2], 5))
				ip = self.rr.GetInput("YOSKL3")   #KAOS2
				ip.SetValue(getBit(inb[2], 6))
				ip = self.rr.GetInput("Y10") 
				ip.SetValue(getBit(inb[2], 7))
				
			else:
				logging.error("Kale: Failed read")
				itext = None

		if self.sendIO:
			self.rr.ShowText("Kale", KALE, otext, itext, 2, 5)

		# Yard-----------------------------------------------------------------------
		outbc = 6
		outb = [0 for _ in range(outbc)]
		sigL2 = self.sigLever["Y2"]
		outb[0] = setBit(outb[0], 0, 1 if sigL2 == "L" else 0)       # Signal Indicators
		outb[0] = setBit(outb[0], 1, 1 if sigL2 == "N" else 0)
		outb[0] = setBit(outb[0], 2, 1 if sigL2 == "R" else 0)
		sigL4 = self.sigLever["Y4"]
		outb[0] = setBit(outb[0], 3, 1 if sigL4 == "L" else 0)    
		outb[0] = setBit(outb[0], 4, 1 if sigL4 == "N" else 0)
		outb[0] = setBit(outb[0], 5, 1 if sigL4 == "R" else 0)
		sigL8 = self.sigLever["Y8"]
		outb[0] = setBit(outb[0], 6, 1 if sigL8 == "L" else 0) 
		outb[0] = setBit(outb[0], 7, 1 if sigL8 == "N" else 0)

		outb[1] = setBit(outb[1], 0, 1 if sigL8 == "R" else 0)
		sigL10 = self.sigLever["Y10"]
		outb[1] = setBit(outb[1], 1, 1 if sigL10 == "L" else 0)    
		outb[1] = setBit(outb[1], 2, 1 if sigL10 == "N" else 0)
		outb[1] = setBit(outb[1], 3, 1 if sigL10 == "R" else 0)
		sigL22 = self.sigLever["Y22"]
		outb[1] = setBit(outb[1], 4, 1 if sigL22 == "L" else 0)    
		outb[1] = setBit(outb[1], 5, 1 if sigL22 == "N" else 0)
		outb[1] = setBit(outb[1], 6, 1 if sigL22 == "R" else 0)
		sigL24 = self.sigLever["Y24"]
		outb[1] = setBit(outb[1], 7, 1 if sigL24 == "L" else 0)    

		outb[2] = setBit(outb[2], 0, 1 if sigL24 == "N" else 0)
		sigL26 = self.sigLever["Y26"]
		outb[2] = setBit(outb[2], 1, 1 if sigL26== "L" else 0)    
		outb[2] = setBit(outb[2], 2, 1 if sigL26 == "N" else 0)
		outb[2] = setBit(outb[2], 3, 1 if sigL26 == "R" else 0)
		sigL34 = self.sigLever["Y34"]
		outb[2] = setBit(outb[2], 4, 1 if sigL34== "L" else 0)    
		outb[2] = setBit(outb[2], 5, 1 if sigL34 == "N" else 0)
		outb[2] = setBit(outb[2], 6, 1 if sigL34 == "R" else 0)
		asp = self.rr.GetOutput("Y34LA").GetAspectBits()
		outb[2] = setBit(outb[2], 7, asp[0])

		asp = self.rr.GetOutput("Y34LB").GetAspectBits()
		outb[3] = setBit(outb[3], 0, asp[0])
		asp = self.rr.GetOutput("Y34R").GetAspectBits()
		outb[3] = setBit(outb[3], 1, asp[0])
		outb[3] = setBit(outb[3], 2, asp[1])
		outb[3] = setBit(outb[3], 3, asp[2])
		outb[3] = setBit(outb[3], 4, self.rr.GetInput("CBKale").GetInvertedValue())     #Circuit breakers
		outb[3] = setBit(outb[3], 5, self.rr.GetInput("CBEastEndJct").GetInvertedValue())
		outb[3] = setBit(outb[3], 6, self.rr.GetInput("CBCornellJct").GetInvertedValue())
		outb[3] = setBit(outb[3], 7, self.rr.GetInput("CBEngineYard").GetInvertedValue())

		outb[4] = setBit(outb[4], 0, self.rr.GetInput("CBWaterman").GetInvertedValue())
		outb[4] = setBit(outb[4], 1, self.rr.GetInput("L20").GetValue())  # adjacent block indicators
		outb[4] = setBit(outb[4], 2, self.rr.GetInput("P50").GetValue())
		outb[4] = setBit(outb[4], 3, self.rr.GetOutput("YSw1").GetLock())  # Switch Locks
		outb[4] = setBit(outb[4], 4, self.rr.GetOutput("YSw3").GetLock())  
		outb[4] = setBit(outb[4], 5, self.rr.GetOutput("YSw7").GetLock()) 
		outb[4] = setBit(outb[4], 6, self.rr.GetOutput("YSw9").GetLock()) 
		outb[4] = setBit(outb[4], 7, self.rr.GetOutput("YSw17").GetLock())  

		outb[5] = setBit(outb[5], 0, self.rr.GetOutput("YSw19").GetLock())
		outb[5] = setBit(outb[5], 1, self.rr.GetOutput("YSw21").GetLock())
		outb[5] = setBit(outb[5], 2, self.rr.GetOutput("YSw23").GetLock())
		outb[5] = setBit(outb[5], 3, self.rr.GetOutput("YSw25").GetLock())
		outb[5] = setBit(outb[5], 4, self.rr.GetOutput("YSw29").GetLock())
		outb[5] = setBit(outb[5], 5, self.rr.GetOutput("YSw33").GetLock())

		otext = formatOText(outb, outbc)
		logging.debug("Yard: Output bytes: %s" % otext)

		inbc = outbc			
		if self.settings.simulation:
			itext = None
		else:
			inb = self.rrBus.sendRecv(YARD, outb, outbc)

			if self.AcceptResponse(inb, inbc, YARD):
				itext = formatIText(inb, inbc)
				logging.debug("Yard: Input Bytes: %s" % itext)
	
				ip = self.rr.GetInput("YSw33")  # Switch positions
				nb = getBit(inb[0], 0)
				rb = getBit(inb[0], 1)
				ip.SetTOState(nb, rb)
	
				if optControl == 0:  # Control by yard
					lvrR = getBit(inb[0], 2)       # signal levers
					lvrCallOn = getBit(inb[0], 3)
					lvrL = getBit(inb[0], 4)
					self.rr.GetInput("Y2.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[0], 5)
					lvrCallOn = getBit(inb[0], 6)
					lvrL = getBit(inb[0], 7)
					self.rr.GetInput("Y4.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
	
					lvrR = getBit(inb[1], 0)
					lvrCallOn = getBit(inb[1], 1)
					lvrL = getBit(inb[1], 2)
					self.rr.GetInput("Y8.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[1], 3)
					lvrCallOn = getBit(inb[1], 4)
					lvrL = getBit(inb[1], 5)
					self.rr.GetInput("Y10.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[1], 6)
					lvrCallOn = getBit(inb[1], 7)
	
					lvrL = getBit(inb[2], 0)
					self.rr.GetInput("Y22.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrCallOn = getBit(inb[2], 1)
					lvrL = getBit(inb[2], 2)
					self.rr.GetInput("Y24.lvr").SetState(leverState(lvrL, lvrCallOn, 0))
					lvrR = getBit(inb[2], 3)
					lvrCallOn = getBit(inb[2], 4)
					lvrL = getBit(inb[2], 5)
					self.rr.GetInput("Y26.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					lvrR = getBit(inb[2], 6)
					lvrCallOn = getBit(inb[2], 7)
	
					lvrL = getBit(inb[3], 0)
					self.rr.GetInput("Y34.lvr").SetState(leverState(lvrL, lvrCallOn, lvrR))
					self.rr.GetInput("yrelease").SetState(getBit(inb[3], 1))  # Y Release switch
					self.rr.GetInput("wos1norm").SetState(getBit(inb[3], 2))  # WOS1 Norm
	
				self.rr.GetInput("Y81W").SetValue(getBit(inb[3], 3))
				self.rr.GetInput("Y82W").SetValue(getBit(inb[3], 4)) 
				self.rr.GetInput("Y83W").SetValue(getBit(inb[3], 5)) 
				self.rr.GetInput("Y84W").SetValue(getBit(inb[3], 6)) 
				self.rr.GetInput("Y81E").SetValue(getBit(inb[3], 7)) 
	
				self.rr.GetInput("Y82E").SetValue(getBit(inb[4], 0)) 
				self.rr.GetInput("Y83E").SetValue(getBit(inb[4], 1)) 
				self.rr.GetInput("Y84E").SetValue(getBit(inb[4], 2))  
				self.rr.GetInput("Y70").SetValue(getBit(inb[4], 3))   # Waterman detection
				self.rr.GetInput("YOSWYW").SetValue(getBit(inb[4], 4))  # WOS1
				# bit 5 is bad
				self.rr.GetInput("Y82").SetValue(getBit(inb[4], 6))  
				self.rr.GetInput("Y83").SetValue(getBit(inb[4], 7))  
	
				self.rr.GetInput("Y84").SetValue(getBit(inb[5], 0))  
				self.rr.GetInput("YOSWYE").SetValue(getBit(inb[5], 1))  # WOS2
				self.rr.GetInput("Y87").SetValue(getBit(inb[5], 2))  
				self.rr.GetInput("Y81").SetValue(getBit(inb[5], 3))  
	
			else:
				logging.error("Yard: Failed read")
				itext = None
	
		if self.sendIO:
			self.rr.ShowText("Yard", YARD, otext, itext, 3, 5)

		# Yard and Waterman switch control by dispatcher
		outbc = 5
		outb = [0 for _ in range(outbc)]
		op = self.rr.GetOutput("YSw1").GetOutPulse()
		outb[0] = setBit(outb[0], 0, 1 if op > 0 else 0)                   # switches
		outb[0] = setBit(outb[0], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw3").GetOutPulse()
		outb[0] = setBit(outb[0], 2, 1 if op > 0 else 0)
		outb[0] = setBit(outb[0], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw7").GetOutPulse()
		outb[0] = setBit(outb[0], 4, 1 if op > 0 else 0)
		outb[0] = setBit(outb[0], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw9").GetOutPulse()
		outb[0] = setBit(outb[0], 6, 1 if op > 0 else 0)
		outb[0] = setBit(outb[0], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("YSw11").GetOutPulse()
		outb[1] = setBit(outb[1], 0, 1 if op > 0 else 0)                   # switches
		outb[1] = setBit(outb[1], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw17").GetOutPulse()
		outb[1] = setBit(outb[1], 2, 1 if op > 0 else 0)
		outb[1] = setBit(outb[1], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw19").GetOutPulse()
		outb[1] = setBit(outb[1], 4, 1 if op > 0 else 0)
		outb[1] = setBit(outb[1], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw21").GetOutPulse()
		outb[1] = setBit(outb[1], 6, 1 if op > 0 else 0)
		outb[1] = setBit(outb[1], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("YSw23").GetOutPulse()
		outb[2] = setBit(outb[2], 0, 1 if op > 0 else 0)                   # switches
		outb[2] = setBit(outb[2], 1, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw25").GetOutPulse()
		outb[2] = setBit(outb[2], 2, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 3, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw27").GetOutPulse()
		outb[2] = setBit(outb[2], 4, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 5, 1 if op < 0 else 0)
		op = self.rr.GetOutput("YSw29").GetOutPulse()
		outb[2] = setBit(outb[2], 6, 1 if op > 0 else 0)
		outb[2] = setBit(outb[2], 7, 1 if op < 0 else 0)

		op = self.rr.GetOutput("YSw33").GetOutPulse()
		outb[3] = setBit(outb[3], 0, 1 if op > 0 else 0)
		outb[3] = setBit(outb[3], 1, 1 if op < 0 else 0)
		# 	YSWOut[3].bit.b2 = ;
		# 	YSWOut[3].bit.b3 = ;
		# 	YSWOut[3].bit.b4 = ;
		# 	YSWOut[3].bit.b5 = ;
		# 	YSWOut[3].bit.b6 = ;
		# 	YSWOut[3].bit.b7 = ;

		op = self.rr.GetOutput("YWWB1").GetOutPulse()  # Y81W
		outb[4] = setBit(outb[4], 0, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWWB2").GetOutPulse()  # Y82W
		outb[4] = setBit(outb[4], 1, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWWB3").GetOutPulse()  # Y83W
		outb[4] = setBit(outb[4], 2, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWWB4").GetOutPulse()  # Y84W
		outb[4] = setBit(outb[4], 3, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWEB1").GetOutPulse()  # Y81E
		outb[4] = setBit(outb[4], 4, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWEB2").GetOutPulse()  # Y82E
		outb[4] = setBit(outb[4], 5, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWEB3").GetOutPulse()  # Y83E
		outb[4] = setBit(outb[4], 6, 1 if op > 0 else 0)
		op = self.rr.GetOutput("YWEB4").GetOutPulse()  # Y84E
		outb[4] = setBit(outb[4], 7, 1 if op > 0 else 0)

		otext = formatOText(outb, outbc)
		logging.debug("YardSW: Output bytes: %s" % otext)
			
		if not self.settings.simulation:
			inb = self.rrBus.sendRecv(YARDSW, outb, outbc)

		if self.sendIO:
			self.rr.ShowText("YdSw", YARDSW, otext, "- no inputs from this node -", 4, 5)

		# No inputs from this node
