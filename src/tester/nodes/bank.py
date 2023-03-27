from tester.node import Node

class Bank(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["C22R", "Signal", 0],
				["C24R 0", "", 0],
				["C24R 1", "", 0],
				["C24R 2", "", 0],
				["C24L 0", "", 0],
				["C24L 1", "", 0],
				["C24L 2", "", 0],
				["C22L 0", "", 0]
			],
		
			[
				["C22L 1", "Signal", 0],
				["C22L 2", "", 0],
				["C18RA", "", 0],
				["C18RB 0", "", 0],
				["C18RB 1", "", 0],
				["C18RB 2", "", 0],
				["C18L 0", "", 0],
				["C18L 1", "", 0]
			],
		
			[
				["C18L 2", "Signal", 0],
				["B10", "Block Ind", 0],
				["C13", "", 0],
				["CSw21a/b", "Hand Switch", 0],
				["CSw19", "", 0],
				["CSw23 N", "Switch", Node.pulsed],
				["CSw23 R", "", Node.pulsed],
				["CSw17 N", "", Node.pulsed]
			],
		
			[
				["CSw17 R", "Switch", Node.pulsed],
				["S20.REL", "Stop Relay", 0],
				["B11.REL", "", 0],
				["B21.REL", "", 0],
				["CBBank", "Breaker Ind", 0],
				["C24L", "Signal Ind", 0]
			]
		]
		
		self.inputs = [
			[
				["CSw23 N", "Switch"],
				["CSw23 R", ""],
				["CSw21a N", ""],
				["CSw21a R", ""],
				["CSw21b N", ""],
				["CSw21b R", ""],
				["CSw19 N", ""],
				["CSw19 R", ""]
			],

			[
				["CSw17 N", "Switch"],
				["CSw17 R", ""],
				["B20", "Block Detection"],
				["B20.E", ""],
				["BOSWW", ""],
				["BOSWE", ""],
				["B11.W", ""],
				["B11", ""]
			],

			[
				["B21.W", "Block Detection"],
				["B21", ""],
				["B21.E", ""],
				["BOSE", ""],
				["CBBank", "Breaker"],
				["CBKale", ""],
				["CBWaterman", ""],
				["CBEngineYard", ""]
			],

			[
				["CBEastEndJct", "Breaker"],
				["CBShore", ""],
				["CBRockyHill", ""],
				["CBHarpersFerry", ""],
				["CBBlockY30", ""],
				["CBBlockY81", ""]
			]
		]
		
		self.AddWidgets()

