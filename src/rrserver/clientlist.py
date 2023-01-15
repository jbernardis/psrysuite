import wx
import logging

class ClientList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(300, 160), style=wx.LC_REPORT)
		self.InsertColumn(0, "IP")
		self.SetColumnWidth(0, 100)
		self.InsertColumn(1, "Port")
		self.SetColumnWidth(1, 100)
		self.InsertColumn(2, "SID")
		self.SetColumnWidth(2, 100)
		self.clientList = []

	def AddClient(self, addr, sid):
		if addr in self.clientList:
			return

		logging.info("Adding new client from %s:%s" % (addr[0], addr[1]))
		index = len(self.clientList)
		self.clientList.append(addr)
		self.InsertItem(index, addr[0])
		self.SetItem(index, 1, "%d" % addr[1])
		self.SetItem(index, 2, "%3d" % sid)

	def DelClient(self, addr):
		logging.info("Removing client with address %s:%s" % (addr[0], addr[1]))
		try:
			index = self.clientList.index(addr)
		except ValueError:
			return

		self.DeleteItem(index)
		del(self.clientList[index])
