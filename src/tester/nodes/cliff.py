from tester.node import Node

class Cliff(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["C2 L", "Signal Ind", 0],
				["C2 N", "", 0],
				["C2 R", "", 0],
				["C4 L", "", 0],
				["C4 N", "", 0],
				["C4 R", "", 0],
				["C6 L", "", 0],
				["C6 N", "", 0]
			],
		
			[
				["C6 R", "Signal Ind", 0],
				["C8 L", "", 0],
				["C8 N", "", 0],
				["C8 R", "", 0],
				["C10 L", "", 0],
				["C10 N", "", 0],
				["C10 R", "", 0],
				["C12 L", "", 0]
			],
		
			[
				["C12 N", "Signal Ind", 0],
				["C12 R", "", 0],
				["C14 L", "", 0],
				["C14 N", "", 0],
				["C14 R", "", 0],
				["Fleet", "Fleet", 0],
				["~Fleet", "Fleet", 0],
				["C18 L", "Signal Ind", 0]
			],
		
			[
				["C18 N", "Signal Ind", 0],
				["C18 R", "", 0],
				["C22 L", "", 0],
				["C22 N", "", 0],
				["C22 R", "", 0],
				["C24 L", "", 0],
				["C24 N", "", 0],
				["C24 R", "", 0]
			],
		
			[
				["CSw3", "Hand Switch", 0],
				["~CSw3", "", 0],
				["CSw11", "", 0],
				["~CSw11", "", 0],
				["CSw15", "", 0],
				["~CSw15", "", 0],
				["CSw19", "", 0],
				["~CSw19", "", 0]
			],
		
			[
				["CSw21a/b", "Hand Switch", 0],
				["~CSw21a/b", "", 0],
				["B10", "Block Ind", 0],
				["CBGreenMtnStn/Yd", "Breaker", 0],
				["CBSheffieldA/B", "", 0],
				["CBCliveden", "", 0],
				["CBReverserC22C23", "", 0],
				["CBBank", "", 0]
			],
		
			[
				["CSw31", "Switch Lock", 0],
				["CSw41", "", 0],
				["CSw43", "", 0],
				["CSw61", "", 0],
				["CSw9", "", 0],
				["CSw13", "", 0],
				["CSw17", "", 0],
				["CSw23", "", 0]
			],
		
			[
				["CSw21a", "Lock Ind", 0],
				["CSw21b", "", 0],
				["CSw19", "", 0],
				["CSw15", "", 0],
				["CSw11", "", 0]
			]		
		]
		
		self.inputs = [
			[
				["CC21W", "Route"],
				["CC40W", ""],
				["CC44W", ""],
				["CC43W", ""],
				["CC42W", ""],
				["CC41W", ""],
				["CC41E", ""],
				["CC42E", ""]
			],

			[
				["CC21E", "Route"],
				["CC40E", ""],
				["CC44E", ""],
				["CC43E", ""],
				["COSSHE", "Block Detection"],
				["C21", ""],
				["C40", ""],
				["C41", ""]
			],

			[
				["C42", "Block Detection"],
				["C43", ""],
				["C44", ""],
				["COSSHW", ""],
				["C2 L", "Sig Lvr"],
				["C2 CO", ""],
				["C2 R", ""],
				["C4 L", ""]
			],

			[
				["C4 CO", "Sig Lvr"],
				["C4 R", ""],
				["C6 L", ""],
				["C6 CO", ""],
				["C6 R", ""],
				["C8 L", ""],
				["C8 CO", ""],
				["C8 R", ""]
			],

			[
				["C10 L", "Sig Lvr"],
				["C10 CO", ""],
				["C10 R", ""],
				["C12 L", ""],
				["C12 CO", ""],
				["C12 R", ""],
				["C14 L", ""],
				["C14 CO", ""]
			],

			[
				["C14 R", "Sig Lvr"],
				["Fleet", "Fleet"],
				["C18 L", "Sig Lvr"],
				["C18 CO", ""],
				["C18 R", ""],
				["C22 L", ""],
				["C22 CO", ""],
				["C22 R", ""]
			],

			[
				["C24 L", "Sig Lvr"],
				["C24 CO", ""],
				["C24 R", ""],
				["Release", "Release"],
				["CSw3", "Hand Switch"],
				["CSw11", ""],
				["CSw15", ""],
				["CSw19", ""]
			],

			[
				["CSw21a/b", "Hand Switch"]
			]
		]
		
		self.AddWidgets()

