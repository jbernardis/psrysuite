import os, winshell, sys

modules = {
	"server": {
		"name": "PSRY Server",
		"dir":  "server",
		"main": "main.py",
		"desc": "Railroad Server",
		"icon": "server.ico"
	},
	"dispatch": {
		"name": "PSRY Dispatcher",
		"dir":  "dispatcher",
		"main": "main.py",
		"desc": "Dispatcher",
		"icon": "server.ico"
	},
	"simulator": {
		"name": "PSRY Simulator",
		"dir":  "simulator",
		"main": "main.py",
		"desc": "Simulator",
		"icon": "server.ico"
	},
	"autorouter": {
		"name": "PSRY Automatic Router",
		"dir":  "autorouter",
		"main": "main.py",
		"desc": "Automatic Router",
		"icon": "server.ico"
	},
	"trainedit": {
		"name": "PSRY Train Editor",
		"dir":  "traineditor",
		"main": "main.py",
		"desc": "Train Editor",
		"icon": "server.ico"
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
