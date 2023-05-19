#import wx
#import wx.lib.newevent
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "advisor.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "advisor.err"), "w")
sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "advisor.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from queue import Queue

import json

from advisor.settings import Settings

from advisor.triggers import Triggers, TriggerPointFront, TriggerPointRear
from advisor.routerequest import RouteRequest
from advisor.turnout import Turnout
from advisor.signal import Signal
from advisor.block import Block
from advisor.overswitch import OverSwitch
from advisor.train import Train
from advisor.route import Route

from advisor.listener import Listener
from advisor.rrserver import RRServer

class MainUnit:
	def __init__(self):
		logging.info("PSRY Adviser starting...")
		self.sessionid = None
		self.settings = Settings()

		self.triggers = Triggers()

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.osList = {}
		self.trains = {}
		self.OSQueue = {}
		self.listener = None
		self.rrServer = None
		self.commandQ = Queue()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return

		
		self.blocks["KOSN10S11"] = Block(self, "KOSN10S11", 0, 'W', True)
		self.blocks["KOSN20S21"] = Block(self, "KOSN20S21", 0, 'E', True)

		self.listener.start()

		logging.info("finished initialize")

	def raiseDeliveryEvent(self, data):  # thread context
		self.commandQ.put(data)
		
	def raiseDisconnectEvent(self): # thread context
		self.commandQ.put("{\"disconnect\": []}")

	def run(self):
		if self.listener is None:
			return 
		
		self.running = True
		while self.running:
			data = self.commandQ.get()
			jdata = json.loads(data)
			for cmd, parms in jdata.items():
				if cmd == "turnout":
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
					ends = [None if e == "-" else e for e in parms["ends"]]
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
							
							self.CheckTrainAtOrigin(name, block)
	
							self.blocks[block].SetTrain(name, loco)
	
				elif cmd == "sessionID":
					self.sessionid = int(parms)
					logging.info("session ID %d" % self.sessionid)
					self.Request({"identify": {"SID": self.sessionid, "function": "ADVISOR"}})
					self.Request({"refresh": {"SID": self.sessionid}})
	
				elif cmd == "end":
					if parms["type"] == "layout":
						self.requestRoutes()
					elif parms["type"] == "routes":
						self.requestTrains()
						
				elif cmd in ["disconnect", "exit"]:
					self.running = False
	
				else:
					if cmd not in ["control", "relay", "handswitch", "siglever", "breaker", "fleet"]:
						logging.info("unknown command ignored: %s: %s" % (cmd, parms))

		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass


	def requestRoutes(self):
		if self.sessionid is not None:
			self.Request({"refresh": {"SID": self.sessionid, "type": "routes"}})

	def requestTrains(self):
		if self.sessionid is not None:
			self.Request({"refresh": {"SID": self.sessionid, "type": "trains"}})

	def SignalLockChange(self, sigName, nLock):
		logging.info("signal %s lock has changed %s" % (sigName, str(nLock)))

	def SignalAspectChange(self, sigName, nAspect):
		logging.info("signal %s aspect has changed %d" % (sigName, nAspect))

	def TurnoutLockChange(self, toName, nLock):
		logging.info("turnout %s lock has changed %s" % (toName, str(nLock)))

	def TurnoutStateChange(self, toName, nState):
		logging.info("turnout %s state has changed %s" % (toName, nState))

	def BlockDirectionChange(self, blkName, nDirection):
		logging.info("block %s has changed direction: %s" % (blkName, nDirection))

	def BlockStateChange(self, blkName, nState):
		logging.info("block %s has changed state: %d" % (blkName, nState))

	def BlockClearChange(self, blkName, nClear):
		logging.info("block %s has changed clear: %s" % (blkName, str(nClear)))

	def BlockTrainChange(self, blkName, oldTrain, oldLoco, newTrain, newLoco):
		if oldTrain is not None:
			try:
				if self.trains[oldTrain].DelBlock(blkName) == 0:
					del(self.trains[oldTrain])
			except KeyError:
				pass

	def TrainAddBlock(self, train, block):
		logging.info("Train %s has moved into block %s" % (train, block))
		routeRequest = self.CheckTrainInBlock(train, block, TriggerPointFront)
		if routeRequest is None:
			return
		
		self.ReportRouteRequest(routeRequest)
			
	def TrainTailInBlock(self, train, block):
		logging.info("Train %s tail in block %s" % (train, block))
		routeRequest = self.CheckTrainInBlock(train, block, TriggerPointRear)
		if routeRequest is None:
			return
		
		self.ReportRouteRequest(routeRequest)		
		
	def ReportRouteRequest(self, routeRequest):	
		osnm = routeRequest.GetOS()
		osblk = self.osList[osnm]			
		actRt = osblk.GetActiveRoute()
		if actRt is not None:
			actRtNm = actRt.GetName()
			
			neededRt = routeRequest.GetRoute()
			entryBlkNm = routeRequest.GetEntryBlock()
			exitBlkNm = neededRt.GetOtherEnd(entryBlkNm)
			signalNm = neededRt.GetSignalForEnd(entryBlkNm)
			aspect = self.signals[signalNm].GetAspect()
			if actRtNm == routeRequest.GetName() and aspect != 0:
				logging.info("already set to the active route with a signal")
				return

		routeRequest.Print()
		logging.info("Advise: Train %s needs a route to block %s via signal %s" % (routeRequest.GetTrain(), exitBlkNm, signalNm))
		req = {"advice": {"msg": "Train %s route to %s via signal %s)" % (routeRequest.GetTrain(), exitBlkNm, signalNm)}}
		self.Request(req)

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
		
		if self.CheckTrainAtTerminus(train, block):
			logging.info("Train %s is at its terminus - no need for further advice" % train)
			return None
		
		return RouteRequest(train, self.routes[rtName], block)
	
	def CheckTrainAtOrigin(self, train, block):
		if self.trains[train].IsAtOrigin() and block != self.triggers.GetOrigin(train):
			self.trains[train].SetAtOrigin(False)
			
	def CheckTrainAtTerminus(self, train, block):
		if not self.trains[train].IsAtOrigin() and block == self.triggers.GetTerminus(train):
			return True
		
		return False

	def Request(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)


main = MainUnit()
main.run()