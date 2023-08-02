#import wx
#import wx.lib.newevent
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)
	
ofp = open(os.path.join(os.getcwd(), "output", "autorouter.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "autorouter.err"), "w")

sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "autorouter.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from queue import Queue

import json

from autorouter.fifo import Fifo

from autorouter.settings import Settings

from autorouter.triggers import Triggers, TriggerPointFront, TriggerPointRear
from autorouter.routerequest import RouteRequest
from autorouter.requestqueue import RequestQueue
from autorouter.turnout import Turnout
from autorouter.signal import Signal
from autorouter.block import Block
from autorouter.overswitch import OverSwitch
from autorouter.train import Train
from autorouter.route import Route

from autorouter.listener import Listener
from autorouter.rrserver import RRServer

class MainUnit:
	def __init__(self):
		logging.info("PSRY AutoRouter starting...")
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
		self.ReqQueue= RequestQueue(self)
		self.listener = None
		self.rrServer = None
		self.commandQ = Queue()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with server")
			self.listener = None
			return

		self.listener.start()
		self.ARTrains = []
		
		self.blocks["KOSN10S11"] = Block(self, "KOSN10S11", 0, 'W', True)
		self.blocks["KOSN20S21"] = Block(self, "KOSN20S21", 0, 'E', True)

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
	
							self.blocks[block].SetTrain(name, loco)
	
				elif cmd == "ar":
					action = parms["action"][0]
					trnm = parms["train"][0]
					if action == "add":
						self.AddTrain(trnm)
					elif action == "remove":
						self.RemoveTrain(trnm)
	
				elif cmd == "sessionID":
					self.sessionid = int(parms)
					logging.info("session ID %d" % self.sessionid)
					self.Request({"identify": {"SID": self.sessionid, "function": "AR"}})
					self.Request({"refresh": {"SID": self.sessionid}})
					
				elif cmd == "debug":
					tag = parms["tag"][0]
					logging.info("debug request with tag %s" % tag)
					self.DumpQueuedRequests()
	
				elif cmd == "end":
					if parms["type"] == "layout":
						self.requestRoutes()
					elif parms["type"] == "routes":
						self.requestTrains()
						
				elif cmd in ["disconnect", "exit"]:
					self.running = False
	
				else:
					if cmd not in ["control", "relay", "handswitch", "siglever", "breaker", "fleet", "trainsignal"]:
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
		if nState == 0:
			# remove any trains we know about from this block
			for tr in self.trains.values():
				if tr.IsInBlock(blkName):
					tr.DelBlock(blkName)

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
			
	def AddTrain(self, train):
		if train not in self.trains:
			return  # unknown train - skip
		
		logging.info("Adding train %s to AR" % train)
		if train not in self.ARTrains:
			self.ARTrains.append(train)
			
		tr = self.trains[train]
		block = tr.GetLatestBlock()
		if block is None:
			return 
		
		self.TrainAddBlock(train, block)
		
	def RemoveTrain(self, train):
		if train not in self.ARTrains:
			return 
		
		logging.info("Removing train %s from AR" % train)
		self.ARTrains.remove(train)
		
		self.DeleteQueuedRequests(train)

	def TrainAddBlock(self, train, block, released=False):
		if train not in self.ARTrains:
			# ignore trains not under AR control
			return
		
		logging.info("Train %s has moved into block %s" % (train, block))
		routeRequest = self.CheckTrainInBlock(train, block, TriggerPointFront)
		if routeRequest is None:
			return
		
		if self.EvaluateRouteRequest(routeRequest):
			self.SetupRoute(routeRequest)
		else:
			self.EnqueueRouteRequest(routeRequest)
			
	def TrainTailInBlock(self, train, block):
		if train not in self.ARTrains:
			# ignore trains not under AR control
			return
		
		logging.info("Train %s tail in block %s" % (train, block))
		routeRequest = self.CheckTrainInBlock(train, block, TriggerPointRear)
		if routeRequest is None:
			return
		
		if self.EvaluateRouteRequest(routeRequest):
			self.SetupRoute(routeRequest)
		else:
			self.EnqueueRouteRequest(routeRequest)

	def TrainRemoveBlock(self, train, block, blocks):
		if len(blocks) == 0:
			return 
		logging.info("Train %s has left block %s and is now in %s" % (train, block, ",".join(blocks)))

	def CheckTrainInBlock(self, train, block, triggerPoint):
		rtName = self.triggers.GetRoute(train, block)
		if rtName is None:
			logging.info("Train/block combination %s/%s not found" % (train, block))
			return None

		blockTriggerPoint = self.triggers.GetTriggerPoint(train, block)
		if blockTriggerPoint != triggerPoint:
			logging.info("Trigger point mismatch, wanted %s, got %s" % (triggerPoint, blockTriggerPoint))
			return None
		
		return RouteRequest(train, self.routes[rtName], block)

	def GetActiveRoute(self, osName):
		if osName in [ "SOSE", "SOSW" ]:
			for s in [ "S8L", "S8R" ]:
				if self.signals[s].GetAspect() != 0:
					return None
		
		return self.osList[osName].GetActiveRoute()

	def EvaluateRouteRequest(self, rteRq):
		logging.info("evaluating routeRequest %s" % rteRq.toString())
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		logging.info("evaluate route %s" % rname)
		rte = self.routes[rname]
		activeRte = self.GetActiveRoute(rte.GetOS())
		tolock = []
		siglock = []
		logging.info("active route = %s" % ("None" if activeRte is None else activeRte.GetName()))
		if activeRte is None or activeRte.GetName() != rname:
			logging.info("evaluating turnouts for route")
			for t in rte.GetTurnouts():
				logging.info("turnout: %s" % t)
				toname, state = t.split(":")
				logging.info("Locked: %s  state = %s" % (self.turnouts[toname].IsLocked(), self.turnouts[toname].GetState()))
				
				if self.turnouts[toname].IsLocked() and self.turnouts[toname].GetState() != state:
					#  turnout is locked AND we need to change it
					tolock.append(toname)
		#  else we are already on this route - no turnout evauation needed
		
		# look at state of exit block
		exitBlockAvailable = False
		ends = rte.GetEnds()
		if ends[0] == blkName:
			exitBlk = ends[1]
		else:
			exitBlk = ends[0]
			
		if exitBlk in self.blocks:
			b = self.blocks[exitBlk]
			state = b.GetState()
			clear = b.GetClear()
			for sbNm in [exitBlk+".E", exitBlk+".W"]:
				if sbNm in self.blocks:
					sb = self.blocks[sbNm]
					state += sb.GetState()
					clear += sb.GetClear()
					
			exitBlockAvailable = state == 0 and clear == 0
			logging.info("Exit block %s State = %d clear = %d" % (exitBlk, state, clear))
		else:
			state = None
			clear = None
		

		sigNm = rte.GetSignalForEnd(blkName)
		logging.info("Evaluating signal: %s" % sigNm)
		if sigNm is not None:
			logging.info("Locked: %s  aspect = %s" % (self.signals[sigNm].IsLocked(), self.signals[sigNm].GetAspect()))
			if self.signals[sigNm].IsLocked() and self.signals[sigNm].GetAspect() == 0:
				siglock.append(sigNm)

		if len(tolock) + len(siglock) == 0 and exitBlockAvailable and activeRte is not None:
			logging.info("eval true")
			return True  # OK to proceed with this route
		else:
			#  TODO - do something with the tolock and siglock arrays
			logging.info("Eval false to=%s sig=%s block %s state = %s clear = %s" % (str(tolock), str(siglock), exitBlk, str(state), str(clear)))
			return False  # this route is unavailable right now

	def SetupRoute(self, rteRq):
		rname = rteRq.GetName()
		blkName = rteRq.GetEntryBlock()
		logging.info("set up route %s" % rteRq.toString())
		rte = self.routes[rname]
		for t in rte.GetTurnouts():
			logging.info("Turnout %s" % t)
			toname, state = t.split(":")
			if self.turnouts[toname].GetState() != state:
				if not toname.startswith("P"):
					cmd = {"turnout": {"name": toname, "status": state}}
					self.ReqQueue.Append(cmd)
					logging.info("command sent: %s" % str(cmd))
				else:
					logging.info("skipping this turnout since we do not control Port")
			else:
				logging.info("turnout already in desired position - no command sent")

		sigNm = rte.GetSignalForEnd(blkName)
		if sigNm is not None:
			logging.info("signal %s" % sigNm)
			try:
				aspect = self.signals[sigNm].GetAspect()
			except:
				logging.info("Unable to retrieve signal aspect - assume 0")
				aspect = 0
				
			if aspect == 0:
				if not sigNm.startswith("P"):
					cmd = {"signal": {"name": sigNm, "aspect": -1}}
					self.ReqQueue.Append(cmd)
					logging.info("command sent: %s" % str(cmd))
				else:
					logging.info("skipping this signal since we do not control Port")
			else:
				logging.info("Current signal aspect (%s) allows movement - no command sent" % aspect)

	def EnqueueRouteRequest(self, rteRq):
		osNm = rteRq.GetOS()
		if osNm not in self.OSQueue:
			self.OSQueue[osNm] = Fifo()

		self.OSQueue[osNm].Append(rteRq)
		logging.info("Queued route request %s" % rteRq.toString())

	def EvaluateQueuedRequests(self):
		if len(self.OSQueue) == 0:
			return
		logging.info("evaluating queued requests")
		for osNm in self.OSQueue:
			logging.info("OS: %s" % osNm)
			req = self.OSQueue[osNm].Peek()
			if req is not None:
				logging.info("Request for block %s" % req.GetName())
				logging.info("%s" % req.toString())
				if self.EvaluateRouteRequest(req):
					logging.info("OK to proceed")
					self.OSQueue[osNm].Pop()
					logging.info("popping from queue for os %s" % osNm)
					self.SetupRoute(req)

		logging.info("end of queued requests")
		
	def DumpQueuedRequests(self):
		logging.info("Number of OSes with requests: %d" % len(self.OSQueue))
		for osNm in self.OSQueue:
			logging.info("OS: %s" % osNm)
			self.OSQueue[osNm].DumpQueue()
			logging.info("===================================")
		logging.info("Done with dump of queues")

	def DeleteQueuedRequests(self, train):
		logging.info("deleting queued request for train %s" % train)
		oslist = list(self.OSQueue.keys())
		for osNm in oslist:
			newQ = Fifo()
			req = self.OSQueue[osNm].Pop()
			while req is not None:
				if req.GetTrain() != train:
					newQ.Append(req)
					
				req = self.OSQueue[osNm].Pop()
				
			self.OSQueue[osNm] = newQ

	def Request(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)

main = MainUnit()
main.run()