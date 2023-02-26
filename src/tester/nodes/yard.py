from tester.node import Node

class Yard(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["Y2 L", "Signal Ind", 0],
				["Y2 N", "", 0],
				["Y2 R", "", 0],
				["Y4 L", "", 0],
				["Y4 N", "", 0],
				["Y4 R", "", 0],
				["Y8 L", "", 0],
				["Y8 N", "", 0]
			],
			[
				["Y8 RL", "Signal Ind", 0],
				["Y10 L", "", 0],
				["Y10 N", "", 0],
				["Y10 R", "", 0],
				["Y22 L", "", 0],
				["Y22 N", "", 0],
				["Y22 R", "", 0],
				["Y24 L", "", 0]
			],
			[
				["Y24 N", "Signal Ind", 0],
				["Y26 L", "", 0],
				["Y26 N", "", 0],
				["Y26 R", "", 0],
				["Y34 L", "", 0],
				["Y34 N", "", 0],
				["Y34 R", "", 0],
				["Y34LA", "Signal", 0]
			],
			[
				["Y34LB", "Signal", 0],
				["Y34R 0", "", 0],
				["Y34R 1", "", 0],
				["Y34R 2", "", 0],
				["Kale", "Breaker Ind", 0],
				["EastJct", "", 0],
				["Cornell", "", 0],
				["EngYard", "", 0]
			],
			[
				["Waterman", "Breaker Ind", 0],
				["L20", "Block Ind", 0],
				["P50", "", 0],
				["YSw1", "Switch Lock", 0],
				["YSw3", "", 0],
				["YSw7", "", 0],
				["YSw9", "", 0],
				["YSw17", "", 0]
			],
			[
				["YSw19", "Switch Lock", 0],
				["YSw21", "", 0],
				["YSw23", "", 0],
				["YSw25", "", 0],
				["YSw29", "", 0],
				["YSw33", "", 0]
			]
		]
		
		self.inputs = [
			[
				["YSw33 N", "Switch"],
				["YSw33 R", ""],
				["L2 R", "Switch Lever"],
				["L2 CallOn", ""],
				["L2 L", ""],
				["L4 R", ""],
				["L4 CallOn", ""],
				["L4 L", ""]
			],

			[
				["L8 R", "Switch Lever"],
				["L8 CallOn", ""],
				["L8 L", ""],
				["L10 R", ""],
				["L10 CallOn", ""],
				["L10 L", ""],
				["L22 R", ""],
				["L22 CallOn", ""]
			],

			[
				["L22 L", "Switch Lever"],
				["L24 CallOn", ""],
				["L24 L", ""],
				["L26 R", ""],
				["L26 CallOn", ""],
				["L26 L", ""],
				["L34 R", ""],
				["L34 CallOn", ""]
			],

			[
				["L24 L", "Switch Lever"],
				["Y Release", ""],
				["WOS1 Norm", ""],
				["Y81W", "Switch Button"],
				["Y82W", ""],
				["Y83W", ""],
				["Y84W", ""],
				["Y81E", ""]
			],

			[
				["Y82E", "Switch Button"],
				["Y83E", ""],
				["W84E", ""],
				["Y70", "Block Detection"],
				["YOSWYW", ""],
				["unused", ""],
				["Y82", ""],
				["Y83", ""]
			],

			[
				["Y84", "Block Detection"],
				["YOSWYE", ""],
				["Y87", ""],
				["Y81", ""]
			]
		]

		
		self.AddWidgets()

