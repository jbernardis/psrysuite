from tester.node import Node

class NassauW(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["N14LC", "Signal", 0],
				["N14LB", "", 0],
				["N20R", "", 0],
				["N20L", "", 0],
				["N14LA 0", "", 0],
				["C14LA 1", "", 0],
				["N16L 0", "", 0],
				["N16L 1", "", 0]
			],
		
			[
				["N18LB 0", "Signal", 0],
				["N18LB 1", "", 0],
				["N18LA 0", "", 0],
				["N18LA 1", "", 0],
				["N16R 0", "", 0],
				["N16R 1", "", 0],
				["N14R 0", "", 0],
				["", "", Node.unused]
			],
		
			[
				["N18R", "Signal", 0],
				["N11W 0", "", 0],
				["N11W 1", "", 0],
				["N11W 2", "", 0],
				["N21W 0", "", 0],
				["N21W 1", "", 0],
				["N21W 2", "", 0],
				["S11", "Block Ind", 0]
			],
		
			[
				["R20", "Block Ind", 0],
				["B20", "", 0],
				["Fleet", "Fleet Ind", 0],
				["~Fleet", "", 0],
				["N14 L", "Sig Lvr", 0],
				["N14 N", "", 0],
				["N14 R", "", 0],
				["N16 L", "", 0]
			],
		
			[
				["N16 N", "Sig Lvr", 0],
				["N16 R", "", 0],
				["N18 L", "", 0],
				["N18 N", "", 0],
				["N18 R", "", 0],
				["N20 L", "", 0],
				["N20 N", "", 0],
				["N20 R", "", 0]
			],
		
			[
				["KSw1 N", "Switch", Node.pulsed],
				["KSw1 R", "", Node.pulsed],
				["KSw3 N", "", Node.pulsed],
				["KSw3 R", "", Node.pulsed],
				["KSw5 N", "", Node.pulsed],
				["KSw5 R", "", Node.pulsed],
				["KSw7 N", "", Node.pulsed],
				["KSw7 R", "", Node.pulsed]
			],
		
			[
				["CBKrulish", "Breaker Ind", 0],
				["CBNassauW", "", 0],
				["CBNassauE", "", 0],
				["CBSptJct", "", 0],
				["CBWilson", "", 0],
				["CBThomas", "", 0],
				["NSWL 0", "Switch Lock", 0],
				["NSWL 1", "", 0]
			],
		
			[
				["NSWL 2", "Switch Lock", 0],
				["NSWL 3", "", 0],
				["S21.Rel", "Stop Relay", 0],
				["N14R 1", "Signal", 0],
				["N14LD", "", 0],
				["N24RD", "", 0]
			]		
		]
		
		self.inputs = [
			[
				["NSw19 N", "Switch"],
				["NSw19 R", ""],
				["NSw21 N", ""],
				["NSw21 R", ""],
				["NSw23 N", ""],
				["NSw23 R", ""],
				["NSw25 N", ""],
				["NSw25 R", ""]
			],

			[
				["NSw27 N", "Switch"],
				["NSw27 R", ""],
				["NSw29 N", ""],
				["NSw29 R", ""],
				["NSw31 N", ""],
				["NSw31 R", ""],
				["NSw33 N", ""],
				["NSw33 R", ""]
			],

			[
				["N21.W", "Block Detection"],
				["N21", ""],
				["N21.E", ""],
				["NWOSTY", ""],
				["NWOSCY", ""],
				["NWOSW", ""],
				["NWOS3", ""],
				["N32", ""]
			],

			[
				["N31", "Block Detection"],
				["N12", ""],
				["Release", "Release"],
				["Fleet", "Fleet"],
				["N14 L", "Sig Lvr"],
				["N14 CO", ""],
				["N14 R", ""],
				["N16 L", ""]
			],

			[
				["N16 CO", "Sig Lvr"],
				["N16 R", ""],
				["N18 L", ""],
				["N18 CO", ""],
				["N18 R", ""],
				["N20 L", ""],
				["N20 CO", ""],
				["N20 R", ""]
			],

			[
				["N24 L", "Sig Lvr"],
				["N24 CO", ""],
				["N24 R", ""],
				["N26 L", ""],
				["N26 CO", ""],
				["N26 R", ""],
				["N28 L", ""],
				["N28 CO", ""]
			],

			[
				["N28 R", "Sig Lvr"],
				["CBKrulishYd", "Breaker"],
				["CBThomas", ""],
				["CBWilson", ""],
				["CBKrulish", ""],
				["CBNassauW", ""],
				["CBNassauE", ""],
				["CBFoss", ""]
			],

			[
				["CBDell", "Breaker"],
				["NSw60A", "Coach Yard Route"],
				["NSw60B", ""],
				["NSw60C", ""],
				["NSw60D", ""],
				["NSw35 N", "Switch"],
				["NSw35 R", ""]
			]
		]
		
		self.AddWidgets()

