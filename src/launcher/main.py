import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
    sys.path.insert(0, cmdFolder)
 

from subprocess import Popen
import time
   
from launcher.settings import Settings
from launcher.rrserver import RRServer

np = len(sys.argv)

if np < 2:
    launchmode = "dispatcher"

else:
    launchmode = sys.argv[1]
    
ofp = open("launch%s.out" % launchmode, "w")
efp = open("launch%s.err" % launchmode, "w")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()

rrServer = RRServer()
rrServer.SetServerAddress(settings.ipaddr, settings.serverport)

interpreter = sys.executable.replace("python.exe", "pythonw.exe")
 
for i in range(len(sys.argv)):
    print("%d: %s" % (i, sys.argv[i]))

if launchmode == "dispatcher":
    print("Launch mode: dispatcher")
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([sys.executable, svrExec])
    print("server started as PID %d" % svrProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([sys.executable, dispExec])
    print("dispatcher started as PID %d" % dispProc.pid)
 
    svrActive = True
    dispActive = True   
    while svrActive or dispActive:
        time.sleep(1)
        if svrActive and svrProc.poll() is not None:
            print("Server has terminated")
            svrActive = False
            
        if dispActive and dispProc.poll() is not None:
            print("Dispatcher has terminated")
            dispActive = False
            rrServer.SendRequest( {"server": {"action": "show"}})    

elif launchmode == "simulation":
    print("launch mode: simulation")
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([sys.executable, svrExec, "simulation"])
    print("server started as PID %d" % svrProc.pid)
    
    simExec = os.path.join(os.getcwd(), "simulator", "main.py")
    simProc = Popen([sys.executable, simExec])
    print("simulator started as PID %d" % simProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([sys.executable, dispExec])
    print("dispatcher started as PID %d" % dispProc.pid)
 
    svrActive = True
    simActive = True
    dispActive = True   
    while svrActive or dispActive or simActive:
        time.sleep(1)
        if svrActive and svrProc.poll() is not None:
            print("Server has terminated")
            svrActive = False
            
        if simActive and simProc.poll() is not None:
            print("Simulator has terminated")
            simActive = False
            
        if dispActive and dispProc.poll() is not None:
            print("Dispatcher has terminated")
            dispActive = False
            rrServer.SendRequest( {"server": {"action": "show"}})    


