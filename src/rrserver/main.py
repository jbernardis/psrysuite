import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

lfn = os.path.join(os.getcwd(), "logs", "rrserver.log")


import logging
import logging.handlers
from dispatcher.settings import Settings
should_roll_over = os.path.isfile(lfn)

settings = Settings()


logLevels = {
	"DEBUG":	logging.DEBUG,
	"INFO":		logging.INFO,
	"WARNING":	logging.WARNING,
	"ERROR":	logging.ERROR,
	"CRITICAL":	logging.CRITICAL,
}

l = settings.debug.loglevel
if l not in logLevels:
	print("unknown logging level: %s.  Defaulting to DEBUG" % l, file=sys.stderr)
	l = "DEBUG"
	
loglevel = logLevels[l]

handler = logging.handlers.RotatingFileHandler(lfn, mode='a', backupCount=5)

logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel, handlers=[handler])
console = logging.StreamHandler()
console.setLevel(loglevel)
formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

if should_roll_over:
	handler.doRollover()

ofp = open(os.path.join(os.getcwd(), "output", "rrserver.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "rrserver.err"), "w")

sys.stdout = ofp
sys.stderr = efp


import json
import socket
import time
import queue
import threading

from subprocess import Popen

from rrserver.bus import Bus
from rrserver.railroad import Railroad
from rrserver.httpserver import HTTPServer
from rrserver.sktserver import SktServer
from rrserver.routedef import RouteDef

from rrserver.clientlist import ClientList
from rrserver.trainlist import TrainList
from rrserver.dccserver import DCCHTTPServer

from dispatcher.constants import RegAspects


class ServerMain:
	def __init__(self):
		self.socketServer = None
		self.dispServer = None
		
		logging.info("PSRY Suite - Railroad server starting %s" % ("" if not settings.rrserver.simulation else " - simulation mode"))
		logging.info("Sending logging output  to %s" % lfn)
		
		self.commandsSeen = []
		
		self.pidAR = None
		self.pidADV = None
		self.DCCSniffer = None
		self.pidDCCSniffer = None
		self.timeValue = None
		self.clockStatus = 2
		self.busInterval = settings.rrserver.businterval
		
		self.cmdQ = queue.Queue()

		self.routeDefs = {}
		self.CrossoverPoints = []

		hostname = socket.gethostname()
		self.ip = socket.gethostbyname(hostname)

		self.clients = {}

		
		if settings.ipaddr is not None:
			if self.ip != settings.ipaddr:
				logging.info("Using configured IP Address (%s) instead of retrieved IP Address: (%s)" % (settings.ipaddr, self.ip))
				self.ip = settings.ipaddr

		logging.info("Creating railroad object")
		self.rr = Railroad(self, self.rrEventReceipt, settings)
		self.clientList = ClientList(self)
		self.trainList = TrainList(self)
		
		self.Initialize()

	def Initialize(self):
		self.CreateDispatchTable()
		try:
			self.dispServer = HTTPServer(self.ip, settings.serverport, self.dispCommandReceipt, self, self.rr)
		except Exception as e:
			logging.error("Unable to Create HTTP server for IP address %s (%s)" % (self.ip, str(e)))
			self.Shutdown()
			
		logging.info("HTTP Server created")

		logging.info("Starting Socket server at address: %s:%d" % (self.ip, settings.socketport))
		self.socketServer = SktServer(self.ip, settings.socketport, self.socketEventReceipt)
		self.socketServer.start()
		
		logging.info("socket server started - starting DCC HTTP Server")

		if not settings.rrserver.simulation:
			logging.info("Starting DCC Server")		
			continueInit = self.StartDCCServer()		
		else:
			logging.info("DCC HTTP Server not started in simulation mode")
			continueInit = True
			
		if continueInit:
			self.rr.Initialize()
		else:
			self.queueCmd({"cmd": ["failedstart"]})

		
	def DelayedStartup(self, _):
		if not settings.rrserver.simulation:
			self.rrBus = Bus(settings.rrserver.rrtty)
			self.rr.setBus(self.rrBus)
			pname = os.path.join(os.getcwd(), "dccsniffer", "main.py")
			self.DCCSniffer = Popen([sys.executable, pname])
			pid = self.DCCSniffer.pid
			logging.info("started DCC sniffer process as PID %d" % pid)

	def StartDCCServer(self):
		self.DCCServer = DCCHTTPServer(settings.ipaddr, settings.dccserverport, settings.rrserver.dcctty)
		if not self.DCCServer.IsConnected():
			logging.error("Failed to open DCC bus on device %s.  Exiting..." % settings.rrserver.dcctty)
			return False
		else:
			logging.info("DCC HTTP server successfully started")
			return True

	def socketEventReceipt(self, cmd):
		logging.info("received socket connection request: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def queueCmd(self, cmd):
		logging.info("queueing command: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def NewClient(self, cmd):
		addr = cmd["addr"]
		skt = cmd["socket"]
		sid = cmd["SID"]
		logging.info("New Client connecting from address: %s:%s" % (addr[0], addr[1]))
		self.socketServer.sendToOne(skt, addr, {"sessionID": sid})
		self.clients[addr] = [skt, sid]
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
			
		layout = {"routes": routes, "blocks": blocks, "subblocks": subblocks, "crossover": self.CrossoverPoints}
		with open(os.path.join(os.getcwd(), "data", "layout.json"), "w") as jfp:
			json.dump(layout, jfp, sort_keys=True, indent=2)


	def refreshClient(self, addr, skt):
		if self.timeValue is not None:
			m = {"clock": [{ "value": self.timeValue, "status": self.clockStatus}]}
			self.socketServer.sendToOne(skt, addr, m)
		
		for m in self.rr.GetCurrentValues():
			self.socketServer.sendToOne(skt, addr, m)
		
		for opt, val in self.rr.GetControlOptions().items():
			m = {"control": [{"name": opt, "value": val}]}
			self.socketServer.sendToOne(skt, addr, m)
			
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "layout"}})

	def sendTrainInfo(self, addr, skt):
		for m in self.trainList.GetSetTrainCmds():
			self.socketServer.sendToOne(skt, addr, m)

		self.socketServer.sendToOne(skt, addr, {"end": {"type": "trains"}})
		self.generateLayoutFile()

	def sendRouteDefs(self, addr, skt):
		for rte in self.routeDefs.values():
			self.socketServer.sendToOne(skt, addr, rte.FormatRoute())
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "routes"}})
		
	def sendSubBlocks(self, addr, skt):
		subs = self.rr.GetSubBlockInfo()
		self.socketServer.sendToOne(skt, addr, {"subblocks": subs})

	def rrEventReceipt(self, cmd):
		self.socketServer.sendToAll(cmd)

	def dispCommandReceipt(self, cmd): # thread context
		#logging.info("HTTP Event: %s" % str(cmd))
		self.cmdQ.put(cmd)
		
	def CreateDispatchTable(self):					
		self.dispatch = {
			"interval": 	self.DoInterval,
			"clock":    	self.DoClock,
			
			"newclient":	self.NewClient,
			"delclient":	self.DelClient,
			"identify": 	self.DoIdentify,
			"refresh":		self.DoRefresh,
			"traintimesrequest":	self.DoTrainTimesRequest,
			"traintimesreport":		self.DoTrainTimesReport,
			
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
			"traincomplete":		self.DoTrainComplete,
			"trainblockorder":		self.DoTrainBlockOrder,
			"assigntrain":  self.DoAssignTrain,
			"checktrains":  self.DoCheckTrains,
			
			"signal":   	self.DoSignal,
			"signallock":	self.DoSignalLock,
			"siglever":		self.DoSigLever,
			"turnout":  	self.DoTurnout,
			"turnoutlock":	self.DoTurnoutLock,
			"turnoutlever":	self.DoTurnoutLever,
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
			"arrequest":	self.DoARRequest,
			"atc":			self.DoATC,
			"atcrequest":	self.DoATCRequest,
			"atcstatus":	self.DoATCStatus,

			"debug":		self.DoDebug,
			"simulate": 	self.DoSimulate,
			"dumptrains":	self.DoDumpTrains,
			
			"dccspeed":		self.DoDCCSpeed,
			
			"quit":			self.DoQuit,
			"delayedstartup":
							self.DelayedStartup,
			"reopen":		self.DoReopen
		}

	def ProcessCommand(self, cmd):
		verb = cmd["cmd"][0]
		if verb == "failedstart":
			logging.info("received failed start command")
			self.forever = False
			return 
		
		if not self.forever:
			return
		
		if verb != "interval":
			try:
				jstr = json.dumps(cmd)
			except:
				jstr = str(cmd)
			logging.info("HTTP Cmd receipt: %s" % jstr)
		
		try:
			handler = self.dispatch[verb]
		except KeyError:
			logging.error("Unknown command: %s" % verb)
		
		else:
			handler(cmd)
			
	def DoInterval(self, _):
		if self.pause > 0:
			'''
			no I/O while pause is active
			'''
			self.pause -= 1
			return 
		
		self.rr.OutIn()

	def DoSigLever(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"siglever": [p]}
		self.socketServer.sendToAll(resp)

	def DoSignal(self, cmd):
		signame = cmd["name"][0]
		try:
			aspect = int(cmd["aspect"][0])
		except KeyError:
			aspect = None
		try:
			aspectType = int(cmd["aspecttype"][0])
		except KeyError:
			logging.info("Received signal command with no aspecttype - assuming regular aspects (%s)" % str(cmd))
			aspectType = None
		try:
			callon = int(cmd["callon"][0]) == 1
		except:
			callon = False
		try:
			frozenaspect = int(cmd["frozenaspect"][0])
		except:
			frozenaspect=None
	
		if aspectType is not None:
			self.rr.SetAspect(signame, aspect, frozenaspect, callon, aspectType=aspectType)
		else:
			self.rr.SetAspect(signame, aspect, frozenaspect, callon)

	def DoSignalLock(self, cmd):			
		signame = cmd["name"][0]
		status = int(cmd["status"][0])
		
		self.rr.SetSignalLock(signame, status)
				
	def DoTurnout(self, cmd):
		swname = cmd["name"][0]
		status = cmd["status"][0]

		self.rr.SetOutPulseTo(swname, status)

	def DoTurnoutLever(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"turnoutlever": [p]}
		self.socketServer.sendToAll(resp)

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
		block = cmd["block"][0]
		relay = block + ".srel"
		status = int(cmd["state"][0])
		
		resp = {"relay": [{ "name": relay, "state": status}]}
		addrList = self.clientList.GetFunctionAddress("DISPLAY")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)

		self.rr.SetRelay(relay, status)
		
	def DoClock(self, cmd):
		value = cmd["value"][0]
		status = cmd["status"][0]
		resp = {"clock": [{ "value": value, "status": status}]}
		self.timeValue = value
		self.clockStatus = status
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("TRACKER") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)
			
	def DoDCCSpeed(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"dccspeed": [p]}
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE") + self.clientList.GetFunctionAddress("TRACKER")
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
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
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
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"control": [p]}
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)
		
	def DoQuit(self, _):
		self.Shutdown()
		
	def DoReopen(self, _):
		self.DoBusReopen()
		
	def DoBusReopen(self):
		if settings.rrserver.simulation:
			return 

		self.pause = 12 # pause I/O for 12 (~5 seconds) cycles while port is re-opened		
		self.rrBus.reopen()

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
			
	def DoTrainBlockOrder(self, cmd):
		try:
			trid = cmd["name"][0]
		except KeyError:
			trid = None

		try:
			blocks = cmd["blocks"]
		except KeyError:
			blocks = None

		try:
			east = cmd["east"][0].startswith("T")
		except (IndexError, KeyError):
			east = None

		if trid is not None and blocks is not None:
			if east is not None:
				self.trainList.SetEast(trid, east)

			print("calling update BO(%s, %s)" % (trid, str(blocks)))
			self.trainList.UpdateTrainBlockOrder(trid, blocks)

			p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
			p["blocks"] = [b for b in blocks]
			resp = {"trainblockorder": [p]}
			self.socketServer.sendToAll(resp)

	def DoTrainTimesRequest(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"traintimesrequest": {}})

	def DoTrainTimesReport(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPLAY")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"traintimesreport": cmd})

	def DoSetTrain(self, cmd):
		try:
			trn = cmd["name"][0]
		except (IndexError, KeyError):
			trn = None
		try:
			loco = cmd["loco"][0]
		except (IndexError, KeyError):
			loco = None
		try:
			east = True if cmd["east"][0] == "1" else False
		except (IndexError, KeyError):
			east = True
		try:
			action = cmd["action"][0]
		except (IndexError, KeyError):
			action = "replace"
		blocks = cmd["blocks"]

		if trn and trn.startswith("??"):
			# this is an unknown train - see if we have a known train in the same block
			ntrn, nloco = self.trainList.FindTrainInBlock(blocks[0])
			if ntrn:
				trn = ntrn
				trinfo = self.trainList.GetTrainInfo(trn)
				east = trinfo["east"]
				
			if nloco:
				loco = nloco
				
		elif trn:
			# this is a known train - see if we have an existing train (known or unknown)
			# in the block, and just replace it
			etrn, eloco = self.trainList.FindTrainInBlock(blocks[0])
			if etrn:
				if self.trainList.RenameTrain(etrn, trn, eloco, loco, east):
					for cmd in self.trainList.GetSetTrainCmds(trn):
						self.socketServer.sendToAll(cmd)
				return
			else: # see if we have it anywhere, and preserve the loco value if we do
				eloco = self.trainList.GetLocoForTrain(trn)
				if eloco is not None:
					if eloco != loco:
						loco = eloco

		# TODO - we need to set the occupancy bit (or clear it is trn is None)
		#self.rr.OccupyBlock(block, 0 if trn is None else 1)
		
		# train information is always echoed back to all listeners
		resp = {"settrain": {"name": trn, "loco": loco, "blocks": blocks, "east": east, "action": action}}
		self.socketServer.sendToAll(resp)

		self.trainList.Update(trn, loco, blocks, east, action)
		
	def DoMoveTrain(self, cmd): #"movetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.PlaceTrain(blknm)
		self.rr.OccupyBlock(blknm, 1)

	def DoRemoveTrain(self, cmd): #"removetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.RemoveTrain(blknm)
		self.rr.OccupyBlock(blknm, 0)

	def DoTrainComplete(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"traincomplete": [p]}
		self.socketServer.sendToAll(resp)

	def DoAssignTrain(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		train = p["train"]	
		try:
			engineer = p["engineer"]
		except KeyError:
			engineer = None
			
		self.trainList.UpdateEngineer(train, engineer)
		
		resp = {"assigntrain": [p]}
		self.socketServer.sendToAll(resp)
		
	def GetTrainList(self):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"dumptrains": ""})
		return self.trainList.GetTrainList()

	def DoRenameTrain(self, cmd):
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
		try:
			east = cmd["east"][0] == "1"
		except (IndexError, KeyError):
			east = None

		if self.trainList.RenameTrain(oname, nname, oloco, nloco, east):
			for cmd in self.trainList.GetSetTrainCmds(nname, nameonly=True):
				self.socketServer.sendToAll(cmd)

	def DoCheckTrains(self, cnd):				
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"checktrains": {}})
		
	def DoTrainSignal(self, cmd):
		trid = cmd["train"][0]
		signal = cmd["signal"][0]
		aspect = cmd["aspect"][0]
		self.trainList.UpdateSignal(trid, signal, aspect)
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"trainsignal": p}
		self.socketServer.sendToAll(resp)
	
	def DoAdvice(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"advice": cmd})
	
	def DoAlert(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
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
			
	def DoDumpTrains(self, cmd):
		self.trainList.Dump()

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

	def DoATC(self, cmd):
		addrList = self.clientList.GetFunctionAddress("ATC") + self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"atc": cmd})

	def DoATCRequest(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"atcrequest": cmd})

	def DoARRequest(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"arrequest": cmd})
					
	def DoATCStatus(self, cmd):
		self.socketServer.sendToAll({"atcstatus": cmd})

	def Shutdown(self):
		logging.info("shutdown requested")
		self.forever = False

	def AtInterval(self):
		if self.forever:
			threading.Timer(self.busInterval, self.AtInterval).start()
			if self.delay is None or self.delay <= 0:
				self.cmdQ.put({"cmd": ["interval"]})
			elif self.delay > 0:
				self.delay -= 1
				if self.delay <= 0:
					self.delay = None
					self.cmdQ.put({"cmd": ["delayedstartup"]})
					
	def ServeForever(self):
		logging.info("serve forever starting")
		self.forever = True
		self.delay = 5  # wait 5 cycles before delayed startup
		self.pause = 0
		self.AtInterval()
		while self.forever:
			while not self.cmdQ.empty():
				self.ProcessCommand(self.cmdQ.get())
			time.sleep(0.005)
			
		logging.info("terminating server threads")
		try:
			self.dispServer.close()
		except Exception as e:
			logging.error("exception %s terminating http server" % str(e))
		
		try:
			self.socketServer.kill()
		except Exception as e:
			logging.error("exception %s terminating socket server" % str(e))
		
		if not settings.rrserver.simulation:
			try:
				self.DCCSniffer.kill()
			except Exception as e:
				logging.error("exception %s terminating DCC Sniffer process" % str(e))
				
			try:
				self.DCCServer.close()
			except Exception as e:
				logging.error("exception %s terminating DCC server" % str(e))
		
			try:
				self.rrBus.close()
			except Exception as e:
				logging.error("exception %s closing Railroad Bus port" % str(e))
			
		logging.info("completed - continuing with shutdown")
		

main = ServerMain()
main.ServeForever()


logging.info("Railroad server terminating")
