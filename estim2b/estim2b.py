#! /usr/bin/python


import serial
import time
import sys


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
    
    battery = -1
    Aout = -1
    Bout = -1
    Cout = -1
    Dout = -1
    mode = -1
    power = "err"
    joined = -1

    ser = serial

    # device e.g. /dev/ttyUSB0
    def __init__(self, device, baudrate=9600, timeout=0):
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

        self.commErr = True

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
                replyArray = replyString.split(":")
                self.battery = int(replyArray[0])
                self.Aout = int(replyArray[1])/2
                self.Bout = int(replyArray[2])/2
                self.Cout = int(replyArray[3])/2
                self.Dout = int(replyArray[4])/2
                self.mode = int(replyArray[5])/2
                self.power = str(replyArray[6])
                self.joined = int(replyArray[7])
                self.commErr = False

    def getStatus(self):
        e2bstat = "----------------------------" + '\n' + \
        "---  Battery : "+str(self.battery)+" ---" + '\n' + \
        "---  A       : "+str(self.Aout)+" ---" + '\n' + \
        "---  B       : "+str(self.Bout)+" ---" + '\n' + \
        "---  C       : "+str(self.Cout)+" ---" + '\n' + \
        "---  D       : "+str(self.Dout)+" ---" + '\n' + \
        "---  mode    : "+str(self.mode)+" ---" + '\n' + \
        "---  power   : "+str(self.power)+" ---" + '\n' + \
        "---  joined  : "+str(self.joined)+" ---" + '\n' + \
        "----------------------------"
        return e2bstat

    def printStatus(self):
        print self.getStatus()
    
    def get(self):
        replyString = self.ser.readline()
        print replyString
        return replyString
    
    def send(self,sendstring):
        self.ser.write(sendstring+"\n\r")
        time.sleep(0.1) # wait for reply
    
    def ping(self):
        self.ser.flushInput()
        self.send("")
        replyString = self.get()
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
        self.send("J")
    
    def unlinkChannels(self):
        self.send("U")
    
    def setDualOutput(self, level):
        if level < 0 or level > 99:
            print "Err: Invalid output level selected!"
            return False
        linkChannels()
        self.send("A"+str(level))
        unlinkchannels()
        return True
    
    def setOutputs(self, levelA, levelB):
        self.setOutput("A", levelA)
        self.setOutput("B", levelB)
   
    def setFeelings(self, levelC, levelD):
        self.setOutput("C", levelC)
        self.setOutput("D", levelD)

    def kill(self):
        self.send("K")
    
    def reset(self):
        self.send("E")
    
    def setMode(self,modestring):
        modenum = self.modekey[modestring]
        if modenum < 0 or modenum > 13:
            print "Invalid mode"
            return False
        self.send("M"+str(modenum))
        return True
        
# Usage:
#myestim = EStim('/dev/ttyUSB1')

