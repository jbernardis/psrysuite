
class Input:
	def __init__(self, name, district):
		self.name = name
		self.district = district
		self.value = 0
		self.rr = None

	def SetRailRoad(self, rr):
		self.rr = rr

	def SetDistrict(self, d):
		self.district = d

	def GetName(self):
		return self.name

	def SetValue(self, v):
		self.value = v

	def GetValue(self):
		return self.value

	def GetEventMessage(self):
		return None


class BreakerInput(Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)

	def SetValue(self, nv):
		if nv == self.value:
			return
		self.value = nv
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetEventMessage(self):
		return {"breaker": [{ "name": self.name, "value": self.value}]}


class RouteInput(Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)

	def SetValue(self, nv):
		if nv == self.value:
			return
		self.value = nv
		if nv == 1:
			self.district.MapRouteToTurnouts(self.name)

	def GetEventMessage(self):
		# Route inputs are communicated indirectly by sending the values for the underlying turnouts
		# this is done by the MapRouteToTurnouts method in district called above
		return None


class BlockInput(Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.subBlocks = []
		self.east = True
		self.clear = False

	def SetValue(self, nv):
		if nv == self.value:
			return
		self.value = nv
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def SetDirection(self, direction):
		nv = direction == 'E'
		if self.east == nv:
			return
		self.east = nv
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage(direction=True))
		if len(self.subBlocks) != 0:
			for sb in self.subBlocks:
				sb.SetDirection(direction)

	def SetClear(self, clear):
		if self.clear == clear:
			return
		self.clear = clear
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage(clear=True))
		if len(self.subBlocks) != 0:
			for sb in self.subBlocks:
				sb.SetClear(clear)

	def GetValue(self):
		return self.value

	def GetEast(self):
		return self.east

	def GetClear(self):
		return self.clear

	def AddSubBlock(self, sub):
		self.subBlocks.append(sub)

	def EvaluateSubBlocks(self):
		nv = 0
		for sb in self.subBlocks:
			sv = sb.GetValue()
			if sv != 0:
				nv = 1
				break
		self.SetValue(nv)

	def GetEventMessage(self, clear=False, direction=False):
		if clear:
			return {"blockclear": [{ "block": self.name, "clear": 1 if self.clear else 0}]}
		if direction:
			return {"blockdir": [{ "block": self.name, "dir": "E" if self.east else "W"}]}
		else:
			# return {"block": [{ "name": self.name, "state": self.value, "dir": "E" if self.east else "W",
			# 					"clear": 1 if self.clear else 0}]}
			return {"block": [{ "name": self.name, "state": self.value}]}

	def ToJson(self):
		sbs = [sb.GetName() for sb in self.subBlocks]
		if len(sbs) > 0:
			return {self.name: sbs}
		else:
			return {}


