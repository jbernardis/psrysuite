from tester.node import Node

class Krulish(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["K8R 0", "Signal", 0],
				["K8R 1", "", 0],
				["K8R 2", "", 0],
				["K4R 0", "", 0],
				["K4R 1", "", 0],
				["K4R 2", "", 0],
				["K2R 0", "", 0],
				["K2R 1", "", 0]
			],
		
			[
				["K2R 2", "Signal", 0],
				["K2L 0", "", 0],
				["K2L 1", "", 0],
				["K2L 2", "", 0],
				["K8LA", "", 0],
				["K8LB 0", "", 0],
				["K8LB 1", "", 0],
				["K8LB 2", "", 0]
			],
			
			[
				["Krulish Yd", "Breaker Ind", 0],
				["N10.Rel", "Stop Relay", 0],
				["N20.Rel", "", 0],
				["N11.Rel", "", 0]
			]
		]
		
		self.inputs = [
			[
				["KSw1 N", "Switch"],
				["KSw1 R", ""],
				["KSw3 N", ""],
				["KSw3 R", ""],
				["KSw5 N", ""],
				["KSw5 R", ""],
				["KSw7 N", ""],
				["KSw7 R", ""]
			],

			[
				["", ""],
				["", ""],
				["N10.W", "Block Detection"],
				["N10", ""],
				["N10.E", ""],
				["N20.W", ""],
				["N20", ""],
				["N20.E", ""]
			],

			[
				["KOSW", "Block Detection"],
				["KOSM", ""],
				["KOSE", ""],
				["N11.W", ""],
				["N11", ""],
				["N11.E", ""]
			]
		]
		
		self.AddWidgets()

