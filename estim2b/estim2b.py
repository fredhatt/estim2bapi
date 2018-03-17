#! env python


import serial
import time
import sys

'''
TODO: 
* add __call__ printing method to EstimStatus so that we 
  can just call print e2b.status
* add a general set method to Estim, so that we can have
  e2b.set(A=10, B=10, C=10, D=10), then the setOutputs 
  and setFeelings will be shortcuts to set.
* add an enforce_consistency=boolean option to Estim, after
  sending a command get the status from the 2B and check it
  matches what EstimStatus thinks the status should be.
'''

class EstimStatus:

    status = {'battery': None, 'A': None, 'B': None, 'C': None, 'D': None,
              'mode': None, 'power': None, 'joined': None}

    def set(self, battery, A, B, C, D, mode, power, joined):
        stat = locals()
        stat.pop('self', None)
        self.status = stat 

    def _set_kw(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.status[k] = v

    def check(self, battery, A, B, C, D, mode, power, joined):
        ndiff = 0
        for k, v in locals():
            if v == self.status[k]:
                ndiff += 1
        return ndiff

    def _format_status(self):
        e2bstat = "==============================\n"
        for k, v in self.status.iteritems():
            space = " "
            for i in range(8 - len(k)):  k += space
            e2bstat += "  {}: {}\n".format(k, v)
        e2bstat += "=============================="
        return e2bstat

    def get(self, formatted=False):
        if formatted:
            return self._format_status()
        else:
            return self.status

    def update(self, command):
        if len(command) == 0: return True
        if command[0] == 'A':
            self._set_kw(A = int(command[1:])*2)
            return True
        if command[0] == 'B':
            self._set_kw(B = int(command[1:])*2)
            return True
        if command[0] == 'C':
            self._set_kw(C = int(command[1:])*2)
            return True
        if command[0] == 'D':
            self._set_kw(D = int(command[1:])*2)
            return True
        if command[0] == 'J':
            self._set_kw(joined=command[1:])
            return True
        if command[0] == 'M':
            self._set_kw(mode=command[1:])
            return True
        if command[0] == 'H' or command[0] == 'L':
            self._set_kw(power=command[0])
            return True
        return False # unrecognised command
        
    



class Estim:
    modekey = {
    "pulse":0,
    "bounce":1,
    "continuous":2,
    "asplit":3,
    "bsplit":4,
    "wave":5,
    "waterfall":6,
    "squeeze":7,
    "milk":8,
    "throb":9,
    "thrust":10,
    "random":11,
    "step":12,
    "training":13
    }
    
    ser = serial

    # device e.g. /dev/ttyUSB0
    def __init__(self, device, baudrate=9600, timeout=0, verbose=True, dryrun=False):
        if not dryrun:
            try:
                self.ser = serial.Serial(
                    device, 
                    baudrate,
                    timeout=timeout, 
                    bytesize=serial.EIGHTBITS, 
                    parity=serial.PARITY_NONE, 
                    stopbits=serial.STOPBITS_ONE)

            except Exception,e:
                print "Error opening serial device!"
                print e
                exit(1)

            if(self.ser.isOpen()):
                print "Opened serial device."

        self.status = EstimStatus()
        self.commErr = True
        self.verbose = verbose
        self.dryrun = dryrun

        self.ping()
        self.printStatus()

    def status(self):
        self.ping() # force update of status
        self.printStatus()

    def parseReply(self, replyString):
        if not ":" in replyString: #check, if reply isn't empty
                self.commErr = True
                print 'Error communicating with E-stim 2B unit!'
                print '  check connection and power.'
        else:
                self.commErr = False
                r = replyString.split(":")
                self.status.set(int(r[0]), int(r[1])/2, int(r[2])/2, int(r[3])/2, int(r[4])/2,
                                int(r[5]), str(r[6]), int(r[7]))

    def getStatus(self):
        return self.status.get(formatted=True)

    def printStatus(self):
        print self.getStatus()
    
    def getReply(self):
        if self.dryrun:
            replyString = "512:66:00:50:50:1:L:0:0"
        else:
            replyString = self.ser.readline()
        if self.verbose:
            print replyString
        return replyString
    
    def send(self, sendstring):
        self.status.update(sendstring)
        if self.dryrun:
            print "send: {}".format(sendstring)
        else:
            self.ser.write(sendstring+"\n\r")
        #time.sleep(0.1) # shouldn't necessary now
    
    def ping(self):
        if not self.dryrun: self.ser.flushInput()
        self.send("")
        replyString = self.getReply()
        self.parseReply(replyString)
        if self.commErr:
            sys.exit(1)

    # Sets the output level [0,99] of a channel.
    # serobj: the serial object to talk to
    # channel: one of A,B,C,D
    # level: the value between 0-99 to set.
    def setOutput(self, channel, level):
        if level < 0 or level > 99:
            print "Err: Invalid output level selected!"
            return False
        self.send(channel+str(level))
        return True
    
    def setLow(self):
        self.send("L")
    
    def setHigh(self):
        self.send("H")
    
    def linkChannels(self):
        self.send("J1")
    
    def unlinkChannels(self):
        self.send("J0")
    
    def setOutputs(self, levelA=None, levelB=None, kill_after=0):
        '''Sets levelA and levelB is they are specified above. 
           Optionally sets the outputs to 0 after kill_after seconds.'''
        if levelA is not None:
            self.setOutput("A", levelA)
        if levelB is not None:
            self.setOutput("B", levelB)

        if kill_after > 0:
             time.sleep(kill_after)
             self.kill()
   
    def setFeelings(self, levelC=None, levelD=None):
        if levelC is not None:
            self.setOutput("C", levelC)
        if levelD is not None:
            self.setOutput("D", levelD)

    def kill(self):
        self.send("K")
    
    def reset(self):
        self.send("E")
    
    def setMode(self, modestring):
        modenum = self.modekey[modestring]
        if modenum < 0 or modenum > 13:
            print "Invalid mode"
            return False
        self.send("M"+str(modenum))
        return True
        
# Usage:
#myestim = EStim('/dev/ttyUSB1')

