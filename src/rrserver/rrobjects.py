import logging

from rrserver.constants import INPUT_BLOCK, INPUT_BREAKER, INPUT_SIGNALLEVER, INPUT_ROUTEIN, INPUT_HANDSWITCH, INPUT_TURNOUTPOS
from dispatcher.constants import RegAspects

class Block:
    def __init__(self, name, district, node, address, east):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.east = east
        self.bits = []
        self.cleared = False
        self.occupied = False
        self.indicators = []
        self.mainBlock = None
        self.mainBlockName = None
        self.subBlocks = []
        self.stoppingBlocks = []
        self.stoppedBlock = None
   
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def District(self):
        return self.district
    
    def InputType(self):
        return INPUT_BLOCK
               
    def dump(self):
        addr = "None" if self.address is None else ("%x" % self.address)
        logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
        logging.info("     east: %s   occupied: %s   cleared: %s  indicators: %s" % (str(self.east), str(self.occupied), str(self.cleared), str(self.indicators)))
        if self.district is None:
            logging.info("<===== NULL BLOCK DEFINITION")

    def IsNullBlock(self):
        return self.district is None
    
    def SetBlockAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
    
    def SetMainBlock(self, blk):
        self.mainBlockName = blk.Name()
        self.mainBlock = blk
        
    def AddSubBlocks(self, blkl):
        self.subBlocks.extend(blkl)
        for b in blkl:
            b.SetMainBlock(self)
        
    def SubBlocks(self):
        return self.subBlocks
        
    def AddStoppingBlocks(self, sbl):
        self.stoppingBlocks.extend(sbl)
        for sb in sbl:
            sb.SetStoppedBlock(self)
            
    def StoppingBlocks(self):
        return self.stoppingBlocks
        
    def SetStoppedBlock(self, blk):
        self.stoppedBlock = blk
        
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
    
    def SetDirection(self, east):
        if self.east == east:
            return False
        
        self.east = east
        return True
        
    def IsEast(self):
        return self.east
    
    def SetOccupied(self, flag):
        if self.occupied == flag:
            return False
        
        self.occupied = flag
        return True

        
    def IsOccupied(self, recurse=True):
        if recurse and self.mainBlock is not None:
            return self.mainBlock.IsOccupied(recurse=False)
        
        '''
        for a block that is subdivided into subblocks, occupied reflects the status of all subblocks or'ed together
        '''
        occ = self.occupied
        for b in self.subBlocks:
            occ = True if b.IsOccupied(recurse=False) else occ
            
        return occ
    
    def SetCleared(self, flag):
        if self.cleared == flag:
            return False
        
        self.cleared = flag
        return True
        
    def IsCleared(self, recurse=True):
        if recurse and self.mainBlock is not None:
            return self.mainBlock.IsCleared(recurse=False)
        '''
        for a block that is subdivided into subblocks, cleared reflects the status of all subblocks or'ed together
        '''
        clr = self.cleared
        for b in self.subBlocks:
            clr = True if b.IsCleared(recurse=False) else clr
            
        return clr
    
    def AddIndicator(self, district, node, address, bits):
        self.indicators.append((district, node, address, bits))
        
    def UpdateIndicators(self):
        '''
        make indicators show the status of this and any stoppingBlocks all or'ed together
        '''
        parentBlk = self
        if self.stoppedBlock is not None:
            parentBlk = self.stoppedBlock
        elif self.mainBlock is not None:
            parentBlk = self.mainBlock
             
        occ = parentBlk.IsOccupied() # the occupancy status of the block and all sublocks
             
        for sb in parentBlk.StoppingBlocks():
            occ = True if sb.IsOccupied(recurse=False) else occ
 
        for ind in parentBlk.indicators:
            district, node, address, bits = ind
            if len(bits) > 0:
                node.SetOutputBit(bits[0][0], bits[0][1], occ)
                
    def GetEventMessages(self):
        return [self.GetEventMessage(), self.GetEventMessage(clear=True), self.GetEventMessage(direction=True)]
 
    def GetEventMessage(self, clear=False, direction=False):
        bname = self.mainBlockName if self.mainBlockName is not None else self.name

        if clear:
            return {"blockclear": [{ "block": bname, "clear": self.IsCleared()}]}
        if direction:
            return {"blockdir": [{ "block": bname, "dir": "E" if self.east else "W"}]}
        else:
            return {"block": [{ "name": bname, "state": self.IsOccupied()}]}
        
