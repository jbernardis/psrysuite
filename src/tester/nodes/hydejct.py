from tester.node import Node

class HydeJct(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["S16R 0", "Signal", 0],
				["S16R 1", "", 0],
				["S16R 2", "", 0],
				["S18R 0", "", 0],
				["S18R 1", "", 0],
				["S18R 2", "", 0],
				["S20R", "", 0],
				["S16L 0", "", 0]
			],
		
			[
				["S16L 1", "Signal", 0],
				["S16L 2", "", 0],
				["S18LB", "", 0],
				["S18LA", "", 0],
				["S20L 0", "", 0],
				["S20L 1", "", 0],
				["S20L 2", "", 0],
				["SSw15 N", "Switch", Node.pulsed]
			],
				
			[
				["SSw15 R", "Switch", Node.pulsed],
				["SSw17 N", "", Node.pulsed],
				["SSw17 R", "", Node.pulsed],
				["SSw19 N", "", Node.pulsed],
				["SSw19 R", "", Node.pulsed],
				["H20.REL", "Stop Relay", 0],
				["P42.REL", "", 0],
				["H11.REL", "", 0]
			]
		]
		
		self.inputs = [
			[
				["SSw15 N", "Switch"],
				["SSw15 R", ""],
				["SSw17 N", ""],
				["SSw17 R", ""],
				["SSw19 N", ""],
				["SSw19 R", ""],
				["H20", "Block Detection"],
				["H20.E", ""]
			],

			[
				["P42.W", "Block Detection"],
				["P42", ""],
				["P42.E", ""],
				["SOSHJW", ""],
				["SOSHJM", ""],
				["SOSHJE", ""],
				["H11.W", ""],
				["H11", ""]
			]
		]
		
		self.AddWidgets()

