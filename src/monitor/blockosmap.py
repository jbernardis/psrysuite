class BlockOSMap:
	def __init__(self, rrserver):
		self.blockosmap = rrserver.Get("blockosmap", {})

		print("retrieved Block OS Map: %s" % str(self.blockosmap))

	def GetEastOSList(self, bname):
		try:
			return self.blockosmap[bname][1]
		except (KeyError, IndexError):
			return []

	def GetWestOSList(self, bname):
		try:
			return self.blockosmap[bname][0]
		except (KeyError, IndexError):
			return []

	def GetOSList(self, bname, east):
		if east:
			return self.GetEastOSList(bname)
		else:
			return self.GetWestOSList(bname)



