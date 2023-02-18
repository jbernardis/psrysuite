from tester.node import Node

class Cornell(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["Y4R 0", "Signal", 0],
				["Y4R 1", "", 0],
				["Y4R 2", "", 0],
				["Y2R", "", 0],
				["Y2L 0", "", 0],
				["Y2L 1", "", 0],
				["Y2L 2", "", 0],
				["Y4LA 0", "", 0]
			],
		
			[
				["Y4LA 1", "Signal", 0],
				["Y4LA 2", "", 0],
				["Y4LB 0", "", 0],
				["Y4LB 1", "", 0],
				["Y4LB 2", "", 0]
			]
		]
		
		self.inputs = [
			[
				["YSw1 N", "Switch"],
				["YSw1 R", ""],
				["YSw3 N", ""],
				["YSw3 R", ""],
				["Y21.W", "Block Detection"],
				["Y21", ""],
				["Y21.E", ""],
				["YOSCJW", ""]
			],

			[
				["YOSCJE", "Block Detection"],
				["L10.W", ""],
				["L10", ""]
			]
		]

		
		self.AddWidgets()

