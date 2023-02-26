from tester.node import Node

class Latham(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["LSw1 N", "Switch", Node.pulsed],
				["LSw1 R", "", Node.pulsed],
				["", "", Node.disabled],
				["LSw3 R", "", Node.pulsed],
				["LSw5 N", "", Node.pulsed],
				["LSw5 R", "", Node.pulsed],
				["LSw7 N", "", Node.pulsed],
				["LSw7 R", "", Node.pulsed]
			],
		
			[
				["LSw9 N", "Switch", Node.pulsed],
				["LSw9 R", "", Node.pulsed],
				["L4R 0", "Signal", 0],
				["L4R 1", "", 0],
				["L4R 2", "", 0],
				["L6RB", "", 0],
				["L6RA 0", "", 0],
				["L6RA 1", "", 0]
			],
			
			[
				["L6RA 2", "Signal", 0],
				["L8R", "", 0],
				["LSw3 N", "Switch", Node.pulsed],
				["", "", Node.unused],
				["L4L", "Signal", 0],
				["L6L 0", "", 0],
				["L6L 1", "", 0],
				["L6L 2", "", 0]
			],
			
			[
				["L8L 0", "Signal", 0],
				["L8L 1", "", 0],
				["L8L 2", "", 0],
				["L10", "Block Ind", 0],
				["L31", "", 0],
				["P11", "", 0],
				["L20.Rel", "Stop Relay", 0],
				["P21.Rel", "", 0]
			],
			
			[
				["L11.Rel", "Stop Relay", 0],
				["L21.Rel", "", 0],
				["P50.Rel", "", 0]
			]
		]
		
		self.inputs = [
			[
				["LSw1 N", "Switch"],
				["LSw1 R", ""],
				["LSw3 N", ""],
				["LSw3 R", ""],
				["LSw5 N", ""],
				["LSw5 R", ""],
				["LSw7 N", ""],
				["LSw7 R", ""]
			],

			[
				["LSw9 N", "Switch"],
				["LSw9 R", ""],
				["L20", "Block Detection"],
				["L20.E", ""],
				["P21", ""],
				["P21.E", ""],
				["LOSOAW", ""],
				["LOSLAM", ""]
			],

			[
				["LOSLAE", "Block Detection"],
				["L11.W", ""],
				["L11", ""],
				["L21.W", ""],
				["L21", ""],
				["L21.E", ""],
				["Cliveden", "Breaker"],
				["Latham", ""]
			],

			[
				["CornellJct", "Breaker"],
				["ParsonsJct", ""],
				["SouthJct", ""],
				["CircusJct", ""],
				["Southport", ""],
				["LavinYard", ""],
				["ReverserP31", ""],
				["ReverserP41", ""]
			],

			[
				["ReverserP50", "Breaker"],
				["ReverserC22C23", ""]
			]
		]
		
		self.AddWidgets()

