from tester.node import Node

class EastJct(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["Y10R 0", "Signal", 0],
				["Y10R 1", "", 0],
				["Y10R 2", "", 0],
				["Y8RA", "", 0],
				["Y8RB", "", 0],
				["Y8RC", "", 0],
				["Y8L 0", "", 0],
				["Y8L 1", "", 0]
			],
		
			[
				["Y8L 2", "Signal", 0],
				["Y10L 0", "", 0],
				["Y10L 1", "", 0],
				["Y10L 2", "", 0]
			]
		]
		
		self.inputs = [
			[
				["YSw7 N", "Switch"],
				["YSw7 R", ""],
				["YSw9 N", ""],
				["YSw9 R", ""],
				["YSw11 N", ""],
				["YSw11 R", ""],
				["Y20", "Block Detection"],
				["Y20.E", ""]
			],

			[
				["YOSEJW", "Block Detection"],
				["YOSEJE", ""],
				["Y11.W", ""],
				["Y11", ""]
			]
		]

		
		self.AddWidgets()

