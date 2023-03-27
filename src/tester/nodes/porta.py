from tester.node import Node

class PortA(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["PA12R 0", "Signal", 0],
				["PA12R 1", "", 0],
				["PA10RA 0", "", 0],
				["PA10RA 1", "", 0],
				["PA12LA", "", 0],
				["PA10RB 0", "", 0],
				["PA10RB 1", "", 0],
				["PA8R 0", "", 0]
			],
		
			[
				["PA8R 1", "Signal", 0],
				["PA12LB", "", 0],
				["PA6R 0", "", 0],
				["PA6R 1", "", 0],
				["PA4RA 0", "", 0],
				["PA4RA 1", "", 0],
				["PA12LC", "", 0],
				["PA4RB 0", "", 0]
			],
		
			[
				["PA4RB 1", "Signal", 0],
				["PA8L", "", 0],
				["PA6LA", "", 0],
				["PA6LB", "", 0],
				["PA6LC", "", 0],
				["Sem10w", "Semaphore", 0],
				["Sem10w", "Semaphore", 0],
				["PA4 L", "Signal Ind", 0]
			],
		
			[
				["PA4 N", "Signal Ind", 0],
				["PA4 R", "", 0],
				["PA6 L", "", 0],
				["PA6 N", "", 0],
				["PA6 R", "", 0],
				["PA8 L", "", 0],
				["PA8 N", "", 0],
				["PA8 R", "", 0]
			],
		
			[
				["PA10 L", "Signal Ind", 0],
				["PA10 N", "", 0],
				["PA10 R", "", 0],
				["PA12 L", "", 0],
				["PA12 N", "", 0],
				["PA12 R", "", 0],
				["PA32 L", "", 0],
				["PA32 N", "", 0],
			],
		
			[
				["PA32 R", "Signal Ind", 0],
				["PA34 L", "", 0],
				["PA34 N", "", 0],
				["PA34 R", "", 0],
				["P21", "Block Ind", 0],
				["P40", "", 0],
				["P50", "Yard Sig Ind", 0],
				["P11", "Latham Sig Ind", 0]
			],
		
			[
				["P21", "Latham Sig Ind", 0],
				["CBParsonsJct", "Breaker", 0],
				["CBSouthport", "", 0],
				["CBLavinYard", "", 0],
				["PASw1", "Switch Lock", 0],
				["PASw3", "", 0],
				["PASw5", "", 0],
				["PASw7", "", 0]
			],
		
			[
				["PASw9", "Switch Lock", 0],
				["PASw11/13", "", 0],
				["PASw15/17", "", 0],
				["PASw19", "", 0],
				["PASw21", "", 0],
				["PASw23", "", 0],
				["PASw27/29/31", "", 0],
				["PASw33", "", 0]
			],
		
			[
				["PASw35", "Switch Lock", 0],
				["PASw37", "", 0],
				["P10.REL", "Stop Relay", 0],
				["P40.REL", "", 0],
				["P31.REL", "", 0],
				["P40", "Semaphore", 0],
				["P40", "Semaphore", 0]
			]		
		]
		
		self.inputs = [
			[
				["PASw1 N", "Switch"],
				["PASw1 R", ""],
				["PASw3 N", ""],
				["PASw3 R", ""],
				["PASw5 N", ""],
				["PASw5 R", ""],
				["PASw7 N", ""],
				["PASw7 R", ""]
			],

			[
				["PASw9 N", "Switch"],
				["PASw9 R", ""],
				["PASw11 N", ""],
				["PASw11 R", ""],
				["PASw13 N", ""],
				["PASw13 R", ""],
				["PASw15 N", ""],
				["PASw15 R", ""]
			],

			[
				["P1", "Block Detection"],
				["P2", ""],
				["P3", ""],
				["P4", ""],
				["P5", ""],
				["P6", ""],
				["P7", ""],
				["POSSP1", ""]
			],

			[
				["POSSP2", "Block Detection"],
				["POSSP3", ""],
				["POSSP4", ""],
				["POSSP5", ""],
				["P10", ""],
				["P10.E", ""],
				["PA4 L", "Sig Lvr"],
				["PA4 CO", ""]
			],

			[
				["PA4 R", "Sig Lvr"],
				["PA6 L", ""],
				["PA6 CO", ""],
				["PA6 R", ""],
				["PA8 L", ""],
				["PA8 CO", ""],
				["PA8 R", ""],
				["PA10 L", ""]
			],

			[
				["PA10 CO", "Sig Lvr"],
				["PA10 R", ""],
				["PA12 L", ""],
				["PA12 CO", ""],
				["PA12 R", ""],
				["PA32 L", ""],
				["PA32 CO", ""],
				["PA32 R", ""]
			],

			[
				["PA34 L", "Sig Lvr"],
				["PA34 CO", ""],
				["PA34 R", ""],
				["Release", "Release"]
			]
		]
		
		self.AddWidgets()

