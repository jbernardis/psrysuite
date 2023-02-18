from tester.node import Node

class YardSw(Node):
	def __init__(self, parent, address):
		Node.__init__(self, parent)
		self.parent = parent
		self.address = address

		self.outputs = [
			[
				["YSw1 N", "Switch", Node.pulsed],
				["YSw1 R", "", Node.pulsed],
				["YSw3 N", "", Node.pulsed],
				["YSw3 R", "", Node.pulsed],
				["YSw7 N", "", Node.pulsed],
				["YSw7 R", "", Node.pulsed],
				["YSw9 N", "", Node.pulsed],
				["YSw9 R", "", Node.pulsed]
			],
			[
				["YSw11 N", "Switch", Node.pulsed],
				["YSw11 R", "", Node.pulsed],
				["YSw17 N", "", Node.pulsed],
				["YSw17 R", "", Node.pulsed],
				["YSw19 N", "", Node.pulsed],
				["YSw19 R", "", Node.pulsed],
				["YSw21 N", "", Node.pulsed],
				["YSw21 R", "", Node.pulsed]
			],
			[
				["YSw23 N", "Switch", Node.pulsed],
				["YSw23 R", "", Node.pulsed],
				["YSw25 N", "", Node.pulsed],
				["YSw25 R", "", Node.pulsed],
				["YSw27 N", "", Node.pulsed],
				["YSw27 R", "", Node.pulsed],
				["YSw29 N", "", Node.pulsed],
				["YSw29 R", "", Node.pulsed]
			],
			[
				["YY51W", "Switch Button", Node.pulsed],
				["YY50W", "", Node.pulsed]
			],
			[
				["YWWB1", "Switch Button", Node.pulsed],
				["YWWB2", "", Node.pulsed],
				["YWWB3", "", Node.pulsed],
				["YWWB4", "", Node.pulsed],
				["YWEB1", "", Node.pulsed],
				["YWEB2", "", Node.pulsed],
				["YWEB3", "", Node.pulsed],
				["YWEB4", "", Node.pulsed]
			]
		]
		
		self.inputs = []
		
		self.AddWidgets()

