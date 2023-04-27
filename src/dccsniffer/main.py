import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "dccsniffer.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "dccsniffer.err"), "w")
sys.stdout = ofp
sys.stderr = efp

import json
import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "dccsniffer.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from dccsniffer.settings import Settings
from dccsniffer.sniffer import Sniffer
from dccsniffer.rrserver import RRServer
from dccsniffer.listener import Listener

class MainUnit:
	def __init__(self):
		self.settings = Settings()
		
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		
		self.sniffer = Sniffer()
		self.sniffer.connect(self.settings.dccsniffertty)
		if not self.sniffer.isConnected():
			logging.error("Unable to connect to port %s for DCC sniffer" % self.settings.dccsniffertty)
			exit(1)
			
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			exit(1)
		self.listener.start()
	
	def run(self):
		self.sniffer.run(self.rrServer)
		
	def raiseDeliveryEvent(self, data):  # thread context
		jdata = json.loads(data)
		for cmd, parms in jdata.items():
			if cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("session ID %d" % self.sessionid)
				self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "DCCSNIFFER"}})
		
	def raiseDisconnectEvent(self): # thread context
		self.sniffer.kill()



main = MainUnit()
main.run()