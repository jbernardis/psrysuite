import requests
import logging
import json

class RRServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except requests.exceptions.ConnectionError:
				logging.error("Unable to send request  is rr server running?")
				
	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			logging.error("Unable to send request  is rr server running?")
			return None
		
		if r.status_code >= 400:
			logging.error("HTTP Error %d" % r.status_code)
			return None
		
		try:
			return r.json()
		except json.decoder.JSONDecodeError:
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
			return 400
		
		if r.status_code >= 400:
			logging.error("HTTP Error %d" % r.status_code)
			return r.status_code
		
		return r.status_code


