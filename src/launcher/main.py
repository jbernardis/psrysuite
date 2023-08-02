import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
    sys.path.insert(0, cmdFolder)
 

from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW, DEVNULL
   
from launcher.settings import Settings

SW_MINIMIZE = 6
infoMinimize = STARTUPINFO()
infoMinimize.dwFlags = STARTF_USESHOWWINDOW
infoMinimize.wShowWindow = SW_MINIMIZE

np = len(sys.argv)

if np < 2:
    mode = "dispatcher"

else:
    mode = sys.argv[1]
        
ofp = open(os.path.join(os.getcwd(), "output", ("launch%s.out" % mode)), "w")
efp = open(os.path.join(os.getcwd(), "output", ("launch%s.err" % mode)), "w")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()

interpreter = sys.executable.replace("python.exe", "pythonw.exe")
interpfg    = sys.executable.replace("pythonw.exe", "python.exe")
 
for i in range(len(sys.argv)):
    print("%d: %s" % (i, sys.argv[i]))

if mode == "remotedispatcher":
    print("Launch mode: remote dispatcher")
    
    settings.SetSimulation(False)
    settings.SetDispatcher(True)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
 
elif mode == "dispatcher":
    print("Launch mode: dispatcher suite")
    
    settings.SetSimulation(False)
    settings.SetDispatcher(True)
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
 
elif mode == "simulation":
    print("launch mode: simulation")
    settings.SetDispatcher(True)
    settings.SetSimulation(True)
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)
    
    simExec = os.path.join(os.getcwd(), "simulator", "main.py")
    simProc = Popen([interpreter, simExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("simulator started as PID %d" % simProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
    
    monExec = os.path.join(os.getcwd(), "monitor", "main.py")
    monProc = Popen([interpreter, monExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("monitor started as PID %d" % monProc.pid)

elif mode == "display":
    print("launch mode: display")
    settings.SetDispatcher(False)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
            
elif mode == "dispatcheronly":
    print("launch mode: dispatcher only")
    settings.SetDispatcher(True)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
             
elif mode == "serveronly":
    print("launch mode: server only")
    settings.SetSimulation(False)
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)
            
else:
    print("Unknown mode.  Must specify either 'dispatcher', 'remote dispatch', 'simulation', 'display', 'dispatcheronly', 'serveronly")
    
print("launcher exiting")  

 

