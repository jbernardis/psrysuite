import select
from threading import Thread
from socketserver import ThreadingMixIn 
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import html
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
			self.wfile.write(body)
		else:
			self.send_response(400)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(body)

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
	def __init__(self, ip, port, cbCommand):
		self.server = ThreadingHTTPServer((ip, port), Handler)
		self.server.setApp(self)
		self.cbCommand = cbCommand
		self.thread = Thread(target=self.server.serve_railroad)
		self.thread.start()

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
		
		elif verb == "getsimscripts":
			fn = os.path.join(os.getcwd(), "data", "simscripts.json")
			logging.info("Retrieving simscripts from file (%s)" % fn)
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

		else:
			self.cbCommand(cmd)
		
		rc = 200
		body = b'request received'

		return rc, body

	def close(self):
		self.server.shut_down()

