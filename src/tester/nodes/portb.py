from tester.node import Node

class PortB(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["PB2R 0", "Signal", 0],
				["PB2R 1", "", 0],
				["PB2R 2", "", 0],
				["PB4R 0", "", 0],
				["PB4R 1", "", 0],
				["PB4R 2", "", 0],
				["PB2L 0", "", 0],
				["PB2L 1", "", 0]
			],
		
			[
				["PB2L 2", "Signal", 0],
				["PB4L 0", "", 0],
				["PB4L 1", "", 0],
				["PB4L 2", "", 0],
				["PB12L 0", "", 0],
				["PB12L 1", "", 0],
				["PB12L 2", "", 0],
				["PB14L 0", "", 0]
			],
		
			[
				["PB14L 1", "Signal", 0],
				["PB14L 2", "", 0],
				["PB12R 0", "", 0],
				["PB12R 1", "", 0],
				["PB12R 2", "", 0],
				["PB14R 0", "", 0],
				["PB14R 1", "", 0],
				["PB14R 2", "", 0]
			],
		
			[
				["PB2 N", "Signal Ind", 0],
				["PB2 R", "", 0],
				["PB2 L", "", 0],
				["PB4 N", "", 0],
				["PB4 R", "", 0],
				["PB4 L", "", 0],
				["PBSw5", "Hand Switch", 0],
				["~PBSw5", "", 0]
			],
		
			[
				["PB12 L", "Signal Ind", 0],
				["PB12 N", "", 0],
				["PB12 R", "", 0],
				["PB14 L", "", 0],
				["PB14 N", "", 0],
				["PB14 R", "", 0],
				["PbSw15a", "Hand Switch", 0],
				["~PBSw15a", "", 0],
			],
		
			[
				["P30", "Block Ind", 0],
				["P42", "", 0],
				["P32", "Shore Signal", 0],
				["P42", "Hyde Jct Signal", 0],
				["CBSouthJct", "Breaker", 0],
				["CBCircusJct", "", 0],
				["PBSw1", "Switch Lock", 0],
				["PBSw3", "", 0]
			],
		
			[
				["PBSw5", "Switch Lock", 0],
				["PASw11", "", 0],
				["PBSw13", "", 0],
				["PASw15a", "", 0],
				["P32.REL", "Stop Relay", 0],
				["P41.REL", "", 0],
				["PBX0", "Crossing Signal", 0]
			]		
		]
		
		self.inputs = [
			[
				["PBSw1 N", "Switch"],
				["PBSw1 R", ""],
				["PBSw3 N", ""],
				["PBSw3 R", ""],
				["PBSw11 N", ""],
				["PBSw11 R", ""],
				["PBSw13 N", ""],
				["PBSw13 R", ""]
			],

			[
				["PBSw5 N", "Switch"],
				["PBSw5 R", ""],
				["PBSw15a N", ""],
				["PBSw15a R", ""],
				["PBSw15b N", ""],
				["PBSw15b R", ""],
				["P40", "Block Detection"],
				["P40.E", ""]
			],

			[
				["POSSJ2", "Block Detection"],
				["POSSJ1", ""],
				["P31.W", ""],
				["P31", ""],
				["P31.E", ""],
				["P32.W", ""],
				["P32", ""],
				["P32.E", ""]
			],

			[
				["POSCJ2", "Block Detection"],
				["POSCJ1", ""],
				["P41.W", ""],
				["P41", ""],
				["P41.E", ""],
				["PB2 L", "Sig Lvr"],
				["PB2 CO", ""],
				["PB2 R", ""]
			],

			[
				["PB4 L", "Sig Lvr"],
				["PB4 CO", ""],
				["PB4 R", ""],
				["PBSw5", "Hand Switch Lock"],
				["PA12 L", "Sig Lvr"],
				["PA12 CO", ""],
				["PA12 R", ""],
				["PA14 L", ""]
			],

			[
				["PA14 CO", "Sig Lvr"],
				["PA14 R", ""],
				["PBSw15a/b", "Hand Switch Lock"],
				["Release", "Release"]
			]
		]
		
		self.AddWidgets()

