from tester.node import Node

class Sheffield(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["CC54E", "Switch Button", Node.pulsed],
				["CC53E", "", Node.pulsed],
				["CC52E", "", Node.pulsed],
				["CC51E", "", Node.pulsed],
				["CC50E", "", Node.pulsed],
				["CC21E", "", Node.pulsed],
				["CC40E", "", Node.pulsed],
				["CC41E", "", Node.pulsed]
			],
		
			[
				["CC42E", "Switch Button", Node.pulsed],
				["CC43E", "", Node.pulsed],
				["CC44E", "", Node.pulsed],
				["CC54W", "", Node.pulsed],
				["CC53W", "", Node.pulsed],
				["CC52W", "", Node.pulsed],
				["CC51W", "", Node.pulsed],
				["CC50W", "", Node.pulsed]
			],
				
			[
				["CC21W", "Switch Button", Node.pulsed],
				["CC40W", "", Node.pulsed],
				["CC41W", "", Node.pulsed],
				["CC42W", "", Node.pulsed],
				["CC43W", "", Node.pulsed],
				["CC44W", "", Node.pulsed],
				["CC30E", "", Node.pulsed],
				["CC10E", "", Node.pulsed]
			],
			
			[
				["CG10E", "Switch Button", Node.pulsed],
				["CG12E", "", Node.pulsed],
				["CC30W", "", Node.pulsed],
				["CC31W", "", Node.pulsed],
				["CC10W", "", Node.pulsed],
				["CG21W", "", Node.pulsed]
			]
		]
		
		self.inputs = [
			[
				["CC50W", "Route"],
				["CC51W", ""],
				["CC52W", ""],
				["CC53W", ""],
				["CC54W", ""],
				["CC50E", ""],
				["CC51E", ""],
				["CC52E", ""]
			],

			[
				["CC53E", "Route"],
				["CC54E", ""],
				["C50", "Block Detection"],
				["C51", ""],
				["C52", ""],
				["C53", ""],
				["C54", ""]
			]
		]
		
		self.AddWidgets()

