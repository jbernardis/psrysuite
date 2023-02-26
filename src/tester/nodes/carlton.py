from tester.node import Node

class Carlton(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["L16R 0", "Signal", 0],
				["L16R 1", "", 0],
				["L16R 2", "", 0],
				["L18R", "", 0],
				["L14R 0", "", 0],
				["L14R 1", "", 0],
				["L14R 2", "", 0],
				["L14L", "", 0]
			],
		
			[
				["L18L 0", "Signal", 0],
				["L18L 1", "", 0],
				["L18L 2", "", 0],
				["LSw11", "Hand Switch", 0],
				["LSw13", "", 0],
				["LSw15 N", "Switch", Node.pulsed],
				["LSw15 R", "", Node.pulsed],
				["LSw17 N", "", Node.pulsed]
			],
			
			[
				["LSw17 R", "Switch", Node.pulsed],
				["L31.Rel", "Stop Relay", 0],
				["D10.Rel", "", 0],
				["S21E 0", "Signal", 0],
				["S21E 1", "", 0],
				["S21E 2", "", 0],
				["N20W 0", "", 0],
				["N21W 1", "", 0]
			],
			
			[
				["N20W 2", "Signal", 0],
				["", "", Node.unused],
				["", "", Node.unused],
				["", "", Node.unused],
				["S11E 0", "Signal", 0],
				["S11E 1", "", 0],
				["S11E 2", "", 0],
				["N10W 0", "", 0]
			],
			
			[
				["N10W 1", "Signal", 0],
				["N10W 2", "", 0],
				["S21.Rel", "Stop Relay", 0],
				["N25.Rel", "", 0]
			]
		]
		
		self.inputs = [
			[
				["LSw11 N", "Switch"],
				["LSw11 R", ""],
				["LSw13 N", ""],
				["LSw13 R", ""],
				["LSw15 N", ""],
				["LSw15 R", ""],
				["LSw17 N", ""],
				["LSw17 R", ""]
			],

			[
				["L31", "Block Detection"],
				["L31.E", ""],
				["LOSCAW", ""],
				["LOSCAM", ""],
				["LOSCAE", ""],
				["D10.W", ""],
				["D10", ""]
			],

			[
				["S21.W", "Block Detection"],
				["S21", ""],
				["S21.E", ""],
				["N25.W", ""],
				["N25", ""],
				["N25.E", ""]
			]
		]
		
		self.AddWidgets()

