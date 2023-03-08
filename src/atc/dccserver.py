import requests
import logging

class DCCServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				logging.info("sending to dcc server: %s %s" % (cmd, str(parms)))
				r = requests.get(self.ipAddr + "/" + cmd, params=parms)
			except requests.exceptions.ConnectionError:
				logging.error("Unable to send request  is dcc server running?")

