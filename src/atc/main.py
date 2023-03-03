#import wx
#import wx.lib.newevent
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import logging
logging.basicConfig(filename=os.path.join("logs", "atc.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from queue import Queue

import json

#from atc.fifo import Fifo

from atc.settings import Settings
#
# from autorouter.triggers import Triggers, TriggerPointFront, TriggerPointRear
# from autorouter.routerequest import RouteRequest
# from autorouter.requestqueue import RequestQueue
from atc.turnout import Turnout
from atc.signal import Signal
from atc.block import Block
from atc.overswitch import OverSwitch
from atc.train import Train
from atc.route import Route

from atc.dccremote import DCCRemote

from atc.listener import Listener
from atc.rrserver import RRServer
from atc.dccserver import DCCServer
from atc.ticker import Ticker

class MainUnit:
	def __init__(self):
		logging.info("PSRY ATC Server starting...")
		self.sessionid = None
		self.settings = Settings()

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.osList = {}
		self.trains = {}
		self.listener = None
		self.rrServer = None
		self.commandQ = Queue()

		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return
		
		self.dccRemote = DCCRemote(self.dccServer)

		self.listener.start()
		
		self.ticker = Ticker(0.4, self.tickerEvent)

		logging.info("finished initialize")

	def raiseDeliveryEvent(self, data):  # thread context
		self.commandQ.put(data)
		
	def raiseDisconnectEvent(self): # thread context
		self.commandQ.put("{\"disconnect\": []}")
		
	def tickerEvent(self):  # thread context
		if self.dccRemote.LocoCount() > 0:
			self.commandQ.put("{\"ticker\": []}")

	def run(self):
		if self.listener is None:
			return 
		
		self.running = True
		while self.running:
			data = self.commandQ.get()
			jdata = json.loads(data)
			logging.info("Received (%s)" % data)
			for cmd, parms in jdata.items():
				if cmd == "ticker":
					for t in self.dccRemote.GetLocos():
						print("What to do with train %s" % t)
						
				elif cmd == "turnout":
					for p in parms:
						turnout = p["name"]
						state = p["state"]
						if turnout not in self.turnouts:
							self.turnouts[turnout] = Turnout(self, turnout, state)
						else:
							self.turnouts[turnout].SetState(state)
	
				elif cmd == "turnoutlock":
					for p in parms:
						toName = p["name"]
						lock = int(p["state"])
						if toName in self.turnouts:
							self.turnouts[toName].Lock(lock != 0)
	
				elif cmd == "block":
					for p in parms:
						block = p["name"]
						state = p["state"]
						if block not in self.blocks:
							self.blocks[block] = Block(self, block, state, 'E', False)
						else:
							b = self.blocks[block]
							b.SetState(state)
	
				elif cmd == "blockdir":
					for p in parms:
						block = p["block"]
						direction = p["dir"]
						if block not in self.blocks:
							self.blocks[block] = Block(self, block, 0, direction, False)
						else:
							b = self.blocks[block]
							b.SetDirection(direction)
	
				elif cmd == "blockclear":
					for p in parms:
						block = p["block"]
						clear = p["clear"]
						if block not in self.blocks:
							self.blocks[block] = Block(self, block, 0, 'E', clear != 0)
						else:
							b = self.blocks[block]
							b.SetClear(clear)
	
				elif cmd == "signal":
					for p in parms:
						sigName = p["name"]
						aspect = int(p["aspect"])
						if sigName not in self.signals:
							self.signals[sigName] = Signal(self, sigName, aspect)
						else:
							self.signals[sigName].SetAspect(aspect)
	
				elif cmd == "signallock":
					for p in parms:
						sigName = p["name"]
						lock = int(p["state"])
						if sigName in self.signals:
							self.signals[sigName].Lock(lock != 0)
	
				elif cmd == "routedef":
					name = parms["name"]
					os = parms["os"]
					ends = parms["ends"]
					signals = parms["signals"]
					turnouts = parms["turnouts"]
					if os not in self.osList:
						self.osList[os] = OverSwitch(os)
	
					rte = Route(self, name, os, ends, signals, turnouts)
					self.routes[name] = rte
					self.osList[os].AddRoute(rte)
	
				elif cmd == "setroute":
					for p in parms:
						blknm = p["block"]
						rtnm = p["route"]
						if blknm not in self.osList:
							self.osList[blknm] = OverSwitch(blknm)
	
						self.osList[blknm].SetActiveRoute(rtnm)
	
				elif cmd == "settrain":
					for p in parms:
						block = p["block"]
						name = p["name"]
						loco = p["loco"]
	
						if name is None:
							self.blocks[block].SetTrain(None, None)
						else:
							if name not in self.trains:
								self.trains[name] = Train(self, name, loco)
	
							self.trains[name].AddBlock(block)
	
							self.blocks[block].SetTrain(name, loco)
	
				elif cmd == "sessionID":
					self.sessionid = int(parms)
					logging.info("session ID %d" % self.sessionid)
					self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "ATC"}})
	
				elif cmd == "end":
					if parms["type"] == "layout":
						self.requestRoutes()
					elif parms["type"] == "routes":
						self.requestTrains()
						
				elif cmd in ["disconnect", "exit"]:
					self.running = False
					
				elif cmd == "atc":
					print("ATC command: %s" % str(parms))
					action = parms["action"][0]
					
					if action == "add":
						train = parms["train"][0]
						loco = parms["loco"][0]
						self.dccRemote.SelectLoco(loco)
						self.dccRemote.PrintList()
							
					elif action == "delete":
						train = parms["train"][0]
						loco = parms["loco"][0]
						self.dccRemote.DropLoco(loco)
						self.dccRemote.PrintList()
	
				else:
					if cmd not in ["control", "relay", "handswitch", "siglever", "breaker", "fleet"]:
						logging.info("unknown command ignored: %s: %s" % (cmd, parms))

		logging.info("terminating socket listener")
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass

		logging.info("terminating timer thread")		
		try:
			self.ticker.stop()
		except:
			pass


	def requestRoutes(self):
		if self.sessionid is not None:
			self.rrServer.SendRequest({"refresh": {"SID": self.sessionid, "type": "routes"}})

	def requestTrains(self):
		if self.sessionid is not None:
			self.rrServer.SendRequest({"refresh": {"SID": self.sessionid, "type": "trains"}})

	def SignalLockChange(self, sigName, nLock):
		logging.info("signal %s lock has changed %s" % (sigName, str(nLock)))
		self.EvaluateQueuedRequests()

	def SignalAspectChange(self, sigName, nAspect):
		logging.info("signal %s aspect has changed %d" % (sigName, nAspect))
		self.EvaluateQueuedRequests()

	def TurnoutLockChange(self, toName, nLock):
		logging.info("turnout %s lock has changed %s" % (toName, str(nLock)))
		self.EvaluateQueuedRequests()

	def TurnoutStateChange(self, toName, nState):
		logging.info("turnout %s state has changed %s" % (toName, nState))
		self.EvaluateQueuedRequests()
		self.ReqQueue.Resume(toName)

	def BlockDirectionChange(self, blkName, nDirection):
		logging.info("block %s has changed direction: %s" % (blkName, nDirection))
		self.EvaluateQueuedRequests()

	def BlockStateChange(self, blkName, nState):
		logging.info("block %s has changed state: %d" % (blkName, nState))
		self.EvaluateQueuedRequests()

	def BlockClearChange(self, blkName, nClear):
		logging.info("block %s has changed clear: %s" % (blkName, str(nClear)))
		self.EvaluateQueuedRequests()

	def BlockTrainChange(self, blkName, oldTrain, oldLoco, newTrain, newLoco):
		if oldTrain is not None:
			try:
				if self.trains[oldTrain].DelBlock(blkName) == 0:
					del(self.trains[oldTrain])
			except KeyError:
				pass

	def TrainAddBlock(self, train, block):
		logging.info("Train %s has moved into block %s" % (train, block))
  # routeRequest = self.CheckTrainInBlock(train, block, TriggerPointFront)
  # if routeRequest is None:
  # 	return
  #
  # if self.EvaluateRouteRequest(routeRequest):
  # 	self.SetupRoute(routeRequest)
  # else:
  # 	self.EnqueueRouteRequest(routeRequest)
			
	def TrainTailInBlock(self, train, block):
		logging.info("Train %s tail in block %s" % (train, block))
  # routeRequest = self.CheckTrainInBlock(train, block, TriggerPointRear)
  # if routeRequest is None:
  # 	return
  #
  # if self.EvaluateRouteRequest(routeRequest):
  # 	self.SetupRoute(routeRequest)
  # else:
  # 	self.EnqueueRouteRequest(routeRequest)

	def TrainRemoveBlock(self, train, block, blocks):
		logging.info("Train %s has left block %s and is now in %s" % (train, block, ",".join(blocks)))
		pass

	def CheckTrainInBlock(self, train, block, triggerPoint):
		rtName = self.triggers.GetRoute(train, block)
		if rtName is None:
			logging.info("train/block combination %s/%s not found" % (train, block))
			return None

		blockTriggerPoint = self.triggers.GetTriggerPoint(train, block)
		if blockTriggerPoint != triggerPoint:
			logging.info("trigger point mismatch, wanted %s, got %s" % (triggerPoint, blockTriggerPoint))
			return None
		
		return None #outeRequest(train, self.routes[rtName], block)

	def EvaluateRouteRequest(self, rteRq):
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		logging.info("evaluate route %s" % rname)
		rte = self.routes[rname]
		os = self.osList[rte.GetOS()]
		activeRte = os.GetActiveRoute()
		tolock = []
		siglock = []
		if activeRte is None or activeRte.GetName() != rname:
			for t in rte.GetTurnouts():
				toname, state = t.split(":")
				if self.turnouts[toname].IsLocked() and self.turnouts[toname].GetState() != state:
					#  turnout is locked AND we need to change it
					tolock.append(toname)
		#  else we are already on this route - no turnout evauation needed

		sigNm = rte.GetSignalForEnd(blkName)
		if sigNm is not None:
			if self.signals[sigNm].IsLocked():
				siglock.append(sigNm)

		if len(tolock) + len(siglock) == 0:
			logging.info("eval true")
			return True  # OK to proceed with this route
		else:
			#  TODO - do something with the tolock and siglock arrays
			logging.info("Eval false %s %s" % (str(tolock), str(siglock)))
			return False  # this route is unavailable right now

	def SetupRoute(self, rteRq):
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		logging.info("set up route %s" % rname)
		rte = self.routes[rname]
		for t in rte.GetTurnouts():
			toname, state = t.split(":")
			if self.turnouts[toname].GetState() != state:
				self.ReqQueue.Append({"turnout": {"name": toname, "status": state}})

		sigNm = rte.GetSignalForEnd(blkName)
		if sigNm is not None:
			self.ReqQueue.Append({"signal": {"name": sigNm, "aspect": -1}})

 # def EnqueueRouteRequest(self, rteRq):
 # 	osNm = rteRq.GetOS()
 # 	if osNm not in self.OSQueue:
 # 		self.OSQueue[osNm] = Fifo()
 #
 # 	self.OSQueue[osNm].Append(rteRq)

	def EvaluateQueuedRequests(self):
		logging.info("evaluating queued requests")
  # for osNm in self.OSQueue:
  # 	logging.info("OS: %s" % osNm)
  # 	req = self.OSQueue[osNm].Peek()
  # 	if req is not None:
  # 		logging.info("Request for block %s" % req.GetName())
  # 		if self.EvaluateRouteRequest(req):
  # 			logging.info("OK to proceed")
  # 			self.OSQueue[osNm].Pop()
  # 			self.SetupRoute(req)
  # logging.info("end of queued requests")


	def Request(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)


main = MainUnit()
main.run()
print("ATC server exiting...")