class StopRelay:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.activated = False
         
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
        
    def Activate(self, flag):
        self.activated = flag
        
    def IsActivated(self):
        return self.activated
    
    def GetEventMessages(self):
        return [self.GetEventMessage()]
    
    def GetEventMessage(self):
        return {"relay": [{ "name": self.name, "state": 1 if self.activated else 0}]}
       

class Breaker:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.bits = []
        self.status = True  # not tripped
        self.indicators = []
        self.proxy = None   # proxy - this breaker shows its status via a proxy breaker
        
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def InputType(self):
        return INPUT_BREAKER
        
    def IsNullBreaker(self):
        return self.district is None
    
    def SetBreakerAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
        
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
     
    def SetStatus(self, flag):
        if self.status == flag:
            return False
        
        self.status = flag
        return True
    
    def SetTripped(self, flag):
        return self.SetStatus(not flag)
    
    def SetOK(self, flag):
        return self.SetStatus(flag)
   
    def SetProxy(self, bname):
        self.proxy = bname
        
    def HasProxy(self):
        return self.proxy is not None
    
    def IsTripped(self):
        return not self.status
        
    def IsOK(self):
        return self.status
    
    def AddIndicator(self, district, node, address, bits):
        self.indicators.append((district, node, address, bits))
       
    def UpdateIndicators(self):
        if len(self.indicators) == 0:
            return False
        
        for ind in self.indicators:
            district, node, address, bits = ind
            if len(bits) > 0:
                node.SetOutputBit(bits[0][0], bits[0][1], 0 if self.status else 1)
        return True

    def GetEventMessage(self):
        return {"breaker": [{ "name": self.name, "value": 1 if self.status else 0}]}
       
    def dump(self):
        addr = "None" if self.address is None else ("%x" % self.address)
        logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
        logging.info("     status: %s " % (str(self.status)))
        logging.info("     # indicators:    %d" % len(self.indicators))
        if self.district is None:
            logging.info("<===== NULL BREAKER DEFINITION")

class Indicator:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.status = False
         
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
        
    def SetOn(self, flag):
        self.status = flag
        
    def IsOn(self):
        return self.status
    
    def GetEventMessage(self):
        return {"indicator": [{ "name": self.name, "state": 1 if self.status else 0}]}
    
class ODevice:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.status = False
         
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
        
    def SetOn(self, flag):
        if self.status == flag:
            return False
    
        self.status = flag
        return True
        
    def IsOn(self):
        return self.status
    
class Lock:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.status = False
         
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
        
    def SetOn(self, flag):
        if self.status == flag:
            return False
        
        self.status = flag
        return True
        
    def IsOn(self):
        return self.status
    

class Signal:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.aspect = 0
        self.aspectType = RegAspects
        self.bits = []
        self.led = []
        self.locked = False
        self.lockBits = []
        self.indicators = []

    def IsNullSignal(self):
        return self.district is None
     
    def SetSignalAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
        
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
    
    def SetAspect(self, aspect):
        if self.aspect == aspect:
            return False
        
        self.aspect = aspect
        return True
    
    def SetAspectType(self, atype):
        self.aspectType = atype
        
    def GetAspectType(self):
        return self.aspectType
        
    def Aspect(self):
        return self.aspect
    
    def Name(self):
        return self.name
    
    def SetLockBits(self, bits):
        self.lockBits = bits
        
    def LockBits(self):
        return self.lockBits

    def Lock(self, locked):
        if self.locked == locked:
            return False
        
        self.locked = locked
        return True
        
    def IsLocked(self):
        return self.locked
    
    def AddIndicator(self, district, node, address, bits):
        self.indicators.append((district, node, address, bits))
        
    def UpdateIndicators(self):
        for ind in self.indicators:
            district, node, address, bits = ind
            if len(bits) > 0:
                node.SetOutputBit(bits[0][0], bits[0][1], 1 if self.aspect != 0 else 0)
                
    def GetEventMessages(self):
        return [self.GetEventMessage(), self.GetEventMessage(lock=True)]
    
    def GetEventMessage(self, lock=False, callon=False):
        if lock:
            return {"signallock": [{ "name": self.name, "state": 1 if self.locked else 0}]}
        else:
            return {"signal": [{ "name": self.name, "aspect": self.aspect, "aspecttype": self.aspectType, "callon": 1 if callon else 0}]}
        
    def dump(self):
        addr = "None" if self.address is None else ("%x" % self.address)
        logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
        logging.info("     LED: %s   locked: %s/%s" % (str(self.led), str(self.locked), str(self.lockBits)))
        if self.district is None:
            logging.info("<===== NULL SIGNAL DEFINITION")

