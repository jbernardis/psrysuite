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
		logging.info("calling ThreadingHTTPServer constructor")
		self.server = ThreadingHTTPServer((ip, port), Handler)
		logging.info("back from constructor")
		self.server.setApp(self)
		self.cbCommand = cbCommand
		logging.info("Creating thread")
		self.thread = Thread(target=self.server.serve_railroad)
		logging.info("starting thread")
		self.thread.start()
		logging.info("thread started")

	def getThread(self):
		return self.thread

	def getServer(self):
		return self.server

	def dispatch(self, cmd):
		verb = cmd["cmd"][0]
		if verb == "getlocos":
			fn = os.path.join(os.getcwd(), "data", "locos.json")
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				return 400, "File Not Found"
			
			except:
				return 400, "Unknown error encountered"
			
			return 200, json.dumps(j)
		
		elif verb == "gettrains":
			fn = os.path.join(os.getcwd(), "data", "trains.json")
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				return 400, "File Not Found"
			
			except:
				return 400, "Unknown error encountered"
			
			return 200, json.dumps(j)
		
		elif verb == "getlayout":
			fn = os.path.join(os.getcwd(), "data", "layout.json")
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				return 400, "File Not Found"
			
			except:
				return 400, "Unknown error encountered"
			
			return 200, json.dumps(j)
		
		elif verb == "getsimscripts":
			fn = os.path.join(os.getcwd(), "data", "simscripts.json")
			try:
				with open(fn, "r") as jfp:
					j = json.load(jfp)
			except FileNotFoundError:
				return 400, "File Not Found"
			
			except:
				return 400, "Unknown error encountered"
			
			return 200, json.dumps(j)

		else:
			self.cbCommand(cmd)
		
		rc = 200
		body = b'request received'

		return rc, body

	def close(self):
		self.server.shut_down()

