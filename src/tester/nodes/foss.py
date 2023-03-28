from tester.node import Node

class Foss(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["D10R 0", "Signal", 0],
				["D10R 1", "", 0],
				["D10R 2", "", 0],
				["D12R 0", "", 0],
				["D12R 1", "", 0],
				["D12R 2", "", 0]
			],
		
			[
				["D10L 0", "Signal", 0],
				["D10L 1", "", 0],
				["D10L 2", "", 0],
				["D12L 0", "", 0],
				["D12L 1", "", 0],
				["D12L 2", "", 0],
				["D21.Rel", "Stop Relay", 0],
				["S10.Rel", "Block Ind", 0]
			],
			
			[
				["", "", Node.disabled],
				["R10.Rel", "Stop Relay", 0],
				["Rocky Hill X", "Crossing Gate", 0],
				["R10W 0", "Signal", 0],
				["R10W 1", "", 0],
				["R10W 2", "", 0]
			]
		]
		
		self.inputs = [
			[
				["D21.W", "Block Detection"],
				["D21A", ""],
				["D21B", ""],
				["D21.E", ""],
				["DOSFOW", ""],
				["DOSFOE", ""],
				["S10.W", ""],
				["S10A", ""]
			],

			[
				["S10B", "Block Detection"],
				["S10C", ""],
				["S10.E", ""],
				["R10.W", ""],
				["R10A", ""],
				["R10B", ""],
				["R10C", ""],
				["R11", ""]
			],

			[
				["R12", "Block Detection"]
			]
		]
		
		self.AddWidgets()

