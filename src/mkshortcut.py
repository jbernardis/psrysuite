import os, winshell, sys

modules = {
	"rrserver": {
		"name": "PSRY Server",
		"dir":  "rrserver",
		"main": "main.py",
		"desc": "Railroad Server",
		"icon": "server.ico"
	},
	"dispatch": {
		"name": "PSRY Dispatcher",
		"dir":  "dispatcher",
		"main": "main.py",
		"desc": "Dispatcher",
		"icon": "dispatch.ico"
	},
	"simulator": {
		"name": "PSRY Simulator",
		"dir":  "simulator",
		"main": "main.py",
		"desc": "Simulator",
		"icon": "simulator.ico"
	},
	"trainedit": {
		"name": "PSRY Train Editor",
		"dir":  "traineditor",
		"main": "main.py",
		"desc": "Train Editor",
		"icon": "editor.ico"
	},
	"tester": {
		"name": "PSRY Tester Utility",
		"dir":  "tester",
		"main": "main.py",
		"desc": "Tester",
		"icon": "tester.ico"
	}
}

psrypath = os.getcwd()
python = sys.executable.replace("python.exe", "pythonw.exe")

desktop = winshell.desktop()
for module in modules:
	link_path = os.path.join(desktop, "%s.lnk" % modules[module]["name"])
	pyfile = os.path.join(psrypath, modules[module]["dir"], modules[module]["main"])

	with winshell.shortcut(link_path) as link:
		link.path = python
		link.arguments = pyfile
		link.working_directory = psrypath
		link.description = modules[module]["desc"]
		link.icon_location = (os.path.join(psrypath, "icons", modules[module]["icon"]), 0)
		link.dump(1)
