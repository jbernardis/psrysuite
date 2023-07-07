import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "rrserver.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "rrserver.err"), "w")

sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "rrserver.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

import json
import socket
import time
import queue
import threading

from subprocess import Popen

from settings import Settings
from railroad import Railroad
from httpserver import HTTPServer
from sktserver import SktServer
from routedef import RouteDef

from clientlist import ClientList
from trainlist import TrainList
from dccserver import DCCHTTPServer

class ServerMain:
	def __init__(self):
		self.socketServer = None
		self.dispServer = None
		logging.info("rr server starting")
		
		self.commandsSeen = []
		
		self.pidAR = None
		self.pidADV = None
		self.pidDispatch = None
		self.pidDCC = None
		self.timeValue = None
		
		self.cmdQ = queue.Queue()

		self.routeDefs = {}
		self.CrossoverPoints = []

		hostname = socket.gethostname()
		self.ip = socket.gethostbyname(hostname)

		self.clients = {}

		self.settings = Settings()
		
		if self.settings.ipaddr is not None:
			if self.ip != self.settings.ipaddr:
				logging.info("Using configured IP Address (%s) instead of retrieved IP Address: (%s)" % (self.settings.ipaddr, self.ip))
				self.ip = self.settings.ipaddr

		logging.info("Creating railroad object")
		self.rr = Railroad(self, self.rrEventReceipt, self.settings)
		self.clientList = ClientList(self)
		self.trainList = TrainList(self)
		
		self.Initialize()

	def Initialize(self):
		self.CreateDispatchTable()
		try:
			self.dispServer = HTTPServer(self.ip, self.settings.serverport, self.dispCommandReceipt, self, self.rr)
		except Exception as e:
			print("Unable to Create HTTP server for IP address %s (%s)" % (self.ip, str(e)))
			self.Shutdown()
			
		logging.info("HTTP Server created")

		logging.info("Starting Socket server at address: %s:%d" % (self.ip, self.settings.socketport))
		self.socketServer = SktServer(self.ip, self.settings.socketport, self.socketEventReceipt)
		self.socketServer.start()
		
		logging.info("socket server started - starting DCC HTTP Server")
		
		if not self.settings.simulation:
			self.StartDCCServer()
		
		logging.info("DCC HTTP server successfully started")
		self.rr.Initialize()
		
	def DelayedStartup(self, _):
		print("delayed startup")

		if not self.settings.simulation:
			pname = os.path.join(os.getcwd(), "dccsniffer", "main.py")
			pid = Popen([sys.executable, pname]).pid
			logging.info("started DCC sniffer process as PID %d" % pid)

	def StartDCCServer(self):
		self.DCCServer = DCCHTTPServer(self.settings.ipaddr, self.settings.dccserverport, self.settings.dcctty)
		if not self.DCCServer.IsConnected():
			logging.error("Failed to open DCC bus on device %s.  Exiting..." % self.settings.dcctty)
			print("Failed to open DCC bus on device %s.  Exiting..." % self.settings.dcctty)
			#exit(1)

	def socketEventReceipt(self, cmd):
		print("received socket connection request: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def NewClient(self, cmd):
		addr = cmd["addr"]
		skt = cmd["socket"]
		sid = cmd["SID"]
		logging.info("New Client connecting from address: %s:%s" % (addr[0], addr[1]))
		self.socketServer.sendToOne(skt, addr, {"sessionID": sid})
		self.clients[addr] = [skt, sid]
		self.refreshClient(addr, skt)
		self.clientList.AddClient(addr, skt, sid, None)

	def DelClient(self, cmd):
		addr = cmd["addr"]
		logging.info("Disconnecting Client from address: %s:%s" % (addr[0], addr[1]))
		try:
			del self.clients[addr]
		except KeyError:
			pass
		
		f = self.clientList.GetFunctionAtAddress(addr)
		self.clientList.DelClient(addr)
		
		if f == "DISPATCH":
			self.deleteClients(["AR", "ADVISOR", "ATC"])
			self.pidAR = None
			self.pidADV = None
					
	def deleteClients(self, clist):
		for cname in clist:
			addrList = self.clientList.GetFunctionAddress(cname)
			for addr, _ in addrList:
				self.socketServer.deleteSocket(addr)
				
	def GetSessions(self):
		return self.clientList.GetClients()
				
	def generateLayoutFile(self):
		routes = {}
		for rte in self.routeDefs.values():
			r = rte.FormatRoute()["routedef"]
			tos = [t.split(":") for t in r["turnouts"]]
			routes[r["name"]] = {"os": r["os"], "ends": r["ends"], "signals": r["signals"], "turnouts": tos}

		subblocks = self.rr.GetSubBlockInfo()
		sbList = []
		for sbl in subblocks.values():
			sbList.extend(sbl)
			
		blks = self.rr.GetBlockInfo()
		blocks = {}
		for bnm, bdir in blks:
			if bnm in sbList:
				continue
			
			if bnm.endswith(".W") or bnm.endswith(".E"):
				sb = bnm[-1]
				bnm = bnm[:-2]
			else:
				sb = None
				
			if bnm not in blocks:
				blocks[bnm] = {"east": 0, "sbeast": None, "sbwest": None}
				
			if sb == "W":
				blocks[bnm]["sbwest"] = ("%s.W" % bnm)
			elif sb == "E":
				blocks[bnm]["sbeast"] = ("%s.E" % bnm)
			else:
				blocks[bnm]["east"] = bdir

		# include definitions for pseudo blocks
		blocks["K10"] =       { "east": 0, "sbeast": None, "sbwest": None }
		blocks["KOSN10S11"] = { "east": 0, "sbeast": None, "sbwest": None }
		blocks["KOSN20S21"] = { "east": 1, "sbeast": None, "sbwest": None }
				
		subblocks = self.rr.GetSubBlockInfo()
			
		layout = {"routes": routes, "blocks": blocks, "subblocks": subblocks, "crossover": self.CrossoverPoints}
		with open(os.path.join(os.getcwd(), "data", "layout.json"), "w") as jfp:
			json.dump(layout, jfp, sort_keys=True, indent=2)


	def refreshClient(self, addr, skt):
		if self.timeValue is not None:
			m = {"clock": [{ "value": self.timeValue}]}
			self.socketServer.sendToOne(skt, addr, m)
		
		for m in self.rr.GetCurrentValues():
			self.socketServer.sendToOne(skt, addr, m)
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "layout"}})

	def sendTrainInfo(self, addr, skt):
		print("send trtain info")
		for m in self.trainList.GetSetTrainCmds():
			self.socketServer.sendToOne(skt, addr, m)
		print("sending end trains")
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "trains"}})
		print("back")

	def sendRouteDefs(self, addr, skt):
		print("send route defs")
		for rte in self.routeDefs.values():
			self.socketServer.sendToOne(skt, addr, rte.FormatRoute())
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "routes"}})
		
	def sendSubBlocks(self, addr, skt):
		print("send sub blocks")
		subs = self.rr.GetSubBlockInfo()
		self.socketServer.sendToOne(skt, addr, {"subblocks": subs})

	def rrEventReceipt(self, cmd):
		print("RR Event receipt: %s" % str(cmd))
		self.socketServer.sendToAll(cmd)

	def dispCommandReceipt(self, cmd): # thread context
		print("HTTP Event: %s" % str(cmd))
		self.cmdQ.put(cmd)
		
	def CreateDispatchTable(self):					
		self.dispatch = {
			"interval": 	self.DoInterval,
			"clock":    	self.DoClock,
			
			"newclient":	self.NewClient,
			"delclient":	self.DelClient,
			"identify": 	self.DoIdentify,
			"refresh":		self.DoRefresh,
			
			"routedef": 	self.DoRouteDef,
			"routedefs":	self.DoRouteDefs,
			"crossover":	self.DoCrossOver,
			"genlayout":	self.DoGenLayout,
			
			"fleet":		self.DoFleet,
			"control":		self.DoControl,
			
			"settrain":		self.DoSetTrain,
			"renametrain":	self.DoRenameTrain,
			"trainsignal":	self.DoTrainSignal,
			"movetrain":	self.DoMoveTrain,
			"removetrain":	self.DoRemoveTrain,
			"traincomplete":self.DoTrainComplete,
			
			"signal":   	self.DoSignal,
			"signallock":	self.DoSignalLock,
			"turnout":  	self.DoTurnout,
			"turnoutlock":	self.DoTurnoutLock,
			"setroute": 	self.DoSetRoute,
			"nxbutton":		self.DoNXButton,
			"blockdir":		self.DoBlockDir,
			"blockdirs":	self.DoBlockDirs,
			"blockclear":	self.DoBlockClear,
			"indicator":	self.DoIndicator,
			"relay":		self.DoRelay,
			"handswitch":	self.DoHandSwitch,
			"districtlock":	self.DoDistrictLock,
			
			"close":		self.DoClose,			
			"advice":		self.DoAdvice,
			"alert":		self.DoAlert,
			"server":		self.DoServer,
			
			"autorouter":	self.DoAutorouter,
			"ar":			self.DoAR,
			"advisor":		self.DoAdvisor,
			"atc":			self.DoATC,
			"atcrequest":	self.DoATCRequest,
			"atcstatus":	self.DoATCStatus,
			
			"debug":		self.DoDebug,
			"simulate": 	self.DoSimulate,
			
			"quit":			self.DoQuit,
			"delayedstartup":
							self.DelayedStartup
		}


	def ProcessCommand(self, cmd):
			
		verb = cmd["cmd"][0]
		if verb != "interval":
			try:
				jstr = json.dumps(cmd)
			except:
				jstr = str(cmd)
			logging.info("Command receipt: %s" % jstr)
			print(verb)
		
		try:
			self.dispatch[verb](cmd)
		except KeyError:
			print("Command not yet supported: %s" % verb)
			
	def DoInterval(self, _):
		self.rr.OutIn()

	def DoSignal(self, cmd):
		signame = cmd["name"][0]
		aspect = int(cmd["aspect"][0])
		self.rr.SetAspect(signame, aspect)

	def DoSignalLock(self, cmd):			
		signame = cmd["name"][0]
		status = int(cmd["status"][0])
		
		self.rr.SetSignalLock(signame, status)
				
	def DoTurnout(self, cmd):
		swname = cmd["name"][0]
		status = cmd["status"][0]

		self.rr.SetOutPulseTo(swname, status)
		
	def DoNXButton(self, cmd):
		try:
			bentry = cmd["entry"][0]
		except (IndexError, KeyError):
			bentry = None
		try:
			bexit = cmd["exit"][0]
		except (IndexError, KeyError):
			bexit = None
		try:
			button = cmd["button"][0]
		except (IndexError, KeyError):
			button = None

		if bentry and bexit:
			self.rr.SetOutPulseNXB(bentry)
			self.rr.SetOutPulseNXB(bexit)
		else:
			self.rr.SetOutPulseNXB(button)
		
	def DoTurnoutLock(self, cmd):
		swname = cmd["name"][0]
		status = int(cmd["status"][0])

		self.rr.SetTurnoutLock(swname, status)
			
	def DoHandSwitch(self, cmd):
		hsname = cmd["name"][0]
		stat = int(cmd["status"][0])

		self.rr.SetHandswitch(hsname, stat)

	def DoSetRoute(self, cmd):
		blknm = cmd["block"][0]
		try:
			route = cmd["route"][0]
		except (IndexError, KeyError):
			route = None

		if route is None:
			ends = None
			signals = None
		else:
			try:
				ends = [None if e == "-" else e for e in cmd["ends"][0:2]]
			except (IndexError, KeyError):
				ends = None
			try:
				signals = cmd["signals"][0:2]
			except (IndexError, KeyError):
				signals = None

		self.rr.SetOSRoute(blknm, route, ends, signals)
		resp = {"setroute": [{ "block": blknm, "route": route}]}
		if ends is not None:
			resp["setroute"][0]["ends"] = ["-" if e is None else e for e in ends]
		if signals is not None:
			resp["setroute"][0]["signals"] = signals

		self.socketServer.sendToAll(resp)

	def DoIndicator(self, cmd):
		indname = cmd["name"][0]
		value = int(cmd["value"][0])

		self.rr.SetIndicator(indname, value == 1)
		# indicator information is always echoed to all listeners
		resp = {"indicator": [{ "name": indname, "value": value}]}
		self.socketServer.sendToAll(resp)

	def DoRelay(self, cmd):
		relay = cmd["block"][0]+".srel"
		status = int(cmd["status"][0])

		self.rr.SetRelay(relay, status)
		
	def DoClock(self, cmd):
		value = cmd["value"][0]
		resp = {"clock": [{ "value": value}]}
		self.timeValue = value
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("TRACKER")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)
			
	def DoSimulate(self, cmd):
		action = cmd["action"][0]
		if action == "occupy":
			block = cmd["block"][0]
			state = int(cmd["state"][0])
			self.rr.OccupyBlock(block, state)
			
		elif action == "breaker":
			brkname = cmd["breaker"][0]
			state = int(cmd["state"][0])
			self.rr.SetBreaker(brkname, state)
			
		elif action == "routein":
			rtname = cmd["name"][0]
			self.rr.SetRouteIn(rtname)
			
		elif action == "turnoutpos":
			toname = cmd["turnout"][0]
			normal = cmd["normal"][0] == "1"
			self.rr.SetTurnoutPos(toname, normal)
			
	def DoIdentify(self, cmd):
		sid = int(cmd["SID"][0])
		function = cmd["function"][0]
		self.clientList.SetSessionFunction(sid, function)
		if function == "DISPATCH":
			self.deleteClients(["AR", "ADVISOR", "ATC"])
			self.pidAR = None
			self.pidADV = None
			
	def DoRouteDef(self, cmd):
		name = cmd["name"][0]
		osNm = cmd["os"][0]
		try:
			signals = cmd["signals"]
		except KeyError:
			signals = []
		try:
			turnouts = cmd["turnouts"]
		except KeyError:
			turnouts = []
		try:
			ends = [None if e == "-" else e for e in cmd["ends"]]
		except KeyError:
			ends = [None, None]

		self.routeDefs[name] = (RouteDef(name, osNm, ends, signals, turnouts))
		
	def DoRouteDefs(self, cmd):
		data = json.loads(cmd["data"][0])
		for r in data:
			name = r["name"]
			osNm = r["os"]
			try:
				signals = r["signals"]
			except KeyError:
				signals = []
			try:
				turnouts = r["turnouts"]
			except KeyError:
				turnouts = []
			try:
				ends = [None if e == "-" else e for e in r["ends"]]
			except KeyError:
				ends = [None, None]

			self.routeDefs[name] = (RouteDef(name, osNm, ends, signals, turnouts))
			
	def DoCrossOver(self, cmd):
		self.CrossoverPoints = []
		for b in cmd["data"]:
			self.CrossoverPoints.append(b.split(":"))
			
	def DoGenLayout(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH")
		if len(addrList) == 0:
			logging.error("Cannot generate layout information until dispatcher has connected")
		else:
			self.generateLayoutFile()
			logging.info("Layout file has been generated")
					
	def DoFleet(self, cmd):
		signame = cmd["name"][0]
		value = int(cmd["value"][0])
		self.rr.SetSignalFleet(signame, value)
		resp = {"fleet": [{"name": signame, "value": value}]}
		# fleeting changes are always echoed back to all listeners
		self.socketServer.sendToAll(resp)
		
	def DoDistrictLock(self, cmd):
		name = cmd["name"][0]
		value = cmd["value"]

		self.rr.SetDistrictLock(name, [int(v) for v in value])
			
	def DoControl(self, cmd):
		name = cmd["name"][0]
		value = int(cmd["value"][0])

		self.rr.SetControlOption(name, value)
		
	def DoQuit(self, _):
		self.Shutdown()

	def DoBlockDir(self, cmd):
		block = cmd["block"][0]
		direction = cmd["dir"][0]
		self.rr.SetBlockDirection(block, direction)

	def DoBlockDirs(self, cmd):
		data = json.loads(cmd["data"][0])
		for b in data:
			block = b["block"]
			direction = b["dir"]
			self.rr.SetBlockDirection(block, direction)

	def DoBlockClear(self, cmd):
		block = cmd["block"][0]
		clear = cmd["clear"][0]
		self.rr.SetBlockClear(block, clear == "1")
		
	def DoRefresh(self, cmd):
		sid = int(cmd["SID"][0])
		for addr, data in self.clients.items():
			if data[1] == sid:
				skt = data[0]
				break
		else:
			logging.info("session %s not found" % sid)
			return

		try:
			reftype = cmd["type"][0]
		except:
			reftype = None

		if reftype is None:
			self.refreshClient(addr, skt)
		elif reftype == "trains":
			self.sendTrainInfo(addr, skt)
		elif reftype == "routes":
			self.sendRouteDefs(addr, skt)
		elif reftype == "subblocks":
			self.sendSubBlocks(addr, skt)
	
	def DoSetTrain(self, cmd):
		try:
			trn = cmd["name"][0]
		except (IndexError, KeyError):
			trn = None
		try:
			loco = cmd["loco"][0]
		except (IndexError, KeyError):
			loco = None
		block = cmd["block"][0]
		# train information is always echoed back to all listeners

		if trn and trn.startswith("??"):
			# this is an unknown train - see if we have a known train in the same block
			ntrn, nloco = self.trainList.FindTrainInBlock(block)
			if ntrn:
				trn = ntrn
			if nloco:
				loco = nloco
				
		elif trn:
			# this is a known train - see if we have an existing train (known or unknown)
			# in the block, and just replace it
			etrn, eloco = self.trainList.FindTrainInBlock(block)
			if etrn:
				if self.trainList.RenameTrain(etrn, trn, eloco, loco):
					for cmd in self.trainList.GetSetTrainCmds(trn):
						self.socketServer.sendToAll(cmd)
				return
			else: # see if we have it anywhere, and preserve the loco value if we do
				eloco = self.trainList.FindTrain(trn)
				if eloco is not None:
					if eloco != loco:
						loco = eloco

		resp = {"settrain": [{"name": trn, "loco": loco, "block": block}]}
		self.socketServer.sendToAll(resp)

		self.trainList.Update(trn, loco, block)
		
	def DoMoveTrain(self, cmd): #"movetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.PlaceTrain(blknm)

	def DoRemoveTrain(self, cmd): #"removetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.RemoveTrain(blknm)

	def DoTrainComplete(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"traincomplete": [p]}
		self.socketServer.sendToAll(resp)
		
	def GetTrainList(self):
		return self.trainList.GetTrainList()

	def DoRenameTrain(self, cmd):
		#print("Incoming HTTP Request: %s" % json.dumps(evt.data), flush=True)
		try:
			oname = cmd["oldname"][0]
		except (IndexError, KeyError):
			oname = None
		try:
			oloco = cmd["oldloco"][0]
		except (IndexError, KeyError):
			oloco = None
		try:
			nname = cmd["newname"][0]
		except (IndexError, KeyError):
			nname = None
		try:
			nloco = cmd["newloco"][0]
		except (IndexError, KeyError):
			nloco = None

		if self.trainList.RenameTrain(oname, nname, oloco, nloco):
			for cmd in self.trainList.GetSetTrainCmds(nname):
				self.socketServer.sendToAll(cmd)
		
	def DoTrainSignal(self, cmd):
		trid = cmd["train"][0]
		signal = cmd["signal"][0]
		aspect = cmd["aspect"][0]
		self.trainList.UpdateSignal(trid, signal, aspect)
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"trainsignal": p}
		self.socketServer.sendToAll(resp)
	
	def DoAdvice(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"advice": cmd})
	
	def DoAlert(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"alert": cmd})
				
	def DoServer(self, cmd):
		action = cmd["action"][0]
		if action == "exit":
			logging.info("HTTP 'server:exit' command received - terminating")
			self.Shutdown()
				
	def DoDebug(self, cmd):
		function = cmd["function"][0]
		addrList = self.clientList.GetFunctionAddress(function)
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"debug": cmd})

	def DoClose(self, cmd):
		function = cmd["function"][0]
		addrList = self.clientList.GetFunctionAddress(function)
		for addr, _ in addrList:
			self.socketServer.deleteSocket(addr)

	def DoAutorouter(self, cmd): # start/kill autorouter process
		stat = cmd["status"][0]
		if stat == "on":
			if not self.clientList.HasFunction("AR"):
				arExec = os.path.join(os.getcwd(), "autorouter", "main.py")
				self.pidAR = Popen([sys.executable, arExec]).pid
				logging.debug("autorouter started as PID %d" % self.pidAR)
		else:
			self.deleteClients(["AR"])
			self.pidAR = None
			
	def DoAR(self, cmd): # forward autorouter messages to all AR cliebts
		addrList = self.clientList.GetFunctionAddress("AR") + self.clientList.GetFunctionAddress("DISPLAY")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"ar": cmd})
			
						
	def DoAdvisor(self, cmd):
		stat = cmd["status"][0]
		if stat == "on":
			if not self.clientList.HasFunction("ADVISOR"):
				advExec = os.path.join(os.getcwd(), "advisor", "main.py")
				self.pidADV = Popen([sys.executable, advExec]).pid
				logging.debug("advisor started as PID %d" % self.pidADV)
		else:
			self.deleteClients(["ADVISOR"])
			self.pidADV = None
			
	def DoATC(self, cmd):
		addrList = self.clientList.GetFunctionAddress("ATC") + self.clientList.GetFunctionAddress("DISPLAY")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"atc": cmd})
				
	def DoATCRequest(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"atcrequest": cmd})
					
	def DoATCStatus(self, cmd):
		self.socketServer.sendToAll({"atcstatus": cmd})

	def Shutdown(self):
		logging.info("shutdown requested")
		self.forever = False

	def AtInterval(self):
		if self.forever:
			threading.Timer(0.4, self.AtInterval).start()
			self.cmdQ.put({"cmd": ["interval"]})
			if self.delay and self.delay > 0:
				self.delay -= 1
				if self.delay <= 0:
					self.delay = None
					self.cmdQ.put({"cmd": ["delayedstartup"]})

	def ServeForever(self):
		logging.info("serve forever starting")
		self.forever = True
		self.delay = 5  # wait 5 cycles before delayed startup
		self.AtInterval()
		while self.forever:
			while not self.cmdQ.empty():
				self.ProcessCommand(self.cmdQ.get())
			time.sleep(0.005)
			
		logging.info("terminating server threads")
		try:
			self.dispServer.close()
		except Exception as e:
			print("exception %s terminating http server" % str(e))
		
		try:
			self.socketServer.kill()
		except Exception as e:
			print("exception %s terminating socket server" % str(e))
		
		if not self.settings.simulation:
			try:
				self.DCCServer.close()
			except Exception as e:
				print("exception %s terminating DCC server" % str(e))
			
		logging.info("completed - continuing with shutdown")
		

main = ServerMain()
main.ServeForever()


logging.info("Railroad server terminating")
