#! env python

import serial
import time
import sys
import platform

'''
TODO: 
* add an enforce_consistency=boolean option to Estim, after
  sending a command get the status from the 2B and check it
  matches what EstimStatus thinks the status should be.
'''

class EstimStatus:

    status = {'battery': None, 'A': None, 'B': None, 'C': None, 'D': None,
              'mode': None, 'power': None, 'joined': None}
                
    keys = ['battery', 'A', 'B', 'C', 'D', 'mode', 'power', 'joined']

    def parseReply(self, replyString):
        print(replyString)
        print(replyString.decode())
        if not ":" in replyString: #check, if reply isn't empty
                print('Error communicating with E-stim 2B unit!')
                print('  check connection and power.')
                return False
        else:
                r = replyString.split(":")
                status_dict = {}
                for i, key in enumerate(self.keys):
                    if i == 6:
                        status_dict[key] = str(r[i])
                    else:
                        status_dict[key] = int(r[i])
                return status_dict

                #self.status.set(int(r[0]), int(r[1])/2, int(r[2])/2, int(r[3])/2, int(r[4])/2,
                #                int(r[5]), str(r[6]), int(r[7]))

    def set(self, battery, A, B, C, D, mode, power, joined):
        stat = locals()
        stat.pop('self', None)
        self.status = stat 

    def _set_kw(self, **kwargs):
        for k, v in kwargs.items():
            self.status[k] = v

    def check(self, battery=None, A=None, B=None, C=None, D=None, mode=None, power=None, joined=None):
        ndiff = 0
        for k, v in locals():
            if v is None: continue
            if v == self.status[k]:
                ndiff += 1
        return ndiff

    def _getstr(self):
        return "{}:{}:{}:{}:{}:{}:{}:00".format(self.status['battery'], self.status['A'], self.status['B'],
            self.status['C'], self.status['D'], self.status['mode'], self.status['power'], self.status['joined'])

    def _format_status(self):
        e2bstat = "==============================\n"
        for k, v in self.status.items():
            space = " "
            for i in range(8 - len(k)):  k += space
            e2bstat += "  {}: {}\n".format(k, v)
        e2bstat += "=============================="
        return e2bstat

    def __call__(self, formatted=False, string=False):
        if string:
            return self._getstr()
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
    def __init__(self, device='auto', baudrate=9600, timeout=0, verbose=True, dryrun=False, check_command=False, delay=0.05):
        if device == 'auto':
            if platform.system() == 'Darwin': device = '/dev/tty.usbserial-FTGD2KUC'
            if platform.system() == 'Linux': device = '/dev/ttyUSB0'
        if not dryrun:
            try:
                self.ser = serial.Serial(
                    device, 
                    baudrate,
                    timeout=timeout, 
                    bytesize=serial.EIGHTBITS, 
                    parity=serial.PARITY_NONE, 
                    stopbits=serial.STOPBITS_ONE)

            except Exception as e:
                print("Error opening serial device!")
                raise(e)

            if(self.ser.isOpen()):
                print("Opened serial device.")
        else:
            print('Running in dryrun mode.')

        self.status = EstimStatus()
        self.commErr = False
        self.verbose = verbose
        self.dryrun = dryrun
        self.check_command = check_command
        self.delay = delay

        #self.printStatus()

    def getStatus(self, formatted=True, check=None):
        ''' Gets the status from the 2B '''
        if not self.dryrun: self.ser.flushInput()
        self.send("")
        replyString = self.recv()
        status_dict = self.status.parseReply(replyString)
        if self.verbose:
            print(replyString)
        if self.commErr or not status_dict:
            print('comm error', self.commErr, status_dict)
            sys.exit(1)
        return status_dict

    def recv(self):
        time.sleep(self.delay)
        if self.dryrun:
            replyString = "512:66:00:50:50:1:L:0:0"
        else:
            replyString = self.ser.readline()
        if self.verbose:
            print(replyString)
        return replyString
    
    def send(self, sendstring):
        self.status.update(sendstring)
        if self.verbose:
            print("send: {}".format(sendstring),)
        if self.dryrun:
            print
        else:
            command = sendstring+"\n\r"
            self.ser.write(command.encode())
            print('(send complete).')
        time.sleep(self.delay)
            

    # Sets the output level [0, 99] of a channel.
    # serobj: the serial object to talk to
    # channel: one of A,B,C,D
    # level: the value between 0-99 to set.
    def setOutput(self, channel, level):
        print('setOutput: {} ({}): {} ({})'.format(channel, level, type(channel), type(level)))
        if channel in ['A', 'B']:
            if level < 0 or level > 100:
                print("Err: Invalid output level selected! A (or B) must be in range 0 to 100.")
                return False
        if channel in ['C', 'D']:
            if level < 2 or level > 100:
                print("Err: Invalid output level selected! C (or D) must be in range 2 to 100.")
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

    def set(self, A=None, B=None, C=None, D=None):
        if A is not None:
            self.setOutput("A", A)
        if B is not None:
            self.setOutput("B", B)
        if C is not None:
            self.setOutput("C", C)
        if D is not None:
            self.setOutput("D", D)
    
    def setOutputs(self, A=None, B=None, kill_after=0):
        '''Sets levelA and levelB is they are specified above. 
           Optionally sets the outputs to 0 after kill_after seconds.'''
        self.set(A=A, B=B)

        if kill_after > 0:
             time.sleep(kill_after)
             self.kill()
   
    def setFeelings(self, C=None, D=None):
        self.set(C=C, D=D)

    def kill(self):
        self.send("K")
    
    def reset(self):
        self.send("E")
    
    def setMode(self, modestring):
        modenum = self.modekey[modestring]
        if modenum < 0 or modenum > 13:
            print("Invalid mode")
            return False
        self.send("M"+str(modenum))
        return True
        
# Usage:
#myestim = EStim('/dev/ttyUSB1')

