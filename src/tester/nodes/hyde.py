from tester.node import Node

class Hyde(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["HSw1 N", "Switch", Node.pulsed],
				["HSw1 R", "", Node.pulsed],
				["HSw3 N", "", Node.pulsed],
				["HSw3 R", "", Node.pulsed],
				["HSw7 N", "", Node.pulsed],
				["HSw7 R", "", Node.pulsed],
				["HSw9 N", "", Node.pulsed],
				["HSw9 R", "", Node.pulsed]
			],
		
			[
				["HSw11 N", "Switch", Node.pulsed],
				["HSw11 R", "", Node.pulsed],
				["HSw23 N", "", Node.pulsed],
				["HSw23 R", "", Node.pulsed],
				["HSw25 N", "", Node.pulsed],
				["HSw25 R", "", Node.pulsed],
				["HSw27 N", "", Node.pulsed],
				["HSw27 R", "", Node.pulsed]
			],
				
			[
				["HSw29 N", "Switch", Node.pulsed],
				["HSw29 R", "", Node.pulsed],
				["HSw15 N", "", Node.pulsed],
				["HSw15 R", "", Node.pulsed],
				["HSw17 N", "", Node.pulsed],
				["HSw17 R", "", Node.pulsed],
				["HSw19 N", "", Node.pulsed],
				["HSw19 R", "", Node.pulsed]
			],
			
			[
				["HSw21 N", "Switch", Node.pulsed],
				["HSw21 R", "", Node.pulsed],
				["H30", "Block Ind", 0],
				["H10", "", 0],
				["H23", "", 0],
				["N25", "", 0],
				["H21.Rel", "Stop Relay", 0],
				["H13.Rel", "", 0]
			],
			
			[
				["CBHydeJct", "Breaker Ind", 0],
				["CBHydeWest", "", 0],
				["CBHydeEast", "", 0],
				["HydePowerWest", "Power", 0],
				["HydePowerEast", "", 0]
			]
		]
		
		self.inputs = [
			[
				["H12W", "Route"],
				["H34W", ""],
				["H33W", ""],
				["H30E", ""],
				["H31W", ""],
				["H32W", ""],
				["H22W", ""],
				["H43W", ""]
			],

			[
				["H42W", "Route"],
				["H41W", ""],
				["H41E", ""],
				["H42E", ""],
				["H43E", ""],
				["H22E", ""],
				["H40E", ""],
				["H12E", ""]
			],

			[
				["H34E", "Route"],
				["H33E", ""],
				["H32E", ""],
				["H31E", ""],
				["H21", "Block Detection"],
				["H21.E", ""],
				["HOSWW2", ""],
				["HOSWW", ""]
			],

			[
				["HOSWE", "Block Detection"],
				["H31", ""],
				["H32", ""],
				["H33", ""],
				["H34", ""],
				["H12", ""],
				["H22", ""],
				["H43", ""]
			],

			[
				["H42", "Block Detection"],
				["H41", ""],
				["H40", ""],
				["HOSEW", ""],
				["HOSEE", ""],
				["H13.W", ""],
				["H13", ""]
			]
		]
		
		self.AddWidgets()

