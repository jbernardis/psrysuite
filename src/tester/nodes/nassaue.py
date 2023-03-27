from tester.node import Node

class NassauE(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["N24RB 0", "Signal", 0],
				["N24RB 1", "", 0],
				["N24RC 0", "", 0],
				["N24RC 1", "", 0],
				["N26RC 0", "", 0],
				["N26RC 1", "", 0],
				["N24RA 0", "", 0],
				["N24RA 1", "", 0]
			],
		
			[
				["N26RA 0", "Signal", 0],
				["N26RA 1", "", 0],
				["N28R", "", 0],
				["B20E 0", "", 0],
				["B20E 1", "", 0],
				["B20E 2", "", 0],
				["N24L", "", 0],
				["N26L 0", "", 0]
			],
		
			[
				["N26L 1", "Signal", 0],
				["N28L 0", "", 0],
				["N28L 1", "", 0],
				["NESL 0", "Switch Lock", 0],
				["NESL 1", "", 0],
				["NESL 2", "", 0],
				["B10.REL", "Stop Relay", 0],
				["N24 L", "Signal Ind", 0]
			],
		
			[
				["N24 N", "Signal Ind", 0],
				["N24 R", "", 0],
				["N26 L", "", 0],
				["N26 N", "", 0],
				["N26 R", "", 0],
				["N28 L", "", 0],
				["N28 N", "", 0],
				["N28 R", "", 0]
			]
		]
		
		self.inputs = [
			[
				["NSw41 N", "Switch"],
				["NSw41 R", ""],
				["NSw43 N", ""],
				["NSw43 R", ""],
				["NSw45 N", ""],
				["NSw45 R", ""],
				["NSw47 N", ""],
				["NSw47 R", ""]
			],

			[
				["NSw51 N", "Switch"],
				["NSw51 R", ""],
				["NSw53 N", ""],
				["NSw53 R", ""],
				["NSw55 N", ""],
				["NSw55 R", ""],
				["NSw57 N", ""],
				["NSw57 R", ""]
			],

			[
				["N22", "Block Detection"],
				["N41", ""],
				["N42", ""],
				["NEOSRH", ""],
				["NEOSW", ""],
				["NEOSE", ""],
				["B10.W", ""],
				["B10", ""]
			],

			[
				["NSw39 N", "Switch"],
				["NSw39 R", ""]
			]
		]
		
		self.AddWidgets()

