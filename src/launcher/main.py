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
    mode = "dispatcher"

else:
    mode = sys.argv[1]
        
ofp = open("launch%s.out" % mode, "w")
efp = open("launch%s.err" % mode, "w")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()

rrServer = RRServer()
rrServer.SetServerAddress(settings.ipaddr, settings.serverport)

interpreter = sys.executable.replace("python.exe", "pythonw.exe")
 
for i in range(len(sys.argv)):
    print("%d: %s" % (i, sys.argv[i]))

if mode == "remotedispatcher":
    print("Launch mode: remote dispatcher")
    
    settings.SetSimulation(False)
    settings.SetDispatcher(True)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([sys.executable, dispExec])
    print("dispatcher started as PID %d" % dispProc.pid)
 
    dispActive = True   
    while dispActive:
        time.sleep(1)
            
        if dispActive and dispProc.poll() is not None:
            print("Dispatcher has terminated")
            dispActive = False
 
elif mode == "dispatcher":
    print("Launch mode: dispatcher")
    
    settings.SetSimulation(False)
    settings.SetDispatcher(True)
    
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

elif mode == "simulation":
    print("launch mode: simulation")
    settings.SetDispatcher(True)
    settings.SetSimulation(True)
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([sys.executable, svrExec])
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

elif mode == "display":
    print("launch mode: display")
    settings.SetDispatcher(False)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([sys.executable, dispExec])
    print("dispatcher started as PID %d" % dispProc.pid)
 
    dispActive = True   
    while dispActive:
        time.sleep(1)
            
        if dispActive and dispProc.poll() is not None:
            print("Dispatcher has terminated")
            dispActive = False
            
else:
    print("Unknown mode.  Must specify either 'dispatch', 'remote dispatch', 'simulation', or 'display'")
 

