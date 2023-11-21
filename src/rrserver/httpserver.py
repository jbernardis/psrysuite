import select
from threading import Thread
from socketserver import ThreadingMixIn 
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import logging

class Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		app = self.server.getApp()

		parsed_path = urlparse(self.path)
		cmdDict = parse_qs(parsed_path.query)
		cmd = parsed_path.path
		if cmd.startswith('/'):
			cmd = cmd[1:]
			
		cmdDict['cmd'] = [cmd]
		rc, b = app.dispatch(cmdDict)
		try:
			body = b.encode()
		except:
			body = b

		if rc == 200:
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			try:
				self.wfile.write(body)
			except ConnectionAbortedError:
				logging.warning("Connection Aborted Error writing 200 response back to requester - ignoring")
		else:
			self.send_response(400)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			try:
				self.wfile.write(body)
			except ConnectionAbortedError:
				logging.warning("Connection Aborted Error writing 400 response back to requester - ignoring")

	def do_POST(self):
		err = False
		try:
			content_length = int(self.headers['Content-Length'])
		except KeyError:
			logging.error("Received POST without content length - ignoring")
			err = True
			
		try:
			filename = self.headers["Filename"]
		except KeyError:
			logging.error("Received POST without file name - ignoring")
			err = True
			
		try:
			directory = self.headers["Directory"]
		except KeyError:
			logging.warning("Received POST without directory name - assuming \"data\"")
			directory = "data"

		if err:
			pass
		else:
			trdata = json.loads(self.rfile.read(content_length))
			
		if not err:
			folder = os.path.join(os.getcwd(), directory)
			fn = os.path.join(folder, filename)
			with open(fn, "w") as jfp:
				json.dump(trdata, jfp, indent=2)
				
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			try:
				b = "File %s saved" % filename
				self.wfile.write(b.encode())
			except ConnectionAbortedError:
				logging.warning("Connection Aborted Error writing 200 response back to requester - ignoring")
		else:
			self.send_response(400)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			try:
				b = "Error saving file %s" % filename
				self.wfile.write(b.encode())
			except ConnectionAbortedError:
				logging.warning("Connection Aborted Error writing 400 response back to requester - ignoring")

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	def serve_railroad(self):
		self.haltServer = False
		while self.haltServer == False:
			r = select.select([self.socket], [], [], 0)[0]
			if r and len(r) > 0:
				self.handle_request()
			else:
				pass #time.sleep(0.0001) # yield to other threads

	def setApp(self, app):
		self.app = app

	def getApp(self):
		return self.app

	def shut_down(self):
		self.haltServer = True

class HTTPServer:
	def __init__(self, ip, port, cbCommand, main, railroad):
		self.server = ThreadingHTTPServer((ip, port), Handler)
		self.server.setApp(self)
		self.cbCommand = cbCommand
		self.thread = Thread(target=self.server.serve_railroad)
		self.thread.start()
		self.main = main
		self.rr = railroad

	def getThread(self):
		return self.thread

	def getServer(self):
		return self.server

	def dispatch(self, cmd):
		verb = cmd["cmd"][0]
		if verb == "getlocos":
			fn = os.path.join(os.getcwd(), "data", "locos.json")
			logging.info("Retrieving loco information from file (%s)" % fn)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			jstr = json.dumps(j)
			logging.info("Returning %d bytes" % len(jstr))
			return 200, jstr
		
		elif verb == "gettrains":
			fn = os.path.join(os.getcwd(), "data", "trains.json")
			logging.info("Retrieving trains information from file (%s)" % fn)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			jstr = json.dumps(j)
			logging.info("Returning %d bytes" % len(jstr))
			return 200, jstr
		
		elif verb == "getlayout":
			fn = os.path.join(os.getcwd(), "data", "layout.json")
			logging.info("Retrieving layout information from file (%s)" % fn)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			jstr = json.dumps(j)
			logging.info("Returning %d bytes" % len(jstr))
			return 200, jstr
		
		elif verb == "getsnapshot":
			fn = os.path.join(os.getcwd(), "data", "snapshot.json")
			logging.info("Retrieving snapshot information from file (%s)" % fn)
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			jstr = json.dumps(j)
			logging.info("Returning %d bytes" % len(jstr))
			return 200, jstr
		
		elif verb == "listdir":
			try:
				directory = cmd["dir"][0]
			except:
				directory = "data"
							
			fqdn = os.path.join(os.getcwd(), directory)
			logging.info("Retrieving directory contents (%s)" % fqdn)

			d = [x for x in os.listdir(fqdn) if not os.path.isdir(os.path.join(fqdn, x))]
			logging.info("Returning %d bytes" % len(d))
			return 200, json.dumps(d)
		
		elif verb == "getfile":
			try:
				fn = cmd["file"][0]
			except:
				fn = None
				
			try:
				directory = cmd["dir"][0]
			except:
				directory = "data"

			if fn is None:
				logging.info("File name not specified")
				return 400, "File name not specified"
							
			fqn = os.path.join(os.getcwd(), directory, fn)
			logging.info("Retrieving file (%s)" % fqn)

			try:
				with open(fqn, "r") as fp:
					d = fp.read()
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			logging.info("Returning %d bytes" % len(d))
			return 200, d
		
		elif verb == "delfile":
			try:
				fn = cmd["file"][0]
			except:
				fn = None
				
			try:
				directory = cmd["dir"][0]
			except:
				directory = "data"

			if fn is None:
				logging.info("File name not specified")
				return 400, "File name not specified"
							
			fqn = os.path.join(os.getcwd(), directory, fn)
			logging.info("Deleting file (%s)" % fqn)

			try:
				os.unlink(fqn)
			except FileNotFoundError:
				logging.info("File not found")
				return 400, "File Not Found"
			
			except:
				logging.info("Unknown error")
				return 400, "Unknown error encountered"
			
			logging.info("File %s deleted" % fqn)
			return 200, "deleted file %s" % fqn
	
		elif verb == "getbits":
			try:
				address = int(cmd["address"][0], 16)
				n, ob, ib = self.rr.GetNodeBits(address)
				resp = {"count": n, "out": ob, "in": ib}
				jstr = json.dumps(resp)
				return 200, jstr
			except Exception as e:
				logging.info("Unknown error: %s" % str(e))
				return 400, str(e)

		elif verb == "setinbit":
			try:
				addr = int(cmd["address"][0], 16)
				vbytes = [int(x) for x in cmd["byte"]]
				vbits = [int(x) for x in cmd["bit"]]
				vals = [int(x) for x in cmd["value"]]
				self.rr.SetInputBitByAddr(addr, vbytes, vbits, vals)
				return 200, "Command received"
			except Exception as e:
				logging.info("Unknown error: %s" % str(e))
				return 400, str(e)
				
		elif verb == "activetrains":
			tl = self.main.GetTrainList()
			if tl is None:
				logging.info("Unknown error")
				return 400, "Unable to retrieve train list"
			else:
				jstr = json.dumps(tl)
				return 200, jstr
		
				
		elif verb == "sessions":
			tl = self.main.GetSessions()
			if tl is None:
				logging.info("Unknown error")
				return 400, "Unable to retrieve train list"
			else:
				jstr = json.dumps(tl)
				return 200, jstr
		
		else:
			self.cbCommand(cmd)
		
		rc = 200
		body = b'request received'

		return rc, body

	def close(self):
		self.server.shut_down()

