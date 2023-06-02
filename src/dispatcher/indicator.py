
class Indicator:
	def __init__(self, frame, district, name):
		self.frame = frame
		self.district = district
		self.name = name
		self.value = 0

	def GetDistrict(self):
		return self.district

	def GetName(self):
		return self.name

	def GetValue(self):
		return self.value

	def SetValue(self, val, force=False):
		if val == self.value and not force:
			return
		self.value = val
		self.frame.Request({"indicator": { "name": self.name, "value": self.value}})

