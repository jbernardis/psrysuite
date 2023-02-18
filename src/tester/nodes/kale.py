from tester.node import Node

class Kale(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["Y22R", "Signal", 0],
				["Y26RA", "", 0],
				["Y26RB", "", 0],
				["Y26RC", "", 0],
				["Y24RA", "", 0],
				["Y24RB", "", 0],
				["Y20H", "Indicator", 0],
				["Y20D", "", 0]
			],
		
			[
				["Y26L", "Signal", 0],
				["Y22L 0", "", 0],
				["Y22L 1", "", 0]
			]
		]
		
		self.inputs = [
			[
				["YSw17 N", "Switch"],
				["YSw17 R", ""],
				["YSw19 N", ""],
				["YSw19 R", ""],
				["YSw21 N", ""],
				["YSw21 R", ""],
				["YSw23 N", ""],
				["YSw23 R", ""]
			],

			[
				["YSw25 N", "Switch"],
				["YSw25 R", ""],
				["YSw27 N", ""],
				["YSw27 R", ""],
				["YSw29 N", ""],
				["YSw28 R", ""],
				["Y30", "Block Detection"],
				["YOSKL4", ""]
			],

			[
				["Y53", "Block Detection"],
				["Y52", ""],
				["Y51", ""],
				["Y50", ""],
				["YOSKL2", ""],
				["YOSKL1", ""],
				["YOSKL3", ""],
				["Y10", ""]
			]
		]

		
		self.AddWidgets()

