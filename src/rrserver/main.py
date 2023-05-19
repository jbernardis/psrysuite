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

import wx.lib.newevent

import json
import socket

from subprocess import Popen

from rrserver.settings import Settings
from rrserver.bus import RailroadMonitor
from rrserver.railroad import Railroad
from rrserver.httpserver import HTTPServer
from rrserver.sktserver import SktServer
from rrserver.routedef import RouteDef

from rrserver.clientlist import ClientList
from rrserver.trainlist import TrainList
from rrserver.iodisplay import IODisplay
from rrserver.dccserver import DCCHTTPServer

(HTTPMessageEvent, EVT_HTTPMESSAGE) = wx.lib.newevent.NewEvent()  
(RailroadEvent, EVT_RAILROAD) = wx.lib.newevent.NewEvent()  
(SocketEvent, EVT_SOCKET) = wx.lib.newevent.NewEvent()  
(IOClearEvent, EVT_CLEARIO) = wx.lib.newevent.NewEvent()  
(IOTextEvent, EVT_TEXTIO) = wx.lib.newevent.NewEvent()  


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=(wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP))
		self.socketServer = None
		self.dispServer = None
		self.rrMonitor = None
		self.Bind(wx.EVT_CLOSE, self.onClose)
		logging.info("pydispatch starting")
		
		self.pidAR = None
		self.pidADV = None
		self.pidDispatch = None
		self.pidDCC = None
		self.timeValue = None

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

		titleString = "PSRY Railroad Server - "
		if self.settings.simulation:
			titleString += "SIMULATION - "
							
		titleString += (" IP:  %s   Listening on port:  %d    Broadcasting on port:  %d    DCC Requests served on port:  %d" % 
				(self.ip, self.settings.serverport, self.settings.socketport, self.settings.dccserverport))
		self.SetTitle(titleString)

		logging.info("Creating railroad object")
		self.rr = Railroad(self, self.rrEventReceipt, self.settings)
		self.clientList = ClientList(self)
		self.trainList = TrainList(self)
		self.ioDisplay = IODisplay(self)

		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		hsz.AddSpacer(20)
		hsz.Add(self.rr)
		hsz.AddSpacer(10)
		vsz2 = wx.BoxSizer(wx.VERTICAL)
		vsz2.Add(self.clientList)
		vsz2.AddSpacer(10)
		vsz2.Add(self.trainList)
		hsz.Add(vsz2)
		hsz.AddSpacer(20)

		vsz.AddSpacer(20)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		self.cbEnableSendIO = wx.CheckBox(self, wx.ID_ANY, "Enable IO Bits display")
		self.cbEnableSendIO.SetValue(self.settings.viewiobits and not self.settings.hide)		
		vsz.Add(self.cbEnableSendIO, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_CHECKBOX, self.OnCbEnableIO, self.cbEnableSendIO)
		vsz.AddSpacer(10)
		
		hsz2 = wx.BoxSizer(wx.HORIZONTAL)
		hsz2.AddSpacer(20)
		hsz2.Add(self.ioDisplay)
		hsz2.AddSpacer(20)
		vsz.Add(hsz2)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		if self.settings.hide:
			self.Iconize()
		else:
			self.Restore()
		
		wx.CallAfter(self.Initialize)

	def Initialize(self):
		self.rr.Initialize()

		logging.info("Opening a railroad monitoring thread on device %s" % self.settings.rrtty)
		self.rrMonitor = RailroadMonitor(self.settings.rrtty, self.rr, self.settings)
		if not self.rrMonitor.initialized:
			logging.error("Failed to open railroad bus on device %s.  Exiting..." % self.settings.rrtty)
			dlg = wx.MessageDialog(self, "Unable to open connection to\nrailroad via port %s\n\nServer is exiting" % self.settings.rrtty,
				"Unable to open port", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			exit(1)
			
		#self.rrMonitor.start()
		logging.info("Railroad monitor thread created - starting HTTP server")

		try:
			self.dispServer = HTTPServer(self.ip, self.settings.serverport, self.dispCommandReceipt)
		except Exception as e:
			print("Unable to Create HTTP server for IP address %s (%s)" % (self.ip, str(e)))
			self.Shutdown()
			
		logging.info("HTTP Server created")
			
		self.Bind(EVT_HTTPMESSAGE, self.onHTTPMessageEvent)
		self.Bind(EVT_RAILROAD, self.onRailroadEvent)
		self.Bind(EVT_SOCKET, self.onSocketEvent)
		self.Bind(EVT_CLEARIO, self.onClearIOEvent)
		self.Bind(EVT_TEXTIO, self.onTextIOEvent)

		logging.info("Starting Socket server at address: %s:%d" % (self.ip, self.settings.socketport))
		self.socketServer = SktServer(self.ip, self.settings.socketport, self.socketEventReceipt)
		self.socketServer.start()
		
		logging.info("socket server started - starting DCC HTTP Server")
		
		if not self.settings.simulation:
			self.StartDCCServer()
		
		logging.info("DCC HTTP server successfully started")
		
		wx.CallLater(2000, self.DelayedStartup)
		
	def DelayedStartup(self):
		self.rrMonitor.start()
		if not self.settings.simulation:
			pname = os.path.join(os.getcwd(), "dccsniffer", "main.py")
			pid = Popen([sys.executable, pname]).pid
			logging.info("started DCC sniffer process as PID %d" % pid)


	def StartDCCServer(self):
		self.DCCServer = DCCHTTPServer(self.settings.ipaddr, self.settings.dccserverport, self.settings.dcctty)
		if not self.DCCServer.IsConnected():
			logging.error("Failed to open DCC bus on device %s.  Exiting..." % self.settings.dcctty)
			dlg = wx.MessageDialog(self, "Unable to open connection to\nDCC via port %s\n\nServer is exiting" % self.settings.dcctty,
				"Unable to open port", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			#exit(1)
		
	def OnCbEnableIO(self, _):
		self.rr.EnableSendIO(self.cbEnableSendIO.IsChecked())
		
	def ClearIO(self):
		evt = IOClearEvent()
		wx.QueueEvent(self, evt)

	def onClearIOEvent(self, _):
		self.ioDisplay.ClearIO()

	def ShowText(self, name, addr, otext, itext, line, lines):
		evt = IOTextEvent(name=name, addr=addr, otext=otext, itext=itext, line=line, lines=lines)
		wx.QueueEvent(self, evt)

	def onTextIOEvent(self, evt):
		self.ioDisplay.ShowText(evt.name, evt.addr, evt.otext, evt.itext, evt.line, evt.lines)

	def socketEventReceipt(self, cmd):
		evt = SocketEvent(data=cmd)
		wx.QueueEvent(self, evt)

	def onSocketEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd == "newclient":
				addr = parms["addr"]
				skt = parms["socket"]
				sid = parms["SID"]
				logging.info("New Client connecting from address: %s:%s" % (addr[0], addr[1]))
				self.socketServer.sendToOne(skt, addr, {"sessionID": sid})
				self.clients[addr] = [skt, sid]
				#self.refreshClient(addr, skt)
				self.clientList.AddClient(addr, skt, sid, None)

			elif cmd == "delclient":
				addr = parms["addr"]
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
		for m in self.trainList.GetSetTrainCmds():
			self.socketServer.sendToOne(skt, addr, m)
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "trains"}})

	def sendRouteDefs(self, addr, skt):
		for rte in self.routeDefs.values():
			self.socketServer.sendToOne(skt, addr, rte.FormatRoute())
		self.socketServer.sendToOne(skt, addr, {"end": {"type": "routes"}})
		
	def sendSubBlocks(self, addr, skt):
		subs = self.rr.GetSubBlockInfo()
		self.socketServer.sendToOne(skt, addr, {"subblocks": subs})

	def rrEventReceipt(self, cmd, addr=None, skt=None):
		evt = RailroadEvent(data=cmd, addr=addr, skt=skt)
		wx.QueueEvent(self, evt)

	def onRailroadEvent(self, evt):
		#logging.info("Railroad event: %s" % json.dumps(evt.data))

		for cmd, parms in evt.data.items():
			if cmd == "refreshoutput":
				for oname in parms:
					self.rr.RefreshOutput(oname)
			elif cmd == "refreshinput":
				for iname in parms:
					self.rr.RefreshInput(iname)
			else:
				self.socketServer.sendToAll(evt.data)

	def dispCommandReceipt(self, cmd): # thread context
		evt = HTTPMessageEvent(data=cmd)
		wx.QueueEvent(self, evt)

	def onHTTPMessageEvent(self, evt):
		#logging.info("HTTP Request: %s" % json.dumps(evt.data))
		verb = evt.data["cmd"][0]

		if verb == "signal":
			signame = evt.data["name"][0]
			aspect = int(evt.data["aspect"][0])
			resp = {"signal": [{"name": signame, "aspect": aspect}]}
			# signal changes are always echoed back to all listeners
			self.socketServer.sendToAll(resp)
			self.rr.SetAspect(signame, aspect)

		elif verb == "genlayout":
			addrList = self.clientList.GetFunctionAddress("DISPATCH")
			if len(addrList) == 0:
				logging.error("Cannot generate layout information until dispatcher has connected")
			else:
				self.generateLayoutFile()
				logging.info("Layout file has been generated")
			
		elif verb == "signallock":
			signame = evt.data["name"][0]
			status = int(evt.data["status"][0])

			self.rr.SetSignalLock(signame, status)
			# signallock information is always echoed to all listeners
			resp = {"signallock": [{ "name": signame, "state": status}]}
			self.socketServer.sendToAll(resp)

		elif verb == "fleet":
			signame = evt.data["name"][0]
			value = int(evt.data["value"][0])
			self.rr.SetSignalFleet(signame, value)
			resp = {"fleet": [{"name": signame, "value": value}]}
			# fleeting changes are always echoed back to all listeners
			self.socketServer.sendToAll(resp)

		elif verb == "settrain":
			try:
				trn = evt.data["name"][0]
			except (IndexError, KeyError):
				trn = None
			try:
				loco = evt.data["loco"][0]
			except (IndexError, KeyError):
				loco = None
			block = evt.data["block"][0]
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

		elif verb == "renametrain":
			#print("Incoming HTTP Request: %s" % json.dumps(evt.data), flush=True)
			try:
				oname = evt.data["oldname"][0]
			except (IndexError, KeyError):
				oname = None
			try:
				oloco = evt.data["oldloco"][0]
			except (IndexError, KeyError):
				oloco = None
			try:
				nname = evt.data["newname"][0]
			except (IndexError, KeyError):
				nname = None
			try:
				nloco = evt.data["newloco"][0]
			except (IndexError, KeyError):
				nloco = None

			if self.trainList.RenameTrain(oname, nname, oloco, nloco):
				for cmd in self.trainList.GetSetTrainCmds(nname):
					self.socketServer.sendToAll(cmd)

		elif verb == "blockdir":
			block = evt.data["block"][0]
			direction = evt.data["dir"][0]
			self.rr.SetBlockDirection(block, direction)

		elif verb == "blockdirs":
			data = json.loads(evt.data["data"][0])
			for b in data:
				block = b["block"]
				direction = b["dir"]
				self.rr.SetBlockDirection(block, direction)

		elif verb == "blockclear":
			block = evt.data["block"][0]
			clear = evt.data["clear"][0]
			self.rr.SetBlockClear(block, clear == "1")

		elif verb == "handswitch":
			hsname = evt.data["name"][0]
			stat = int(evt.data["status"][0])

			self.rr.SetHandSwitch(hsname, stat)
			# handswitch information is always echoed to all listeners
			resp = {"handswitch": [{"name": hsname, "state": stat}]}
			self.socketServer.sendToAll(resp)

		elif verb == "turnout":
			swname = evt.data["name"][0]
			status = evt.data["status"][0]
			try:
				force = evt.data["force"][0]
			except:
				force = False

			self.rr.SetOutPulseTo(swname, status)

			# turnouts are not normally echoed back to listeners.  Instead,
			# the turnout information that the railroad reponds with is sent
			# back to listeners to convey this information.  In simulation, we echo
			if self.settings.simulation:
				self.rr.GetInput(swname).SetState(status, force=force)

		elif verb == "nxbutton":
			try:
				bentry = evt.data["entry"][0]
			except (IndexError, KeyError):
				bentry = None
			try:
				bexit = evt.data["exit"][0]
			except (IndexError, KeyError):
				bexit = None
			try:
				button = evt.data["button"][0]
			except (IndexError, KeyError):
				button = None

			if bentry and bexit:
				self.rr.SetOutPulseNXB(bentry)
				self.rr.SetOutPulseNXB(bexit)
			else:
				self.rr.SetOutPulseNXB(button)

			# nxbuttons are not normally echoed back to listeners.  Instead,
			# the turnout information that the railroad reponds with is sent
			# back to listeners to convey this information.  In simulation we echo
			if self.settings.simulation:
				if bentry and bexit:
					self.rr.EvaluateNXButtons(bentry, bexit)
				else:
					self.rr.EvaluateNXButton(button)

		elif verb == "turnoutlock":
			swname = evt.data["name"][0]
			status = int(evt.data["status"][0])

			self.rr.SetSwitchLock(swname, status)
			# turnoutlock information is always echoed to all listeners
			resp = {"turnoutlock": [{ "name": swname, "state": status}]}
			self.socketServer.sendToAll(resp)

		elif verb == "indicator":
			indname = evt.data["name"][0]
			value = int(evt.data["value"][0])

			self.rr.SetIndicator(indname, value)
			# indicator information is always echoed to all listeners
			resp = {"indicator": [{ "name": indname, "value": value}]}
			self.socketServer.sendToAll(resp)

		elif verb == "relay":
			relay = evt.data["block"][0]+".srel"
			status = int(evt.data["status"][0])

			self.rr.SetRelay(relay, status)
			
		elif verb == "clock":
			value = evt.data["value"][0]
			resp = {"clock": [{ "value": value}]}
			self.timeValue = value
			addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("TRACKER")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, resp)

		elif verb == "refresh":
			sid = int(evt.data["SID"][0])
			for addr, data in self.clients.items():
				if data[1] == sid:
					skt = data[0]
					break
			else:
				logging.info("session %s not found" % sid)
				return

			try:
				reftype = evt.data["type"][0]
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

		elif verb == "setroute":
			blknm = evt.data["block"][0]
			try:
				route = evt.data["route"][0]
			except (IndexError, KeyError):
				route = None

			if route is None:
				ends = None
				signals = None
			else:
				try:
					ends = [None if e == "-" else e for e in evt.data["ends"][0:2]]
				except (IndexError, KeyError):
					ends = None
				try:
					signals = evt.data["signals"][0:2]
				except (IndexError, KeyError):
					signals = None

			self.rr.SetOSRoute(blknm, route, ends, signals)
			resp = {"setroute": [{ "block": blknm, "route": route}]}
			if ends is not None:
				resp["setroute"][0]["ends"] = ["-" if e is None else e for e in ends]
			if signals is not None:
				resp["setroute"][0]["signals"] = signals

			self.socketServer.sendToAll(resp)

		elif verb == "movetrain":
			try:
				blknm = evt.data["block"][0]
			except (IndexError, KeyError):
				return
			self.rr.PlaceTrain(blknm)

		elif verb == "removetrain":
			try:
				blknm = evt.data["block"][0]
			except (IndexError, KeyError):
				return
			self.rr.RemoveTrain(blknm)
			
		elif verb == "trainsignal":
			trid = evt.data["train"][0]
			signal = evt.data["signal"][0]
			aspect = evt.data["aspect"][0]
			self.trainList.UpdateSignal(trid, signal, aspect)
			p = {tag: evt.data[tag][0] for tag in evt.data if tag != "cmd"}
			resp = {"trainsignal": p}
			self.socketServer.sendToAll(resp)
			
		elif verb == "traincomplete":
			p = {tag: evt.data[tag][0] for tag in evt.data if tag != "cmd"}
			resp = {"traincomplete": [p]}
			self.socketServer.sendToAll(resp)

		elif verb == "control":
			name = evt.data["name"][0]
			value = int(evt.data["value"][0])

			self.rr.SetControlOption(name, value)

		elif verb == "districtlock":
			name = evt.data["name"][0]
			value = evt.data["value"]

			self.rr.SetDistrictLock(name, [int(v) for v in value])

		elif verb == "routedef":
			name = evt.data["name"][0]
			osNm = evt.data["os"][0]
			try:
				signals = evt.data["signals"]
			except KeyError:
				signals = []
			try:
				turnouts = evt.data["turnouts"]
			except KeyError:
				turnouts = []
			try:
				ends = [None if e == "-" else e for e in evt.data["ends"]]
			except KeyError:
				ends = [None, None]

			self.routeDefs[name] = (RouteDef(name, osNm, ends, signals, turnouts))

		elif verb == "routedefs":
			data = json.loads(evt.data["data"][0])
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
			
		elif verb == "crossover":
			self.CrossoverPoints = []
			for b in evt.data["data"]:
				self.CrossoverPoints.append(b.split(":"))
			
		elif verb == "identify":
			sid = int(evt.data["SID"][0])
			function = evt.data["function"][0]
			self.clientList.SetSessionFunction(sid, function)
			if function == "DISPATCH":
				self.deleteClients(["AR", "ADVISOR", "ATC"])
				self.pidAR = None
				self.pidADV = None

			
		elif verb == "autorouter":
			stat = evt.data["status"][0]
			if stat == "on":
				if not self.clientList.HasFunction("AR"):
					arExec = os.path.join(os.getcwd(), "autorouter", "main.py")
					self.pidAR = Popen([sys.executable, arExec]).pid
					logging.debug("autorouter started as PID %d" % self.pidAR)
			else:
				self.deleteClients(["AR"])
				self.pidAR = None
				
		elif verb == "ar":
			addrList = self.clientList.GetFunctionAddress("AR") + self.clientList.GetFunctionAddress("DISPLAY")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"ar": evt.data})
				
		elif verb == "atc":
			addrList = self.clientList.GetFunctionAddress("ATC") + self.clientList.GetFunctionAddress("DISPLAY")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"atc": evt.data})
				
		elif verb == "atcrequest":
			addrList = self.clientList.GetFunctionAddress("DISPATCH")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"atcrequest": evt.data})
					
		elif verb == "atcstatus":
			self.socketServer.sendToAll({"atcstatus": evt.data})
						
		elif verb == "advisor":
			stat = evt.data["status"][0]
			if stat == "on":
				if not self.clientList.HasFunction("ADVISOR"):
					advExec = os.path.join(os.getcwd(), "advisor", "main.py")
					self.pidADV = Popen([sys.executable, advExec]).pid
					logging.debug("advisor started as PID %d" % self.pidADV)
			else:
				self.deleteClients(["ADVISOR"])
				self.pidADV = None
	
		elif verb == "advice":
			addrList = self.clientList.GetFunctionAddress("DISPATCH")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"advice": evt.data})
	
		elif verb == "alert":
			addrList = self.clientList.GetFunctionAddress("DISPATCH")
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"alert": evt.data})
				
		elif verb == "server":
			action = evt.data["action"][0]
			if action == "show":
				self.Restore()
				self.Raise()
			elif action == "hide":
				self.Iconize()
			elif action == "exit":
				logging.info("HTTP 'server:exit' command received - terminating")
				self.Shutdown()
				
		elif verb == "debug":
			function = evt.data["function"][0]
			addrList = self.clientList.GetFunctionAddress(function)
			for addr, skt in addrList:
				self.socketServer.sendToOne(skt, addr, {"debug": evt.data})

		elif verb == "close":
			function = evt.data["function"][0]
			addrList = self.clientList.GetFunctionAddress(function)
			for addr, skt in addrList:
				self.socketServer.deleteSocket(addr)

		elif verb == "quit":
			logging.info("HTTP 'quit' command received - terminating")
			self.Shutdown()

	def onClose(self, _):
		self.Shutdown()

	def Shutdown(self):
		logging.info("Killing socket server...")
		try:
			self.socketServer.kill()
		except:
			pass

		logging.info("killing HTTP server...")
		try:
			self.dispServer.close()
		except:
			pass

		logging.info("killing DCC HTTP server...")
		try:
			self.DCCServer.close()
		except:
			pass

		logging.info("closing bus to railroad...")
		try:
			self.rrMonitor.kill()
		except:
			pass

		logging.info("exiting...")
		self.Destroy()


class App(wx.App):
	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
		self.frame = None

	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()
