from tester.node import Node

class Parsons(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["PA34LB 0", "Signal", 0],
				["PA34LB 1", "", 0],
				["PA34LB 0", "", 0],
				["PA32L", "", 0],
				["PA34LA 0", "", 0],
				["PA34LA 1", "", 0],
				["PA34LA 2", "", 0],
				["PA34RD 0", "", 0]
			],
		
			[
				["PA34RD 1", "Signal", 0],
				["PA34RD 2", "", 0],
				["PA34RC", "", 0],
				["PA32RA 0", "", 0],
				["PA32RA 1", "", 0],
				["PA32RB 2", "", 0],
				["PA34RB", "", 0],
				["PA32RB 0", "", 0]
			],
		
			[
				["PA32RB 1", "Signal", 0],
				["PA32RB 2", "", 0],
				["PA34RA", "", 0],
				["P20.REL", "Stop Relay", 0],
				["L30.REL", "", 0],
				["P50.REL", "", 0],
				["P11.REL", "", 0],
			]		
		]
		
		self.inputs = [
			[
				["PASw27 N", "Switch"],
				["PASw27 R", ""],
				["PASw29 N", ""],
				["PASw29 R", ""],
				["PASw31 N", ""],
				["PASw31 R", ""],
				["PASw33 N", ""],
				["PASw33 R", ""]
			],

			[
				["PASw35 N", "Switch"],
				["PASw35 R", ""],
				["PASw37 N", ""],
				["PASw37 R", ""],
				["P20", "Block Detection"],
				["P20.E", ""],
				["P30.W", ""],
				["P30", ""]
			],

			[
				["P30.E", "Block Detection"],
				["POSPJ1", ""],
				["POSPJ2", ""],
				["P50.W", ""],
				["P50", ""],
				["P50.E", ""],
				["P11.W", ""],
				["P11", ""]
			],

			[
				["P11.E", "Block Detection"]
			]
		]
		
		self.AddWidgets()

