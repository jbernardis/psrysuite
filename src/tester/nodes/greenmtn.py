from tester.node import Node

class GreenMtn(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["C2RB 0", "Signal", 0],
				["C2RB 1", "", 0],
				["C2RB 2", "", 0],
				["C2RD", "", 0],
				["C2L 0", "", 0],
				["C2L 1", "", 0],
				["C2L 2", "", 0],
				["C2RA 0", "", 0]
			],
		
			[
				["C2RA 1", "Signal", 0],
				["C2RC", "", 0],
				["C4LA 0", "", 0],
				["C4LA 1", "", 0],
				["C4LB 0", "", 0],
				["C4LB 1", "", 0],
				["C4LC 0", "", 0],
				["C4LC 1", "", 0]
			],
			
			[
				["C4LC 2", "Signal", 0],
				["C4LD", "", 0],
				["C4R 0", "", 0],
				["C4R 1", "", 0],
				["C4R 2", "", 0],
				["CSw3", "Hand Switch", 0]
			]
		]
		
		self.inputs = [
			[
				["CC30E", "Route"],
				["CC10E", ""],
				["CG10E", ""],
				["CG12E", ""],
				["CC31W", ""],
				["CC30W", ""],
				["CC10W", ""],
				["CG21W", ""]
			],

			[
				["CSw3 N", "Switch"],
				["CSw3 R", ""],
				["C11", "Block Detection"],
				["COSGMW", ""],
				["C10", ""],
				["C30", ""],
				["C31", ""],
				["COSGME", ""]
			],

			[
				["C20", "Block Detection"]
			]
		]
		
		self.AddWidgets()

