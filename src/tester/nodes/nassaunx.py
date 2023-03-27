from tester.node import Node

class NassauNX(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["NT12", "Switch Button", Node.pulsed],
				["NN60", "", Node.pulsed],
				["NN11", "", Node.pulsed],
				["NN21", "", Node.pulsed],
				["NW10", "", Node.pulsed],
				["NN32W", "", Node.pulsed],
				["NN31W", "", Node.pulsed],
				["NN12W", "", Node.pulsed]
			],
		
			[
				["NN22W", "Switch Button", Node.pulsed],
				["NN41W", "", Node.pulsed],
				["NN42W", "", Node.pulsed],
				["NW20W", "", Node.pulsed],
				["NW11", "", Node.pulsed],
				["NN32E", "", Node.pulsed],
				["NN31E", "", Node.pulsed],
				["NN12E", "", Node.pulsed]
			],
				
			[
				["NN22E", "Switch Button", Node.pulsed],
				["NN41E", "", Node.pulsed],
				["NN42E", "", Node.pulsed],
				["NW20E", "", Node.pulsed],
				["NR10", "", Node.pulsed],
				["NB10", "", Node.pulsed],
				["NB20", "", Node.pulsed]
			]
		]
		
		self.inputs = [	]
		
		self.AddWidgets()