'''
signal lever is a separate class because there is only 1 signal lever for each grouping of Lx and Rx signals
'''
class SignalLever:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.led = None
        self.state = "N"
        self.callon = False
        self.bits = []

    def IsNullLever(self):
        return self.district is None
    
    def SetLeverAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
    
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def InputType(self):
        return INPUT_SIGNALLEVER
          
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
     
    def SetLed(self, bits, district, node, addr):
        self.led = [bits, district, node, addr]
        self.UpdateLed()
        
    def LedBits(self):
        return self.led
    
    def SetLever(self, bits):
        self.bits = bits
        
    def LeverBits(self):
        return self.bits
    
    def SetLeverState(self, rbit, cbit, lbit):
        self.callon = cbit == 1
        nstate = self.state
        if lbit is not None and lbit != 0:
            nstate = "L"
        elif rbit is not None and rbit != 0:
            nstate = "R"
        elif (lbit is None or lbit == 0) and (rbit is None or rbit == 0):
            nstate = "N"

        if nstate != self.state:
            self.state = nstate
            return True
        
        return False
    
    def UpdateLed(self):
        if self.led is not None:
            bits, district, node, addr = self.led
            bt = bits[0]
            if bt:
                node.SetOutputBit(bt[0], bt[1], 1 if self.state == 'R' else 0)
            bt = bits[1]
            if bt:
                node.SetOutputBit(bt[0], bt[1], 1 if self.state not in ["L", "R"] else 0)
            bt = bits[2]
            if bt:
                node.SetOutputBit(bt[0], bt[1], 1 if self.state == 'L' else 0)
                
    def GetEventMessages(self):
        return [self.GetEventMessage()]
       
    def GetEventMessage(self):
        return {"siglever": [{ "name": self.name+".lvr", "state": self.state, "callon": 1 if self.callon else 0}]}


class RouteIn:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.state = False
   
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def InputType(self):
        return INPUT_ROUTEIN
    
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
     
    def SetState(self, state):
        self.state = state
        
    def GetState(self):
        return self.state
    
    def GetEventMessage(self):
        return None

 
class Turnout:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.normal = True
        self.lastReadNormal = None
        self.bits = []
        self.led = None
        self.lever = []
        self.position = None
        self.leverState = 'N'
        self.locked = False
        self.lockBits = []
        self.force = False
        self.lockBitValue = 0
   
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def InputType(self):
        return INPUT_TURNOUTPOS
        
    def dump(self):
        addr = "None" if self.address is None else ("%x" % self.address)
        logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
        logging.info("     normal: %s   locked: %s/%s" % (str(self.normal), self.locked, str(self.lockBits)))
        logging.info("     led:    %s" % str(self.led))
        logging.info("     lever:  %s/%s" % (self.leverState, str(self.lever)))
        logging.info("     pos:    %s" % self.position)
        if self.district is None:
            logging.info("<===== NULL TURNOUT DEFINITION")

    def IsNullTurnout(self):
        return self.district is None
    
    def SetTurnoutAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
        
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
    
    def SetNormal(self, normal):
        if self.normal == normal:
            return False
        
        self.normal = normal
        return True
        
    def IsNormal(self):
        return self.normal
    
    def SetLed(self, bits, district, node, addr):
        self.led = [bits, district, node, addr]
        self.UpdateLed()
        
    def LedBits(self):
        return self.led
     
    def UpdateLed(self):
        if self.led is not None:
            bits, district, node, addr = self.led
            bt = bits[0]
            if bt:
                node.SetOutputBit(bt[0], bt[1], 1 if self.normal else 0)
            bt = bits[1]
            if bt:
                node.SetOutputBit(bt[0], bt[1], 0 if self.normal else 1)
   
    def SetLever(self, bits, district, node, addr):
        self.lever = [bits, district, node, addr]
        
    def LeverBits(self):
        return self.lever
    
    def HasLever(self):
        return len(self.lever) > 0
    
    def SetLeverState(self, state):
        if state != self.leverState:
            self.leverState = state
            return True
        
        return False
    
    def SetPosition(self, bits, district, node, addr):
        self.position = [bits, district, node, addr]
        node.SetInputBit(bits[0][0], bits[0][1], 1)
        
    def Position(self):
        return self.position
    
    def SetLockBits(self, bits, district, node, addr):
        self.lockBits = [bits, district, node, addr]
        
    def UpdateLockBits(self, release=False):
        if len(self.lockBits) == 0:
            return
        bits, district, node, addr = self.lockBits
        
        newLockBit = 0 if release else 1 if self.locked else 0
        if newLockBit != self.lockBitValue:
            node.SetOutputBit(bits[0][0], bits[0][1], newLockBit)
            self.lockBitValue = newLockBit
      
    def LockBits(self):
        return self.lockBits
    
    def Lock(self, locked):
        if self.locked == locked:
            return False
        
        self.locked = locked
        return True
        
    def IsLocked(self):
        return self.locked
    
    def GetEventMessages(self):
        return [self.GetEventMessage(), self.GetEventMessage(lock=True)]
        
    def GetEventMessage(self, lock=False, force=False):
        self.force = force
        if lock:
            return {"turnoutlock": [{ "name": self.name, "state": 1 if self.locked else 0}]}
        else:
            return {"turnout": [{ "name": self.name, "state": "N" if self.normal else "R", "force": self.force}]}
 
