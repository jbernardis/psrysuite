import logging

class ClientList:
	def __init__(self, parent):
		self.sids = []
		self.skts = []
		self.functions = []
		self.clientList = []

	def AddClient(self, addr, skt, sid, function):
		if addr in self.clientList:
			return

		logging.info("Adding new client from %s:%s" % (addr[0], addr[1]))
		self.clientList.append(addr)
		self.sids.append(sid)
		self.skts.append(skt)
		self.functions.append("")
		
	def GetClients(self):
		return [[self.sids[x], self.functions[x], self.clientList[x][0], self.clientList[x][1]] for x in range(len(self.sids))]
		
	def SetSessionFunction(self, sid, function):
		try:
			index = self.sids.index(sid)
		except ValueError:
			return
		
		self.functions[index] = function
		
	def HasFunction(self, function):
		return function in self.functions

	
	def GetFunctionAddress(self, function):
		cl = []
		for i in range(len(self.clientList)):
			if function == self.functions[i]:
				cl.append((self.clientList[i], self.skts[i]))
			
		return cl
	
	def GetFunctionAtAddress(self, address):
		for i in range(len(self.clientList)):
			if self.clientList[i] == address:
				return self.functions[i]
			
		return None
	
	def Count(self):
		return len(self.clientList)

	def DelClient(self, addr):
		logging.info("Removing client with address %s:%s" % (addr[0], addr[1]))
		try:
			index = self.clientList.index(addr)
		except ValueError:
			return

		del(self.clientList[index])
		del(self.sids[index])
		del(self.skts[index])
		del(self.functions[index])
