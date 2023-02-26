from tester.node import Node

class Shore(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["S4R 0", "Signal", 0],
				["S4R 1", "", 0],
				["S4R 2", "", 0],
				["S12R 0", "", 0],
				["S12R 1", "", 0],
				["S12R 2", "", 0],
				["S4LA", "", 0],
				["S4LB 0", "", 0]
			],
		
			[
				["S4LB 1", "Signal", 0],
				["S4LB 2", "", 0],
				["S4LC 1", "", 0],
				["S4LC 1", "", 0],
				["S4LC 2", "", 0],
				["S12LA 0", "", 0],
				["S12LA 1", "", 0],
				["S12LA 2", "", 0]
			],
			
			[
				["S12LB", "Signal", 0],
				["S12LC 0", "", 0],
				["S12LC 1", "", 0],
				["S12LC 2", "", 0],
				["F10H", "", 0],
				["F10D", "", 0],
				["S8R", "", 0],
				["S8L", "", 0]
			],
			
			[
				["", "", Node.unused],
				["", "", Node.unused],
				["S10", "Block Detection", 0],
				["H20", "", 0],
				["S21", "", 0],
				["P32", "", 0],
				["Shore", "Breaker Ind", 0],
				["Harpers Ferry", "", 0]
			],
			
			[
				["SSw1", "Hand Switch", 0],
				["SSw3 N", "Switch", Node.pulsed],
				["SSw3 R", "", Node.pulsed],
				["SSw5 N", "", Node.pulsed],
				["SSw5 R", "", Node.pulsed],
				["SSw7 N", "", Node.pulsed],
				["SSw7 R", "", Node.pulsed],
				["SSw9 N", "", Node.pulsed]
			],
			
			[
				["SSw9 R", "Switch", Node.pulsed],
				["SSw11 N", "", Node.pulsed],
				["SSw11 R", "", Node.pulsed],
				["SSw13 N", "", Node.pulsed],
				["SSw13 R", "", Node.pulsed],
				["BX", "Crossing Relay", 0],
				["S20.Rel", "Stop Relay", 0],
				["S11.Rel", "", 0]
			],
			
			[
				["H30.Rel", "Stop Relay", 0],
				["H10.Rel", "", 0],
				["F10.Rel", "", 0],
				["F11.Rel", "", 0],
				["S21", "", 0],
				["CSw15", "Hand Switch", 0],
				["SXG", "Bortell Gate", 0]
			]
		]
		
		self.inputs = [
			[
				["SSw1 N", "Switch"],
				["SSw1 R", ""],
				["SSw3 N", ""],
				["SSw3 R", ""],
				["SSw5 N", ""],
				["SSw5 R", ""],
				["SSw7 N", ""],
				["SSw7 R", ""]
			],

			[
				["SSw9 N", "Switch"],
				["SSw9 R", ""],
				["SSw11 N", ""],
				["SSw11 R", ""],
				["SSw13 N", ""],
				["SSw13 R", ""],
				["S20.W", "Block Detection"],
				["S20A", ""]
			],

			[
				["S20B", "Block Detection"],
				["S20C", ""],
				["S20.E", ""],
				["SOSW", ""],
				["SOSE", ""],
				["S11.W", ""],
				["S11B", ""],
				["S11.E", ""]
			],

			[
				["H30.W", "Block Detection"],
				["H30B", ""],
				["H10.W", ""],
				["H10B", ""],
				["F10", ""],
				["F10.E", ""],
				["SOSHF", ""],
				["F11.W", ""]
			],

			[
				["F11", "Block Detection"],
				["unused", ""],
				["CSw15 N", "Switch"],
				["CSw15 R", ""],
				["S11A", "Block Detection"],
				["H30A", ""],
				["H10A", ""]
			]
		]

		
		self.AddWidgets()

