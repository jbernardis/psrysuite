import wx
import wx.lib.newevent

import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import logging
logging.basicConfig(filename=os.path.join("logs", "atc.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

import json
import pprint

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
from atc.dccloco import DCCLoco
from atc.atclist import ATCListCtrl
from atc.listener import Listener
from atc.rrserver import RRServer
from atc.dccserver import DCCServer
from atc.ticker import Ticker

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 
(TickerEvent, EVT_TICKER) = wx.lib.newevent.NewEvent() 

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.sessionid = None
		self.settings = Settings()
		self.initialized = False
		
		self.posx = 0
		self.posy = 0

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.osList = {}
		self.trains = {}
		self.listener = None
		self.rrServer = None
		
		logging.info("psry atc server starting")

		self.SetTitle("PSRY ATC Server")
		
		self.atcList = ATCListCtrl(self, os.getcwd())

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.atcList)
		hsz.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		wx.CallAfter(self.Initialize)
		
	def SetPos(self):
		self.SetPosition((self.posx, self.posy))

	def Initialize(self):
		logging.info("enter initialize")
		self.Bind(EVT_DELIVERY, self.OnDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.OnDisconnectEvent)
		self.Bind(EVT_TICKER, self.OnTickerEvent)
		
		if not self.ProcessScripts():
			return

		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return
		self.listener.start()
		
		logging.info("socket connection created")
		
		self.dccRemote = DCCRemote(self.dccServer)
		
		self.ticker = Ticker(0.4, self.raiseTickerEvent)

		self.initialized = True
		self.SetPos()
		logging.info("exit initialize")

	def ProcessScripts(self):
		logging.info(os.path.join(os.getcwd(), "data", "layout.json"))
		try:
			with open(os.path.join(os.getcwd(), "data", "layout.json"), "r") as jfp:
				layout = json.load(jfp)
		except:
			logging.error("Unable to load layout file")
			return False
		
		subblocks = layout["subblocks"]
		submap = {}
		for blk, sublist in subblocks.items():
			for sub in sublist:
				submap[sub] = blk
		
		try:
			with open(os.path.join(os.getcwd(), "data", "simscripts.json"), "r") as jfp:
				scripts = json.load(jfp)
		except:
			logging.error("Unable to load scripts")
			return False
		
		self.scripts = {}
		
		for train, script in scripts.items():
			sigList = [[None, None, None]]
			for step in script:
				cmd = list(step.keys())[0]
				if cmd == "waitfor":
					sig = step[cmd]["signal"]
					osb = step[cmd]["os"]
					rte = step[cmd]["route"]
					sigList.append([sig, osb, rte])

			sigList.append([None, None, None])					
			sigx = 0

			steps = {}			
			for step in script:
				cmd = list(step.keys())[0]
				if cmd in ["placetrain", "movetrain"]:
					blk = step[cmd]["block"]
					if blk in submap:
						blk = submap[blk]
						
					steps[blk] = {
							"sigbehind": sigList[sigx][0],
							"sigahead": {
								   "signal": str(sigList[sigx+1][0]),
								   "os": str(sigList[sigx+1][1]),
								   "route": str(sigList[sigx+1][2])
							}
					}

				elif cmd == "waitfor":
					sigx += 1
			self.scripts[train] = steps
			
		return True
	
	def HaveScript(self, train):
		return train in self.scripts
	
	def GetSignalBehind(self, train, block):
		if not self.HaveScript(train):
			return None
		
		if block not in self.scripts[train]:
			return None
		
		return {"signal": self.scripts[train][block]["sigbehind"], "os": None, "route": None}
	
	def GetSignalAhead(self, train, block):
		if not self.HaveScript(train):
			return None
		
		if block not in self.scripts[train]:
			return None
		
		return self.scripts[train][block]["sigahead"]

	def tickerEvent(self):  # thread context
		if self.dccRemote.LocoCount() > 0:
			self.commandQ.put("{\"ticker\": []}")
			
	def raiseTickerEvent(self):
		evt = TickerEvent()
		wx.QueueEvent(self, evt)
		
	def OnTickerEvent(self, _):
		for dccl in self.dccRemote.GetDCCLocos():
			trnm = dccl.GetTrain()
			gs, ga = dccl.GetGoverningSignal()
			aspect = 0  # assume STOP

			if "os" in gs and gs["os"] is None:
				# if we are already in the OS, dont pay attention to the aspect as it is now red - just keep using
				# the old value
				aspect = ga
							
			elif "signal" in gs:
				signame = gs["signal"]
				if signame in self.signals:
					aspect = self.signals[signame].GetAspect()
					
				if "os" in gs and "route" in gs and aspect != 0:
					overswitch = gs["os"]
					route = gs["route"]
					if overswitch in self.osList and self.osList[overswitch].GetActiveRouteName() != route:
						# either we don't know that OS or its not set to the needed route
						aspect = 0
	
			dccl.SetGoverningAspect(aspect)
			self.dccRemote.SelectLoco(dccl)	
			
			step = dccl.GetSpeedStep()				
			self.dccRemote.ApplySpeedStep(step)
			
			self.atcList.RefreshTrain(dccl)

	def raiseDeliveryEvent(self, data): # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			print("Unable to parse (%s)" % data)
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)
			
	def OnDeliveryEvent(self, evt):  # thread context
		for cmd, parms in evt.data.items():
			#print("Received: %s: %s" % (cmd, parms))
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
				print("action = (%s)" % action)
				
				if action == "add":
					trnm = parms["train"][0]
					if not self.HaveScript(trnm):
						# we do not have a script for this train - reject the request
						self.RRRequest({"atcstatus": {"action": "reject", "train": trnm}})
						return
					
					tr = self.atcList.FindTrain(trnm)
					if tr is not None:
						return #ignore if we already have the train
					
					loco = parms["loco"][0]
					dccl = DCCLoco(trnm, loco)
					self.atcList.AddTrain(dccl)
					
					tr = self.trains[trnm]
					blk = tr.GetFirstBlock()
					dccl.SetGoverningSignal(self.GetSignalAhead(trnm, blk))
					self.dccRemote.SelectLoco(dccl)
						
				elif action == "delete":
					train = parms["train"][0]
					loco = parms["loco"][0]
					self.dccRemote.DropLoco(loco)
					
				elif action == "hide":
					if "x" in parms:
						self.posx = int(parms["x"][0])
					if "y" in parms:
						self.posy = int(parms["y"][0])
					print("show/reset, %s %s" % (self.posx, self.posy))
					self.Hide()
				
				elif action in ["show", "reset" ]:
					if "x" in parms:
						self.posx = int(parms["x"][0])
					if "y" in parms:
						self.posy = int(parms["y"][0])
					print("show/reset, %s %s" % (self.posx, self.posy))
					self.Show()
					self.SetPos()

			else:
				if cmd not in ["control", "relay", "handswitch", "siglever", "breaker", "fleet"]:
					logging.info("unknown command ignored: %s: %s" % (cmd, parms))


	def requestRoutes(self):
		if self.sessionid is not None:
			self.RRRequest({"refresh": {"SID": self.sessionid, "type": "routes"}})

	def requestTrains(self):
		if self.sessionid is not None:
			self.RRRequest({"refresh": {"SID": self.sessionid, "type": "trains"}})

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
		#self.ReqQueue.Resume(toName)

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
		dccl = self.dccRemote.GetDCCLocoByTrain(train)
		if dccl is None:
			logging.info("TrainAddBlock ignoring train %s because it is not on ATC" % train)
			return
		
		logging.info("Train %s has moved into block %s" % (train, block))
		
		# set governing signal to the signal behind us UNLESS we have already switched to the signal ahead of us
		gs = dccl.GetGoverningSignal()
		sig = self.GetSignalAhead(train, block)
		if gs != sig:
			gs = self.GetSignalBehind(train, block)
			dccl.SetGoverningSignal(gs)
			
  # routeRequest = self.CheckTrainInBlock(train, block, TriggerPointFront)
  # if routeRequest is None:
  # 	return
  #
  # if self.EvaluateRouteRequest(routeRequest):
  # 	self.SetupRoute(routeRequest)
  # else:
  # 	self.EnqueueRouteRequest(routeRequest)
			
	def TrainTailInBlock(self, train, block):
		dccl = self.dccRemote.GetDCCLocoByTrain(train)
		if dccl is None:
			logging.info("TrainTailInBlock ignoring train %s because it is not on ATC" % train)
			return
		
		logging.info("Train %s tail in block %s" % (train, block))
		
		gs = self.GetSignalAhead(train, block)
		dccl.SetGoverningSignal(gs)

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
		print("Train %s has left block %s and is now in %s" % (train, block, ",".join(blocks)))
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


	def RRRequest(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def OnDisconnectEvent(self, _):
		self.kill()
		
	def OnClose(self, evt):
		#self.kill()
		return
		
	def kill(self):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		
		try:
			self.ticker.stop()
		except:
			pass
		
		self.Destroy()

class App(wx.App):
	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
		self.frame = None

	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


ofp = open("atc.out", "w")
efp = open("atc.err", "w")

sys.stdout = ofp
sys.stderr = efp


app = App(False)
app.MainLoop()

logging.info("exiting program")