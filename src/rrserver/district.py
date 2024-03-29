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
		return [], []
		
	def GetNodes(self):
		return self.nodes
	
	def Released(self, _):
		return False
	
	def PressButton(self, bname):
		pass
			
	def TurnoutLeverChange(self, _):
		pass

	def SetHandswitch(self, nm, st):
		pass
	
	def SetHandswitchIn(self, obj, newval):
		pass
	
	def CheckTurnoutPosition(self, turnout):
		pass
		
	def RouteIn(self, rt, stat):
		pass
	
	def GetRouteInMsg(self, r):
		return None
	
	def ShowBreakerState(self, _):
		pass
	
	def SelectRouteIn(self, _):
		return None
	
	def SetAspect(self, snm, asp):
		return False
	
	def VerifyAspect(self, signame, aspect):
		return aspect
			
	def setBus(self, bus):
		self.rrBus = bus
		for nd in self.nodes.values():
			nd.setBus(bus)
