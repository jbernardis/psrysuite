from tester.node import Node

class Cliveden(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["C14R 0", "Signal", 0],
				["C14R 1", "", 0],
				["C14R 2", "", 0],
				["C14LA 0", "", 0],
				["C14LA 1", "", 0],
				["C14LA 2", "", 0],
				["C14LB 0", "", 0],
				["C14LB 1", "", 0]
			],
		
			[
				["C14LB 2", "Signal", 0],
				["C12R 0", "", 0],
				["C12R 1", "", 0],
				["C12R 2", "", 0],
				["C10R 0", "", 0],
				["C10R 1", "", 0],
				["C10R 2", "", 0],
				["", "", Node.unused]
			],
			
			[
				["C12L 0", "Signal", 0],
				["C12L 1", "", 0],
				["C12L 2", "", 0],
				["C10L 0", "", 0],
				["C10L 1", "", 0],
				["C10L 2", "", 0],
				["CSw11", "Hand Switch", 0],
				["CSw13 N", "Switch", Node.pulsed]
			],
			
			[
				["CSw13 R", "Signal", Node.pulsed],
				["CSw9 N", "Switch", Node.pulsed],
				["", "", Node.unused],
				["C13.Rel", "Stop Relay", 0],
				["C23.Rel", "", 0],
				["C12.Rel", "", 0],
				["CSw9 R", "Switch", Node.pulsed],
				["", "", Node.unused]
			]
		]
		
		self.inputs = [
			[
				["CSw13 N", "Switch"],
				["CSw13 R", ""],
				["CSw11 N", ""],
				["CSw11 R", ""],
				["CSw9 N", ""],
				["CSw9 R", ""],
				["", ""],
				["", ""]
			],

			[
				["C13.W", "Block Detection"],
				["C13", ""],
				["C13.E", ""],
				["COSCLW", ""],
				["C12.W", ""],
				["C12", ""],
				["C23.W", ""],
				["C23", ""]
			],

			[
				["COSCLEW", "Block Detection"],
				["COSCLEE", ""],
				["C22", ""],
				["", ""],
				["Green Mtn Stn", "Breaker"],
				["Sheffield A", ""],
				["Green Mtn Yd", ""],
				["Hyde Jct", ""]
			],

			[
				["Hyde West", "Breaker"],
				["Hyde East", ""],
				["Southport Jct", ""],
				["Carlton", ""],
				["Sheffield B", ""]
			]
		]
		
		self.AddWidgets()

