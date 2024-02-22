HyYdPt = "HyYdPt"
LaKr   = "LaKr"
NaCl   = "NaCl"

screensList = [HyYdPt, LaKr, NaCl]

# block statuses
EMPTY = 0
OCCUPIED = 1
CLEARED = 2

# block types
BLOCK = 10
OVERSWITCH = 11
STOPPINGBLOCK = 12

# turnout status
NORMAL = 20
REVERSE = 21

# turnout types
TURNOUT = 30
SLIPSWITCH = 31

# basic signal aspects
STOP = 0b000
CLEAR= 0b011

# route types
MAIN = 40
SLOW = 41
DIVERGING = 42
RESTRICTING = 43

# aspect types
RegAspects = 50
RegSloAspects = 51
AdvAspects = 52
SloAspects = 53

def turnoutstate(st, short=False):
	if st == NORMAL:
		return "Nml" if short else "Normal"
	if st == REVERSE:
		return "Rev" if short else "Reverse"
	
	return "??"

def statusname(status):
	if status == EMPTY:
		return "EMPTY"
	
	elif status == "OCCUPIED":
		return "OCCUPIED"
	
	elif status == CLEARED:
		return "CLEARED"
	
	else:
		return "None"

def aspectname(aspect, atype):
	if atype == RegAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Medium Clear"

		elif aspect == 0b110:
			return "Approach Slow"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == RegSloAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b111:
			return "Slow clear"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Slow Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == AdvAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Clear"

		elif aspect == 0b110:
			return "Advance Approach"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == SloAspects:
		if aspect == 0b01:
			return "Slow Clear"

		elif aspect == 0b11:
			return "Slow Approach"

		elif aspect == 0b10:
			return "Restricting"

		else:
			return "Stop"

	else:
		return "Stop"

def aspectprofileindex(aspect, atype):
	""" 
	return the index used to determine maximum speed from a locomotive's profile
	the return value ranges from 0 - the least permissive (stop)
	to 3 for the most permissive (clear)
	"""
	if atype == RegAspects:
		if aspect == 0b011:
			return 3 # Clear
		
		elif aspect == 0b010:
			return 2 # Approach Medium
		
		elif aspect == 0b111:
			return 2 # Medium Clear
		
		elif aspect == 0b110:
			return 1 # Approach Slow
		
		elif aspect == 0b001:
			return 2 # Approach
		
		elif aspect == 0b101:
			return 2 # Medium Approach
		
		elif aspect == 0b100:
			return 1 # Restricting
		
		else:
			return 0 # Stop
	
	elif atype == RegSloAspects:
		if aspect == 0b011:
			return 3 # Clear
		
		elif aspect == 0b111:
			return 2 # Slow clear
		
		elif aspect == 0b001:
			return 2 # Approach
		
		elif aspect == 0b101:
			return 1 # Slow Approach
		
		elif aspect == 0b100:
			return 1 # Restricting
		
		else:
			return 0 # Stop
	
	elif atype == AdvAspects:
		if aspect == 0b011:
			return 3 # Clear
		
		elif aspect == 0b010:
			return 2 # Approach Medium
		
		elif aspect == 0b111:
			return 3 # Clear
		
		elif aspect == 0b110:
			return 2 # Advance Approach
		
		elif aspect == 0b001:
			return 2 # Approach
		
		elif aspect == 0b101:
			return 2 # Medium Approach
		
		elif aspect == 0b100:
			return 1 # Restricting
		
		else:
			return 0 # Stop
	
	elif atype == SloAspects:
		if aspect == 0b01:
			return 2 # Slow Clear
		
		elif aspect == 0b11:
			return 1 # Slow Approach
		
		elif aspect == 0b10:
			return 1 # Restricting
		
		else:
			return 0 #cStop
	
	else:
		return 0 # Stop
	
def restrictedaspect(atype):
	return 0b10 if atype == SloAspects else 0b100

def aspecttype(atype):
	if atype == RegAspects:
		return "Regular"
	if atype == RegSloAspects:
		return "Reg Slow"
	if atype == AdvAspects:
		return "Advance"
	if atype == SloAspects:
		return "Slow"
	return "unknown"
		
		
def routetype(rtype):
	if rtype == MAIN:
		return "MAIN"
	if rtype == DIVERGING:
		return "DIVERGING"
	if rtype == SLOW:
		return "SLOW"
	if rtype == RESTRICTING:
		return "RESTRICTING"
	
def statustype(stat):
	if stat == CLEARED:
		return "CLEARED"
	else:
		return "NOT CLEARED"
	
