import wx
import logging

class ClientList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(300, 160), style=wx.LC_REPORT)
		self.InsertColumn(0, "Function")
		self.SetColumnWidth(0, 70)
		self.InsertColumn(1, "IP")
		self.SetColumnWidth(1, 100)
		self.InsertColumn(2, "Port")
		self.SetColumnWidth(2, 80)
		self.InsertColumn(3, "SID")
		self.SetColumnWidth(3, 50)
		self.clientList = []
		self.sids = []

	def AddClient(self, addr, sid, function):
		if addr in self.clientList:
			return

		logging.info("Adding new client from %s:%s" % (addr[0], addr[1]))
		index = len(self.clientList)
		self.clientList.append(addr)
		self.sids.append(sid)
		self.InsertItem(index, "??" if function is None else function)
		self.SetItem(index, 1, addr[0])
		self.SetItem(index, 2, "%d" % addr[1])
		self.SetItem(index, 3, "%3d" % sid)
		
	def SetSessionFunction(self, sid, function):
		try:
			index = self.sids.index(sid)
		except ValueError:
			return
		
		self.SetItem(index, 0, function)

	def DelClient(self, addr):
		logging.info("Removing client with address %s:%s" % (addr[0], addr[1]))
		try:
			index = self.clientList.index(addr)
		except ValueError:
			return

		self.DeleteItem(index)
		del(self.clientList[index])
		del(self.sids[index])
