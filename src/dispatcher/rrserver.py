import requests
import logging

class RRServer(object):
	def __init__(self):
		self.ipAddr = None
		#self.rrSession = requests.Session()
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				#self.rrSession.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
				requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.7)
			except requests.exceptions.ConnectionError:
				logging.error("Unable to send request  is rr server running?")
				
	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			logging.error("Unable to send get request is rr server running?")
			return None
		
		if r.status_code >= 400:
			logging.error("HTTP Error %d" % r.status_code)
			return None
		
		try:
			return r.json()
		except:
			return r.text
				
	def Post(self, fn, directory,  data):
		headers = {
		    'Filename': fn,
		    'Directory': directory
		}
		try:
			r = requests.post(self.ipAddr, headers=headers, json=data, timeout=4.0)
		except requests.exceptions.ConnectionError:
			logging.error("Unable to send post request is rr server running?")
			print("error 1", flush=True)
			return 400
		
		if r.status_code >= 400:
			logging.error("HTTP Error %d" % r.status_code)
			print("error 2", flush=True)
			return r.status_code
		
		return r.status_code

