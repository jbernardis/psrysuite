import os
import configparser

INIFILE = "psry.ini"
GLOBAL = "global"

def parseBoolean(val, defaultVal):
    lval = val.lower()
    
    if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
        return True
    
    if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
        return False
    
    return defaultVal

class Settings:
    def __init__(self):
        self.datafolder = os.path.join(os.getcwd(), "data")
        self.inifile = os.path.join(self.datafolder, INIFILE)

        self.ipaddr = "192.168.1.138"
        self.serverport = 9000
        self.socketport = 9001
        self.dccserverport = 9002
        
        self.showcameras = True
        self.pages = 1
        
        self.rrtty = "COM5"
        self.dcctty = "COM6"
        
        self.dccsniffertty = "COM4"

        
        self.cfg = configparser.ConfigParser()
        self.cfg.optionxform = str
        if not self.cfg.read(self.inifile):
            print("Settings file %s does not exist.  Using default values" % INIFILE)
            return
            
        if self.cfg.has_section(GLOBAL):
            for opt, value in self.cfg.items(GLOBAL):
                if opt == 'serverport':
                    try:
                        s = int(value)
                    except:
                        print("invalid value in ini file for server port: (%s)" % value)
                        s = 9000
                    self.serverport = s
                        
                elif opt == 'dccserverport':
                    try:
                        s = int(value)
                    except:
                        print("invalid value in ini file for dcc server port: (%s)" % value)
                        s = 9002
                    self.dccserverport = s
                        
                elif opt == 'socketport':
                    try:
                        s = int(value)
                    except:
                        print("invalid value in ini file for socket port: (%s)" % value)
                        s = 9001
                    self.socketport = s
                        
                elif opt == 'ipaddr':
                    self.ipaddr = value        
        
        else:
            print("Missing global section - assuming defaults")
 
        section = "dispatcher"           
        if self.cfg.has_section(section):
            for opt, value in self.cfg.items(section):
                if opt == 'showcameras':
                    self.showcameras = parseBoolean(value, False)
                    
                elif opt == 'pages':
                    try:
                        s = int(value)
                    except:
                        print("invalid value in ini file for pages: (%s)" % value)
                        s = 3

                    if s not in [1, 3]:
                        print("Invalid values for pages: %d" % s)
                        s = 3
                    self.pages = s
        
        else:
            print("Missing %s section - assuming defaults" % section)

        section = "rrserver"           
        if self.cfg.has_section(section):
            for opt, value in self.cfg.items(section):
                if opt == "rrtty":
                    self.rrtty = value

                elif opt == "dcctty":
                    self.dcctty = value
       
        else:
            print("Missing %s section - assuming defaults" % section)

        section = "dccsniffer"           
        if self.cfg.has_section(section):
            for opt, value in self.cfg.items(section):
                if opt == 'dccsniffertty':
                    self.dccsniffertty = value
       
        else:
            print("Missing %s section - assuming defaults" % section)
