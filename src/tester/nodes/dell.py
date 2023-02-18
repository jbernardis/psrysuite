from tester.node import Node

class Dell(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["D4RA 0", "Signal", 0],
				["D4RA 1", "", 0],
				["D4RA 2", "", 0],
				["D4RB 0", "", 0],
				["D4RB 1", "", 0],
				["D4RB 2", "", 0],
				["D6RA", "", 0],
				["D6RB", "", 0]
			],
		
			[
				["D4L 0", "Signal", 0],
				["D4L 1", "", 0],
				["D4L 2", "", 0],
				["D6L 0", "", 0],
				["D6L 1", "", 0],
				["D6L 2", "", 0],
				["Laporte X", "Crossing Gate", 0],
				["H13", "Block Ind", 0]
			],
			
			[
				["D10", "Block Ind", 0],
				["S20", "", 0],
				["DSw9", "Hand Switch", 0],
				["DSw1 N", "Switch", Node.pulsed],
				["DSw1 R", "", Node.pulsed],
				["DSw3 N", "", Node.pulsed],
				["DSw3 R", "", Node.pulsed],
				["DSw5 N", "", Node.pulsed]
			],
			
			[
				["DSw5 R", "Switch", Node.pulsed],
				["DSw7 N", "", Node.pulsed],
				["DSw7 R", "", Node.pulsed],
				["DSw11 N", "", Node.pulsed],
				["DSw11 R", "", Node.pulsed],
				["D20.Rel", "Stop Relay", 0],
				["H23.Rel", "", 0],
				["D11.rel", "", 0]
			]
		]
		
		self.inputs = [
			[
				["DSw1 N", "Switch"],
				["DSw1 R", ""],
				["DSw3 N", ""],
				["DSw3 R", ""],
				["DSw5 N", ""],
				["DSw5 R", ""],
				["DSw7 N", ""],
				["DSw7 R", ""]
			],

			[
				["DSw9 N", "Switch"],
				["DSw9 R", ""],
				["DSw11 N", ""],
				["DSw11 R", ""],
				["D20", "Block Detection"],
				["D20.E", ""],
				["H23", ""],
				["H23.E", ""]
			],

			[
				["DOSVJW", "Block Detection"],
				["DOSVJE", ""],
				["D11.W", ""],
				["D11A", ""],
				["D11B", ""],
				["D11.E", ""]
			]
		]

		
		self.AddWidgets()

