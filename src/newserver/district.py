import logging


class District:
	def __init__(self, parent, name, settings):
		self.parent = parent
		self.name = name
		self.address = None
		self.settings = settings

		self.routeMap = {}
		self.rrBus = None
		
	def Name(self):
		return self.name
				
	def OutIn(self):
		for nd in self.nodes.values():
			nd.OutIn()

	def Initialize(self):
		pass
			
	def GetControlOption(self):
		return []
		
	def GetNodes(self):
		return self.nodes
	
	def Released(self):
		return False
	
	def PressButton(self, bname):
		pass
			
	def TurnoutLeverChange(self, _):
		pass

	def SetHandSwitch(self, nm, st):
		pass
	
	def CheckTurnoutPosition(self, turnout):
		pass
		
	def RouteIn(self, rt, stat):
		pass
	
	def ShowBreakerState(self, _):
		pass
	
	def SelectRouteIn(self, _):
		return None
			
	def setBus(self, bus):
		self.rrBus = bus
		for nd in self.nodes.values():
			nd.setBus(bus)