class OutNXButton:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.bits = []
        
    def Name(self):
        return self.name
        
    def SetBits(self, bits):
        self.bits = bits
        
    def Bits(self):
        return self.bits
   
class Handswitch:
    def __init__(self, name, district, node, address):
        self.name = name
        self.district = district
        self.node = node
        self.address = address
        self.normal = True
        self.bits = []
        self.indicators = []
        self.locked = False
        self.reverseIndicators = []
        self.unlock = None
   
    def Name(self):
        return self.name
        
    def Address(self):
        return self.address
    
    def District(self):
        return self.district
    
    def InputType(self):
        return INPUT_HANDSWITCH
        
    def dump(self):
        addr = "None" if self.address is None else ("%x" % self.address)
        logging.info("%s: district: %s  addr: %s" % (self.name, "None" if self.district is None else self.district.name, addr))
        logging.info("     normal: %s   locked: %s" % (str(self.normal), self.locked))
        logging.info("     ind:    %s" % str(self.indBits))
        logging.info("     pos:    %s" % self.bits)

        if self.district is None:
            logging.info("<===== NULL HANDSWITCH DEFINITION")

    def IsNullHandswitch(self):
        return self.district is None
    
    def SetHandswitchAddress(self, district, node, address):
        self.district = district
        self.node = node
        self.address = address
    
    def SetNormal(self, normal):
        if self.normal == normal:
            return False
        
        self.normal = normal
        self.UpdateReverseIndicators()
        return True
        
    def IsNormal(self):
        return self.normal
    
    def AddIndicator(self, district, node, addr, bits, inverted):
        self.indicators.append([district, node, addr, bits, inverted])
        self.UpdateIndicators()
   
    def UpdateIndicators(self):
        if len(self.indicators) == 0:
            return False
        # indicators with one bit: simple on/off led to show lock status
        # indicators with 2 bits: panel indicators with one being the inverted value of the other
        lval = 1 if self.locked else 0
        for ind in self.indicators:
            district, node, address, bits, inverted = ind
            if len(bits) == 1:
                node.SetOutputBit(bits[0][0], bits[0][1], 1-lval if inverted else lval)
            elif len(bits) == 2:
                node.SetOutputBit(bits[0][0], bits[0][1], 1-lval if inverted else lval)
                node.SetOutputBit(bits[1][0], bits[1][1], lval if inverted else 1-lval)
            else:
                logging.warning("Hand switch indicator for %s has an unexpected number of bits")
            
        return True
   
    def AddReverseIndicator(self, district, node, addr, bits):
        self.reverseIndicators.append([district, node, addr, bits])
        self.UpdateReverseIndicators()
   
    def UpdateReverseIndicators(self):
        if len(self.reverseIndicators) == 0:
            return False
        rval = 0 if self.normal else 1
        for ind in self.reverseIndicators:
            district, node, address, bits = ind
            if len(bits) == 1:
                node.SetOutputBit(bits[0][0], bits[0][1], rval)
            
        return True
  
    def AddUnlock(self, district, node, addr, bits):
        self.unlock = [district, node, addr, bits]
        
    def GetUnlock(self):
        return self.unlock

    def SetBits(self, bits):
        self.bits = bits  # the position is where we read the switch position
        self.node.SetInputBit(bits[0][0], bits[0][1], 1)
        
    def Bits(self):
        return self.bits
        
    def Position(self):
        return [self.district, self.node, self.address, self.bits]
    
    def Lock(self, locked):
        if self.locked == locked:
            return False
        
        self.locked = locked
        return True
        
    def IsLocked(self):
        return self.locked
        
    def GetEventMessage(self, lock=False):
        if lock:
            return {"handswitch": [{ "name": self.name+".hand", "state": 1 if self.locked else 0}]}
        else:
            return {"turnout": [{ "name": self.name, "state": "N" if self.normal else "R"}]}
 