class SubBlockInput(Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.parent = None
		self.east = True
		self.clear = False
	
	def SetParent(self, parent):
		self.parent = parent
		self.parent.AddSubBlock(self)
		self.east = self.parent.GetEast()

	def SetValue(self, nv):
		if nv == self.value:
			return
		self.value = nv
		if self.parent:
			self.parent.EvaluateSubBlocks()
		self.rr.RailroadEvent({"refreshinput": [self.name]})

	def SetClear(self, nv):
		if nv == self.clear:
			return
		self.clear = nv
		if self.parent:
			self.parent.EvaluateSubBlocks()
		self.rr.RailroadEvent({"refreshinput": [self.name]})

	def SetDirection(self, direction):
		self.east = direction == "E"
		self.rr.RailroadEvent({"refreshinput": [self.name]})

	def GetValue(self):
		return self.value

	def GetClear(self):
		return self.clear

	def GetEast(self):
		return self.east

	def GetEventMessage(self):
		return None

	def ToJson(self):
		return {}


class TurnoutInput(Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.state = "N"  # assume normal switch position to start

	def SetState(self, nb, rb):
		if nb != 0 and rb == 0:
			ns = 'N'
		elif rb != 0 and nb == 0:
			ns = 'R'
		else:
			# erroneous case - just assume normal
			ns = 'N'
		self.SetState(ns)

	def SetState(self, ns):
		if ns == self.state:
			return
		self.state = ns
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetState(self):
		return self.state
		
	def GetEventMessage(self):
		return {"turnout": [{ "name": self.name, "state": self.state}]}


class SignalLeverInput (Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.state = "N"

	def SetState(self, state):
		if state == self.state:
			return

		self.state = state
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetState(self):
		return self.state

	def GetEventMessage(self):
		return {"siglever": [{ "name": self.name, "state": self.state}]}


class FleetLeverInput (Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.state = 0

	def SetState(self, state):
		if state == self.state:
			return

		self.state = state
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetState(self):
		return self.state

	def GetEventMessage(self):
		return {"control": [{ "name": self.name, "value": self.state}]}


class ToggleInput (Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.state = 0

	def SetState(self, state):
		if state == self.state:
			return

		self.state = state
		self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetState(self):
		return self.state

	def GetEventMessage(self):
		return {"control": [{ "name": self.name, "value": self.state}]}


class HandswitchLeverInput (Input):
	def __init__(self, name, district):
		Input.__init__(self, name, district)
		self.state = 0

	def SetState(self, state):
		if state == self.state:
			return

		self.state = state
		# self.rr.RailroadEvent({"refreshinput": [self.name]})
		self.rr.RailroadEvent(self.GetEventMessage())

	def GetState(self):
		return self.state

	def GetEventMessage(self):
		hsname = self.name.split(".")[0] + ".hand"
		return {"handswitch": [{ "name": hsname, "state": self.state}]}


class Output:
	def __init__(self, name, district):
		self.name = name
		self.district = district
		self.value = 0
		self.rr = None

	def SetRailRoad(self, rr):
		self.rr = rr

	def GetName(self):
		return self.name

	def GetEventMessage(self):
		pass


class IndicatorOutput(Output):
	def __init__(self, name, district):
		Output.__init__(self, name, district)
		self.status = False

	def SetStatus(self, flag=True):
		if self.status == flag:
			return

		self.status = flag
		# self.rr.RailroadEvent({"refreshinput": [self.name]})

	def GetEventMessage(self):
		pass

	def GetStatus(self):
		return self.status


class HandSwitchOutput(IndicatorOutput):
	def __init__(self, name, district):
		IndicatorOutput.__init__(self, name, district)

	def GetEventMessage(self):
		return {"handswitch": [{ "name": self.name, "state": self.status}]}


class RelayOutput(IndicatorOutput):
	def __init__(self, name, district):
		IndicatorOutput.__init__(self, name, district)

	def GetEventMessage(self):
		return {"relay": [{ "name": self.name, "state": self.status}]}


class SignalOutput(Output):
	def __init__(self, name, district):
		Output.__init__(self, name, district)
		self.aspect = 0
		self.locked = False

	def SetAspect(self, aspect):
		if aspect == self.aspect:
			return

		self.aspect = aspect
		self.rr.RailroadEvent({"refreshoutput": [self.name]})

	def IsAspectNonZero(self):
		return self.aspect != 0

	def GetAspect(self):
		return self.aspect

	def SetLock(self, lock):
		if self.locked and lock == 1:
			return
		if not self.locked and lock == 0:
			return

		self.locked = lock == 1
		self.rr.RailroadEvent({"refreshoutput": [self.name]})

	def IsLocked(self):
		return self.locked

	def GetAspectBit(self, abit):
		mask = (1 << abit) & 0xff
		rv = mask & self.aspect
		return 1 if rv != 0 else 0

	def GetEventMessage(self):
		return {"signal": [{ "name": self.name, "aspect": self.aspect}]}


class PulsedOutput(Output):
	def __init__(self, name, district, pulseLen=1):
		Output.__init__(self, name, district)
		self.pulseLen = pulseLen

	def SetPulseLen(self, pulseLen):
		self.pulseLen = pulseLen


class TurnoutOutput(PulsedOutput):
	def __init__(self, name, district, pulseLen=1):
		PulsedOutput.__init__(self, name, district, pulseLen)
		self.normal = False;
		self.reverse = False;
		self.normalPulses = 0;
		self.reversePulses = 0;
		self.locked = False
		self.status = None

	def GetStatus(self):
		return self.status

	def SetLock(self, value):
		self.locked = value != 0

	def GetLock(self):
		return self.locked

	def SetOutPulseTo(self, status):
		if status == "N":
			self.normalPulses = self.pulseLen
			self.reversePulses = 0
			self.status = status
		elif status == "R":
			self.normalPulses = 0
			self.reversePulses = self.pulseLen
			self.status = status
		else:
			self.normalPulses = 0
			self.reversePulses = 0
			self.status = None
		self.rr.RailroadEvent({"refreshoutput": [self.name]})

	def GetOutPulseValue(self):
		if self.normalPulses > 0:
			return self.normalPulses
		elif self.reversePulses > 0:
			return -self.reversePulses
		else:
			return 0

	def GetOutPulse(self):
		if self.normalPulses > 0:
			self.normalPulses -= 1
			rv = 1
		elif self.reversePulses > 0:
			self.reversePulses -= 1
			rv = -1
		else:
			return 0

		if rv != 0:
			self.rr.RailroadEvent({"refreshoutput": [self.name]})

		return rv


class NXButtonOutput(PulsedOutput):
	def __init__(self, name, district, pulseLen=1):
		PulsedOutput.__init__(self, name, district, pulseLen)
		self.pulses = 0;
		self.status = None

	def GetStatus(self):
		return self.status

	def SetOutPulseNXB(self):
		self.pulses = self.pulseLen
		self.rr.RailroadEvent({"refreshoutput": [self.name]})

	def GetOutPulseValue(self):
		return self.pulses

	def GetOutPulse(self):
		if self.pulses > 0:
			self.pulses -= 1
			rv = 1
		else:
			rv = 0

		if rv != 0:
			self.rr.RailroadEvent({"refreshoutput": [self.name]})
		return rv
